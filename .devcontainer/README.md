# OpenClaw Codespace Setup

這個 `.devcontainer` 配置讓你可以在 GitHub Codespaces 中輕鬆開發 OpenClaw。

## 🚀 快速開始

1. 點擊 GitHub 上的 **Code** 按鈕
2. 選擇 **Codespaces** 標籤
3. 點擊 **Create codespace on main**

## 📦 包含的功能

- **Python 3.11** - 主要開發語言
- **Node.js 20** - 前端開發工具
- **Git & GitHub CLI** - 版本控制
- **VS Code 擴充套件**:
  - Python 支援與 Pylance
  - Black 程式碼格式化
  - Jupyter Notebooks
  - GitHub Copilot (如果已啟用)

## 🔧 自動化設定

Codespace 啟動時會自動：
- 安裝 Python 相依套件 (`requirements.txt`)
- 設定 Python 開發環境
- 配置程式碼格式化和 linting

## 🌐 端口轉發

預設轉發的端口：
- `8000` - Python 開發伺服器
- `3000` - 前端開發伺服器
- `5000` - Flask/其他應用

## 💡 使用提示

啟動 Codespace 後，在終端機執行：
```bash
# 檢查 Python 版本
python --version

# 安裝相依套件（如果自動安裝失敗）
pip install -r requirements.txt

# 開始開發！
```

## 🛠️ 自訂設定

需要修改配置？編輯 `.devcontainer/devcontainer.json`
