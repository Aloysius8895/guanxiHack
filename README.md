# CoMinVi 本地网站副本

来源：https://www.cominvi.com.mx/  
抓取日期：2026-10-01（Asia/Kuala_Lumpur）

已使用当前项目的 `main.py` 抓取首页，再通过 `tools/mirror.py` 读取其网络记录，补齐站内页面、图片、字体、视频、脚本及动画依赖。原项目核心代码未修改。

## 打开网站

本次会话已启动预览：**http://127.0.0.1:8002/**

以后在项目根目录启动：

```powershell
python guanxiHack/serve.py
```

然后在浏览器打开 http://127.0.0.1:8002/ 。保持终端运行，按 Ctrl+C 停止。
也可以在 PowerShell 执行 `./guanxiHack/start.ps1`。

如果端口已被本次预览占用，直接打开上述地址即可。需要另一个端口时：

```powershell
python guanxiHack/serve.py --port 8080
```

请使用提供的服务器，不要双击 HTML：ES 模块、无扩展名页面、动画、地图和视频 Range 请求需要 HTTP 服务。

## 已保存内容

- 24 个英语／西班牙语页面：主页、服务、技术、安全、关于我们、博客及文章、招聘、联系、隐私声明。
- 593 个成功下载的文件，共 104,372,828 字节（约 99.54 MiB，单份原始资源）。`raw` 与 `site` 分别保留原件和本地版本，因此整个文件夹更大。
- 原站 HTML、CSS、JavaScript、字体、图片、视频及矿物动画资源。
- 洞穴动画：桌面端 150 帧、手机端 132 帧，以及两个尺寸的 MP4 开场视频。
- 博客依赖脚本、联系页初始地图样式、瓦片、文字和图标资源。

## 文件位置

| 路径 | 内容 |
| --- | --- |
| `site/` | 可运行的本地网站；主页是 `site/index.html` |
| `site/_assets/` | 按来源域名保存的资源 |
| `raw/` | 未做地址替换的下载原件 |
| `capture/` | 现有爬虫的原始输出：HTML、截图、网络记录及报告 |
| `manifest.json` | 每个 URL 对应的本地路径、大小、类型、状态与失败原因 |
| `verification/` | 桌面、手机、滚动和菜单截图，以及 JSON 验证结果 |
| `serve.py` | 本地服务器，支持无扩展名页面、视频分段及地图绝对地址 |
| `tools/` | 补充抓取与验证脚本 |

本地化处理包括资源域名替换、保留 ES 模块目录关系、移除因内容变化失效的原始 SRI 校验属性、修正原站服务页封面 URL 中多余的分号。原始下载内容仍在 `raw/`。

## 验证结果与实际范围

- 24 个页面均返回 HTTP 200，初始加载未发现缺失本地资源或外部请求。联系页在全页检查后完成地图地址兼容修复，并单独复测通过，见 `verification/contact.json`。
- 桌面 1440×1000 和手机 390×844：首页开场、后续滚动、菜单显示及服务页跳转均已实际验证。
- 服务页、英语和西班牙语首页均已检查；视频 `bytes=0-99` 请求返回 206 和正确的 100 字节。
- 原站的菜单会显示，但 `aria-expanded` 仍为 `false`；本地保留该行为，菜单测试以可见状态和实际跳转为准。
- 首页滚动会请求 6 个 `/lottie/icon-11.json` 至 `icon-16.json`，原站均返回 404，本地也缺少这些统计图标动画。4 个备用 WebM 返回 404，但对应可用 MP4 已保存；另一个结构化数据里的 `logo.png` 返回 403。11 个原站失败地址及原因均记录在 `manifest.json`。
- 地图已保存抓取视角的资源；任意平移、缩放到未抓取区域不能保证离线可用。
- 这是公开前端镜像，未获取服务器源码、数据库、CMS 管理后台或表单处理服务。社交媒体、邮件链接仍指向原目标。没有测试表单提交。
- 保留原站设计与动画实现，但不承诺动态视频、动画时刻或不同浏览器渲染逐像素一致。

## 重建与复查

在项目根目录运行：

```powershell
# 重用已有抓取记录与下载缓存，补抓并生成 site
python guanxiHack/tools/mirror.py

# 先启动 serve.py，再运行需要的检查（可在最后传入其他端口）
python guanxiHack/tools/verify.py
python guanxiHack/tools/check_pages.py
python guanxiHack/tools/check_interactions.py
```

现有项目首次抓取命令：

```powershell
python main.py --url https://www.cominvi.com.mx/ --name cominvi --output-dir guanxiHack/capture --headless true --max-scrolls 100 --max-body-size-mb 20
```

原站采用自定义滚动容器，现有 `main.py` 的窗口滚动未完整覆盖长页面。因此补充验证脚本使用鼠标滚轮，实际触发原站滚动及延迟加载。
