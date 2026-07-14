"""Sitemap / robots / manifest 测试。

跑:
  python -m pytest tests/test_sitemap.py -v
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.seo import write_sitemap, write_robots, write_manifest  # noqa: E402
from scripts.paths import DIST  # noqa: E402


class TestSitemap:
    """sitemap.xml 格式 + 内容测试。"""

    def test_basic_structure(self, tmp_path):
        pages = [
            ("/index.html", "daily", 1.0),
            ("/day/day-01.html", "monthly", 0.8),
        ]
        # 临时替换 DIST
        import scripts.seo as seo_mod

        original_dist = seo_mod.DIST
        seo_mod.DIST = tmp_path
        try:
            out = write_sitemap(pages)
            content = out.read_text(encoding="utf-8")
            assert '<?xml version="1.0"' in content
            assert "<urlset" in content
            assert "<url>" in content
            assert "<loc>" in content
            assert "<priority>1.0</priority>" in content
        finally:
            seo_mod.DIST = original_dist

    def test_count_pages_27(self):
        """期望 27 个 URL(1 + 20 + 6)。"""
        if not (DIST / "index.html").exists():
            import pytest

            pytest.skip("需要先 build")
        from scripts.seo import collect_pages

        pages = collect_pages()
        assert len(pages) >= 27


class TestRobots:
    """robots.txt 格式测试。"""

    def test_format(self, tmp_path):
        import scripts.seo as seo_mod

        original_dist = seo_mod.DIST
        seo_mod.DIST = tmp_path
        try:
            out = write_robots()
            content = out.read_text(encoding="utf-8")
            assert "User-agent: *" in content
            assert "Allow: /" in content
            assert "Sitemap:" in content
        finally:
            seo_mod.DIST = original_dist


class TestManifest:
    """PWA manifest 测试。"""

    def test_format(self, tmp_path):
        import scripts.seo as seo_mod

        original_dist = seo_mod.DIST
        seo_mod.DIST = tmp_path
        try:
            out = write_manifest()
            data = json.loads(out.read_text(encoding="utf-8"))
            assert data["name"] == "新疆自驾 20 天"
            assert data["start_url"] == "./"
            assert data["display"] == "standalone"
            assert len(data["icons"]) >= 2
            for icon in data["icons"]:
                assert icon["src"].startswith("assets/")
                assert "192" in icon["sizes"] or "512" in icon["sizes"]
        finally:
            seo_mod.DIST = original_dist
