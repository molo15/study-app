# -*- coding: utf-8 -*-
"""发布准备：生成应用图标与启动页资源。

- 5 密度传统图标 mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher.png (48/72/96/144/192)
- 自适应图标 mipmap-anydpi-v26/ic_launcher.xml + drawable/ic_launcher_foreground.png(512)
- 启动页 drawable/launch_background.xml(浅) + drawable-night/launch_background.xml(深)
  + launch_logo_light/dark.png + values/colors.xml

图标设计：深青(#00696D)圆角方形底 + 白色开放书本(书脊金点星)。
启动页：品牌过渡，居中图标+「考研刷题」文字。
"""
import os
import math

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/
RES = os.path.join(BASE, '..', 'app', 'android', 'app', 'src', 'main', 'res')

PRIMARY = (0x00, 0x69, 0x6D)   # 深青 #00696D
GOLD = (0xE2, 0xB9, 0x3B)      # 金色 #E2B93B
WHITE = (255, 255, 255)
LIGHT_BG = (0xF4, 0xF7, 0xF6)  # 浅色背景
DARK_BG = (0x10, 0x14, 0x18)    # 深色背景

FONT = r'C:\Windows\Fonts\msyh.ttc'  # 微软雅黑


def rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_book(draw, cx, cy, w, h, color):
    """开放书本：两页多边形 + 书脊 + 底部书口线。"""
    # 左页（页面向左微张）
    left = [
        (cx - w / 2, cy + h / 2),
        (cx - w / 2 + 26, cy - h / 2),
        (cx - 6, cy - h / 2 + 10),
        (cx - 6, cy + h / 2 - 6),
    ]
    # 右页
    right = [
        (cx + w / 2, cy + h / 2),
        (cx + w / 2 - 26, cy - h / 2),
        (cx + 6, cy - h / 2 + 10),
        (cx + 6, cy + h / 2 - 6),
    ]
    draw.polygon(left, fill=color)
    draw.polygon(right, fill=color)
    # 书脊阴影线
    draw.line([(cx, cy - h / 2 + 10), (cx, cy + h / 2 - 6)],
              fill=PRIMARY, width=4)
    # 底部书口线
    draw.line([(cx - w / 2 + 2, cy + h / 2 - 2), (cx + w / 2 - 2, cy + h / 2 - 2)],
              fill=tuple(int(v * 0.82) for v in color), width=5)


def make_icon(size):
    """传统/前景图标：深青圆角底 + 白书 + 金点。"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 圆角方形底（半径约 22%）
    radius = int(size * 0.22)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=PRIMARY)
    # 书本位于中心 62% 安全区
    cx = cy = size / 2
    w = size * 0.52
    h = size * 0.40
    draw_book(draw, cx, cy + size * 0.02, w, h, WHITE)
    # 金色重点星（书右上）
    s = size * 0.09
    sx, sy = cx + w * 0.42, cy - h * 0.46
    draw.polygon(star_points(sx, sy, s, s * 2.2), fill=GOLD)
    return img


def star_points(cx, cy, r_in, r_out, n=5):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        ang = math.pi / 2 + i * math.pi / n
        pts.append((cx + r * math.cos(ang), cy - r * math.sin(ang)))
    return pts


def make_foreground(size=512):
    """自适应图标前景：透明底，图案占中心 62%（安全区）。"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = size / 2
    w = size * 0.56
    h = size * 0.44
    draw_book(draw, cx, cy + size * 0.02, w, h, WHITE)
    s = size * 0.10
    sx, sy = cx + w * 0.42, cy - h * 0.46
    draw.polygon(star_points(sx, sy, s, s * 2.2), fill=GOLD)
    return img


def make_launch_logo(bg_color, fg_color, dark):
    """启动页 logo：图标(深青底圆角) + 「考研刷题」文字，浅/深两版。"""
    W, H = 720, 720
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    icon = make_icon(360)
    img.paste(icon, ((W - 360) // 2, 90), icon)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT, 72)
    except Exception:
        font = ImageFont.load_default()
    text = '考研刷题'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2 - bbox[0], 500), text, font=font, fill=fg_color)
    return img


def main():
    # 传统图标 5 密度
    for dpi, px in [('mdpi', 48), ('hdpi', 72), ('xhdpi', 96),
                    ('xxhdpi', 144), ('xxxhdpi', 192)]:
        d = os.path.join(RES, f'mipmap-{dpi}')
        os.makedirs(d, exist_ok=True)
        make_icon(px).save(os.path.join(d, 'ic_launcher.png'))

    # 自适应图标
    anydpi = os.path.join(RES, 'mipmap-anydpi-v26')
    os.makedirs(anydpi, exist_ok=True)
    drawable = os.path.join(RES, 'drawable')
    os.makedirs(drawable, exist_ok=True)
    make_foreground().save(os.path.join(drawable, 'ic_launcher_foreground.png'))
    with open(os.path.join(drawable, 'ic_launcher_background.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<color xmlns:android="http://schemas.android.com/apk/res/android">'
                '#00696D</color>\n')
    with open(os.path.join(drawable, 'ic_launcher_foreground.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<bitmap xmlns:android="http://schemas.android.com/apk/res/android" '
                'android:src="@drawable/ic_launcher_foreground"/>')
    with open(os.path.join(anydpi, 'ic_launcher.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
                '    <background android:drawable="@drawable/ic_launcher_background"/>\n'
                '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n'
                '</adaptive-icon>\n')

    # 启动页 logo（浅/深）
    make_launch_logo(LIGHT_BG, PRIMARY, dark=False).save(
        os.path.join(drawable, 'launch_logo_light.png'))
    make_launch_logo(DARK_BG, WHITE, dark=True).save(
        os.path.join(drawable, 'launch_logo_dark.png'))

    # 启动页背景 XML（浅）
    with open(os.path.join(RES, 'drawable', 'launch_background.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<layer-list xmlns:android="http://schemas.android.com/apk/res/android">\n'
                '    <item android:drawable="@color/launch_bg_light"/>\n'
                '    <item>\n'
                '        <bitmap android:gravity="center" '
                'android:src="@drawable/launch_logo_light"/>\n'
                '    </item>\n'
                '</layer-list>\n')
    # 深色启动页
    night = os.path.join(RES, 'drawable-night')
    os.makedirs(night, exist_ok=True)
    with open(os.path.join(night, 'launch_background.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<layer-list xmlns:android="http://schemas.android.com/apk/res/android">\n'
                '    <item android:drawable="@color/launch_bg_dark"/>\n'
                '    <item>\n'
                '        <bitmap android:gravity="center" '
                'android:src="@drawable/launch_logo_dark"/>\n'
                '    </item>\n'
                '</layer-list>\n')
    # 颜色定义
    values = os.path.join(RES, 'values')
    os.makedirs(values, exist_ok=True)
    with open(os.path.join(values, 'colors.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<resources>\n'
                '    <color name="launch_bg_light">#F4F7F6</color>\n'
                '    <color name="launch_bg_dark">#101418</color>\n'
                '</resources>\n')

    print('✅ 已生成：')
    for root, _, files in os.walk(RES):
        for fn in files:
            if fn in ('ic_launcher.png', 'launch_background.xml', 'colors.xml',
                      'ic_launcher.xml', 'ic_launcher_foreground.png',
                      'ic_launcher_background.xml', 'launch_logo_light.png',
                      'launch_logo_dark.png', 'ic_launcher_foreground.xml'):
                print('  ', os.path.relpath(os.path.join(root, fn), os.path.join(BASE, '..')))


if __name__ == '__main__':
    main()
