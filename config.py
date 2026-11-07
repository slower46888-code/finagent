# -*- coding: utf-8 -*-
"""全局配置：密钥加载（st.secrets / 环境变量）、账号体系、提示词"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "data" / "docs"
INDEX_DIR = BASE_DIR / "data" / "chroma"


def get_env(name: str, default: str = "") -> str:
    """优先读取 Streamlit secrets（部署到 Streamlit Cloud 时），其次环境变量"""
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.environ.get(name, default)


# ---- 全局 ----
APP_VERSION = "v2.0"

# ---- DeepSeek（对话模型，OpenAI 兼容接口）----
# 仅从 Streamlit Secrets / 环境变量读取，密钥绝不写入代码或仓库
DEEPSEEK_API_KEY = get_env("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = get_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = get_env("DEEPSEEK_MODEL", "deepseek-chat")

# ---- SiliconFlow（向量模型 BGE-M3，用于语义检索；未配置时自动降级为关键词检索）----
SILICONFLOW_API_KEY = get_env("SILICONFLOW_API_KEY")
SILICONFLOW_BASE_URL = get_env("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
EMBED_MODEL = get_env("EMBED_MODEL", "BAAI/bge-m3")

# ---- 测试账号（竞赛演示用途，明文保存；生产环境应改为数据库+哈希）----
ACCOUNTS = {
    "admin": {"password": "Admin123456", "name": "管理员", "role": "admin"},
    "judge": {"password": "Judge123456", "name": "评审用户", "role": "user"},
}

# ---- 系统提示词 ----
SYSTEM_PROMPT = """你是"智融投研助手"，一名专业的金融领域智能问答助手，服务对象为金融从业者和个人投资者。

请严格遵循以下规则：
1. 优先依据【参考资料】回答问题，并在引用处标注编号，如 [1]、[2]。
2. 如果参考资料不足以回答问题，请明确说明"知识库中暂无相关内容"，绝不编造。
3. 回答使用中文，先给结论，再简要解释，通俗易懂、条理清晰。
4. 回答涉及具体投资建议时，必须在末尾附上风险提示。
5. 结合对话历史理解用户的追问，保持上下文连贯。"""

# ---- 首页欢迎语 ----
WELCOME = """您好，我是 **智融投研助手** 👋，一名金融领域智能问答智能体。

我可以基于金融知识库回答您的问题，例如：
- 什么是杜邦分析？如何用它拆解企业经营状况？
- A 股主板和创业板的涨跌幅限制有什么不同？
- 什么是 LPR？它如何影响房贷利率？
- ETF 和普通指数基金有什么区别？
- 个人投资者如何做好风险管理？

您可以连续追问，我会结合上下文回答。回答中的 **[1][2]** 编号对应下方的引用来源，点击可查看原文。
也可以点击下方示例问题快速体验。"""

DISCLAIMER = "⚠️ 本智能体输出由 AI 生成，仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。"
