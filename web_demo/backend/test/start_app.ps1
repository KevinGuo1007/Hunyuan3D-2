# 一键启动脚本
# 设置编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 设置 PowerShell 控制台编码
Set-ItemProperty -Path HKCU:\Console -Name CodePage -Value 65001 -Type DWord

# 确保 PowerShell 使用 UTF-8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# 激活虚拟环境
Write-Host "激活虚拟环境..."
& "D:\Hunyuan3D-2\.venv\Scripts\Activate.ps1"

# 构建前端
Write-Host "构建前端..."
Set-Location "D:\Hunyuan3D-2\web_demo\backend\web"
pnpm generate

# 确保数据库目录存在
Write-Host "准备数据库..."
New-Item -ItemType Directory -Path "D:\Hunyuan3D-2\web_demo\backend\data" -Force | Out-Null

# 启动后端服务器
Write-Host "启动后端服务器..."
Set-Location "D:\Hunyuan3D-2"
uvicorn web_demo.backend.app.main:app
