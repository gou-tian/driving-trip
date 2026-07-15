"""加载 trip.json + weather_cities.json → 数据访问层。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from scripts.paths import SRC_DATA


@dataclass
class Day:
    """单日结构。"""

    num: int
    date: str
    date_full: str
    title: str
    route: str
    route_class: str
    temp: str
    weather_text: str
    weather_class: str
    badges: list
    route_detail: str
    clothes: str
    play: list
    warn: list


@dataclass
class WeatherCity:
    """日所在城市的经纬度。"""

    day: int
    city: str
    lat: float
    lon: float
    date: str  # YYYY-MM-DD


def load_days() -> list[Day]:
    """加载 20 天行程。"""
    raw = json.loads((SRC_DATA / "trip.json").read_text(encoding="utf-8"))
    return [Day(**d) for d in raw]


def load_weather_cities() -> list[WeatherCity]:
    """加载 20 个城市经纬度。"""
    raw = json.loads((SRC_DATA / "weather_cities.json").read_text(encoding="utf-8"))
    return [WeatherCity(**c) for c in raw]


def get_weather_city(days_index: list[WeatherCity], day_num: int) -> WeatherCity | None:
    """按日编号查找城市。"""
    for c in days_index:
        if c.day == day_num:
            return c
    return None


def load_info() -> dict:
    """加载 src/data/info.json(通用信息 11 section 数据)。"""
    import json

    from scripts.paths import SRC_DATA_INFO

    if not SRC_DATA_INFO.exists():
        return {}
    return json.loads(SRC_DATA_INFO.read_text(encoding="utf-8"))
