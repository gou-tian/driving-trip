"""HTML 渲染器(纯字符串 format,无外部模板引擎依赖)。

原因:PEP 668 不让 pip install,改用 stdlib .format() 方案。
  - 所有 partial 模板是 {{ name }} 占位
  - 渲染时把全局 context dict 传入
  - 把 partials/head.html 等作为函数式 R include 入口
"""

from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote

from scripts.paths import (
    SITE_LANG,
    SITE_NAME,
    SITE_DESC,
    SITE_TIMEZONE_OFFSET,
    SITE_URL,
    SRC,
    SRC_PARTIALS,
)
from scripts.trip_data import Day, WeatherCity, get_weather_city

# ============================================================
# 工具
# ============================================================


def _read(name: str) -> str:
    """读 partial 模板原文。"""
    return (SRC_PARTIALS / name).read_text(encoding="utf-8")


def _include(partial: str, ctx: dict) -> str:
    """include 一个 partial,用 ctx 渲染。"""
    tmpl = _read(partial)
    return _render_str(tmpl, ctx)


def _render_str(tmpl: str, ctx: dict) -> str:
    """对字符串模板做 {{ key }} 替换 + {% include ... %} 嵌套。"""

    # 1. 处理 {% include "partial.html" %}
    def include_repl(m):
        partial = m.group(1)
        if partial in ctx:
            return str(ctx[partial])
        # 默认从 partials/ 加载
        partial_path = SRC_PARTIALS / partial
        if partial_path.exists():
            return _render_str(partial_path.read_text(encoding="utf-8"), ctx)
        return f"<!-- missing include: {partial} -->"

    tmpl = re.sub(
        r'\{%\s*include\s+"([^"]+)"\s*%\}',
        include_repl,
        tmpl,
    )

    # 2. 简单 {{ expr }} 替换
    #   - 顶层直接 dict key
    #   - a.b 访问 dict / obj
    #   - 函数调用 {{ pad2(d.num) }} → pad2(取整数字)
    #   - 自动忽略 Jinja-style 过滤器 {{ x | safe }} → 取 x
    def var_repl(m):
        expr = m.group(1).strip()
        # 剥离 Jinja-style 过滤器:只取 | 之前的部分
        if "|" in expr:
            expr = expr.split("|", 1)[0].strip()
        # 支持函数调用语法 {{ fn(arg.path) }}
        m_call = re.match(r"^(\w+)\((.+)\)$", expr)
        if m_call:
            fn_name = m_call.group(1)
            arg_path = m_call.group(2).strip()
            fn = ctx.get(fn_name)
            if callable(fn):
                # 求值参数
                parts = arg_path.split(".")
                cur: Any = ctx
                for p in parts:
                    if isinstance(cur, dict):
                        cur = cur.get(p, "")
                    else:
                        cur = getattr(cur, p, "")
                    if cur is None:
                        cur = ""
                try:
                    return str(fn(cur))
                except Exception:
                    return ""
        # 普通访问
        parts = expr.split(".")
        cur: Any = ctx
        for p in parts:
            if isinstance(cur, dict):
                cur = cur.get(p, "")
            else:
                cur = getattr(cur, p, "")
            if cur is None:
                cur = ""
        return str(cur)

    tmpl = re.sub(r"\{\{\s*([^}]+?)\s*\}\}", var_repl, tmpl)
    return tmpl


# ============================================================
# 全局 context 构造(每个页面都会用到)
# ============================================================


def common_context() -> dict:
    """所有页面共享的字段。"""
    return {
        "site_name": SITE_NAME,
        "site_lang": SITE_LANG,
        "site_tz": SITE_TIMEZONE_OFFSET,
        "site_url": SITE_URL,
        "build_date": date.today().isoformat(),
        "logo_emoji": "🚗",
        "pad2": lambda n: f"{int(n):02d}",
    }


def depth_prefix(depth: int) -> str:
    """当前页相对根目录的前缀('../' * depth)。"""
    return "../" * depth


def render_css_url(version: str = "v2", depth: int = 0) -> str:
    """生成 css/theme.min.css?v=xxx 相对 URL。

    depth: 当前页所在目录深度(0=根,1=子目录)
    """
    prefix = "../" * depth
    return f"{prefix}css/theme.min.css?v={version}"


def render_js_url(filename: str = "weather.js", depth: int = 0) -> str:
    """生成 js/xxx.js 相对 URL。"""
    prefix = "../" * depth
    return f"{prefix}js/{filename}"


# ============================================================
# JSON-LD
# ============================================================


def jsonld_website() -> str:
    """首页 JSON-LD:WebSite + ItemList(20 个 Day)。"""
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL + "/",
        "inLanguage": "zh-CN",
        "description": "2026 年新疆自驾 20 天攻略,含白哈巴",
    }
    return json.dumps(data, ensure_ascii=False)


def jsonld_day(day: Day) -> str:
    """每日详情页 JSON-LD:Article + Place。"""
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"D{day.num} · {day.title}",
        "datePublished": day.date_full,
        "inLanguage": "zh-CN",
        "url": f"{SITE_URL}/day/day-{day.num:02d}.html",
        "description": day.route,
    }
    return json.dumps(data, ensure_ascii=False)


def jsonld_article(title: str, desc: str) -> str:
    """通用 Article JSON-LD。"""
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "inLanguage": "zh-CN",
    }
    return json.dumps(data, ensure_ascii=False)


# ============================================================
# 顶层渲染入口
# ============================================================


def render_home(days: list[Day], weather_cities: list[WeatherCity], css_ver: str) -> str:
    """渲染首页。"""
    city_by_day = {c.day: c for c in weather_cities}

    # 预渲染:20 行 weather 速查表(模板渲染器不支持 for/if,所以 Python 拼好)
    rows = []
    for d in days:
        c = city_by_day[d.num]
        rows.append(
            f"<tr>"
            f'<td><a href="day/day-{d.num:02d}.html">D{d.num}</a></td>'
            f"<td>{d.date}</td>"
            f"<td>{d.route}</td>"
            f'<td><span class="weather-block" '
            f'data-lat="{c.lat}" data-lon="{c.lon}" '
            f'data-date="{c.date}" data-city="{c.city}">{d.temp}</span></td>'
            f"<td>{'⭐' if d.route_class == 'star' else '—'}</td>"
            f"</tr>"
        )
    weather_rows = "\n        ".join(rows)

    # 预渲染:20 个日卡片
    cards = []
    for d in days:
        badges_html = ""
        if d.route_class == "star":
            badges_html += '<div class="badge">⭐</div>'
        if d.weather_class == "hot":
            badges_html += '<div class="badge hot">热</div>'
        elif d.weather_class == "cold":
            badges_html += '<div class="badge cold">冷</div>'
        cards.append(
            f'<a class="day-card" href="day/day-{d.num:02d}.html">'
            f'<div class="day-num">D{d.num}</div>'
            f'<div class="day-date">{d.date}</div>'
            f'<div class="day-route">{d.title}</div>'
            f'<div class="day-temp">🌡️ {d.temp}</div>'
            f"{badges_html}"
            f"</a>"
        )
    day_cards = "\n      ".join(cards)

    ctx = common_context()
    ctx.update(
        {
            "title": f"{SITE_NAME} · 含白哈巴 · 一站式手册",
            "desc": SITE_DESC,
            "og_type": "website",
            "og_image": "assets/og-default.png",
            "canonical": f"{SITE_URL}/",
            "jsonld": jsonld_website(),
            "css_ver": css_ver,
            "depth": 0,
            "depth_prefix": "",
            "css_url": render_css_url(css_ver, depth=0),
            "weather_js_url": render_js_url("weather.js", depth=0),
            "theme_js_url": render_js_url("theme.js", depth=0),
            "page": "home",
            "is_home": True,
            "weather_rows": weather_rows,
            "day_cards": day_cards,
            "active_home": "active",
        }
    )
    tmpl = (SRC / "home.html.tmpl").read_text(encoding="utf-8")
    return _render_str(tmpl, ctx)


def render_day(day: Day, weather_cities: list[WeatherCity], css_ver: str) -> str:
    """渲染单日详情页。"""
    city = get_weather_city(weather_cities, day.num)

    # 预渲染:badges · weather · play · warn · 翻页
    badges = "".join(f'<span class="badge">{b}</span>' for b in day.badges)

    uv_label = "极强(极热段)" if day.weather_class == "hot" else "强(山区弱、平原强)"
    if city:
        weather_block = (
            f'<div class="weather-block" '
            f'data-lat="{city.lat}" data-lon="{city.lon}" '
            f'data-date="{city.date}" data-city="{city.city}">'
            f'<span class="temp"><strong>预测温区:</strong>{day.temp}</span>'
            f'<span class="desc"><strong>天气:</strong>{day.weather_text}</span>'
            f'<span class="uv"><strong>紫外线:</strong>{uv_label}</span>'
            f"</div>"
            f'<p class="text-sm text-subtle" style="margin-top:var(--s-2);">'
            f"💡 浏览器会自动拉取 Open-Meteo 16 天实时预报;失败时保留上方静态值</p>"
        )
    else:
        weather_block = f"<p>{day.temp}</p>"

    play_html = "\n".join(f"<li>{item}</li>" for item in day.play)
    warn_html = "\n".join(f"<li>{item}</li>" for item in day.warn)

    total = len(weather_cities)
    if day.num > 1:
        prev = f'<a class="prev" href="day-{day.num - 1:02d}.html">← 上一天</a>'
    else:
        prev = '<a class="prev" href="../index.html">← 回首页</a>'
    next_link = (
        f'<a href="day-{day.num + 1:02d}.html">下一天 →</a>'
        if day.num < total
        else '<a href="../index.html">回到首页 →</a>'
    )
    nav_html = prev + f'\n    <a class="home" href="../index.html">🏠 回首页</a>\n    ' + next_link

    ctx = common_context()
    ctx.update(
        {
            "title": f"D{day.num} · {day.title}",
            "desc": f"{day.title} · {day.temp} · {day.weather_text[:60]}",
            "og_type": "article",
            "og_image": "assets/og-default.png",
            "canonical": f"{SITE_URL}/day/day-{day.num:02d}.html",
            "jsonld": jsonld_day(day),
            "css_ver": css_ver,
            "depth": 1,
            "depth_prefix": "../",
            "css_url": render_css_url(css_ver, depth=1),
            "weather_js_url": render_js_url("weather.js", depth=1),
            "theme_js_url": render_js_url("theme.js", depth=1),
            "page": "day",
            "is_day": True,
            "day": day,
            "city": city,
            "badges_html": badges,
            "weather_block": weather_block,
            "play_html": play_html,
            "warn_html": warn_html,
            "nav_html": nav_html,
            "home_link": "../index.html",
        }
    )
    tmpl = (SRC / "day.html.tmpl").read_text(encoding="utf-8")
    return _render_str(tmpl, ctx)


def render_amap(
    chapter_id: str, title: str, body_html: str, css_ver: str, is_index: bool = False
) -> str:
    """渲染 amap 页面。

    chapter_id: 'index' | 'chapter-9-1' | ... 'chapter-9-5'
    """
    is_chapter = chapter_id != "index"
    depth = 1

    nav_items = [
        ("index.html", "📑 主页"),
        ("chapter-9-1.html", "9.1 使用方法"),
        ("chapter-9-2.html", "9.2 36 POI 链接"),
        ("chapter-9-3.html", "9.3 19 路线链接"),
        ("chapter-9-4.html", "9.4 多点标注"),
        ("chapter-9-5.html", "9.5 实战 + 同步"),
    ]

    nav_links = []
    for href, label in nav_items:
        # 全部是子目录内部相对引用(amap/chapter-*.html 同级)
        rel = href
        active_cls = (
            ' class="active"'
            if (
                (is_index and label == "📑 主页")
                or (not is_index and chapter_id == href.replace(".html", ""))
            )
            else ""
        )
        nav_links.append(f'<a href="{rel}"{active_cls}>{label}</a>')

    ctx = common_context()
    ctx.update(
        {
            "title": title,
            "desc": "高德导航行程一键设置 · 36 个 POI + 19 条路线链接",
            "og_type": "article",
            "og_image": "assets/og-default.png",
            "canonical": f"{SITE_URL}/amap/{chapter_id}.html",
            "jsonld": jsonld_article(title, ctx.get("desc", "")),
            "css_ver": css_ver,
            "depth": depth,
            "depth_prefix": depth_prefix(depth),
            "css_url": render_css_url(css_ver, depth=depth),
            "weather_js_url": render_js_url("weather.js", depth=depth),
            "theme_js_url": render_js_url("theme.js", depth=depth),
            "page": "amap",
            "is_amap": True,
            "is_index": is_index,
            "chapter_id": chapter_id,
            "nav_html": "\n".join(nav_links),
            "active_label": "📑 主页" if is_index else "",
            "header_subtitle": "20 天 · 含白哈巴版 · 数据基准 2026/07/14",
            "body_html": body_html,
        }
    )
    tmpl = (SRC / "amap.html.tmpl").read_text(encoding="utf-8")
    return _render_str(tmpl, ctx)
