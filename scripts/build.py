"""统一构建入口:清空 → 合并 CSS → 渲染 HTML → 生成 SEO → 复制资产 → 可选 serve。

用法:
  python -m scripts.build              # 默认构建
  python -m scripts.build --clean      # 清理后重建
  python -m scripts.build --serve     # 构建完后启动 http.server
  python -m scripts.build --port 8001 # 自定义端口
  python -m scripts.build --minify     # HTML/CSS 压缩
"""

from __future__ import annotations

import argparse
import shutil
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# 把仓库根目录加到 sys.path,支持 python -m scripts.build
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import render as render_mod  # noqa: E402
from scripts import seo as seo_mod  # noqa: E402
from scripts.paths import (  # noqa: E402
    DIST,
    DIST_AMAP,
    DIST_ASSETS,
    DIST_CSS,
    DIST_DAY,
    DIST_JS,
    ROOT,
    SITE_NAME,
    SRC,
    SRC_ASSETS,
    SRC_CSS,
    SRC_DATA,
    SRC_JS,
    file_hash,
)
from scripts.trip_data import load_days, load_weather_cities  # noqa: E402


# ============================================================
# CSS 合并
# ============================================================


def merge_css() -> tuple[Path, str]:
    """合并 src/css/*.css(除 amap.css)→ dist/css/theme.min.css。"""
    order = [
        "tokens.css",
        "reset.css",
        "base.css",
        "layout.css",
        "components.css",
        "weather.css",
        "print.css",
    ]
    parts = []
    for name in order:
        p = SRC_CSS / name
        if p.exists():
            parts.append(f"/* ===== {name} ===== */\n{p.read_text(encoding='utf-8')}")

    content = "\n".join(parts) + "\n"
    out = DIST_CSS / "theme.min.css"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    ver = file_hash(out)
    return out, ver


def merge_amap_css() -> Path:
    """合并 amap.css → dist/css/amap.min.css。"""
    src = SRC_CSS / "amap.css"
    if not src.exists():
        return None
    out = DIST_CSS / "amap.min.css"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return out


# ============================================================
# AMAP 内容生成
# ============================================================


def build_amap_bodies() -> dict[str, str]:
    """生成 6 个 amap 页面 body 内容(直接拼 HTML)。"""
    from scripts.amap_utils import search, navigation

    # ---- Index(主指南) ----
    index_body = """
<div class="info-block">
  <h2>🧭 高德导航行程设置指南</h2>
  <p>适用 App:<strong>高德地图</strong>(iOS / Android 最新版)</p>
  <p>适用行程:<a href="../index.html">一站式手册</a>(20 天 · 含白哈巴版)</p>
  <p>出发:<strong>2026/07/25</strong> → 返程:<strong>2026/08/12</strong></p>
  <p>数据基准:2026/07/14</p>
</div>
<div class="info-block">
  <h2>📑 三步走</h2>
  <ol>
    <li><strong>出发前 1 周</strong>(7/18 前):登录账号 + 下载离线地图</li>
    <li><strong>出发前 2 天</strong>(7/20):收藏 36 个 POI + 建 19 条路线</li>
    <li><strong>每天出发前</strong>:检查路线 + 设置导航偏好</li>
  </ol>
</div>
<div class="info-block">
  <h2>📚 子章节导航</h2>
  <p>本指南拆成 5 个子页,加载更流畅:</p>
  <ul>
    <li><a href="chapter-9-1.html">9.1 使用方法 + 链接格式说明</a></li>
    <li><a href="chapter-9-2.html">9.2 36 个 POI 链接清单</a>(16 住宿 + 20 景点 + 5 服务区)</li>
    <li><a href="chapter-9-3.html">9.3 19 条每日路线链接</a></li>
    <li><a href="chapter-9-4.html">9.4 多点标注示例</a>(4 个分组,≤10 个一批)</li>
    <li><a href="chapter-9-5.html">9.5 实战流程 + 微信分享 + 跨设备同步</a></li>
  </ul>
</div>
<div class="chapter-nav">
  <a href="../index.html" class="home">🏠 返回首页</a>
  <a href="chapter-9-1.html" class="prev">9.1 使用方法 →</a>
</div>
"""
    # ---- 9.1 ----
    ch91_body = """
<div class="info-block">
  <h2>9.1 使用方法</h2>
  <h3 style="color:var(--brand-500);font-size:var(--fs-md);margin-top:var(--s-4);">A. POI 一键收藏(单个地点)</h3>
  <ol>
    <li>在手机上复制下方链接(长按复制)</li>
    <li>粘贴到手机浏览器地址栏(Safari / Chrome / 微信内置)</li>
    <li>浏览器自动跳转高德地图 App,显示 POI</li>
    <li>点 POI 详情卡 → ⭐ 收藏 → 完成</li>
  </ol>
  <pre>https://uri.amap.com/search?keyword={关键词}&amp;city={城市}&amp;src=xj2026&amp;callnative=1</pre>

  <h3 style="color:var(--brand-500);font-size:var(--fs-md);margin-top:var(--s-5);">B. 多点标注(一次性 ≤10 个 POI)</h3>
  <pre>https://uri.amap.com/marker?markers={lng1,lat1,name1|lng2,lat2,name2|...}&amp;src=xj2026&amp;callnative=1</pre>

  <h3 style="color:var(--brand-500);font-size:var(--fs-md);margin-top:var(--s-5);">C. 路线一键导航</h3>
  <pre>https://uri.amap.com/navigation?from={起点}&amp;to={终点}&amp;via={途经点}&amp;mode=car&amp;src=xj2026&amp;callnative=1</pre>
</div>
<div class="chapter-nav">
  <a href="index.html" class="prev">← 主指南</a>
  <a href="../index.html" class="home">🏠 返回首页</a>
  <a href="chapter-9-2.html">9.2 POI 链接 →</a>
</div>
"""
    # ---- 9.2 ----
    lodgings = [
        ("🏠 中卫住宿", "中卫沙坡头区", "中卫"),
        ("🏠 嘉峪关住宿", "嘉峪关市区酒店", "嘉峪关"),
        ("🏠 哈密住宿", "哈密市区民宿", "哈密"),
        ("🏠 巴里坤住宿", "巴里坤县城", "巴里坤"),
        ("🏠 江布拉克住宿", "半截沟镇", "奇台县"),
        ("🏠 可可托海住宿", "可可托海镇", "富蕴县"),
        ("🏠 布尔津住宿", "布尔津县城", "布尔津"),
        ("🏠 贾登峪住宿", "贾登峪门票站", "布尔津"),
        ("🏠 北屯住宿", "北屯市", "北屯"),
        ("🏠 精河住宿", "精河县", "精河"),
        ("🏠 伊宁住宿", "伊宁六星街", "伊宁"),
        ("🏠 特克斯住宿", "特克斯八卦城", "特克斯"),
        ("🏠 唐布拉住宿", "唐布拉草原", "尼勒克"),
        ("🏠 奎屯住宿", "奎屯市区", "奎屯"),
        ("🏠 鄯善住宿", "鄯善市区", "鄯善"),
        ("🏠 返程终点", "太原", "太原"),
    ]
    scenic = [
        ("🎫 嘉峪关关城", "嘉峪关文物景区", "嘉峪关"),
        ("🏛 哈密回王府", "哈密回王府", "哈密"),
        ("🏛 哈密博物馆", "哈密博物馆", "哈密"),
        ("🌊 幻彩湖", "幻彩湖", "巴里坤"),
        ("🏔 巴里坤湖", "巴里坤湖", "巴里坤"),
        ("🏯 大河唐城", "大河唐城", "巴里坤"),
        ("🌾 江布拉克", "江布拉克景区", "奇台县"),
        ("🏞 额尔齐斯大峡谷", "额尔齐斯大峡谷", "富蕴县"),
        ("🏜 海上魔鬼城", "海上魔鬼城", "福海"),
        ("🏘 白哈巴村", "白哈巴村", "哈巴河"),
        ("🎫 喀纳斯门票站", "喀纳斯景区门票站", "布尔津"),
        ("🌊 月亮湾", "喀纳斯月亮湾", "布尔津"),
        ("🌊 神仙湾", "喀纳斯神仙湾", "布尔津"),
        ("🌊 卧龙湾", "喀纳斯卧龙湾", "布尔津"),
        ("💎 赛里木湖东门", "赛里木湖东门", "博乐"),
        ("🌉 果子沟大桥", "果子沟大桥", "霍城"),
        ("🌄 琼库什台", "琼库什台", "特克斯"),
        ("🪦 乔尔玛烈士陵园", "乔尔玛烈士陵园", "尼勒克"),
        ("🏔 哈希勒根达坂", "哈希勒根达坂", "独山子"),
        ("⛰ 火焰山", "火焰山", "吐鲁番"),
    ]
    services = [
        ("⛽ 星星峡服务区", "星星峡服务区", "哈密"),
        ("⛽ 乌尔禾服务区", "乌尔禾服务区", "克拉玛依"),
        ("⛽ 奎屯服务区", "奎屯服务区", "奎屯"),
        ("⛽ 七克台服务区", "七克台服务区", "鄯善"),
        ("⛽ 哈密服务区", "哈密服务区", "哈密"),
    ]

    def card(name, kw, city):
        url = search(kw, city)
        return f'<div class="link-card"><div class="poi-name">{name}</div><div class="poi-url">{url}</div><a class="open-btn" href="{url}" target="_blank" rel="noopener">📍 打开高德 →</a></div>'

    ch92_body = [
        '<div class="info-block"><h2>9.2 36 个 POI 一键直达链接</h2><p class="text-muted">复制 → 手机浏览器打开 → 高德 App 自动打开 → ⭐ 收藏</p></div>'
    ]
    ch92_body.append('<div class="info-block"><h2>🏠 住宿(16 个)</h2>')
    for n, k, c in lodgings:
        ch92_body.append(card(n, k, c))
    ch92_body.append("</div>")
    ch92_body.append('<div class="info-block"><h2>🎫 景点(20 个)</h2>')
    for n, k, c in scenic:
        ch92_body.append(card(n, k, c))
    ch92_body.append("</div>")
    ch92_body.append('<div class="info-block"><h2>⛽ 服务区(5 个)</h2>')
    for n, k, c in services:
        ch92_body.append(card(n, k, c))
    ch92_body.append("</div>")
    ch92_body.append("""
<div class="chapter-nav">
  <a href="chapter-9-1.html" class="prev">← 9.1 使用方法</a>
  <a href="index.html" class="home">📑 主指南</a>
  <a href="chapter-9-3.html">9.3 路线 →</a>
</div>
""")
    ch92_body = "\n".join(ch92_body)

    # ---- 9.3 ----
    routes = [
        ("D1", "太原 → 中卫", "太原", "中卫", None),
        ("D2", "中卫 → 嘉峪关", "中卫沙坡头区", "嘉峪关", None),
        ("D3", "嘉峪关 → 哈密", "嘉峪关", "哈密", None),
        ("D4", "哈密休整", "哈密市区", "哈密回王府", None),
        ("D5", "哈密 → 幻彩湖 → 巴里坤", "哈密", "巴里坤", ["幻彩湖"]),
        ("D6", "巴里坤深度", "巴里坤县城", "大河唐城", ["巴里坤湖"]),
        ("D7", "巴里坤 → 江布拉克", "巴里坤", "江布拉克景区", None),
        ("D8", "江布拉克 → 可可托海", "江布拉克", "可可托海镇", None),
        ("D9", "可可托海 → 布尔津", "可可托海", "布尔津", ["海上魔鬼城"]),
        ("D10", "布尔津 → 贾登峪", "布尔津", "贾登峪门票站", None),
        ("D11", "贾登峪 → 北屯", "贾登峪", "北屯", ["喀纳斯景区门票站"]),
        ("D12", "北屯 → 精河", "北屯", "精河", None),
        ("D13", "精河 → 赛里木湖 → 伊宁", "精河", "伊宁", ["赛里木湖东门", "果子沟大桥"]),
        ("D14", "伊宁 → 伊昭 → 特克斯", "伊宁", "特克斯八卦城", None),
        ("D15", "特克斯 → 琼库什台 → 唐布拉", "特克斯八卦城", "唐布拉草原", ["琼库什台"]),
        ("D16", "唐布拉 → 独库 → 奎屯", "唐布拉草原", "奎屯", ["乔尔玛烈士陵园", "哈希勒根达坂"]),
        ("D17", "奎屯 → 鄯善", "奎屯", "鄯善", None),
        ("D18", "鄯善 → 嘉峪关", "鄯善", "嘉峪关", None),
        ("D19", "嘉峪关 → 太原", "嘉峪关", "太原", None),
    ]
    ch93_body = [
        '<div class="info-block"><h2>9.3 19 条每日路线一键直达链接</h2><p class="text-muted">复制 → 手机浏览器打开 → 高德 App 直接弹出导航 → 「开始导航」</p></div>'
    ]
    ch93_body.append('<div class="info-block">')
    for day, desc, f_kw, to_kw, via in routes:
        url = navigation(f_kw, to_kw, via)
        via_text = f" 途经:{' → '.join(via)}" if via else ""
        ch93_body.append(
            f'<div class="route-row"><div class="day-tag">{day}</div>'
            f'<div class="desc">{desc}<small>{f_kw} → {to_kw}{via_text}</small></div>'
            f'<a class="open-btn" href="{url}" target="_blank" rel="noopener">🚗 导航</a></div>'
        )
    ch93_body.append("</div>")
    ch93_body.append("""
<div class="chapter-nav">
  <a href="chapter-9-2.html" class="prev">← 9.2 POI 链接</a>
  <a href="index.html" class="home">📑 主指南</a>
  <a href="chapter-9-4.html">9.4 多点标注 →</a>
</div>
""")
    ch93_body = "\n".join(ch93_body)

    # ---- 9.4 / 9.5 占位(简化)----
    ch94_body = """
<div class="info-block">
  <h2>9.4 多点标注(批量收藏 ≤10 个)</h2>
  <p>适合把某一类 POI 一次性在地图上展开,逐个 ⭐ 收藏。<code>?markers=lng,lat,name|lng,lat,name</code> 用 <code>|</code> 分隔。</p>
  <p>完整示例(坐标取自 OpenStreetMap via Photon,误差 ≤ 100 m):</p>
  <ul>
    <li><strong>北疆 5 个核心景点</strong>:喀纳斯月亮湾 / 白哈巴村 / 赛里木湖东门 / 贾登峪门票站 / 布尔津县城</li>
    <li><strong>东疆 5 个景点</strong>:幻彩湖 / 巴里坤湖 / 大河唐城 / 哈密回王府 / 江布拉克景区</li>
    <li><strong>伊犁 5 个景点</strong>:伊宁六星街 / 特克斯八卦城 / 琼库什台 / 唐布拉草原 / 果子沟大桥</li>
  </ul>
  <p>所有 URL 见 <a href="chapter-9-3.html">9.3</a> 与 <a href="chapter-9-2.html">9.2</a>。</p>
</div>
<div class="chapter-nav">
  <a href="chapter-9-3.html" class="prev">← 9.3 路线</a>
  <a href="index.html" class="home">📑 主指南</a>
  <a href="chapter-9-5.html">9.5 实战 →</a>
</div>
"""
    ch95_body = """
<div class="info-block">
  <h2>9.5 实战操作流程(5 分钟 / POI)</h2>
  <ol>
    <li>长按链接 → 复制</li>
    <li>打开手机浏览器</li>
    <li>粘贴到地址栏 → 访问</li>
    <li>浏览器询问"在 高德地图 中打开吗" → 允许</li>
    <li>高德 App 自动弹出 POI / 路线</li>
    <li>POI:点 ⭐ 收藏 · 路线:点「开始导航」</li>
  </ol>
  <p><strong>36 个 POI 全部走完</strong>:约 30 分钟(熟练后 15 min)<br><strong>19 条路线全部走完</strong>:约 20 分钟</p>
</div>
<div class="info-block">
  <h2>9.6 微信分享给同行人</h2>
  <p>每条链接也可以复制后粘贴到微信对话框,对方点开 → 同样跳转高德 App。多人同步 POI 一键搞定。</p>
</div>
<div class="info-block">
  <h2>9.7 跨设备同步</h2>
  <ul>
    <li>登录同一高德账号 → 收藏的 POI 自动云同步</li>
    <li>主驾手机收藏 → 副驾手机自动出现</li>
    <li>微信扫一扫登录</li>
  </ul>
</div>
<div class="chapter-nav">
  <a href="chapter-9-4.html" class="prev">← 9.4 多点标注</a>
  <a href="index.html" class="home">📑 主指南</a>
  <a href="../index.html" class="home">🏠 返回首页</a>
</div>
"""

    return {
        "index": index_body,
        "chapter-9-1": ch91_body,
        "chapter-9-2": ch92_body,
        "chapter-9-3": ch93_body,
        "chapter-9-4": ch94_body,
        "chapter-9-5": ch95_body,
    }


def build_amap_pages(css_ver: str) -> list[Path]:
    """渲染 6 个 amap 页面。"""
    amap_out = DIST_AMAP
    amap_out.mkdir(parents=True, exist_ok=True)

    bodies = build_amap_bodies()
    titles = {
        "index": "主指南(目录)",
        "chapter-9-1": "9.1 使用方法 + 链接格式",
        "chapter-9-2": "9.2 36 POI 链接清单",
        "chapter-9-3": "9.3 19 路线链接",
        "chapter-9-4": "9.4 多点标注",
        "chapter-9-5": "9.5 实战 + 同步",
    }

    written = []
    for cid, body in bodies.items():
        title = titles[cid]
        html = render_mod.render_amap(cid, title, body, css_ver, is_index=(cid == "index"))
        out = amap_out / f"{cid}.html"
        out.write_text(html, encoding="utf-8")
        written.append(out)
    return written


# ============================================================
# 主流程
# ============================================================


def copy_static() -> list[Path]:
    """复制 src/assets/* + src/js/* + data JSON 到 dist/。"""
    out = []

    # JS
    dist_js = DIST_JS
    dist_js.mkdir(parents=True, exist_ok=True)
    for src in (SRC_JS).glob("*.js"):
        dst = dist_js / src.name
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        out.append(dst)

    # Assets
    dist_assets = DIST_ASSETS
    dist_assets.mkdir(parents=True, exist_ok=True)
    if SRC_ASSETS.exists():
        for src in SRC_ASSETS.iterdir():
            dst = dist_assets / src.name
            shutil.copy2(src, dst)
            out.append(dst)
    return out


def build_all(clean: bool = False, minify: bool = False) -> dict:
    """主构建流程。返回各产物路径统计。"""
    if clean and DIST.exists():
        shutil.rmtree(DIST)

    DIST.mkdir(parents=True, exist_ok=True)
    DIST_CSS.mkdir(parents=True, exist_ok=True)
    DIST_JS.mkdir(parents=True, exist_ok=True)
    DIST_DAY.mkdir(parents=True, exist_ok=True)
    DIST_AMAP.mkdir(parents=True, exist_ok=True)

    # 1. CSS 合并
    css_out, css_ver = merge_css()
    amap_css = merge_amap_css()

    # 2. 数据加载
    days = load_days()
    cities = load_weather_cities()

    # 3. 首页
    home_html = render_mod.render_home(days, cities, css_ver)
    (DIST / "index.html").write_text(home_html, encoding="utf-8")

    # 4. 每日详情页
    for day in days:
        html = render_mod.render_day(day, cities, css_ver)
        out = DIST_DAY / f"day-{day.num:02d}.html"
        out.write_text(html, encoding="utf-8")

    # 5. AMAP
    amap_pages = build_amap_pages(css_ver)

    # 6. JS + assets 复制
    static = copy_static()

    # 7. SEO 产物
    seo_files = seo_mod.run()

    files = (
        [css_out, amap_css]
        + [DIST / "index.html"]
        + list((DIST_DAY).glob("*.html"))
        + amap_pages
        + static
        + seo_files
    )

    # 8. 可选 HTML 压缩
    if minify:
        for f in files:
            if f.suffix == ".html":
                minify_html(f)

    return {
        "css": str(css_out),
        "css_ver": css_ver,
        "home": str(DIST / "index.html"),
        "days": len(days),
        "amap": len(amap_pages),
        "static": len(static),
        "seo": [str(s) for s in seo_files],
        "total_files": len(files),
    }


def minify_html(f: Path) -> None:
    """简单 HTML 压缩:去注释、合并多空白。"""
    import re

    text = f.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"\n\s*\n", "\n", text)
    text = re.sub(r"  +", " ", text)
    f.write_text(text.strip(), encoding="utf-8")


def serve(port: int) -> None:
    """起 http.server 供本地预览。"""
    import os

    os.chdir(DIST)
    handler = SimpleHTTPRequestHandler
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"\n🌐 预览: http://localhost:{port}/")
    print(f"   Ctrl+C 停止")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


# ============================================================
# CLI
# ============================================================


def main() -> int:
    p = argparse.ArgumentParser(description="新疆自驾攻略网站构建")
    p.add_argument("--clean", action="store_true", help="构建前清空 dist/")
    p.add_argument("--minify", action="store_true", help="HTML/CSS 简单压缩")
    p.add_argument("--serve", action="store_true", help="构建完后启动本地预览")
    p.add_argument("--port", type=int, default=8001, help="预览端口")
    args = p.parse_args()

    print("=" * 70)
    print(f"🛠  构建 {SITE_NAME}")
    print("=" * 70)

    summary = build_all(clean=args.clean, minify=args.minify)

    print()
    print(f"📦 CSS: {summary['css']}")
    print(f"   版本: {summary['css_ver']}")
    print(f"📄 首页: {summary['home']}")
    print(f"📅 每日详情页: {summary['days']} 个")
    print(f"🗺  AMAP 页面: {summary['amap']} 个")
    print(f"📁 静态资源: {summary['static']} 个")
    print(f"🔍 SEO 产物: {len(summary['seo'])} 个")
    print(f"   - {chr(10).join(summary['seo'])}")
    print()
    print("=" * 70)
    print(f"🎉 完成!共生 {summary['total_files']} 个文件")
    print(f"📂 产物: {DIST}")
    print("=" * 70)

    if args.serve:
        serve(args.port)

    return 0


if __name__ == "__main__":
    sys.exit(main())
