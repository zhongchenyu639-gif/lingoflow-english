@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==================================================
echo   LingoFlow - 推送到 GitHub 并触发苹果端云端打包
echo ==================================================
echo.

git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 尚未绑定 GitHub 远程仓库。
    echo 请先在浏览器打开 https://github.com/new 创建一个空仓库（不要勾选 README）。
    echo 然后把仓库地址粘贴到下方（例如 https://github.com/你的用户名/lingoflow.git）：
    echo.
    set /p REPO_URL=请输入 GitHub 仓库地址: 
    if "%REPO_URL%"=="" (
        echo 未输入仓库地址，已取消。
        pause
        exit /b 1
    )
    git remote add origin "%REPO_URL%"
    if errorlevel 1 (
        echo 设置远程仓库失败，请检查地址格式。
        pause
        exit /b 1
    )
)

echo.
echo 正在推送 main 分支到 GitHub（首次会弹出浏览器登录授权）...
git push -u origin main
if errorlevel 1 (
    echo.
    echo 推送失败。请确认仓库地址正确且已完成 GitHub 登录授权。
    pause
    exit /b 1
)

echo.
echo ==================================================
echo   推送成功！GitHub Actions 已开始自动打包苹果安装包
echo   请打开你 GitHub 仓库的 "Actions" 页面，等待约 3~5 分钟
echo   即可在页面底部 Artifacts 下载:
echo     - LingoFlow-iOS-ipa  (iPhone / iPad 安装包)
echo     - LingoFlow-macOS-dmg (Mac 桌面端安装包)
echo ==================================================
pause
