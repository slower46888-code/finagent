# -*- coding: utf-8 -*-
"""RAG 核心引擎：文档解析 → 分块 → 索引构建 → 检索 → 大模型问答"""
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import jieba
import chromadb
from rank_bm25 import BM25Okapi

import config

SUPPORTED_SUFFIXES = (".md", ".txt", ".pdf", ".docx")


# ---------- 1. 文档加载 ----------
def load_document(path: Path) -> str:
    """按文件类型解析文本：markdown/txt/pdf/docx"""
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt"):
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if suffix == ".docx":
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    return ""


# ---------- 2. 文本分块 ----------
def split_text(text: str, max_len: int = 600) -> List[str]:
    """按段落合并分块，保证每个分块语义完整（适合中文文档）"""
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if current and len(current) + len(p) + 1 > max_len:
            chunks.append(current)
            current = p
        else:
            current = f"{current}\n{p}" if current else p
    if current:
        chunks.append(current)
    return chunks


# ---------- 3. RAG 引擎 ----------
class RAGEngine:
    def __init__(self):
        config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(config.INDEX_DIR))
        self.col = self._client.get_or_create_collection("fin_docs")
        self.bm25 = None
        self.bm25_entries: List[dict] = []   # [{id, text, source}]
        self.use_embeddings = bool(config.SILICONFLOW_API_KEY)
        self.emb_client = None
        self.llm_client = None
        if self.use_embeddings:
            from openai import OpenAI
            self.emb_client = OpenAI(
                api_key=config.SILICONFLOW_API_KEY, base_url=config.SILICONFLOW_BASE_URL
            )
        if config.DEEPSEEK_API_KEY:
            from openai import OpenAI
            self.llm_client = OpenAI(
                api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL
            )
        self._refresh_bm25()

    # ----- 索引构建 -----
    def _doc_state_hash(self) -> str:
        """根据文件名+大小+修改时间计算知识库状态指纹，用于检测文档变化"""
        h = hashlib.md5()
        for f in sorted(config.DOCS_DIR.glob("*")):
            if f.suffix.lower() in SUPPORTED_SUFFIXES:
                st = f.stat()
                h.update(f"{f.name}|{st.st_size}|{st.st_mtime}".encode())
        return h.hexdigest()

    def build(self, force: bool = False) -> int:
        """构建/增量更新知识库索引。force=True 强制重建；否则仅在文档变化时重建。"""
        config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
        state_file = config.INDEX_DIR / "state.txt"
        current_state = self._doc_state_hash()
        if not force and state_file.exists() and state_file.read_text() == current_state and self.col.count() > 0:
            return self.col.count()
        # 重建索引
        self._client.delete_collection("fin_docs")
        self.col = self._client.get_or_create_collection("fin_docs")
        files = [f for f in sorted(config.DOCS_DIR.glob("*")) if f.suffix.lower() in SUPPORTED_SUFFIXES]
        ids, documents, metadatas = [], [], []
        for f in files:
            text = load_document(f)
            if not text:
                continue
            for i, chunk in enumerate(split_text(text)):
                ids.append(f"{f.name}::{i}")
                documents.append(chunk)
                metadatas.append({"source": f.name, "chunk": i})
        if not ids:
            state_file.write_text(current_state)
            return 0
        embeddings = self._embed(documents) if self.use_embeddings else None
        self.col.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        state_file.write_text(current_state)
        self._refresh_bm25()
        return len(ids)

    # ----- 向量化 -----
    def _embed(self, texts: List[str]) -> List[List[float]]:
        out = []
        for i in range(0, len(texts), 32):
            resp = self.emb_client.embeddings.create(model=config.EMBED_MODEL, input=texts[i:i + 32])
            out.extend([d.embedding for d in resp.data])
        return out

    # ----- 关键词检索索引（BM25，用于混合检索和无向量 API 时的降级）-----
    def _refresh_bm25(self):
        got = self.col.get()
        self.bm25_entries = []
        for cid, doc, meta in zip(got["ids"] or [], got["documents"] or [], got["metadatas"] or []):
            if doc:
                self.bm25_entries.append({"id": cid, "text": doc, "source": meta.get("source", "")})
        corpus = [jieba.lcut_for_search(e["text"]) for e in self.bm25_entries]
        self.bm25 = BM25Okapi(corpus) if corpus else None

    # ----- 检索（向量 + BM25 双路，RRF 融合；无向量 API 时仅 BM25）-----
    def retrieve(self, query: str, k: int = 4) -> List[dict]:
        if not self.bm25:
            return []
        tokens = jieba.lcut_for_search(query)
        scores = self.bm25.get_scores(tokens)
        ranked = sorted(range(len(scores)), key=lambda i: -scores[i])
        rrf: Dict[str, float] = {}
        for rank, i in enumerate(ranked[:50]):
            if scores[i] <= 0:
                break
            rrf[self.bm25_entries[i]["id"]] = rrf.get(self.bm25_entries[i]["id"], 0) + 1.0 / (60 + rank)
        if self.use_embeddings:
            try:
                qemb = self._embed([query])[0]
                res = self.col.query(query_embeddings=[qemb], n_results=10)
                for rank, cid in enumerate(res["ids"][0]):
                    rrf[cid] = rrf.get(cid, 0) + 1.0 / (60 + rank)
            except Exception:
                pass  # 向量检索失败时降级为纯关键词检索
        by_id = {e["id"]: e for e in self.bm25_entries}
        top = sorted(rrf.items(), key=lambda x: -x[1])[:k]
        return [
            {"source": by_id[cid]["source"], "text": by_id[cid]["text"]}
            for cid, _ in top
        ]

    # ----- 问答 -----
    def answer(self, question: str, history: Optional[List[dict]] = None) -> Tuple[str, List[dict]]:
        if not self.llm_client:
            return ("⚠️ 未配置 DeepSeek API Key，请联系管理员在 Streamlit 的 Secrets 中配置后重试。", [])
        sources = self.retrieve(question, k=4)
        if sources:
            context = "\n\n".join(
                f"[{i + 1}]（来源：{s['source']}）\n{s['text']}" for i, s in enumerate(sources)
            )
        else:
            context = "（知识库为空或未检索到相关内容）"
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        for m in (history or [])[-6:]:
            if m.get("role") in ("user", "assistant"):
                messages.append({"role": m["role"], "content": m["content"]})
        messages.append({
            "role": "user",
            "content": f"【参考资料】\n{context}\n\n【用户问题】\n{question}",
        })
        try:
            resp = self.llm_client.chat.completions.create(
                model=config.DEEPSEEK_MODEL, messages=messages, temperature=0.3, max_tokens=1500,
            )
            return (resp.choices[0].message.content or "").strip(), sources
        except Exception as e:
            return f"❌ 调用大模型失败：{e}", sources
