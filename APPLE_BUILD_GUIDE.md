# LingoFlow 苹果端（iPhone / iPad / Mac）打包与安装指南

由于苹果官方强制要求使用 macOS + Xcode 编译签名才能生成 `.ipa`（iPhone/iPad 安装包）和 `.dmg`（Mac 安装包），本项目已在当前工程中直接集成了 **Capacitor iOS 配置**、**离线客户端存储引擎（`frontend/storage.js`）** 与 **GitHub Actions 云端自动打包流水线**。

---

## 方式一：GitHub Actions 云端免费自动打包 `.ipa` 与 `.dmg`

### 1. 上传当前项目到 GitHub
在 `c:\反重力\english-learning-desktop` 目录打开 PowerShell，初始化仓库并推送到你的 GitHub 仓库（首次需在 GitHub 新建一个空仓库）：

```powershell
cd "c:\反重力\english-learning-desktop"
git init
git add .
git commit -m "feat: support iOS IPA and macOS DMG cloud builds"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<你的仓库名>.git
git push -u origin main
```

### 2. 下载打包好的苹果安装包
1. 打开你的 GitHub 仓库页面，点击顶部 **Actions** 标签页。
2. 找到工作流 **Build Apple Apps (iOS IPA & macOS DMG)**（也可点击右侧 **Run workflow** 手动触发）。
3. 等待约 3～5 分钟构建完成，在页面底部的 **Artifacts** 区域即可直接下载：
   - **`LingoFlow-iOS-ipa`**（解压后得到 `LingoFlow-iOS.ipa`，适用于 iPhone / iPad）
   - **`LingoFlow-macOS-dmg`**（解压后得到 `LingoFlow-macOS.dmg`，适用于 Mac 苹果电脑）

### 3. 安装 `LingoFlow-iOS.ipa` 到 iPhone / iPad
云端生成的 `.ipa` 为未签名构建包（无需付费苹果开发者账号，可用免费个人 Apple ID 自签安装）：
1. 在 Windows 上安装 **Sideloadly**（或 **爱思助手** / **AltStore**），用数据线连接 iPhone / iPad。
2. 将 `LingoFlow-iOS.ipa` 拖入工具，输入自己的 Apple ID 完成个人签名安装。
3. 安装完成后，在 iPhone 的 **设置 → 通用 → VPN与设备管理** 中信任你的 Apple ID，即可正常打开使用（所有词库、卡片进度、收藏、笔记均离线存储在手机本地）。

---

## 方式二：零工具免签名 —— 局域网 Safari「添加到主屏幕」（立即可用）

如果你不想连接数据线自签 `.ipa`，在 Windows 上启动静态服务后，用同一 Wi-Fi 下的 iPhone / iPad Safari 打开即可安装成独立全屏 App：

1. 在电脑运行：
   ```powershell
   cd "c:\反重力\english-learning-desktop\frontend"
   ..\.venv\Scripts\python.exe -m http.server 8765 --bind 0.0.0.0
   ```
2. 查看电脑局域网 IP（运行 `ipconfig`），在 iPhone / iPad 的 **Safari** 浏览器访问 `http://<你的电脑IP>:8765`。
3. 点击底部 **分享图标 → 添加到主屏幕**，桌面上就会出现独立的 **LingoFlow** 图标，打开即全屏 App 体验（数据保存在设备的本地存储中）。
