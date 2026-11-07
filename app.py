# -*- coding: utf-8 -*-
"""智融投研助手 - Streamlit 主程序：登录、知识库管理、智能问答"""
import streamlit as st

import config
import rag
from ui import inject_css, brand_header, page_header

st.set_page_config(page_title="智融投研助手", page_icon="💹", layout="wide")
inject_css()

# 示例问题（快捷提问，减少误输入）
EXAMPLES = [
    "什么是杜邦分析？",
    "A股创业板涨跌幅限制是多少？",
    "什么是LPR？它如何影响房贷？",
    "ETF和普通指数基金有什么区别？",
]
QUESTION_MAX_LEN = 300


@st.cache_resource
def get_engine() -> rag.RAGEngine:
    engine = rag.RAGEngine()
    engine.build()  # 知识库为空或文档有变化时自动构建索引
    return engine


def render_sources(sources):
    """渲染引用来源折叠面板"""
    with st.expander(f"📚 引用来源（{len(sources)} 条）"):
        for i, s in enumerate(sources, 1):
            st.markdown(f"**[{i}] 来源文档：{s['source']}**\n\n{s['text'][:200]}……")


def submit_question(prompt: str):
    """校验并提交问题：去除首尾空白、长度校验后进入问答流程"""
    prompt = prompt.strip()
    if len(prompt) < 2:
        st.toast("⚠️ 问题太短，请描述得更具体一些", icon="⚠️")
        return
    if len(prompt) > QUESTION_MAX_LEN:
        st.toast(f"⚠️ 问题超过 {QUESTION_MAX_LEN} 字，请精简后重试", icon="⚠️")
        return
    engine = get_engine()
    history = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")][-6:]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("正在检索知识库并生成回答…"):
            answer, sources = engine.answer(prompt, history)
        st.markdown(answer)
        if sources:
            render_sources(sources)
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    st.rerun()


# ================= 登录 =================
if "authed" not in st.session_state:
    st.session_state.authed = False
    st.session_state.user = None
    st.session_state.messages = []

if not st.session_state.authed:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        brand_header()
        with st.form("login_form"):
            st.text_input("账号", placeholder="请输入账号", key="login_user")
            st.text_input("密码", placeholder="请输入密码", type="password", key="login_pwd")
            submitted = st.form_submit_button("登 录", use_container_width=True)
        if submitted:
            account = config.ACCOUNTS.get(st.session_state.login_user.strip())
            if account and account["password"] == st.session_state.login_pwd:
                st.session_state.authed = True
                st.session_state.user = st.session_state.login_user.strip()
                st.session_state.messages = [{"role": "assistant", "content": config.WELCOME}]
                st.rerun()
            else:
                st.error("账号或密码错误，请重试")
    st.stop()

# ================= 已登录 =================
account = config.ACCOUNTS[st.session_state.user]
is_admin = account["role"] == "admin"
engine = get_engine()

with st.sidebar:
    st.subheader(f"👤 {account['name']}")
    st.caption(f"账号：{st.session_state.user} · 角色：{'管理员' if is_admin else '普通用户'}")
    if st.button("退出登录", use_container_width=True):
        for key in ("authed", "user", "messages"):
            st.session_state.pop(key, None)
        st.rerun()
    if st.button("🗑️ 清空当前对话", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": config.WELCOME}]
        st.rerun()
    st.divider()

    # ---- 知识库管理（仅管理员） ----
    if is_admin:
        st.subheader("📁 知识库管理")
        st.caption("上传文档后自动更新知识库，支持 PDF / DOCX / MD / TXT")
        uploaded = st.file_uploader(
            "上传文档", type=["pdf", "docx", "md", "txt"], accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded:
            for f in uploaded:
                (config.DOCS_DIR / f.name).write_bytes(f.getbuffer())
            with st.spinner("文档已保存，正在更新知识库…"):
                n = engine.build()
            st.success(f"✅ 已入库 {len(uploaded)} 个文件，知识库共 {n} 个片段")
        docs = [f.name for f in sorted(config.DOCS_DIR.glob("*")) if f.suffix.lower() in rag.SUPPORTED_SUFFIXES]
        if docs:
            st.caption(f"当前知识库文档（{len(docs)} 个）：")
            for name in docs:
                c1, c2 = st.columns([4, 1])
                c1.write(f"📄 {name}")
                if c2.button("🗑️", key=f"del_{name}", help=f"删除 {name}"):
                    (config.DOCS_DIR / name).unlink(missing_ok=True)
                    engine.build()
                    st.rerun()
        if st.button("🔄 重建索引", use_container_width=True):
            with st.spinner("正在重建知识库索引…"):
                n = engine.build(force=True)
            st.success(f"✅ 重建完成，共 {n} 个片段")
        st.divider()

    st.caption("💡 检索模式：" + ("向量 + 关键词混合检索" if engine.use_embeddings else "关键词检索（未配置向量 API）"))
    st.caption("⚙️ 模型状态：" + ("✅ DeepSeek 已接入" if config.DEEPSEEK_API_KEY else "❌ 未配置 API Key"))
    st.caption(f"📌 版本：{config.APP_VERSION}")
    st.caption(config.DISCLAIMER)

# ================= 主界面：智能问答 =================
page_header("金融知识问答 · 引用溯源 · 多轮对话")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])
        if msg.get("sources"):
            render_sources(msg["sources"])

# 示例问题快捷按钮
st.caption("💡 点击示例问题快速体验，或输入您自己的疑问：")
for row in (EXAMPLES[:2], EXAMPLES[2:]):
    cols = st.columns(2)
    for col, ex in zip(cols, row):
        if col.button(ex, use_container_width=True, key=f"example_{ex}"):
            submit_question(ex)

# 提问输入框
prompt = st.chat_input(f"请输入您想了解的金融问题（{QUESTION_MAX_LEN} 字以内）…", max_chars=QUESTION_MAX_LEN)
if prompt:
    submit_question(prompt)
