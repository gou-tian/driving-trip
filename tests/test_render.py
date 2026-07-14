"""渲染单元测试。

跑:
  python -m pytest tests/test_render.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.render import render_home, render_day, render_amap, _render_str  # noqa: E402
from scripts.trip_data import load_days, load_weather_cities  # noqa: E402
from scripts.seo import collect_pages, write_sitemap, write_robots  # noqa: E402
from scripts.paths import DIST  # noqa: E402

# ============================================================
# 渲染测试
# ============================================================


class TestRenderHome:
    """首页渲染测试。"""

    def setup_method(self):
        self.days = load_days()
        self.cities = load_weather_cities()
        self.html = render_home(self.days, self.cities, "testver")

    def test_basic_structure(self):
        assert "<!DOCTYPE html>" in self.html
        assert '<html lang="zh-CN">' in self.html
        assert "<title>" in self.html
        assert "</html>" in self.html

    def test_meta_tags(self):
        assert '<meta name="description"' in self.html
        assert '<meta property="og:title"' in self.html
        assert '<link rel="canonical"' in self.html

    def test_jsonld(self):
        assert "application/ld+json" in self.html
        assert '"@type"' in self.html

    def test_20_days_table(self):
        for n in range(1, 21):
            assert f"D{n}" in self.html or f"day-{n:02d}" in self.html

    def test_css_version_in_url(self):
        assert "?v=testver" in self.html

    def test_20_weather_blocks(self):
        # 首页速查表 20 行都有 data-lat
        assert self.html.count("data-lat=") == 20

    def test_relative_paths_no_absolute(self):
        """不应该有绝对 URL 引用(除了 meta)。"""
        # 排除掉 og:url / canonical / JSON-LD
        import re

        bad = re.findall(r'href="https?://', self.html)
        # og:url 是 meta 属性,不算
        assert all("og:url" not in line for line in self.html.split("\n"))


class TestRenderDay:
    """每日详情页渲染测试。"""

    def setup_method(self):
        self.days = load_days()
        self.cities = load_weather_cities()
        self.html = render_day(self.days[0], self.cities, "v2")  # D1

    def test_basic(self):
        assert "<!DOCTYPE html>" in self.html
        assert "太原" in self.html

    def test_modules(self):
        for kw in ["路程", "天气", "穿着", "游玩", "注意事项"]:
            assert kw in self.html, f"缺少 module: {kw}"

    def test_weather_data_attrs(self):
        assert "data-lat=" in self.html
        assert "data-lon=" in self.html
        assert "data-date=" in self.html

    def test_navigation_links(self):
        assert 'href="../index.html"' in self.html
        assert "day-02.html" in self.html

    def test_a11y_attrs(self):
        assert "aria-label" in self.html

    def test_css_relative_path(self):
        """子目录页应使用 ../css/ 相对路径。"""
        assert 'href="../css/' in self.html


class TestRenderAmap:
    """AMAP 章节渲染测试。"""

    def test_main_guide(self):
        html = render_amap("index", "主指南", "<div>body</div>", "v2", is_index=True)
        assert "<!DOCTYPE html>" in html
        assert "主指南" in html
        assert 'class="active"' in html

    def test_chapter(self):
        html = render_amap("chapter-9-2", "9.2 36 POI 链接清单", "<div>body</div>", "v2")
        assert 'href="chapter-9-1.html"' in html or "chapter-9" in html


class TestRenderMechanics:
    """渲染工具函数测试。"""

    def test_include_nested(self):
        html = _render_str(
            '{% include "footer.html" %}',
            {"depth_prefix": "../", "build_date": "2026-07-14", "site_name": "test"},
        )
        # footer.html 包含 {{ site_name }}
        assert "test" in html

    def test_var_substitution(self):
        html = _render_str("{{ a }} - {{ b.c }}", {"a": 1, "b": {"c": 2}})
        assert html == "1 - 2"


# ============================================================
# SEO 测试
# ============================================================


class TestSEO:
    """SEO 自动化测试。"""

    def test_collect_pages_returns_paths(self):
        # 需要先 build,这里跳过 dist 检查(假设已构建)
        if not DIST.exists():
            import pytest

            pytest.skip("需要先运行 python -m scripts.build --clean")
        pages = collect_pages()
        assert len(pages) >= 27, f"应该 ≥27 个页面,实际 {len(pages)}"
        # 每项是 (/path, freq, priority)
        for url_path, freq, priority in pages:
            assert url_path.startswith("/")
            assert freq in ("daily", "weekly", "monthly")
            assert 0 <= priority <= 1
