# 🚗 新疆自驾 20 天 · 含白哈巴 · 一站式手册

> 2026 年 7-8 月新疆自驾攻略 · 实时天气 + 高德导航行程一键直达

[![部署](https://img.shields.io/badge/deploy-https%3A%2F%2Fgtian.cn%2Fxinjiang--trip-blue)](https://gtian.cn/xinjiang-trip)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ 特性

- 🌡️ **实时天气** — Open-Meteo 16 天预报,无需 API key
- 🧭 **高德导航** — 36 个 POI + 19 条路线 **一键直达链接**
- 🎨 **现代 UI** — 色彩卡片风格 + 冷调中性 + 完整暗色模式
- ♿ **WCAG 2.1 AA** — skip-link / aria-label / focus 可见 / 对比度 ≥ 4.5
- 🔍 **SEO 完整** — sitemap / robots / Open Graph / JSON-LD / manifest
- 📦 **零运行时依赖** — 纯 stdlib Python + 浏览器原生 API
- 🌐 **子路径兼容** — 全部相对路径,可部署到任意 URL

## 🚀 快速开始

```bash
# 1. 构建产物
python -m scripts.build --clean

# 2. 本地预览(构建后启动 http.server)
python -m scripts.build --serve --port 8001
# → 浏览器打开 http://localhost:8001/

# 3. 启用 HTML 压缩
python -m scripts.build --minify
```

### 帮助

```bash
python -m scripts.build --help
```

## 📂 项目结构

```
xinjiang-trip-website/
├── src/                    # 源(编辑这里)
│   ├── partials/           # 可复用 HTML 片段(7 个)
│   ├── css/                # 8 个分层 CSS(tokens/reset/base/...)
│   ├── js/                 # weather.js + theme.js
│   ├── assets/             # favicon / icons / og-default
│   ├── data/               # trip.json + weather_cities.json
│   └── *.html.tmpl         # 3 个页面模板
│
├── scripts/                # 构建
│   ├── paths.py            # 路径常量 + 资源 URL 工具
│   ├── trip_data.py        # 加载 trip.json → dataclass
│   ├── amap_utils.py       # URI 工厂
│   ├── render.py           # 模板引擎(纯 stdlib)
│   ├── seo.py              # sitemap + robots + manifest
│   ├── build.py            # CLI 入口(主)
│   └── gen_assets.py       # 占位图标生成
│
├── dist/                   # 构建产物(部署这目录,gitignore)
├── docs/                   # 4 个深入文档
├── tests/                  # 单元测试
├── _old_build/             # 旧版备份(部署后可删)
└── README.md + LICENSE + CHANGELOG.md
```

## 🎨 设计系统

详见 [docs/STYLEGUIDE.md](docs/STYLEGUIDE.md)。

### 5 模块语义色

| 模块    | 颜色 token              | 用途 |
| ------- | ----------------------- | ---- |
| 📍 路程 | `--m-route` `#0369a1`   | 蓝色 |
| 🌡️ 天气 | `--m-weather` `#d97706` | 橙色 |
| 👔 穿着 | `--m-clothes` `#7c3aed` | 紫色 |
| 🎯 游玩 | `--m-play` `#0f766e`    | 青色 |
| ⚠️ 注意 | `--m-warn` `#b91c1c`    | 红色 |

所有视觉决策都通过 CSS 变量(见 [src/css/tokens.css](src/css/tokens.css))。

## 📦 数据来源

| 数据     | 来源                                                                   | 说明                  |
| -------- | ---------------------------------------------------------------------- | --------------------- |
| 实时天气 | [Open-Meteo](https://open-meteo.com)                                   | 公共 API,无需 key     |
| POI 坐标 | [OpenStreetMap via Photon](https://photon.komoot.io)                   | 脚本友好              |
| 高德跳转 | [高德官方 URI](https://lbs.amap.com/api/amap-mobile/guide/ios/ios-uri) | 高德地图 App 自动调起 |

## 🚢 部署

详见 [docs/DEPLOY.md](docs/DEPLOY.md)。

### Netlify / Vercel / 自托管

```bash
# 上传整个 dist/ 目录即可
rsync -av dist/ user@server:/var/www/xinjiang-trip/
```

### 子路径兼容性

全部资源用 **相对路径**(`css/theme.min.css`、`../css/theme.min.css`),无需 `<base>` 标签,可部署到:

- 根域名:`https://example.com/`
- 子路径:`https://example.com/xinjiang-trip/`(当前部署)

## 🧪 测试

```bash
# Lint
uvx ruff check scripts/

# 单元测试
python -m pytest tests/ -v

# 构建 + 检查产物
python -m scripts.build --clean
test -f dist/sitemap.xml && test -f dist/robots.txt && echo "✅ SEO 文件齐全"
grep -c '<url>' dist/sitemap.xml          # → 27
```

## 📚 深入文档

| 文档                                         | 内容                    |
| -------------------------------------------- | ----------------------- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 架构设计 + 数据流       |
| [docs/DEPLOY.md](docs/DEPLOY.md)             | 多种部署方式 + 故障排查 |
| [docs/STYLEGUIDE.md](docs/STYLEGUIDE.md)     | 设计 token + 组件规范   |
| [docs/SEO-A11Y.md](docs/SEO-A11Y.md)         | SEO / WCAG 检查清单     |

## 📅 版本

- **当前**:v2.0.0(全面规范化重构)
- **数据基准**:2026/07/14
- **出发日期**:2026/07/25

详见 [CHANGELOG.md](CHANGELOG.md)。

## 📝 License

MIT — 详见 [LICENSE](LICENSE)
