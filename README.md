# 🚗 新疆自驾 20 天 · 含白哈巴 · 一站式手册

> 2026 年 7-8 月新疆自驾攻略 · 实时天气 + 高德导航行程一键直达

[![部署](https://img.shields.io/badge/deploy-trip.gtian.cn%2Fxinjiang-blue)](https://trip.gtian.cn/xinjiang/)
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
xinjiang/                    # 项目根(★ git 仓库)
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

### 双站部署架构

| 站         | 域名                                                      | 托管                                | 触发                                                                 |
| ---------- | --------------------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------- |
| **主站**   | [trip.gtian.cn/xinjiang](https://trip.gtian.cn/xinjiang/) | 腾讯云 nginx 自托管                 | `push main` → [deploy.yml](.github/workflows/deploy.yml)             |
| **镜像站** | [driving-trip.gtian.cn](https://driving-trip.gtian.cn/)   | GitHub Pages(仓库 CNAME 指向该域名) | `push main` → [deploy-pages.yml](.github/workflows/deploy-pages.yml) |

两份产物**字节级一致**(同一 dist + 同一 commit),仅 `SITE_URL` 环境变量不同 → sitemap/canonical/OG 自动指向正确的对外域名。

### 主站:腾讯云 nginx

[deploy.yml](.github/workflows/deploy.yml) `push main` 触发后:

1. 检出代码
2. `python -m scripts.build --clean`
3. 备份线上旧版 → `xinjiang.bak.YYYYMMDD-HHMMSS`
4. `rsync --delete` 上传(用 `--rsync-path=sudo rsync`)
5. `chown www:www`
6. curl 验证 200 + 关键内容
7. 清理 7 天以上旧备份

**首次配置**(GitHub 仓库 Settings → Secrets):

| Secret            | 内容                                                             |
| ----------------- | ---------------------------------------------------------------- |
| `SSH_PRIVATE_KEY` | `cat ~/资料/个人资料/qq-cloud/QQ20270207.pem` 全文(含 BEGIN/END) |
| `SSH_KNOWN_HOSTS` | `ssh-keyscan -H gtian.cn` 输出                                   |
| `REMOTE_DIR`      | `/www/wwwroot/trip.gtian.cn/xinjiang`                            |

可选 Variable:`PUBLIC_URL` 默认 `https://trip.gtian.cn/xinjiang/`。

```bash
# 推送触发自动部署
git push origin main
# → 5-15 秒后 https://trip.gtian.cn/xinjiang/ 自动更新
```

### 镜像站:driving-trip.gtian.cn(GT 顶级域名)

[deploy-pages.yml](.github/workflows/deploy-pages.yml) 用 `SITE_URL=https://driving-trip.gtian.cn/` 重新构建 dist,再经 GitHub Actions → Pages 部署:

```yaml
env:
  SITE_URL: https://driving-trip.gtian.cn/
run: python3 -m scripts.build --clean
```

托管方案:仓库 [gou-tian/driving-trip](https://github.com/gou-tian/driving-trip) Settings → Pages → Custom domain 设为 `driving-trip.gtian.cn`,DNS 加 CNAME `driving-trip → gou-tian.github.io`,GitHub 自动签发 Let's Encrypt。

**优势**:

- 顶级域名,比 `gou-tian.github.io/driving-trip/` 短 21 字符,适合纸质打印/口头分享
- 服务器宕了仍可访问(独立可用区)
- 与主站内容严格同步(同一 commit + 同一 commit SHA)

### 手动部署(本地脚本)

```bash
cd /Users/goutian/ai/claude/travel/xinjiang
./scripts/deploy.sh              # 真部署
./scripts/deploy.sh --dry-run    # 仅模拟
./scripts/deploy.sh --rollback   # 回滚
```

### 子路径兼容性

全部资源用 **相对路径**(`css/theme.min.css`、`../css/theme.min.css`),无需 `<base>` 标签,可部署到根域名或任意子路径。

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
- **出发日期**:2026/07/23

详见 [CHANGELOG.md](CHANGELOG.md)。

## 📝 License

MIT — 详见 [LICENSE](LICENSE)
