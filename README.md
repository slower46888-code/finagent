# 智融投研助手（FinAgent）

> 金融领域智能问答智能体 —— 让人工智能赋能千行百业

🌐 **线上访问**：https://finagent-dbbgsjvln9whresjc3t3uo.streamlit.app

基于 **RAG（检索增强生成）** 技术的金融智能问答系统：将金融知识文档构建为知识库，结合 DeepSeek 大模型，为用户提供**带引用溯源**的专业问答，支持多轮对话与文档在线管理。

## 核心功能

- 💬 **智能问答**：基于金融知识库（财报分析、交易规则、风险管理、基金投资、金融政策等）回答问题
- 📚 **引用溯源**：每条回答标注引用编号，可展开查看知识库原文，杜绝大模型"幻觉"
- 🔁 **多轮对话**：支持连续追问，上下文连贯
- 📁 **知识库管理**：管理员可在线上传 PDF / DOCX / MD / TXT 文档，自动更新知识库
- 🔑 **账号体系**：登录访问，区分管理员与普通用户

## 快速开始（本地运行）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置密钥
# 将 .streamlit/secrets.toml.example 复制为 .streamlit/secrets.toml
# 填入 DEEPSEEK_API_KEY（必填）和 SILICONFLOW_API_KEY（可选，不填则用关键词检索）

# 3. 启动
streamlit run app.py
```

浏览器自动打开 http://localhost:8501 ，使用测试账号登录。

## 测试账号

| 账号 | 密码 | 角色 | 权限 |
|---|---|---|---|
| `admin` | `Admin123456` | 管理员 | 问答 + 上传/删除知识库文档 |
| `judge` | `Judge123456` | 普通用户 | 问答 |

## 部署到 Streamlit Cloud（获取访问链接）

1. 将本项目推送到 GitHub 仓库（注意：`.streamlit/secrets.toml` 已被 gitignore，不会泄露密钥）
2. 打开 https://share.streamlit.io → Sign in with GitHub → **Create app** → 选择仓库和 `app.py`
3. 在 App 设置 → **Secrets** 中粘贴 `.streamlit/secrets.toml.example` 的内容并填入真实密钥 → Save
4. 应用自动部署完成，获得访问链接：`https://<应用名>.streamlit.app`

**提示**：免费版应用闲置一段时间后会休眠，首次打开需等待约 30–60 秒冷启动，属正常现象；若链接打不开，请检查应用是否仍存在、GitHub 仓库是否被删除。

## 目录结构

```
├── app.py                # Streamlit 主程序（登录、知识库管理、聊天界面）
├── rag.py                # RAG 核心（文档解析、分块、索引、检索、问答）
├── config.py             # 配置（密钥、账号、提示词）
├── data/docs/            # 知识库文档（内置示例 + 管理员上传）
├── data/chroma/          # 向量索引（运行时自动生成）
├── requirements.txt      # 依赖
├── 方案说明.md            # 比赛方案文档
└── .streamlit/secrets.toml.example
```

## 免责声明

本智能体输出由 AI 生成，仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。
