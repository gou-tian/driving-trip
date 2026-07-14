"""SEO 自动化产物:sitemap.xml + robots.txt + manifest.webmanifest。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from scripts.paths import DIST, DIST_ASSETS, SITE_NAME, SITE_URL


def _today() -> str:
    return date.today().isoformat()


def write_sitemap(pages: list[tuple[str, str, float]]) -> Path:
    """生成 dist/sitemap.xml。

    pages: [(url_path, changefreq, priority), ...]
           例:[('/index.html', 'daily', 1.0), ('/day/day-01.html', 'monthly', 0.8), ...]
    """
    today = _today()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url_path, freq, priority in pages:
        url = SITE_URL.rstrip("/") + url_path
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    out = DIST / "sitemap.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_robots(sitemap_filename: str = "sitemap.xml") -> Path:
    """生成 dist/robots.txt。"""
    content = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/{sitemap_filename}\n"
    out = DIST / "robots.txt"
    out.write_text(content, encoding="utf-8")
    return out


def write_manifest() -> Path:
    """生成 PWA manifest.webmanifest。"""
    manifest = {
        "name": SITE_NAME,
        "short_name": "新疆自驾",
        "description": "2026 年新疆自驾 20 天攻略 · 含白哈巴",
        "start_url": "./",
        "display": "standalone",
        "orientation": "portrait",
        "theme_color": "#143f6e",
        "background_color": "#f4f6fa",
        "lang": "zh-CN",
        "icons": [
            {
                "src": "assets/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": "assets/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    }
    import json

    out = DIST / "manifest.webmanifest"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def collect_pages() -> list[tuple[str, str, float]]:
    """自动遍历 dist/ 收集所有 .html 的相对路径。"""
    pages: list[tuple[str, str, float]] = []
    if (DIST / "index.html").exists():
        pages.append(("/index.html", "weekly", 1.0))
    if (DIST / "amap" / "index.html").exists():
        pages.append(("/amap/index.html", "monthly", 0.7))

    day_dir = DIST / "day"
    if day_dir.exists():
        for f in sorted(day_dir.glob("day-*.html")):
            pages.append((f"/day/{f.name}", "monthly", 0.8))

    amap_dir = DIST / "amap"
    if amap_dir.exists():
        for f in sorted(amap_dir.glob("chapter-*.html")):
            pages.append((f"/amap/{f.name}", "monthly", 0.6))

    return pages


def run() -> list[Path]:
    """执行所有 SEO 文件生成。"""
    out = []
    pages = collect_pages()
    out.append(write_sitemap(pages))
    out.append(write_robots())
    out.append(write_manifest())
    return out
