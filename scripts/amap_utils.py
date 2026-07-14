"""高德 URI 工厂:search / marker / navigation 链接生成。

公共实例对脚本友好,无严格限制、无 API key。
"""

from __future__ import annotations

from urllib.parse import quote, urlencode

BASE = "https://uri.amap.com"


def search(keyword: str, city: str = "", src: str = "xj2026") -> str:
    """POI 搜索链接。"""
    params = {"keyword": keyword, "src": src, "callnative": "1"}
    if city:
        params["city"] = city
    return f"{BASE}/search?{urlencode(params)}"


def marker(lon: float, lat: float, name: str, src: str = "xj2026") -> str:
    """POI marker 链接(精准经纬度)。"""
    return (
        f"{BASE}/marker?"
        f"position={lon},{lat}&name={quote(name)}"
        f"&src={src}&callnative=1&coordinate=gaode"
    )


def multi_marker(markers: list, src: str = "xj2026") -> str:
    """多 POI marker 链接。markers: [(lon, lat, name), ...]"""
    segs = "|".join(f"{lon},{lat},{quote(name)}" for lon, lat, name in markers)
    return f"{BASE}/marker?markers={quote(segs)}&src={src}&callnative=1"


def navigation(
    from_kw: str, to_kw: str, via: list | None = None, mode: str = "car", src: str = "xj2026"
) -> str:
    """路线导航链接。"""
    params = {
        "from": from_kw,
        "to": to_kw,
        "mode": mode,
        "src": src,
        "callnative": "1",
    }
    if via:
        params["via"] = "|".join(via)
    return f"{BASE}/navigation?{urlencode(params)}"
