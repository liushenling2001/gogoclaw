# GogoClaw 一键安装脚本 (Windows PowerShell)
# 用法：Invoke-WebRequest -Uri https://raw.githubusercontent.com/liushenling2001/gogoclaw/main/scripts/install.ps1 -UseBasicParsing | Invoke-Expression

$ErrorActionPreference = "Stop"

# 颜色函数
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Green }
function Write-Warn { Write-Host "[WARN] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

# 检测管理员权限
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查 Python
function Check-Python {
    Write-Info "检查 Python..."
    
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    }
    
    if (-not $pythonCmd) {
        Write-Error "未找到 Python，请先安装 Python 3.10+"
        Write-Info "下载地址：https://www.python.org/downloads/"
        exit 1
    }
    
    $pythonVersion = & $pythonCmd --version
    Write-Info "Python 版本：$pythonVersion"
    
    # 检查版本 >= 3.10
    $version = [System.Version]($pythonVersion -replace 'Python ', '')
    if ($version.Major -lt 3 -or ($version.Major -eq 3 -and $version.Minor -lt 10)) {
        Write-Error "Python 版本过低，需要 3.10+，当前：$pythonVersion"
        exit 1
    }
    
    $script:PYTHON_CMD = $pythonCmd.Source
}

# 检查 Git
function Check-Git {
    Write-Info "检查 Git..."
    
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCmd) {
        Write-Error "未找到 Git，请先安装"
        Write-Info "下载地址：https://git-scm.com/download/win"
        exit 1
    }
    
    $script:GIT_CMD = $gitCmd.Source
}

# 设置安装目录
function Setup-Directories {
    Write-Info "设置安装目录..."
    
    $installDir = if ($env:GOGOCLAW_INSTALL_DIR) {
        $env:GOGOCLAW_INSTALL_DIR
    } else {
        "$HOME\.gogoclaw"
    }
    
    $script:INSTALL_DIR = $installDir
    
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    New-Item -ItemType Directory -Force -Path "$installDir\workspace" | Out-Null
    New-Item -ItemType Directory -Force -Path "$installDir\sessions" | Out-Null
    New-Item -ItemType Directory -Force -Path "$installDir\memory" | Out-Null
    
    Write-Info "安装目录：$installDir"
}

# 克隆仓库
function Clone-Repo {
    Write-Info "克隆仓库..."
    
    $repoUrl = if ($env:GOGOCLAW_REPO) {
        $env:GOGOCLAW_REPO
    } else {
        "https://github.com/liushenling2001/gogoclaw.git"
    }
    
    $repoDir = "$INSTALL_DIR\repo"
    $script:REPO_DIR = $repoDir
    
    if (Test-Path "$repoDir\.git") {
        Write-Info "更新仓库..."
        Set-Location $repoDir
        & git pull
    } else {
        Write-Info "克隆仓库到 $repoDir"
        & git clone $repoUrl $repoDir
    }
}

# 创建虚拟环境
function Setup-Venv {
    Write-Info "创建 Python 虚拟环境..."
    
    $venvPath = "$INSTALL_DIR\venv"
    
    if (-not (Test-Path $venvPath)) {
        & $PYTHON_CMD -m venv $venvPath
    }
    
    # 激活虚拟环境
    $script:ACTIVATE_SCRIPT = "$venvPath\Scripts\Activate.ps1"
    & $ACTIVATE_SCRIPT
    
    # 升级 pip
    python -m pip install --upgrade pip
}

# 安装依赖
function Install-Dependencies {
    Write-Info "安装 Python 依赖..."
    
    Set-Location $REPO_DIR
    pip install -e .
}

# 初始化配置
function Init-Config {
    Write-Info "初始化配置..."
    
    $configDir = "$HOME\.gogoclaw"
    $configFile = "$configDir\gogoclaw.json"
    
    if (-not (Test-Path $configFile)) {
        New-Item -ItemType Directory -Force -Path $configDir | Out-Null
        
        $config = @{
            gateway = @{
                host = "127.0.0.1"
                port = 18789
                auth_enabled = $false
            }
            agents = @{
                main = @{
                    agent_id = "main"
                    name = "GogoClaw"
                    model = @{
                        provider = "dashscope"
                        model_name = "qwen-plus"
                        api_key = ""
                    }
                    system_prompt = "You are GogoClaw, a helpful AI assistant."
                    tools = @("execute_command", "read_file", "write_file", "list_directory", "browser_navigate", "search_memory")
                    sandbox_enabled = $false
                    memory_enabled = $true
                }
            }
            memory = @{
                provider = "sqlite"
                vector_enabled = $false
            }
        }
        
        $config | ConvertTo-Json -Depth 10 | Set-Content $configFile -Encoding UTF8
        Write-Info "配置文件已创建：$configFile"
        Write-Warn "请编辑配置文件，设置你的 API Key"
    } else {
        Write-Info "配置文件已存在"
    }
}

# 创建启动脚本
function Create-Launcher {
    Write-Info "创建启动脚本..."
    
    $launcherPath = "$INSTALL_DIR\start.ps1"
    
    $launcher = @"
# GogoClaw 启动脚本 (PowerShell)

`$InstallDir = "`$HOME\.gogoclaw"
& "`$InstallDir\venv\Scripts\Activate.ps1"

Write-Host "Starting GogoClaw Gateway..." -ForegroundColor Green
gogoclaw gateway

Write-Host ""
Write-Host "Access Web UI at: http://127.0.0.1:18789" -ForegroundColor Cyan
"@
    
    $launcher | Set-Content $launcherPath -Encoding UTF8
}

# 显示使用说明
function Show-Usage {
    Write-Host ""
    Write-Info "=========================================="
    Write-Info "GogoClaw 安装完成！"
    Write-Info "=========================================="
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Yellow
    Write-Host "1. 编辑配置文件：notepad `$HOME\.gogoclaw\gogoclaw.json"
    Write-Host "2. 设置你的 API Key (阿里云/智谱/Kimi/Ollama 等)"
    Write-Host "3. 启动服务：& `$HOME\.gogoclaw\start.ps1"
    Write-Host ""
    Write-Host "支持的模型提供商:" -ForegroundColor Cyan
    Write-Host "  - dashscope (阿里云通义千问)"
    Write-Host "  - zhipu (智谱 AI)"
    Write-Host "  - kimi (月之暗面)"
    Write-Host "  - ollama (本地模型)"
    Write-Host "  - openai (OpenAI)"
    Write-Host "  - anthropic (Claude)"
    Write-Host "  - google (Gemini)"
    Write-Host ""
    Write-Host "访问 Web UI: http://127.0.0.1:18789" -ForegroundColor Cyan
    Write-Host ""
}

# 主函数
function Main {
    Write-Info "开始安装 GogoClaw..."
    
    Check-Python
    Check-Git
    Setup-Directories
    Clone-Repo
    Setup-Venv
    Install-Dependencies
    Init-Config
    Create-Launcher
    Show-Usage
}

# 运行
Main
