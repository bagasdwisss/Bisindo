import os
import math
from PIL import Image, ImageDraw

os.makedirs("assets/kosakata", exist_ok=True)

def load_hand(letter, scale=1.0, flip_h=False, rotate_deg=0):
    path = f"assets/abjad/{letter}.png"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    im = Image.open(path).convert("RGBA")
    if flip_h:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rotate_deg != 0:
        im = im.rotate(rotate_deg, resample=Image.BICUBIC, expand=True)
    if scale != 1.0:
        nw = max(1, int(im.width * scale))
        nh = max(1, int(im.height * scale))
        im = im.resize((nw, nh), resample=Image.LANCZOS)
    return im

def create_card(w=400, h=300):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))

def draw_arrow(draw, start, end, color=(59, 130, 246, 255), width=5, arrow_size=12):
    draw.line([start, end], fill=color, width=width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    x1 = end[0] - arrow_size * math.cos(angle - math.pi / 6)
    y1 = end[1] - arrow_size * math.sin(angle - math.pi / 6)
    x2 = end[0] - arrow_size * math.cos(angle + math.pi / 6)
    y2 = end[1] - arrow_size * math.sin(angle + math.pi / 6)
    draw.polygon([end, (x1, y1), (x2, y2)], fill=color)

def draw_curved_arrow(draw, points, color=(59, 130, 246, 255), width=5, arrow_size=12):
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=width)
    end = points[-1]
    prev = points[-2]
    dx = end[0] - prev[0]
    dy = end[1] - prev[1]
    angle = math.atan2(dy, dx)
    x1 = end[0] - arrow_size * math.cos(angle - math.pi / 6)
    y1 = end[1] - arrow_size * math.sin(angle - math.pi / 6)
    x2 = end[0] - arrow_size * math.cos(angle + math.pi / 6)
    y2 = end[1] - arrow_size * math.sin(angle + math.pi / 6)
    draw.polygon([end, (x1, y1), (x2, y2)], fill=color)

# 1. ambil: 1 hand, reaching open then closing inward to chest
def make_ambil():
    c = create_card()
    h1 = load_hand("B", scale=1.05, rotate_deg=-15)
    h2 = load_hand("S", scale=1.05)
    c.alpha_composite(h1, (220, 60))
    c.alpha_composite(h2, (60, 90))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (230, 160), (160, 160), color=(59, 130, 246, 255), width=6)
    return c

# 2. apa: 2 open hands palms up at chest level (BISINDO: TIMRP)
def make_apa():
    c = create_card()
    h_l = load_hand("B", scale=1.05, flip_h=True, rotate_deg=25)
    h_r = load_hand("B", scale=1.05, rotate_deg=-25)
    c.alpha_composite(h_l, (40, 70))
    c.alpha_composite(h_r, (210, 70))
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(70, 75), (60, 50), (45, 60)], color=(59, 130, 246, 255), width=5)
    draw_curved_arrow(d, [(330, 75), (340, 50), (355, 60)], color=(59, 130, 246, 255), width=5)
    # Question indicator
    d.arc([(185, 30), (215, 65)], start=180, end=360, fill=(59, 130, 246, 255), width=5)
    d.line([(200, 65), (200, 80)], fill=(59, 130, 246, 255), width=5)
    d.ellipse([(196, 90), (204, 98)], fill=(59, 130, 246, 255))
    return c

# 3. bantu: 1 hand fist pushing forward / supporting
def make_bantu():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=80)
    h_fist = load_hand("S", scale=1.1)
    c.alpha_composite(h_base, (80, 130))
    c.alpha_composite(h_fist, (140, 40))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (260, 110), (340, 110), color=(16, 185, 129, 255), width=6)
    return c

# 4. berdoa: Two clasped hands flat in prayer at chest (TIMRP)
def make_berdoa():
    c = create_card()
    h1 = load_hand("B", scale=1.15, rotate_deg=-10)
    h2 = load_hand("B", scale=1.15, flip_h=True, rotate_deg=10)
    c.alpha_composite(h1, (100, 40))
    c.alpha_composite(h2, (180, 40))
    d = ImageDraw.Draw(c)
    # Spiritual golden radiance
    cx, cy = 200, 25
    color = (245, 158, 11, 255)
    d.line([(cx, cy-12), (cx, cy+4)], fill=color, width=3)
    d.line([(cx-12, cy-8), (cx-4, cy+2)], fill=color, width=3)
    d.line([(cx+12, cy-8), (cx+4, cy+2)], fill=color, width=3)
    return c

# 5. berhenti: 1 hand, flat open palm facing forward (TIMRP, -78 deg)
def make_berhenti():
    c = create_card()
    h = load_hand("B", scale=1.35)
    pos = ((c.width - h.width)//2 - 15, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    cx, cy, r = 310, 80, 32
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(239, 68, 68, 255))
    d.rounded_rectangle([(cx-22, cy-6), (cx+22, cy+6)], radius=3, fill=(255, 255, 255, 255))
    return c

# 6. berjalan: 2 hands - V hand walking legs downward (ang=82 deg) on horizontal B palm (ang=-7 deg)
def make_berjalan():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=90)
    h_walk = load_hand("V", scale=1.15, rotate_deg=180)
    c.alpha_composite(h_base, (60, 140))
    c.alpha_composite(h_walk, (140, 30))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (240, 140), (320, 140), color=(16, 185, 129, 255), width=6)
    return c

# 7. berpikir: 1 hand, index finger TI pointing to temple (ang=-46 deg)
def make_berpikir():
    c = create_card()
    h = load_hand("D", scale=1.25, rotate_deg=-25)
    c.alpha_composite(h, (90, 70))
    d = ImageDraw.Draw(c)
    color = (245, 158, 11, 255)
    d.ellipse([(250, 90), (266, 106)], fill=color)
    d.ellipse([(280, 65), (300, 85)], fill=color)
    d.ellipse([(315, 35), (345, 65)], fill=color)
    return c

# 8. betul: 1 hand, TI thumb & index extended in confirmation (L/check shape)
def make_betul():
    c = create_card()
    h = load_hand("L", scale=1.25, rotate_deg=10)
    c.alpha_composite(h, (90, 65))
    d = ImageDraw.Draw(c)
    cx, cy, r = 290, 100, 32
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(16, 185, 129, 255))
    d.line([(cx-16, cy), (cx-6, cy+12), (cx+16, cy-12)], fill=(255, 255, 255, 255), width=6)
    return c

# 9. bisindo: Official BISINDO sign (two B hands meeting in front)
def make_bisindo():
    c = create_card()
    h1 = load_hand("B", scale=1.05, flip_h=True, rotate_deg=15)
    h2 = load_hand("B", scale=1.05, rotate_deg=-15)
    c.alpha_composite(h1, (50, 75))
    c.alpha_composite(h2, (210, 75))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([(130, 20), (270, 58)], radius=10, fill=(16, 185, 129, 255))
    d.rectangle([(130, 56), (270, 58)], fill=(5, 150, 105, 255))
    return c

# 10. buat: 2 hands, fists tapping on each other
def make_buat():
    c = create_card()
    h_top = load_hand("S", scale=1.1, rotate_deg=-20)
    h_bot = load_hand("S", scale=1.1, rotate_deg=10)
    c.alpha_composite(h_top, (130, 30))
    c.alpha_composite(h_bot, (140, 130))
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(105, 110), (95, 130), (115, 150)], color=(59, 130, 246, 255), width=5)
    draw_curved_arrow(d, [(285, 100), (295, 80), (275, 60)], color=(59, 130, 246, 255), width=5)
    return c

# 11. hati-hati: 2 hands, both forming V sign (TIM), alternating forward
def make_hati_hati():
    c = create_card()
    h1 = load_hand("V", scale=1.15, rotate_deg=-15)
    h2 = load_hand("V", scale=1.15, rotate_deg=15)
    c.alpha_composite(h1, (70, 65))
    c.alpha_composite(h2, (210, 65))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (130, 50), (130, 20), color=(59, 130, 246, 255), width=5)
    draw_arrow(d, (270, 20), (270, 50), color=(59, 130, 246, 255), width=5)
    return c

# 12. ingat: 1 hand, index touching temple then idea flash
def make_ingat():
    c = create_card()
    h = load_hand("D", scale=1.25, rotate_deg=-15)
    c.alpha_composite(h, (85, 70))
    d = ImageDraw.Draw(c)
    color = (250, 204, 21, 255)
    cx, cy = 290, 75
    d.ellipse([(cx-18, cy-18), (cx+18, cy+18)], fill=color)
    d.polygon([(cx-10, cy+15), (cx+10, cy+15), (cx+6, cy+26), (cx-6, cy+26)], fill=(202, 138, 4, 255))
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1 = cx + 25 * math.cos(rad)
        y1 = cy + 25 * math.sin(rad)
        x2 = cx + 35 * math.cos(rad)
        y2 = cy + 35 * math.sin(rad)
        d.line([(x1, y1), (x2, y2)], fill=color, width=4)
    return c

# 13. jangan: 1 hand, index TI upright waving left-right in red
def make_jangan():
    c = create_card()
    h = load_hand("D", scale=1.3)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2 + 10)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(140, 50), (200, 35), (260, 50)], color=(239, 68, 68, 255), width=5)
    draw_curved_arrow(d, [(260, 65), (200, 80), (140, 65)], color=(239, 68, 68, 255), width=5)
    return c

# 14. janji: 1 hand, pinky/fingers upright (BISINDO: IM) with golden promise ring
def make_janji():
    c = create_card()
    h = load_hand("I", scale=1.3)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    cx, cy = pos[0] + h.width//2 + 15, pos[1] + 35
    color = (245, 158, 11, 255)
    d.ellipse([(cx-16, cy-16), (cx+16, cy+16)], outline=color, width=4)
    d.line([(cx-24, cy), (cx+24, cy)], fill=color, width=3)
    d.line([(cx, cy-24), (cx, cy+24)], fill=color, width=3)
    return c

# 15. kamu: 1 hand, index pointing forward to conversational partner
def make_kamu():
    c = create_card()
    h = load_hand("G", scale=1.25) # G is pointing horizontally forward
    pos = ((c.width - h.width)//2 - 20, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_arrow(d, (240, 130), (330, 130), color=(59, 130, 246, 255), width=6)
    return c

# 16. keren: 2 hands, both forming TIM (Y/shaka 3-finger shape) in dataset!
def make_keren():
    c = create_card()
    h1 = load_hand("Y", scale=1.1, rotate_deg=-15)
    h2 = load_hand("Y", scale=1.1, flip_h=True, rotate_deg=15)
    c.alpha_composite(h1, (55, 65))
    c.alpha_composite(h2, (205, 65))
    d = ImageDraw.Draw(c)
    color = (245, 158, 11, 255)
    cx, cy = 200, 45
    d.line([(cx-12, cy), (cx+12, cy)], fill=color, width=4)
    d.line([(cx, cy-12), (cx, cy+12)], fill=color, width=4)
    return c

# 17. maaf: 1 hand, flat palm/fist circling gently on chest
def make_maaf():
    c = create_card()
    h = load_hand("A", scale=1.25)
    pos = ((c.width - h.width)//2 - 10, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(260, 90), (280, 130), (240, 170), (200, 140)], color=(59, 130, 246, 255), width=5)
    return c

# 18. melihat: 1 hand, two fingers pointing forward from eye level (IP, ang=-51 deg)
def make_melihat():
    c = create_card()
    h = load_hand("V", scale=1.2, rotate_deg=-85)
    c.alpha_composite(h, (60, 75))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (230, 110), (330, 110), color=(59, 130, 246, 255), width=6)
    draw_arrow(d, (230, 150), (330, 150), color=(59, 130, 246, 255), width=6)
    return c

# 19. membaca: 2 hands - base horizontal open palm TIMRP (170 deg), reading hand scanning
def make_membaca():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=80)
    h_scan = load_hand("U", scale=1.15, rotate_deg=130)
    c.alpha_composite(h_base, (70, 120))
    c.alpha_composite(h_scan, (140, 35))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (120, 120), (250, 120), color=(59, 130, 246, 255), width=5)
    return c

# 20. menggambar: 2 hands - base palm + drawing gesture with wavy curve
def make_menggambar():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=85)
    h_brush = load_hand("D", scale=1.1, rotate_deg=140)
    c.alpha_composite(h_base, (70, 125))
    c.alpha_composite(h_brush, (150, 40))
    d = ImageDraw.Draw(c)
    points = [(100, 120), (140, 100), (180, 125), (220, 105), (260, 120)]
    for i in range(len(points)-1):
        d.line([points[i], points[i+1]], fill=(139, 92, 246, 255), width=5)
    return c

# 21. menulis: 2 hands - base palm (paper) + writing hand holding pen
def make_menulis():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=85)
    h_pen = load_hand("D", scale=1.1, rotate_deg=145)
    c.alpha_composite(h_base, (70, 125))
    c.alpha_composite(h_pen, (150, 40))
    d = ImageDraw.Draw(c)
    d.line([(240, 50), (175, 125)], fill=(59, 130, 246, 255), width=7)
    d.line([(100, 135), (120, 128), (140, 136), (165, 130)], fill=(35, 24, 21, 255), width=3)
    return c

# 22. minta: 1 hand/2 hands, palm up reaching forward (TIMRP, -173 deg)
def make_minta():
    c = create_card()
    h1 = load_hand("B", scale=1.05, flip_h=True, rotate_deg=35)
    h2 = load_hand("B", scale=1.05, rotate_deg=-35)
    c.alpha_composite(h1, (65, 75))
    c.alpha_composite(h2, (185, 75))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (200, 50), (200, 95), color=(59, 130, 246, 255), width=5)
    return c

# 23. mulai: 2 hands, hand slicing path forward (TIMRP, -78 deg)
def make_mulai():
    c = create_card()
    h_l = load_hand("B", scale=1.1, rotate_deg=45)
    h_r = load_hand("V", scale=1.15, rotate_deg=-30)
    c.alpha_composite(h_l, (60, 80))
    c.alpha_composite(h_r, (180, 50))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (150, 60), (260, 40), color=(16, 185, 129, 255), width=6)
    return c

# 24. nama: 2 hands (TIMRP and T tapping each other in dataset)
def make_nama():
    c = create_card()
    h1 = load_hand("H", scale=1.15)
    h2 = load_hand("H", scale=1.15, flip_h=True)
    c.alpha_composite(h1, (70, 75))
    c.alpha_composite(h2, (200, 75))
    d = ImageDraw.Draw(c)
    cx, cy = 195, 115
    d.ellipse([(cx-10, cy-10), (cx+10, cy+10)], fill=(16, 185, 129, 150))
    return c

# 25. paham: 1 hand, opening from temple outward (TIMRP, -62 deg)
def make_paham():
    c = create_card()
    h1 = load_hand("D", scale=1.0, rotate_deg=-20)
    h2 = load_hand("B", scale=1.15, rotate_deg=15)
    c.alpha_composite(h1, (50, 90))
    c.alpha_composite(h2, (200, 60))
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(140, 90), (180, 70), (220, 80)], color=(16, 185, 129, 255), width=6)
    return c

# 26. perkenalkan: 1 hand, hand presenting forward welcomingly (T, -57 deg)
def make_perkenalkan():
    c = create_card()
    h = load_hand("B", scale=1.2, rotate_deg=-20)
    pos = ((c.width - h.width)//2 - 20, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_arrow(d, (240, 100), (320, 80), color=(59, 130, 246, 255), width=6)
    return c

# 27. sabar: 1 hand, flat palm on chest stroking downward (TIMRP, -162 deg)
def make_sabar():
    c = create_card()
    h = load_hand("B", scale=1.25, rotate_deg=10)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_arrow(d, (280, 70), (280, 180), color=(16, 185, 129, 255), width=6)
    return c

# 28. salah: 1 hand, EXACT DATASET: TP (Thumb & Pinky extended, Y-shape, ang=-103 deg) under chin!
def make_salah():
    c = create_card()
    # In BISINDO, 'salah' is the Y-handshape (thumb & pinky extended) placed near the chin
    h = load_hand("Y", scale=1.3, rotate_deg=-10)
    pos = ((c.width - h.width)//2 - 10, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    # Red X indicator
    cx, cy, r = 290, 80, 28
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(239, 68, 68, 255))
    d.line([(cx-12, cy-12), (cx+12, cy+12)], fill=(255, 255, 255, 255), width=5)
    d.line([(cx+12, cy-12), (cx-12, cy+12)], fill=(255, 255, 255, 255), width=5)
    return c

# 29. sama-sama: 1 hand, EXACT DATASET: TP (Thumb & Pinky extended, Y-shape, ang=-26 deg) waving!
def make_sama_sama():
    c = create_card()
    h = load_hand("Y", scale=1.3, rotate_deg=-25)
    pos = ((c.width - h.width)//2 - 10, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    # Waving left-right arrows
    draw_curved_arrow(d, [(130, 45), (180, 30), (230, 45)], color=(59, 130, 246, 255), width=5)
    draw_curved_arrow(d, [(230, 60), (180, 75), (130, 60)], color=(59, 130, 246, 255), width=5)
    return c

# 30. saya: 1 hand, index finger pointing inward to own chest
def make_saya():
    c = create_card()
    h = load_hand("D", scale=1.25, rotate_deg=145)
    pos = ((c.width - h.width)//2 + 20, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_arrow(d, (250, 160), (170, 160), color=(59, 130, 246, 255), width=6)
    return c

# 31. semangat: 2 hands, two clenched fists T + T pulled down with power
def make_semangat():
    c = create_card()
    h1 = load_hand("S", scale=1.15)
    h2 = load_hand("S", scale=1.15, flip_h=True)
    c.alpha_composite(h1, (65, 80))
    c.alpha_composite(h2, (205, 80))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (130, 40), (130, 85), color=(239, 68, 68, 255), width=6)
    draw_arrow(d, (270, 40), (270, 85), color=(239, 68, 68, 255), width=6)
    return c

# 32. siapa: 1 hand, index finger near chin with circular question motion
def make_siapa():
    c = create_card()
    h = load_hand("D", scale=1.25)
    pos = ((c.width - h.width)//2 - 20, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(260, 100), (290, 80), (280, 50), (250, 60), (250, 85)], color=(59, 130, 246, 255), width=5)
    return c

# 33. terima kasih: 1 hand, open palm from chin pushed forward (TIMRP, -93 deg)
def make_terima_kasih():
    c = create_card()
    h = load_hand("B", scale=1.25, rotate_deg=-15)
    pos = ((c.width - h.width)//2 - 20, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(140, 60), (210, 40), (280, 60)], color=(59, 130, 246, 255), width=6)
    return c

# 34. terlambat: 2 hands, EXACT DATASET: TIRP (rock / ILY handshape on both hands)
def make_terlambat():
    c = create_card()
    # In dataset: TIRP = thumb, index, pinky (ILY / rock sign)
    h1 = load_hand("Y", scale=1.1, rotate_deg=-15)
    h2 = load_hand("Y", scale=1.1, flip_h=True, rotate_deg=15)
    c.alpha_composite(h1, (60, 75))
    c.alpha_composite(h2, (200, 75))
    d = ImageDraw.Draw(c)
    # Clock / backward time sweep
    cx, cy, r = 200, 40, 22
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=(239, 68, 68, 255), width=3)
    d.line([(cx, cy), (cx, cy-12)], fill=(239, 68, 68, 255), width=3)
    d.line([(cx, cy), (cx+10, cy)], fill=(239, 68, 68, 255), width=3)
    draw_curved_arrow(d, [(150, 120), (200, 95), (250, 120)], color=(239, 68, 68, 255), width=5)
    return c

# 35. tolong: 1 hand/2 hands, hand reaching upward asking for help (TIM, -152 deg)
def make_tolong():
    c = create_card()
    h = load_hand("B", scale=1.25, rotate_deg=25)
    pos = ((c.width - h.width)//2 - 15, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_arrow(d, (260, 160), (260, 70), color=(16, 185, 129, 255), width=6)
    return c

# 36. tunggu: 1 hand, flat palm facing down waving gently (TIMRP, -170 deg)
def make_tunggu():
    c = create_card()
    h = load_hand("B", scale=1.25, rotate_deg=90)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2 + 10)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    color = (245, 158, 11, 255)
    draw_arrow(d, (130, 65), (130, 95), color=color, width=5)
    draw_arrow(d, (270, 95), (270, 65), color=color, width=5)
    return c

# 37. waktu: 2 hands, TI index finger tapping left wrist watch (TI, 18 deg)
def make_waktu():
    c = create_card()
    h_arm = load_hand("B", scale=1.1, rotate_deg=90)
    h_tap = load_hand("D", scale=1.1, rotate_deg=140)
    c.alpha_composite(h_arm, (70, 125))
    c.alpha_composite(h_tap, (150, 40))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([(145, 150), (185, 180)], radius=6, fill=(2, 132, 199, 255), outline=(35, 24, 21, 255), width=2)
    d.ellipse([(150, 135), (180, 165)], outline=(59, 130, 246, 255), width=3)
    d.ellipse([(140, 125), (190, 175)], outline=(59, 130, 246, 180), width=2)
    return c

# 38. ya: 1 hand, fist nodding downward (TIMRP / S fist nodding, -150 deg)
def make_ya():
    c = create_card()
    h = load_hand("S", scale=1.25)
    pos = ((c.width - h.width)//2 - 20, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(260, 60), (290, 90), (275, 140)], color=(16, 185, 129, 255), width=6)
    return c

generators = {
    "ambil": make_ambil,
    "apa": make_apa,
    "bantu": make_bantu,
    "berdoa": make_berdoa,
    "berhenti": make_berhenti,
    "berjalan": make_berjalan,
    "berpikir": make_berpikir,
    "betul": make_betul,
    "bisindo": make_bisindo,
    "buat": make_buat,
    "hati-hati": make_hati_hati,
    "ingat": make_ingat,
    "jangan": make_jangan,
    "janji": make_janji,
    "kamu": make_kamu,
    "keren": make_keren,
    "maaf": make_maaf,
    "melihat": make_melihat,
    "membaca": make_membaca,
    "menggambar": make_menggambar,
    "menulis": make_menulis,
    "minta": make_minta,
    "mulai": make_mulai,
    "nama": make_nama,
    "paham": make_paham,
    "perkenalkan": make_perkenalkan,
    "sabar": make_sabar,
    "salah": make_salah,
    "sama-sama": make_sama_sama,
    "saya": make_saya,
    "semangat": make_semangat,
    "siapa": make_siapa,
    "terima kasih": make_terima_kasih,
    "terlambat": make_terlambat,
    "tolong": make_tolong,
    "tunggu": make_tunggu,
    "waktu": make_waktu,
    "ya": make_ya
}

print(f"Building ALL {len(generators)} authentic dataset-verified vocabulary cards...")
for name, gen_fn in generators.items():
    card = gen_fn()
    out_file = f"assets/kosakata/{name}.png"
    card.save(out_file)
    print(f"  [OK] Saved {out_file} ({card.width}x{card.height})")

print(f"\nAll {len(generators)} authentic vocabulary cards built successfully!")
