# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 新疆自驾攻略 · 项目说明(2026/07/15 更新)

## 项目性质

旅游规划文档 + PDF 生成脚本 + 静态网站(单一 git 仓库,2026/07/15 合并):

| 子目录                            | git 状态                  | 性质                                                                                                |
| --------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------- |
| `plan-1/` / `plan-2/` / `plan-3/` | **未跟踪**(.gitignore 外) | 早期/中期/归档方案(plan-3 在 2026/07/15 政策核查后冻结,见 [plan-3/ARCHIVED.md](plan-3/ARCHIVED.md)) |
| `plan-4/`                         | **未跟踪**(.gitignore 外) | ★ 当前主版本(20 天含白哈巴·精简东疆版)                                                              |
| `xinjiang-trip-website/`          | **未跟踪**(.gitignore 外) | 旧版 fallback(legacy 旧产物 + 已废弃脚本),仅留作历史参考                                            |
| 仓库根(src/ scripts/ docs/ ...)   | **★ git 仓库**            | 静态网站 v2.0.0(GT 主站 + driving-trip.gtian.cn 镜像,Python 纯 stdlib 构建)                         |

## 文件结构

```
xinjiang/                     ★ git 仓库根(2026/07/15 起)
├── src/                      静态网站源(编辑这里)
│   ├── partials/             7 个复用 HTML 片段
│   ├── css/                  8 个分层 CSS(tokens/reset/base/layout/components/weather/print/amap)
│   ├── css/tokens.css        单一真相源:CSS 变量(色/间距/字号/dark mode)
│   ├── js/                   weather.js / date.js / theme.js
│   ├── data/                 trip.json / weather_cities.json / info.json
│   ├── assets/               favicon / icons / og-default
│   └── *.html.tmpl           4 类页面模板(home/day/info/amap)
├── scripts/                  构建脚本(纯 stdlib)
│   ├── build.py              统一构建入口(merge_css / render HTML / SEO)
│   ├── render.py             HTML 渲染器(纯 stdlib regex,白名单守卫)
│   ├── paths.py              路径常量 + file_hash(缓存破坏)
│   ├── trip_data.py          trip.json / weather_cities.json / info.json 加载
│   ├── amap_utils.py         URI 工厂
│   ├── seo.py                sitemap + robots + manifest
│   ├── gen_assets.py         占位图标生成
│   └── deploy.sh             真部署脚本(已弃用,改 GitHub Actions)
├── tests/                    pytest 测试(test_render / test_sitemap)
├── docs/                     ARCHITECTURE / DEPLOY / SEO-A11Y / STYLEGUIDE
├── dist/                     41 文件构建产物(不 commit)
├── .github/workflows/        deploy-pages.yml + deploy.yml
├── pyproject.toml            dependencies=[] (纯 stdlib)
├── ruff.toml / .editorconfig / .gitignore / .git
├── README.md / CHANGELOG.md / LICENSE
│
├── plan-1/                    早期方案(15/20 天对比,未跟踪)
├── plan-2/                    中期方案(README + docs/ + research/,未跟踪)
├── plan-3/                    📦 历史归档(2026/07/15 冻结,见 ARCHIVED.md,未跟踪)
├── plan-4/                    ★ 当前主版本(未跟踪)
│   ├── 🚗 20天·含白哈巴·精简东疆版·一站式手册.md  主行程(单文件含 20 天详情)
│   ├── 📅 20天·含白哈巴·精简东疆方案+通用信息.md
│   ├── 📅 20天完整版方案.md
│   ├── 📅 19天精简版方案+通用信息.md
│   ├── 🌡️ 20天·逐日天气·穿衣·游玩注意事项.md
│   ├── 🧭 高德导航行程设置指南.md
│   ├── 📍 POI 一键直达链接(OSM版 / Nominatim版).md  ×2
│   ├── 🍴 20天·含白哈巴·精简东疆版·按行程美食攻略.md
│   ├── 💰 通用信息·费用住宿注意事项.md
│   └── _build_pdf_*.py 等 PDF 生成脚本
├── xinjiang-trip-website/    旧版 fallback(legacy,未跟踪)
│   ├── _build_amap_site.py / _build_site.py / _weather_data.py
│   ├── index.html / day/ / amap/ / css/ (顶层旧产物)
│   ├── _old_html/ / _old_build/ (本地 fallback)
│   └── dist/ (__pycache__ 等)
│
└── .claude/                  全项目配置(settings.json 钩子 + skills + agents)
```

## 常用命令

```bash
# 进入仓库根(2026/07/15 起,git 仓库就在根目录)
cd /Users/goutian/ai/claude/travel/xinjiang

# 默认构建(41 个 dist 文件)
python3 -m scripts.build --clean

# 构建 + 启动 dev server
python3 -m scripts.build --serve --port 8001
# → http://localhost:8001/

# Lint Python(钩子会自动跑)
uvx ruff check scripts/

# git 操作(直接在仓库根)
git st -s && git commit -m "..."

# plan-4 PDF 脚本(如有需求)
cd /Users/goutian/ai/claude/travel/xinjiang/plan-4
python3 _build_pdf_20d.py
```

## 推荐方式:Claude 已配置以下自动化

| 工具                                  | 作用                                                 |
| ------------------------------------- | ---------------------------------------------------- |
| Skill `/build-pdf`                    | 一键重建 PDF,支持 15d / amap / food / combined / all |
| Agent `travel-fact-checker`           | 并行核对门票、政策、限行等实时数据(WebSearch)        |
| `.claude/agents/` + `.claude/skills/` | 项目专属 agent(核对/重构)与 skill(快速执行)          |
| PostToolUse 钩子                      | 改 .py 自动 Ruff;改 plan-3/\*.md 提醒重跑 PDF        |
| PreToolUse 钩子                       | 拦截批量破坏 emoji `.md` 源文件;拦截手工编辑 `.pdf`  |
| Stop 钩子                             | 收尾时提醒清理 `/tmp/xinjiang*.html`                 |

## 输出物约束

- **网站 dist/ 41 文件** 不 commit(由 build.py 重新生成)
- **PDF 体积大(1-3 MB)**,不要纳入版本控制
- **临时 HTML 在 /tmp**,每次跑脚本会覆盖
- **不要手工改 .pdf / dist/** → 改对应 .md / 源文件后跑 `python3 _build_pdf_*.py` 或 `python3 -m scripts.build`
- **github-actions.yml** 自动部署 `dist/` 到 driving-trip.gtian.cn 镜像 + trip.gtian.cn/xinjiang

## 数据基准与保鲜

- **攻略数据基准:2026/07/15 政策快照**(原 2026/07/13 版已被取代)
- 关键 3 处修复:①乌市限行 9:30/19:30 高峰 ②独库预约入口"文旅厅"公众号 ③白哈巴 75 元(非 194)
- 出发时间:**2026 年 7 月 23 日暑期**
- **数据保鲜窗口**:门票、政策、限行 6-9 月期间会调整,出发前 1-2 周用 `travel-fact-checker` 重新核查
- 见 `~/.claude/projects/.../memory/xinjiang-policy-2026-07-15-snapshot.md`

## 通用信息页(/info/)架构

- 7 块参考数据(只保留客观可查证):政策摘要 14 行 / 费用明细 20d / 景区门票 10 个 / 住宿价格区间 / 电子边防证 / 加油站安检 / 关键限行限速 / 药品 / 应急电话 / 关键来源
- **预算 5,000 元/人**(20d 实际人均 5,460,微超)
- 主观指南类(单司机节奏/关怀/穿衣/民俗/避坑操作/物品/核对清单)已删除
- 详见 `src/data/info.json` + `src/info.html.tmpl`

## 用户场景备忘

- **6 人出行:2 成人 + 2 老人 + 2 中学生(13-16 岁)**
- 出发地:太原
- **预算 5,000 元/人**(7/15 政策基准)
- 单司机友好为前提
- 进疆前不游玩
- **住宿优先民宿 6 人间**

## 2026/07/15 重组说明

仓库从 `xinjiang-trip-website/` 子目录合并到 `/xinjiang/` 根。9 个 commit 完整保留(物理 move + .git 上移,index 路径不变),`xinjiang-trip-website/` 留下仅作 legacy fallback。详细:本 commit message。
