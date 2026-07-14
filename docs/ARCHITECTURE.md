# 架构设计

## 数据流

```
src/data/trip.json           ──┐
src/data/weather_cities.json ──┤
                               │
src/partials/*.html ────────  ┤
src/css/*.css ─────────────   ┤
src/js/*.js ───────────────   ┤
src/assets/*                 ─┤
                               │
                               ▼
                    scripts/build.py
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
         CSS 合并        模板渲染         SEO 生成
       (merge_css)    (render.py)      (seo.py)
                │              │              │
                ▼              ▼              ▼
            dist/css/      dist/*.html     dist/
                           dist/day/       sitemap.xml
                           dist/amap/      robots.txt
                                          manifest.webmanifest
```

## 核心模块

### `scripts/paths.py`

路径常量 + 资源 URL 工具:

- `ROOT / SRC / DIST` — 三个根路径
- `asset(rel, v)` — 生成相对资源 URL
- `file_hash(path)` — 8 位 SHA1(自动版本号)

### `scripts/trip_data.py`

加载 `src/data/*.json` → `@dataclass`:

- `Day(num, date, title, route, temp, ...)`
- `WeatherCity(day, city, lat, lon, date)`

### `scripts/render.py`

模板引擎 — **纯 stdlib `(str).format()`**,无外部依赖:

- `_render_str(tmpl, ctx)` — 处理 `{{ var }}` 占位 + `{% include "name.html" %}`
- `render_home / render_day / render_amap` — 三类页面

### `scripts/amap_utils.py`

高德 URI 工厂:

- `search(keyword, city)` → 单 POI 链接
- `marker(lon, lat, name)` → 精准 marker 链接
- `multi_marker([(lon,lat,name), ...])` → 多点合并
- `navigation(from, to, via)` → 路线导航

### `scripts/seo.py`

自动生成:

- `dist/sitemap.xml` — 遍历 dist/ 所有 .html
- `dist/robots.txt` — 指向 sitemap
- `dist/manifest.webmanifest` — PWA 配置

### `scripts/build.py`

统一 CLI:

```bash
python -m scripts.build --clean --minify --serve --port 8001
```

## 渲染管道

每个 HTML 页面都按以下顺序拼装:

```
1. _render_str 处理 {% include %} 和 {{ var }}
2. 模板顶部:{% include "head.html" %} → 自动塞 12 个 <meta>
3. 模板中部:{% include "skip-link.html" %} + {% include "header.html" %}
4. 页面主体内容(html.tmpl 自带)
5. 模板底部:{% include "footer.html" %}
```

### 头部 partial 包含

`src/partials/head.html` 自动注入:

- `<meta charset>` + viewport + theme-color
- `<title>` + `<meta description>` + canonical
- `<link rel="icon">` + `<link rel="apple-touch-icon">` + manifest
- Open Graph (og:type / title / description / url / image)
- Twitter Card
- `<link rel="stylesheet" href="css/theme.min.css?v={hash}">`
- `<script defer src="theme.js">` + `<script defer src="weather.js">`
- `<script type="application/ld+json">{...}</script>`

## 资源引用策略

**全部相对路径**,无 `<base>`,无绝对 URL:

| 所在页             | CSS 引用                     | JS 引用            | 首页引用        |
| ------------------ | ---------------------------- | ------------------ | --------------- |
| `/index.html`      | `css/theme.min.css?v=xxx`    | `js/weather.js`    | (self)          |
| `/day/day-NN.html` | `../css/theme.min.css?v=xxx` | `../js/weather.js` | `../index.html` |
| `/amap/index.html` | `../css/theme.min.css?v=xxx` | `../js/weather.js` | `../index.html` |

可部署到:

- 根域名 `https://example.com/`
- 子路径 `https://example.com/xinjiang-trip/`
- 自定义端口 `http://localhost:8000/`

## 模板变量约定

### 全局(任何页面都有)

- `{{ site_name }}` · `{{ site_lang }}` · `{{ site_tz }}` · `{{ site_url }}`
- `{{ build_date }}` · `{{ logo_emoji }}`
- `{{ depth }}` · `{{ depth_prefix }}`(`""` for root, `"../"` for subdir)
- `{{ css_url }}` · `{{ theme_js_url }}` · `{{ weather_js_url }}`
- `{{ title }}` · `{{ desc }}` · `{{ canonical }}` · `{{ og_type }}` · `{{ og_image }}` · `{{ jsonld }}`

### 页面特定

| 页面 | 额外变量                                                                   |
| ---- | -------------------------------------------------------------------------- |
| home | `days` · `weather_cities`                                                  |
| day  | `day: Day` · `city: WeatherCity` · `prev_link` · `next_link` · `home_link` |
| amap | `chapter_id` · `nav_html` · `body_html`                                    |

## 部署产物清单

```
dist/
├── index.html                          # 首页
├── day/day-01.html ~ day-20.html      # 20 个每日页
├── amap/
│   ├── index.html                      # 主指南
│   └── chapter-9-1.html ~ chapter-9-5.html  # 5 个章节
├── css/
│   ├── theme.min.css                   # 7 个 CSS 合并(自动 hash)
│   └── amap.min.css                    # 高德专属样式
├── js/
│   ├── weather.js                      # Open-Meteo 客户端
│   └── theme.js                        # 暗色模式切换
├── assets/
│   ├── favicon.svg
│   ├── icon-192.png / icon-512.png     # PWA icons
│   ├── apple-touch-icon.png
│   └── og-default.png                  # OG image
├── sitemap.xml                         # 27 URLs
├── robots.txt                          # 指向 sitemap
└── manifest.webmanifest                # PWA
```

总计 **39 个文件 / ~150 KB**(未压缩)
