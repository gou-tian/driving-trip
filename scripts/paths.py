"""路径常量 + 资源 URL 工具。

部署到子路径时,所有引用都走 asset() 函数生成相对 URL,
避免引入 <base> 或硬编码域名前缀。
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"

# ============= 源 / 产物路径 =============
SRC_PARTIALS = SRC / "partials"
SRC_CSS = SRC / "css"
SRC_JS = SRC / "js"
SRC_DATA = SRC / "data"
SRC_ASSETS = SRC / "assets"

DIST_CSS = DIST / "css"
DIST_JS = DIST / "js"
DIST_DAY = DIST / "day"
DIST_AMAP = DIST / "amap"
DIST_INFO = DIST / "info"
DIST_ASSETS = DIST / "assets"

SRC_DATA_INFO = SRC_DATA / "info.json"

# ============= 站点元数据 =============
SITE_NAME = "新疆自驾 20 天"
SITE_DESC = (
    "2026 年 7-8 月 20 天新疆自驾攻略 · 含白哈巴 · 精简东疆版 · 实时天气 + 高德导航行程一键直达"
)
# 支持 SITE_URL 环境变量覆盖,默认部署到 gtian.cn(自托管 nginx)
# GH Pages 部署时设为 https://<user>.github.io/<repo>/
SITE_URL = os.environ.get("SITE_URL", "https://trip.gtian.cn/xinjiang")
SITE_LOCALE = "zh_CN"
SITE_LANG = "zh-CN"
SITE_TIMEZONE_OFFSET = "+08:00"


# ============= 自动版本号 =============
def file_hash(path: Path) -> str:
    """8 位 SHA1 哈希(用于 CSS/JS 文件版本号)。"""
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8]


def asset(rel: str, v: str = "") -> str:
    """生成相对资源 URL:css/theme.min.css?v=abc123

    rel: 相对 DIST 根的路径,如 'css/theme.min.css'
    v:   版本号,默认空
    """
    if v:
        return f"{rel}?v={v}"
    return rel


def relpath_from(from_html: Path, target: str) -> str:
    """生成从 HTML 文件到 target 的相对路径。

    from_html: HTML 文件绝对路径
    target:    相对资源路径,如 'css/theme.min.css'
    """
    target_path = (from_html.parent / target).resolve()
    return os.path.relpath(target_path, start=from_html.parent)
