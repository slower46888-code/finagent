# -*- coding: utf-8 -*-
"""界面主题与通用组件：统一配色、字体、间距、按钮与交互状态（金融风格）"""
import streamlit as st

# ==================== 主题样式 ====================
CSS = """
<style>
/* ---------- 主题变量 ---------- */
:root {
  --primary: #16437E;          /* 主色：金融深蓝 */
  --primary-hover: #0F3362;
  --primary-soft: #E8F0FB;
  --accent: #C9A227;           /* 点缀：琥珀金 */
  --bg: #F5F7FA;
  --card: #FFFFFF;
  --border: #E3E8F0;
  --text: #1F2430;
  --text-soft: #5B6472;
  --success: #1E8E5A;
  --danger: #C0392B;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --shadow: 0 6px 20px rgba(22, 67, 126, 0.08);
}

/* ---------- 全局 ---------- */
html, body, .stApp, [class*="css"] {
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Segoe UI", system-ui, sans-serif;
  color: var(--text);
}
.stApp {
  background: radial-gradient(1200px 500px at 85% -10%, rgba(201, 162, 39, 0.16), transparent 60%),
              linear-gradient(165deg, #102A52 0%, #16396E 42%, #1D4E89 74%, #2563A8 100%) fixed;
}

/* 主内容区：居中限宽、统一留白 */
.block-container { max-width: 1100px; padding-top: 2.2rem; padding-bottom: 4rem; }

/* 隐藏默认菜单与页脚 */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* 直接位于背景上的辅助文字改为浅色，保证深色背景可读性 */
.block-container [data-testid="stCaptionContainer"] p { color: #C9D6EA; }

/* ---------- 品牌头部 ---------- */
.brand-header { text-align: center; margin: 1.2rem 0 1.6rem; }
.brand-title { font-size: 1.9rem; font-weight: 700; color: #FFFFFF; letter-spacing: 0.02em; }
.brand-sub { font-size: 0.95rem; color: #C9D6EA; margin-top: 0.45rem; }
.brand-line {
  width: 64px; height: 3px; border-radius: 2px; margin: 0.9rem auto 0;
  background: linear-gradient(90deg, #FFFFFF, var(--accent));
}

.page-header { margin: 0.4rem 0 0.2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: #FFFFFF; }
.page-sub { font-size: 0.88rem; color: #C9D6EA; margin-left: 0.8rem; }

/* ---------- 登录卡片 ---------- */
[data-testid="stForm"] {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2rem 2.2rem;
  box-shadow: var(--shadow);
}

/* ---------- 输入框 ---------- */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.55rem 0.8rem;
  background: #FFFFFF;
  transition: border-color .15s ease, box-shadow .15s ease;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(22, 67, 126, 0.12);
  outline: none;
}

/* ---------- 按钮 ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stBaseButton-secondary"] {
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: #FFFFFF;
  color: var(--primary);
  font-weight: 600;
  padding: 0.45rem 1rem;
  transition: all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--primary);
  background: var(--primary-soft);
  color: var(--primary-hover);
}
.stButton > button:active, .stDownloadButton > button:active {
  transform: translateY(1px);
}
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button {
  background: var(--primary);
  color: #FFFFFF;
  border: 1px solid var(--primary);
  width: 100%;
  border-radius: var(--radius-sm);
  padding: 0.6rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  transition: all .15s ease;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
  box-shadow: 0 4px 12px rgba(22, 67, 126, 0.25);
}

/* ---------- 聊天消息 ---------- */
[data-testid="stChatMessage"] {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 0.85rem 1.1rem;
  box-shadow: 0 2px 8px rgba(22, 67, 126, 0.04);
  margin-bottom: 0.35rem;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
  background: var(--primary-soft);
  border-radius: 50%;
}

/* ---------- 提问输入框 ---------- */
[data-testid="stChatInput"] {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: #FFFFFF;
  padding: 0.4rem 0.6rem;
  transition: border-color .15s ease, box-shadow .15s ease;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(22, 67, 126, 0.12);
}
[data-testid="stChatInput"] textarea { font-family: inherit; }

/* ---------- 引用来源折叠面板 ---------- */
[data-testid="stExpander"] {
  background: #FBFCFE;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}
[data-testid="stExpander"] summary {
  color: var(--primary);
  font-weight: 600;
  font-size: 0.85rem;
}

/* ---------- 侧边栏 ---------- */
[data-testid="stSidebar"] {
  background: #FFFFFF;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stCaption, [data-testid="stCaptionContainer"] p {
  color: var(--text-soft);
  font-size: 0.82rem;
}
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h2 {
  color: var(--primary);
}

/* ---------- 提示框 / 弹窗 ---------- */
[data-testid="stAlert"] { border-radius: var(--radius-sm); }
[data-testid="stToast"] { border-radius: var(--radius-sm); }

/* ---------- 加载动画 ---------- */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ---------- 滚动条 ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #C9D4E4; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #A9BAD4; }

/* ---------- 响应式：平板 / 手机 ---------- */
@media (max-width: 768px) {
  .block-container { padding: 1rem 0.9rem 3.5rem; }
  .brand-title { font-size: 1.5rem; }
  .page-title { font-size: 1.25rem; }
  .page-sub { display: block; margin: 0.3rem 0 0; }
  [data-testid="stForm"] { padding: 1.4rem 1.2rem; }
  [data-testid="stChatMessage"] { padding: 0.7rem 0.85rem; }
}
</style>
"""


def inject_css() -> None:
    """注入全局主题样式（每次脚本运行调用一次）"""
    st.markdown(CSS, unsafe_allow_html=True)


def brand_header(title: str = "智融投研助手", subtitle: str = "金融领域智能问答智能体 · 让人工智能赋能千行百业") -> None:
    """登录页品牌头部"""
    st.markdown(
        f'<div class="brand-header">'
        f'<div class="brand-title">💹 {title}</div>'
        f'<div class="brand-sub">{subtitle}</div>'
        f'<div class="brand-line"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def page_header(subtitle: str) -> None:
    """已登录主页面标题"""
    st.markdown(
        f'<div class="page-header">'
        f'<span class="page-title">💹 智融投研助手</span>'
        f'<span class="page-sub">{subtitle}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
