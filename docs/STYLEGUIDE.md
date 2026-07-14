# 设计系统 · Style Guide

## 视觉风格

**色彩卡片 · 冷调中性** — 远离纯灰,统一深沉、内敛、信息密度高的风格。

---

## 1. 颜色 Tokens

详见 [src/css/tokens.css](../src/css/tokens.css)。

### 主品牌色

| Token          | Light     | Dark      | 用途             |
| -------------- | --------- | --------- | ---------------- |
| `--brand-500`  | `#2563a8` | `#82c0f0` | 主按钮、链接     |
| `--brand-700`  | `#143f6e` | (同)      | 标题渐变末端     |
| `--accent-500` | `#d97706` | `#f59e0b` | 暖强调、hot 徽章 |

### 5 模块语义色

| Token         | Light     | Dark      | 语义 |
| ------------- | --------- | --------- | ---- |
| `--m-route`   | `#0369a1` | `#38bdf8` | 路程 |
| `--m-weather` | `#d97706` | `#f59e0b` | 天气 |
| `--m-clothes` | `#7c3aed` | `#a78bfa` | 穿着 |
| `--m-play`    | `#0f766e` | `#2dd4bf` | 游玩 |
| `--m-warn`    | `#b91c1c` | `#f87171` | 注意 |

### 中性(冷调)

| Token          | Light     | Dark      |
| -------------- | --------- | --------- |
| `--bg`         | `#f4f6fa` | `#0b1220` |
| `--bg-deep`    | `#e9eef5` | `#070d18` |
| `--card-bg`    | `#ffffff` | `#131c2e` |
| `--text`       | `#0f1b2d` | `#e5ecf5` |
| `--text-muted` | `#5b6b80` | `#95a3b8` |
| `--border`     | `#dfe6f0` | `#243049` |

### 对比度(关键)

| 背景          | 前景           | 浅色对比 | 暗色对比 | WCAG |
| ------------- | -------------- | -------- | -------- | ---- |
| `--card-bg`   | `--text`       | 14.8:1   | 14.6:1   | AAA  |
| `--card-bg`   | `--text-muted` | 6.4:1    | 6.1:1    | AA   |
| `--bg`        | `--brand-500`  | 5.2:1    | —        | AA   |
| `--brand-700` | white          | 8.4:1    | —        | AAA  |

---

## 2. 间距 Tokens

| Token   | 值   | 用途              |
| ------- | ---- | ----------------- |
| `--s-1` | 4px  | 紧凑间距          |
| `--s-2` | 8px  | 元素内部          |
| `--s-3` | 12px | 行间              |
| `--s-4` | 16px | 卡片内            |
| `--s-5` | 24px | 区块间距          |
| `--s-6` | 32px | 大区块            |
| `--s-7` | 48px | section padding   |
| `--s-8` | 64px | 顶部 banner       |
| `--s-9` | 96px | Hero 顶部 padding |

---

## 3. 字号 Tokens

| Token       | 值   | 比例  |
| ----------- | ---- | ----- |
| `--fs-xs`   | 12px | 0.75  |
| `--fs-sm`   | 14px | 0.875 |
| `--fs-base` | 16px | 1.0   |
| `--fs-md`   | 18px | 1.125 |
| `--fs-lg`   | 22px | 1.375 |
| `--fs-xl`   | 28px | 1.75  |
| `--fs-2xl`  | 36px | 2.25  |

(1.25 minor-third 比例)

---

## 4. 圆角 / 阴影

### 圆角

| Token      | 值    | 用途      |
| ---------- | ----- | --------- |
| `--r-sm`   | 8px   | 小元素    |
| `--r-md`   | 12px  | 按钮、tag |
| `--r-lg`   | 16px  | 卡片      |
| `--r-xl`   | 24px  | Hero tag  |
| `--r-pill` | 999px | 徽章      |

### 阴影

| Token    | 值                                               | 用途       |
| -------- | ------------------------------------------------ | ---------- |
| `--sh-1` | `0 1px 2px rgb(.../.06), 0 1px 3px rgb(.../.08)` | 卡片静态   |
| `--sh-2` | `0 4px 12px rgb(.../.08)`                        | 卡片 hover |
| `--sh-3` | `0 12px 32px rgb(.../.12)`                       | 弹窗       |
| `--sh-4` | `0 24px 48px rgb(.../.16)`                       | Hero       |

---

## 5. 组件规范

### 按钮 `.btn`

```html
<button class="btn btn-primary">主操作</button>
<a class="btn btn-secondary" href="#">次操作</a>
<button class="btn btn-ghost">文字按钮</button>
```

变体:

- `.btn-primary` — 主色背景
- `.btn-secondary` — 浅底 + 边框
- `.btn-ghost` — 纯文字 + hover 浅底
- `.btn-icon` — 36×36 圆形图标
- `.btn-sm` — 小号

### 卡片 `.card`

```html
<div class="card">默认</div>
<div class="card card-interactive">可点击</div>
<div class="card card-accent route">左侧蓝条</div>
```

5 模块色变体:`.card-accent.route / weather / clothes / play / warn`

### 标签 `.tag`

```html
<span class="tag tag-route">路程</span> <span class="tag tag-warn">⚠ 注意</span>
```

### 提示 `.alert`

```html
<div class="alert alert-info">信息</div>
<div class="alert alert-warning">警告</div>
<div class="alert alert-critical">危险</div>
```

---

## 6. 排版规范

### 标题层级

- `<h1>` 每个页面唯一,字号 `--fs-2xl` (36px)
- `<h2>` 区块标题,字号 `--fs-xl` (28px)
- `<h3>` 模块标题 / 卡片标题,字号 `--fs-md` (18px)

### 段落

- `line-height: 1.7`(中文阅读优化)
- `margin-bottom: var(--s-3)`(12px)

### 链接

- 默认 `--brand-500`
- hover `--brand-700` + `text-underline-offset: 2px`

### 列表

- `<ul> / <ol>` 自动 `padding-inline-start: var(--s-5)`
- `<li>` 行间 `var(--s-1)`

---

## 7. 响应式策略

### 断点

| Token     | 值     | 用途              |
| --------- | ------ | ----------------- |
| `--bp-sm` | 480px  | 手机大屏 / 小手机 |
| `--bp-md` | 768px  | 平板              |
| `--bp-lg` | 1024px | 小屏笔电          |
| `--bp-xl` | 1280px | 桌面              |

### CSS 媒体查询

只用 max-width 一档:`@media (max-width: 768px)`,调整 hero 字号、卡片网格变 2 列、day-nav 变纵列。

JS 用 `matchMedia('(min-width: 769px)')` 做切换。

---

## 8. 暗色模式

### 切换

```html
<button class="theme-toggle" data-theme-toggle>🌙</button>
```

JS 写 `<html data-theme="dark">` 翻转 + localStorage 记忆。

### 颜色适配

`@media (prefers-color-scheme: dark)` 在 tokens.css 里重写同名变量,组件 CSS 完全不感知。

---

## 9. 动效

```css
--ease: cubic-bezier(0.2, 0.6, 0.2, 1); /* 缓出 */
--t-fast: 120ms; /* hover */
--t-base: 200ms; /* 卡片 */
--t-slow: 400ms; /* 弹窗 */
```

`@media (prefers-reduced-motion: reduce)` 自动归零。
