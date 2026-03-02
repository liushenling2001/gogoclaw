#!/bin/bash
# GogoClaw 一键安装脚本 (Ubuntu/macOS)
# 用法：curl -fsSL https://raw.githubusercontent.com/liushenling2001/gogoclaw/main/install.sh | bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
    else
        OS="unknown"
    fi
    log_info "检测到操作系统：$OS"
}

# 检查 Python
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python 版本：$PYTHON_VERSION"
        
        # 检查版本 >= 3.10
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
            PYTHON_CMD="python3"
        else
            log_error "Python 版本过低，需要 3.10+，当前：$PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "未找到 Python3，请先安装 Python 3.10+"
        exit 1
    fi
}

# 检查 pip
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        log_error "未找到 pip3，请先安装"
        exit 1
    fi
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    case $OS in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y python3-pip python3-venv git curl
            ;;
        fedora|rhel)
            sudo dnf install -y python3-pip python3-devel git curl
            ;;
        arch)
            sudo pacman -Sy --noconfirm python-pip python-virtualenv git curl
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install python3 git
            else
                log_warn "未找到 Homebrew，请手动安装 Python 和 Git"
            fi
            ;;
        *)
            log_warn "未知操作系统，请确保已安装 Python 3.10+、pip 和 Git"
            ;;
    esac
}

# 创建安装目录
setup_directories() {
    INSTALL_DIR="${GOGOCLAW_INSTALL_DIR:-$HOME/.gogoclaw}"
    
    log_info "安装目录：$INSTALL_DIR"
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/workspace"
    mkdir -p "$INSTALL_DIR/sessions"
    mkdir -p "$INSTALL_DIR/memory"
}

# 克隆或更新仓库
clone_repo() {
    REPO_URL="${GOGOCLAW_REPO:-https://github.com/liushenling2001/gogoclaw.git}"
    REPO_DIR="$INSTALL_DIR/repo"
    
    if [ -d "$REPO_DIR/.git" ]; then
        log_info "更新仓库..."
        cd "$REPO_DIR"
        git pull
    else
        log_info "克隆仓库..."
        git clone "$REPO_URL" "$REPO_DIR"
    fi
}

# 创建虚拟环境
setup_venv() {
    log_info "创建 Python 虚拟环境..."
    
    if [ ! -d "$INSTALL_DIR/venv" ]; then
        $PYTHON_CMD -m venv "$INSTALL_DIR/venv"
    fi
    
    source "$INSTALL_DIR/venv/bin/activate"
    pip install --upgrade pip
}

# 安装依赖
install_deps() {
    log_info "安装 Python 依赖..."
    
    cd "$REPO_DIR"
    pip install -e .
}

# 初始化配置
init_config() {
    log_info "初始化配置..."
    
    CONFIG_DIR="$HOME/.gogoclaw"
    CONFIG_FILE="$CONFIG_DIR/gogoclaw.json"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        mkdir -p "$CONFIG_DIR"
        
        cat > "$CONFIG_FILE" << EOF
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 18789,
    "auth_enabled": false
  },
  "agents": {
    "main": {
      "agent_id": "main",
      "name": "GogoClaw",
      "model": {
        "provider": "dashscope",
        "model_name": "qwen-plus",
        "api_key": ""
      },
      "system_prompt": "You are GogoClaw, a helpful AI assistant.",
      "tools": ["execute_command", "read_file", "write_file", "list_directory", "browser_navigate", "search_memory"],
      "sandbox_enabled": false,
      "memory_enabled": true
    }
  },
  "memory": {
    "provider": "sqlite",
    "vector_enabled": false
  }
}
EOF
        log_info "配置文件已创建：$CONFIG_FILE"
        log_warn "请编辑配置文件，设置你的 API Key"
    else
        log_info "配置文件已存在"
    fi
}

# 创建启动脚本
create_launcher() {
    log_info "创建启动脚本..."
    
    cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
# GogoClaw 启动脚本

INSTALL_DIR="$HOME/.gogoclaw"
source "$INSTALL_DIR/venv/bin/activate"

echo "Starting GogoClaw Gateway..."
gogoclaw gateway

echo ""
echo "Access Web UI at: http://127.0.0.1:18789"
EOF
    
    chmod +x "$INSTALL_DIR/start.sh"
}

# 显示使用说明
show_usage() {
    echo ""
    log_info "=========================================="
    log_info "GogoClaw 安装完成！"
    log_info "=========================================="
    echo ""
    echo "下一步:"
    echo "1. 编辑配置文件：nano ~/.gogoclaw/gogoclaw.json"
    echo "2. 设置你的 API Key (阿里云/智谱/Kimi/Ollama 等)"
    echo "3. 启动服务：$INSTALL_DIR/start.sh"
    echo ""
    echo "支持的模型提供商:"
    echo "  - dashscope (阿里云通义千问)"
    echo "  - zhipu (智谱 AI)"
    echo "  - kimi (月之暗面)"
    echo "  - ollama (本地模型)"
    echo "  - openai (OpenAI)"
    echo "  - anthropic (Claude)"
    echo "  - google (Gemini)"
    echo ""
    echo "访问 Web UI: http://127.0.0.1:18789"
    echo ""
}

# 主函数
main() {
    log_info "开始安装 GogoClaw..."
    
    detect_os
    check_python
    check_pip
    install_system_deps
    setup_directories
    clone_repo
    setup_venv
    install_deps
    init_config
    create_launcher
    show_usage
}

# 运行
main
