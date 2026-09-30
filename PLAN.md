# CoMinVi 本地镜像方案

目标：使用现有项目抓取 https://www.cominvi.com.mx/，所有交付物放在 guanxiHack。

采用原始 HTML + 原站 CSS/JavaScript/二进制资源镜像，保留原有响应式布局和动画。
现有 main.py 输出保留在 capture；补充脚本读取其网络记录继续下载，递归发现公开站内页面。
不重新设计网页，不改动现有爬虫核心，不复制后台服务。

1. [x] 执行现有 main.py，保留 HTML、网络记录、截图与报告。
2. [x] tools/mirror.py：读取网络记录，抓取站内 HTML、引用资源、CSS/JS 依赖、动画清单中的桌面及手机帧。保留 raw 原件，site 为本地化版本，manifest.json 记录来源与失败项。
3. [x] serve.py 与 start.ps1：只在回环地址提供 site，支持无扩展名页面及视频 Range 请求；不代理到远程后台。
4. [x] tools/verify.py：复用 crawler.browser，验证桌面/手机首页、滚动、菜单和子页；保存截图、控制台错误与缺失请求，补齐缺失资源。
5. [x] README.md：给出启动方法、抓取统计、实际验证结果与尚未复刻的服务器功能。

验证标准：本地 HTML/图片/字体/样式/脚本可读取；首页动画加载后可滚动；站内链接可本地打开；远程请求与缺失文件在报告中明确记录。动态动画不承诺逐帧截图完全相同。
