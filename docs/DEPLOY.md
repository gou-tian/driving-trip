# 部署指南 · Deploy

## 概述

`dist/` 是构建产物,**这是唯一需要部署的目录**。所有路径都是相对的,支持任意 URL 形态。

---

## 1. 准备工作

```bash
# 1. 构建产物
python -m scripts.build --clean

# 2. 检查
ls dist/
# 应该有: index.html, day/, amap/, css/, js/, assets/,
#        sitemap.xml, robots.txt, manifest.webmanifest
```

---

## 2. Netlify(零配置)

### 方式 A:Git 集成(推荐)

1. 推代码到 GitHub
2. Netlify → "Add new site" → "Import from Git"
3. 配置:
   - Build command: `python -m scripts.build --clean`
   - Publish directory: `dist`
4. Netlify 自动分配 `https://xxx.netlify.app/` 或绑定自定义域

### 方式 B:手动拖拽

1. Netlify → "Sites" → 拖拽整个 `dist/` 到页面
2. **不要**拖整个项目根(包含 `src/`、`scripts/` 会暴露源代码);只拖 `dist/` 即可

---

## 3. Vercel

```bash
npm i -g vercel
cd xinjiang
vercel --prod
```

Vercel 自动检测 Python / 静态项目。

如果需要构建步骤,加 `vercel.json`:

```json
{
  "buildCommand": "python -m scripts.build --clean",
  "outputDirectory": "dist",
  "framework": null
}
```

---

## 4. Cloudflare Pages

- Git 集成
- Build command: `python -m scripts.build --clean`
- Build output: `dist`

---

## 5. 自托管(Nginx)

### 静态文件部署

```bash
# 1. 同步到服务器
rsync -avz --delete dist/ user@server:/var/www/xinjiang-trip/

# 2. Nginx 配置(/etc/nginx/sites-available/xinjiang-trip.conf)
server {
  listen 80;
  server_name gtian.cn;

  # 子路径部署
  location /xinjiang-trip/ {
    alias /var/www/xinjiang-trip/;
    index index.html;
    try_files $uri $uri/ $uri.html =404;
  }
}
```

### 缓存策略(性能优化)

```nginx
# HTML:每次都新(避免内容更新看不到)
location ~* /xinjiang-trip/.*\.html$ {
  add_header Cache-Control "public, max-age=0, must-revalidate";
}

# CSS/JS/图片:长期缓存(用版本号或 hash 失效)
location ~* /xinjiang-trip/(css|js|assets)/ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

### HTTPS

用 Let's Encrypt:

```bash
sudo certbot --nginx -d gtian.cn
```

---

## 6. 部署到子路径

### 当前部署

`https://gtian.cn/xinjiang-trip/` 是子路径。

### 切换部署到子路径的步骤

```bash
# 1. 同步 dist 内容
rsync -avz --delete dist/ user@server:/var/www/xinjiang-trip/

# 2. 确认可访问
curl -I https://gtian.cn/xinjiang-trip/
curl -I https://gtian.cn/xinjiang-trip/css/theme.min.css
```

### 重要:全部资源相对路径

`dist/index.html` 里:

```html
<link rel="stylesheet" href="css/theme.min.css?v=xxx" />
```

无论部署到根域还是子路径,都正常工作,**无需修改任何 HTML**。

---

## 7. 部署前验证

```bash
# 1. 所有产物文件存在
test -f dist/index.html && echo "✅ index"
test -f dist/sitemap.xml && echo "✅ sitemap"
test -f dist/robots.txt && echo "✅ robots"
test -f dist/manifest.webmanifest && echo "✅ manifest"
test -f dist/css/theme.min.css && echo "✅ CSS"
test -f dist/js/weather.js && echo "✅ JS"
test -f dist/js/theme.js && echo "✅ theme JS"
test -f dist/assets/favicon.svg && echo "✅ favicon"

# 2. 内容大小合理
du -sh dist/  # 应 < 200 KB

# 3. HTML 含 SEO 元数据
grep -q 'application/ld+json' dist/index.html && echo "✅ JSON-LD"
grep -q 'og:title' dist/index.html && echo "✅ OpenGraph"

# 4. 路径全部相对(没有 http:// 绝对 URL)
grep -E 'href="https?://' dist/index.html | head -3
# 应该有 og:url 等 meta,但 href 不应有绝对 URL
```

---

## 8. 部署后验证

```bash
# 1. 主要 URL 200
curl -I https://gtian.cn/xinjiang-trip/

# 2. CSS/JS 200
curl -I https://gtian.cn/xinjiang-trip/css/theme.min.css

# 3. Sitemap 可被 robots 抓
curl -I https://gtian.cn/xinjiang-trip/sitemap.xml

# 4. 浏览器手动测试
open https://gtian.cn/xinjiang-trip/  # macOS
```

在 Chrome DevTools 里:

- Lighthouse 跑一遍(Performance / A11y / SEO / BP)
- Mobile 模拟器测试
- Network 面板确认无 404

---

## 9. 故障排查

### 部署后样式全没了

**原因**:服务器上 css 文件夹丢失,或者路径不对。

**修复**:

```bash
# 检查服务器上文件
ssh user@server ls /var/www/xinjiang-trip/css/

# 应有 theme.min.css 等
```

### 暗色模式不工作

**原因**:JS 加载失败(没部署 js/ 目录)

**修复**:检查 `dist/js/` 是否有 `weather.js` 和 `theme.js`

### 实时天气不更新

**原因 1**:浏览器阻止第三方 API(CORS)

- 不可能,Open-Meteo 默认放行所有域

**原因 2**:JavaScript 报错

- DevTools Console 看错误

**原因 3**:日期超出 Open-Meteo 范围(>15 天)

- 这是预期行为,显示静态值,banner 提示

### Sitemap 提交搜索

[Google Search Console](https://search.google.com/search-console) → Sitemaps → 提交 `https://gtian.cn/xinjiang-trip/sitemap.xml`

---

## 10. 进阶:PWA 部署(可选)

当前 `manifest.webmanifest` 已就绪,要启用完整 PWA 需要加 service worker(`src/sw.js`)。

暂未实现。详见 [Web.dev PWA 指南](https://web.dev/articles/install-criteria)。
