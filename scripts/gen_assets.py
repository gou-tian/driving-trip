"""生成 src/assets/ 占位图标(PNG)。

策略:避开 emoji 字体兼容问题,改用蓝色渐变 + "XJ" 文字 logo。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC_ASSETS = Path(__file__).resolve().parents[1] / "src" / "assets"


def _grad_bg(size: tuple[int, int]) -> Image.Image:
    """生成蓝-深蓝渐变背景。"""
    img = Image.new("RGB", size, (20, 63, 110))
    draw = ImageDraw.Draw(img)
    w, h = size
    for y in range(h):
        ratio = y / h
        r = int(20 + (37 - 20) * ratio)
        g = int(63 + (99 - 63) * ratio)
        b = int(110 + (168 - 110) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _sys_font(size: int) -> ImageFont.FreeTypeFont:
    """加载系统普通字体(Mac 默认 Helvetica / Arial)。"""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def make_icon(size: int, name: str) -> None:
    img = _grad_bg((size, size))
    draw = ImageDraw.Draw(img)

    # 圆角:在内部填充白色描边
    padding = size // 8
    draw.rectangle(
        [padding, padding, size - padding, size - padding],
        outline="#ffd966",
        width=max(2, size // 32),
    )

    # 中间字母 "XJ"
    font = _sys_font(int(size * 0.36))
    text = "XJ"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - tw) // 2 - bbox[0], (size - th) // 2 - bbox[1]),
        text,
        font=font,
        fill="white",
    )

    # 底部小副标题
    sub_font = _sys_font(int(size * 0.10))
    sub = "新疆"
    bbox2 = draw.textbbox((0, 0), sub, font=sub_font)
    sw = bbox2[2] - bbox2[0]
    draw.text(
        ((size - sw) // 2 - bbox2[0], size * 0.78),
        sub,
        font=sub_font,
        fill="#ffd966",
    )
    out = SRC_ASSETS / name
    img.save(out, format="PNG", optimize=True)
    print(f"✅ {out.name} ({size}×{size}, {out.stat().st_size:,} B)")


def make_og(size: tuple[int, int] = (1200, 630), name: str = "og-default.png") -> None:
    img = _grad_bg(size)
    draw = ImageDraw.Draw(img)
    font = _sys_font(int(size[0] * 0.08))
    text = "XJ · 新疆自驾 20 天"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size[0] - tw) // 2 - bbox[0], (size[1] - th) // 2 - bbox[1] - size[0] * 0.05),
        text,
        font=font,
        fill="white",
    )
    sub_font = _sys_font(int(size[0] * 0.025))
    sub = "含白哈巴 · 精简东疆版 · 实时天气 + 高德导航一键直达"
    bbox2 = draw.textbbox((0, 0), sub, font=sub_font)
    sw = bbox2[2] - bbox2[0]
    draw.text(
        ((size[0] - sw) // 2 - bbox2[0], size[1] // 2 + size[0] * 0.04),
        sub,
        font=sub_font,
        fill="#ffd966",
    )
    out = SRC_ASSETS / name
    img.save(out, format="PNG", optimize=True)
    print(f"✅ {out.name} ({size[0]}×{size[1]}, {out.stat().st_size:,} B)")


def main():
    SRC_ASSETS.mkdir(parents=True, exist_ok=True)
    make_icon(192, "icon-192.png")
    make_icon(512, "icon-512.png")
    make_icon(180, "apple-touch-icon.png")
    make_og()


if __name__ == "__main__":
    main()
