"""Pure-Python inline-SVG chart renderers.

No JavaScript or CDN dependency, so both the live dashboard and the exported
report are fully self-contained and work offline. Palette matches the neon
theme from ``app/globals.css``.
"""

from __future__ import annotations

import math
from html import escape
from typing import Sequence

COLORS = {
    "purple": "#a855f7",
    "cyan": "#06b6d4",
    "green": "#22c55e",
    "orange": "#f97316",
    "red": "#ef4444",
    "blue": "#3b82f6",
    "yellow": "#eab308",
    "grid": "#2a2a44",
    "axis": "#888888",
    "muted": "#6b7280",
}

_CLASSIFICATION_COLORS = [COLORS["orange"], COLORS["cyan"], COLORS["purple"], COLORS["green"], COLORS["blue"]]


def _empty(message: str = "No data") -> str:
    return (
        '<div style="height:200px;display:flex;align-items:center;'
        'justify-content:center;color:#6b7280;font-size:13px">'
        f"{escape(message)}</div>"
    )


def bar_chart(data: Sequence[dict], key_label: str, key_value: str,
              color: str = COLORS["purple"], height: int = 200) -> str:
    """Vertical bar chart. `data` items expose key_label (x) and key_value (y)."""
    items = [d for d in data if d.get(key_value) is not None]
    if not items:
        return _empty()

    width, pad_l, pad_b, pad_t = 340, 32, 34, 12
    plot_h = height - pad_b - pad_t
    plot_w = width - pad_l - 10
    max_v = max(int(d[key_value]) for d in items) or 1
    n = len(items)
    slot = plot_w / n
    bar_w = min(slot * 0.6, 46)

    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" '
             'preserveAspectRatio="xMidYMid meet" role="img">']
    # gridlines + y labels
    for i in range(4):
        y = pad_t + plot_h * i / 3
        val = round(max_v * (3 - i) / 3)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - 10}" y2="{y:.1f}" '
                     f'stroke="{COLORS["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l - 6}" y="{y + 4:.1f}" text-anchor="end" '
                     f'font-size="10" fill="{COLORS["axis"]}">{val}</text>')
    # bars
    for i, d in enumerate(items):
        v = int(d[key_value])
        bh = plot_h * (v / max_v)
        x = pad_l + slot * i + (slot - bar_w) / 2
        y = pad_t + plot_h - bh
        label = escape(str(d.get(key_label, ""))[:10])
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" '
                     f'rx="3" fill="{color}"><title>{label}: {v}</title></rect>')
        parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{height - 12}" text-anchor="middle" '
                     f'font-size="10" fill="{COLORS["axis"]}">{label}</text>')
    parts.append("</svg>")
    return "".join(parts)


def doughnut_chart(data: Sequence[dict], key_label: str, key_value: str,
                   height: int = 200) -> str:
    """Doughnut chart with a legend, matching the pie in the original UI."""
    items = [d for d in data if int(d.get(key_value) or 0) > 0]
    if not items:
        return _empty()

    total = sum(int(d[key_value]) for d in items)
    cx, cy, r, inner = 100, height / 2, 70, 40
    parts = [f'<svg viewBox="0 0 340 {height}" width="100%" height="{height}" '
             'preserveAspectRatio="xMidYMid meet" role="img">']
    angle = -math.pi / 2
    for i, d in enumerate(items):
        frac = int(d[key_value]) / total
        sweep = frac * 2 * math.pi
        end = angle + sweep
        color = _CLASSIFICATION_COLORS[i % len(_CLASSIFICATION_COLORS)]
        large = 1 if sweep > math.pi else 0
        x1, y1 = cx + r * math.cos(angle), cy + r * math.sin(angle)
        x2, y2 = cx + r * math.cos(end), cy + r * math.sin(end)
        ix2, iy2 = cx + inner * math.cos(end), cy + inner * math.sin(end)
        ix1, iy1 = cx + inner * math.cos(angle), cy + inner * math.sin(angle)
        path = (f'M {x1:.2f} {y1:.2f} A {r} {r} 0 {large} 1 {x2:.2f} {y2:.2f} '
                f'L {ix2:.2f} {iy2:.2f} A {inner} {inner} 0 {large} 0 {ix1:.2f} {iy1:.2f} Z')
        label = escape(str(d.get(key_label, "")))
        parts.append(f'<path d="{path}" fill="{color}"><title>{label}: {int(d[key_value])} '
                     f'({frac * 100:.0f}%)</title></path>')
        angle = end
    parts.append(f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="20" '
                 f'font-weight="700" fill="#e5e7eb">{total}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 15}" text-anchor="middle" font-size="10" '
                 f'fill="{COLORS["muted"]}">total</text>')
    # legend
    ly = 24
    for i, d in enumerate(items):
        color = _CLASSIFICATION_COLORS[i % len(_CLASSIFICATION_COLORS)]
        label = escape(str(d.get(key_label, "")))
        parts.append(f'<rect x="200" y="{ly - 9}" width="10" height="10" rx="2" fill="{color}"/>')
        parts.append(f'<text x="216" y="{ly}" font-size="11" fill="#cbd5e1">'
                     f'{label} · {int(d[key_value])}</text>')
        ly += 22
    parts.append("</svg>")
    return "".join(parts)


def line_chart(data: Sequence[dict], key_label: str, key_value: str,
               color: str = COLORS["orange"], height: int = 200) -> str:
    """Line chart for time-series trend data."""
    items = [d for d in data if d.get(key_value) is not None]
    if not items:
        return _empty()
    if len(items) == 1:  # a single point still deserves a marker
        items = [items[0], items[0]]

    width, pad_l, pad_b, pad_t, pad_r = 340, 32, 34, 12, 12
    plot_h = height - pad_b - pad_t
    plot_w = width - pad_l - pad_r
    max_v = max(int(d[key_value]) for d in items) or 1
    n = len(items)

    def px(i: int) -> float:
        return pad_l + (plot_w * i / (n - 1) if n > 1 else plot_w / 2)

    def py(v: int) -> float:
        return pad_t + plot_h * (1 - v / max_v)

    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" '
             'preserveAspectRatio="xMidYMid meet" role="img">']
    for i in range(4):
        y = pad_t + plot_h * i / 3
        val = round(max_v * (3 - i) / 3)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" '
                     f'stroke="{COLORS["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l - 6}" y="{y + 4:.1f}" text-anchor="end" '
                     f'font-size="10" fill="{COLORS["axis"]}">{val}</text>')
    pts = [(px(i), py(int(d[key_value]))) for i, d in enumerate(items)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    # area fill
    area = f"{pad_l},{pad_t + plot_h} " + poly + f" {px(n - 1):.1f},{pad_t + plot_h}"
    parts.append(f'<polygon points="{area}" fill="{color}" opacity="0.12"/>')
    parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" '
                 'stroke-width="2" stroke-linejoin="round"/>')
    for (x, y), d in zip(pts, items):
        v = int(d[key_value])
        lbl = escape(str(d.get(key_label, ""))[-5:])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}">'
                     f'<title>{lbl}: {v}</title></circle>')
    # x labels (first / mid / last to avoid clutter)
    for idx in sorted({0, n // 2, n - 1}):
        lbl = escape(str(items[idx].get(key_label, ""))[-5:])
        parts.append(f'<text x="{px(idx):.1f}" y="{height - 12}" text-anchor="middle" '
                     f'font-size="10" fill="{COLORS["axis"]}">{lbl}</text>')
    parts.append("</svg>")
    return "".join(parts)
