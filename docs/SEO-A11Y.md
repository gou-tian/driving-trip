# SEO & 无障碍检查清单

## ✅ 已实现

### SEO

- ✅ 每页唯一 `<title>` 和 `<meta description>`
- ✅ 每页唯一 `<link rel="canonical">`
- ✅ Open Graph(og:type / title / description / url / image)
- ✅ Twitter Card(summary_large_image)
- ✅ 自动生成 `dist/sitemap.xml`(27 个 URL)
- ✅ 自动生成 `dist/robots.txt`
- ✅ 自动生成 PWA `dist/manifest.webmanifest`
- ✅ JSON-LD:
  - 首页:`WebSite`
  - 每日页:`Article` + 路线元数据
  - AMAP 页:`Article`
- ✅ `<meta name="theme-color">`(light + dark)
- ✅ `<meta name="robots" content="index,follow">`
- ✅ `<link rel="icon">` + apple-touch-icon + manifest
- ✅ 全部资源相对路径(可任意部署到子路径)

### 无障碍 (WCAG 2.1 AA)

- ✅ `<html lang="zh-CN">`
- ✅ Skip-link(`.skip-link` 隐藏,`:focus-visible` 显示)
- ✅ `<main role="main" id="main">`
- ✅ `<nav aria-label="主导航">`
- ✅ `<footer role="contentinfo">`
- ✅ `<button aria-pressed aria-label="切换深色模式">`
- ✅ `:focus-visible { outline: 3px solid var(--focus-ring); }`
- ✅ 颜色对比度 ≥ 4.5:1(浅色)/ ≥ 14.5:1(暗色 `--text` on `--card-bg`)
- ✅ `<th>` 表头语义化
- ✅ 颜色不作为唯一信息载体(徽章 = 颜色 + 文字)
- ✅ `prefers-reduced-motion: reduce` 关闭动效

---

## 📋 部署前人工检查

### HTML 验证

```bash
# W3C HTML Validator(在线)
https://validator.w3.org/nu/?doc=https://gtian.cn/xinjiang-trip/

# 或本地
python -c "
from html.parser import HTMLParser
import sys
class V(HTMLParser):
  def __init__(self): super().__init__(); self.errs = []
  def error(self, msg): self.errs.append(msg)
v = V()
v.feed(open('dist/index.html').read())
print('Errors:', len(v.errs))
for e in v.errs[:5]: print(e)
"
```

### Lighthouse(Chrome DevTools)

1. 打开 DevTools → Lighthouse 标签
2. 模式:**Navigation + Mobile**
3. 类别:**Performance / Accessibility / Best Practices / SEO**(全部勾选)
4. 点击 **Analyze page load**
5. 目标分数:
   - Performance ≥ 90
   - Accessibility ≥ 95
   - Best Practices ≥ 90
   - SEO ≥ 95

### axe DevTools

- DevTools → axe DevTools 标签
- 自动扫描所有页面
- 修复 **Critical** 和 **Serious** 问题

### 键盘测试

- Tab 顺序:从 logo → nav 链接 → 按钮 → 卡片
- 全部可聚焦
- 焦点环可见(蓝色 3px outline)
- Esc / Enter 在 dialog 上工作

### 屏幕阅读器(macOS VoiceOver)

```bash
# 启用 VoiceOver
cmd + fn + F5

# 跳到主内容区(skip-link)
tab → enter → "跳到主要内容" 跳转
```

### 颜色对比度

每个新建页面用 WebAIM Contrast Checker:

https://webaim.org/resources/contrastchecker/

- `--text` on `--card-bg` ≥ 4.5:1
- `--text-muted` on `--card-bg` ≥ 4.5:1
- `--brand-500` 用于按钮文字 → white ≥ 4.5:1

---

## 🔍 SEO 提交动作

### Google Search Console

1. https://search.google.com/search-console/
2. 添加属性:`https://gtian.cn/xinjiang-trip/`
3. 验证(HTML 文件 / DNS TXT)
4. Sitemaps → 提交 `/sitemap.xml`
5. URL 检查:`/`、`/day/day-01.html` 等关键页面

### Bing Webmaster

类似步骤:https://www.bing.com/webmasters

### 百度站长

类似步骤:https://ziyuan.baidu.com/

---

## 📊 期望 SEO 表现

### 索引覆盖

- 27 个 HTML 应全部被索引
- 后台 1-7 天内大部分会被发现
- 慢的话 1 个月

### 站内搜索关键词

主要优化词:

- "新疆自驾 20 天"
- "新疆自驾 7 月"
- "白哈巴 自驾"
- "独库公路 自驾"
- "新疆 实时天气"
- "新疆 高德 一键导航"

详见 `<meta name="description">` 每页唯一。

---

## 🚨 WCAG 关键失败模式速查

| 失败                | 修复                             |
| ------------------- | -------------------------------- |
| 文本对比度 < 4.5:1  | 调 `--text-muted` 更深           |
| 缺少 alt 文本       | 加 `alt="..."`(本项目基本无图)   |
| 链接/按钮无可见焦点 | `:focus-visible` 加 outline      |
| 缺少 `<label>`      | 加 `aria-label` 或 `<label>`     |
| 只有 emoji 没文字   | 加 `aria-label`                  |
| `<h1>` 多于 1 个    | 只留 1 个                        |
| 导航无 `<nav>`      | 包 `<nav aria-label>`            |
| 表格无 `<th>`       | 升级 `<td>` → `<th scope="col">` |

本项目已规避以上常见失败。
