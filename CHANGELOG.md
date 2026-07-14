# Changelog · 新疆自驾攻略网站

记录所有重要变更。格式遵循 [Keep a Changelog](https://keepachangelog.com/)。

## [2.0.0] - 2026-07-14

### 🎉 重磅:全面规范化重构

#### 新增

- **项目结构**:src / scripts / dist / docs / tests 分层
- **CSS 7 层拆分**:tokens / reset / base / layout / components / weather / print
- **设计系统 tokens**:颜色、间距、字号、圆角、阴影、断点统一变量
- **暗色模式**:手动切换 + 跟随系统偏好,localStorage 记忆
- **通用按钮 / 卡片 / Tag / Alert / Skip-link** 组件库
- **WCAG 2.1 AA**:skip-link、aria-label、focus 可见、对比度 ≥ 4.5
- **SEO 自动化**:sitemap.xml / robots.txt / manifest.webmanifest
- **Open Graph + Twitter Card**:每页 `<head>` 自动生成
- **JSON-LD**:首页 WebSite、每日页 Article 全部自动输出
- **README / LICENSE / CHANGELOG / docs/**:完整文档体系
- **`python -m scripts.build`**:统一 CLI(--clean/--minify/--serve)

#### 改进

- 数据从 Python 抽到 `src/data/*.json`(20 天 + 20 城市经纬度)
- 高德 URI 工厂 `scripts/amap_utils.py`(search / marker / multi / navigation)
- 资源路径统一用 `asset()` 函数 + 自动 SHA1 版本号
- 模板引擎用纯 stdlib `.format()`(无需 Jinja2 安装)
- Python 路径全部 `Path(__file__).resolve().parents[N]`(无硬编码绝对路径)

#### 维护

- 旧 _build_\*.py + \_weather_data.py 移到 `_old_build/root/`
- 旧 theme.css + weather.js 移到 `_old_build/css/`
- 旧 HTML 备份到 `_old_html/`(33 个文件)
- 旧 css/day/amap/index.html **保留不动**(用户手动部署切换)

---

## [1.x] - 2026/06-07

### 已有功能

- 20 天单日详情页
- 高德一键直达链接(36 POI + 19 路线)
- Open-Meteo 实时天气集成
- 静态值 fallback
- 单一 theme.css 文件(407 行)
- 单一 index.html + day/_.html + amap/_.html
- 手动 `?v=2` 版本号
- 部署到 `https://gtian.cn/xinjiang-trip/`

---

## 数据基准

- **2026/07/14** — 当前基准(trip.json + weather_cities.json)
- 出发 **2026/07/25** — 数据使用前请评估时效性
- 23,104 B 数据 + 2,250 B 城市 = 25 KB
