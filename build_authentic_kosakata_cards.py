import os
import math
from PIL import Image, ImageDraw, ImageFont

os.makedirs("assets/kosakata", exist_ok=True)

# Helper function to load and resize an abjad hand image with lanczos filter
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
    # Draw arrow shaft
    draw.line([start, end], fill=color, width=width)
    # Draw arrowhead
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

# 1. ambil (open hand closing into fist pulling inward)
def make_ambil():
    c = create_card()
    h1 = load_hand("B", scale=1.1, rotate_deg=-20)
    h2 = load_hand("S", scale=1.1)
    c.alpha_composite(h1, (220, 60))
    c.alpha_composite(h2, (60, 90))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (230, 160), (160, 160), color=(59, 130, 246, 255), width=6)
    return c

# 2. apa (two open hands tilted palms up with question shrug)
def make_apa():
    c = create_card()
    h_l = load_hand("B", scale=1.05, flip_h=True, rotate_deg=25)
    h_r = load_hand("B", scale=1.05, rotate_deg=-25)
    c.alpha_composite(h_l, (40, 70))
    c.alpha_composite(h_r, (210, 70))
    d = ImageDraw.Draw(c)
    # Question shrug blue arrows
    draw_curved_arrow(d, [(70, 75), (60, 50), (45, 60)], color=(59, 130, 246, 255), width=5)
    draw_curved_arrow(d, [(330, 75), (340, 50), (355, 60)], color=(59, 130, 246, 255), width=5)
    # Big stylized question mark in center
    d.ellipse([(190, 40), (210, 60)], fill=(59, 130, 246, 255))
    d.arc([(185, 30), (215, 65)], start=180, end=360, fill=(59, 130, 246, 255), width=6)
    d.line([(200, 65), (200, 80)], fill=(59, 130, 246, 255), width=6)
    d.ellipse([(196, 92), (204, 100)], fill=(59, 130, 246, 255))
    return c

# 3. bantu (base flat hand supporting fist pushing forward)
def make_bantu():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=80)
    h_fist = load_hand("S", scale=1.1)
    c.alpha_composite(h_base, (80, 130))
    c.alpha_composite(h_fist, (140, 40))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (260, 110), (340, 110), color=(16, 185, 129, 255), width=6)
    return c

# 5. berhenti (flat open hand STOP)
def make_berhenti():
    c = create_card()
    h = load_hand("B", scale=1.35)
    pos = ((c.width - h.width)//2 - 15, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    # Red STOP circle badge
    cx, cy, r = 310, 80, 32
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(239, 68, 68, 255))
    d.rounded_rectangle([(cx-22, cy-6), (cx+22, cy+6)], radius=3, fill=(255, 255, 255, 255))
    return c

# 6. berjalan (two fingers walking across palm)
def make_berjalan():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=90)
    h_walk = load_hand("V", scale=1.15, rotate_deg=180)
    c.alpha_composite(h_base, (60, 140))
    c.alpha_composite(h_walk, (140, 30))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (240, 140), (320, 140), color=(16, 185, 129, 255), width=6)
    return c

# 7. berpikir (index finger at temple)
def make_berpikir():
    c = create_card()
    h = load_hand("D", scale=1.25, rotate_deg=-15)
    c.alpha_composite(h, (90, 70))
    d = ImageDraw.Draw(c)
    # Thought sparkles at top right
    color = (245, 158, 11, 255)
    d.ellipse([(250, 90), (266, 106)], fill=color)
    d.ellipse([(280, 65), (300, 85)], fill=color)
    d.ellipse([(315, 35), (345, 65)], fill=color)
    return c

# 8. betul (thumbs up + green checkmark)
def make_betul():
    c = create_card()
    h = load_hand("A", scale=1.3, rotate_deg=-20)
    c.alpha_composite(h, (80, 65))
    d = ImageDraw.Draw(c)
    # Green Checkmark badge
    cx, cy, r = 290, 100, 32
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(16, 185, 129, 255))
    d.line([(cx-16, cy), (cx-6, cy+12), (cx+16, cy-12)], fill=(255, 255, 255, 255), width=6)
    return c

# 9. bisindo (two B hands + BISINDO badge)
def make_bisindo():
    c = create_card()
    h1 = load_hand("B", scale=1.05, flip_h=True, rotate_deg=15)
    h2 = load_hand("B", scale=1.05, rotate_deg=-15)
    c.alpha_composite(h1, (50, 75))
    c.alpha_composite(h2, (210, 75))
    d = ImageDraw.Draw(c)
    # Centered BISINDO badge at top
    d.rounded_rectangle([(130, 20), (270, 58)], radius=10, fill=(16, 185, 129, 255))
    # Draw "BISINDO" text using basic lines for sharpness
    d.rectangle([(130, 56), (270, 58)], fill=(5, 150, 105, 255))
    return c

# 10. buat (two fists tapping/twisting)
def make_buat():
    c = create_card()
    h_top = load_hand("S", scale=1.1, rotate_deg=-20)
    h_bot = load_hand("S", scale=1.1, rotate_deg=10)
    c.alpha_composite(h_top, (130, 30))
    c.alpha_composite(h_bot, (140, 130))
    d = ImageDraw.Draw(c)
    # Tapping arrows
    draw_curved_arrow(d, [(105, 110), (95, 130), (115, 150)], color=(59, 130, 246, 255), width=5)
    draw_curved_arrow(d, [(285, 100), (295, 80), (275, 60)], color=(59, 130, 246, 255), width=5)
    return c

# 11. hati-hati (two V hands alternating forward)
def make_hati_hati():
    c = create_card()
    h1 = load_hand("V", scale=1.15)
    h2 = load_hand("V", scale=1.15)
    c.alpha_composite(h1, (70, 65))
    c.alpha_composite(h2, (210, 65))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (130, 50), (130, 20), color=(59, 130, 246, 255), width=5)
    draw_arrow(d, (270, 20), (270, 50), color=(59, 130, 246, 255), width=5)
    return c

# 12. ingat (index finger at temple + lightbulb sparkle)
def make_ingat():
    c = create_card()
    h = load_hand("D", scale=1.25, rotate_deg=-10)
    c.alpha_composite(h, (85, 70))
    d = ImageDraw.Draw(c)
    # Golden idea bulb / sparkle
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

# 13. jangan (upright index waving left-right in red)
def make_jangan():
    c = create_card()
    h = load_hand("D", scale=1.3)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2 + 10)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    # Left-right double curved waving arrows in red
    draw_curved_arrow(d, [(140, 50), (200, 35), (260, 50)], color=(239, 68, 68, 255), width=5)
    draw_curved_arrow(d, [(260, 65), (200, 80), (140, 65)], color=(239, 68, 68, 255), width=5)
    return c

# 14. janji (pinky upright + golden promise sparkle ring)
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

# 16. keren (shaka sign + sparkles)
def make_keren():
    c = create_card()
    h = load_hand("Y", scale=1.3)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    color = (245, 158, 11, 255)
    cx, cy = pos[0] + h.width - 20, pos[1] + 25
    d.line([(cx-12, cy), (cx+12, cy)], fill=color, width=4)
    d.line([(cx, cy-12), (cx, cy+12)], fill=color, width=4)
    cx2, cy2 = pos[0] + 15, pos[1] + 35
    d.line([(cx2-8, cy2), (cx2+8, cy2)], fill=color, width=3)
    d.line([(cx2, cy2-8), (cx2, cy2+8)], fill=color, width=3)
    return c

# 18. melihat (two fingers pointing forward with sight arrows)
def make_melihat():
    c = create_card()
    h = load_hand("V", scale=1.2, rotate_deg=-85)
    c.alpha_composite(h, (60, 75))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (230, 110), (330, 110), color=(59, 130, 246, 255), width=6)
    draw_arrow(d, (230, 150), (330, 150), color=(59, 130, 246, 255), width=6)
    return c

# 19. membaca (open palm book + scanning fingers)
def make_membaca():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=80)
    h_scan = load_hand("U", scale=1.15, rotate_deg=130)
    c.alpha_composite(h_base, (70, 120))
    c.alpha_composite(h_scan, (140, 35))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (120, 120), (250, 120), color=(59, 130, 246, 255), width=5)
    return c

# 20. menggambar (palette + sketch wave)
def make_menggambar():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=85)
    h_brush = load_hand("D", scale=1.1, rotate_deg=140)
    c.alpha_composite(h_base, (70, 125))
    c.alpha_composite(h_brush, (150, 40))
    d = ImageDraw.Draw(c)
    # Artistic brush curve in purple
    points = [(100, 120), (140, 100), (180, 125), (220, 105), (260, 120)]
    for i in range(len(points)-1):
        d.line([points[i], points[i+1]], fill=(139, 92, 246, 255), width=5)
    return c

# 21. menulis (paper palm + writing pen)
def make_menulis():
    c = create_card()
    h_base = load_hand("B", scale=1.1, rotate_deg=85)
    h_pen = load_hand("D", scale=1.1, rotate_deg=145)
    c.alpha_composite(h_base, (70, 125))
    c.alpha_composite(h_pen, (150, 40))
    d = ImageDraw.Draw(c)
    # Blue pen body
    d.line([(240, 50), (175, 125)], fill=(59, 130, 246, 255), width=7)
    # Writing scribble
    d.line([(100, 135), (120, 128), (140, 136), (165, 130)], fill=(35, 24, 21, 255), width=3)
    return c

# 22. minta (two cupped palms reaching forward)
def make_minta():
    c = create_card()
    h1 = load_hand("B", scale=1.05, flip_h=True, rotate_deg=35)
    h2 = load_hand("B", scale=1.05, rotate_deg=-35)
    c.alpha_composite(h1, (65, 75))
    c.alpha_composite(h2, (185, 75))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (200, 50), (200, 95), color=(59, 130, 246, 255), width=5)
    return c

# 23. mulai (hand slicing path between fingers)
def make_mulai():
    c = create_card()
    h_l = load_hand("B", scale=1.1, rotate_deg=45)
    h_r = load_hand("V", scale=1.15, rotate_deg=-30)
    c.alpha_composite(h_l, (60, 80))
    c.alpha_composite(h_r, (180, 50))
    d = ImageDraw.Draw(c)
    draw_arrow(d, (150, 60), (260, 40), color=(16, 185, 129, 255), width=6)
    return c

# 25. paham (hand opening outward from temple)
def make_paham():
    c = create_card()
    h1 = load_hand("D", scale=1.0, rotate_deg=-20)
    h2 = load_hand("B", scale=1.15, rotate_deg=15)
    c.alpha_composite(h1, (50, 90))
    c.alpha_composite(h2, (200, 60))
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(140, 90), (180, 70), (220, 80)], color=(16, 185, 129, 255), width=6)
    return c

# 27. sabar (hand on chest stroking gently downward)
def make_sabar():
    c = create_card()
    h = load_hand("B", scale=1.25, rotate_deg=10)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_arrow(d, (280, 70), (280, 180), color=(16, 185, 129, 255), width=6)
    return c

# 28. salah (crossed fingers forming X)
def make_salah():
    c = create_card()
    h1 = load_hand("D", scale=1.2, rotate_deg=35)
    h2 = load_hand("D", scale=1.2, flip_h=True, rotate_deg=-35)
    c.alpha_composite(h1, (65, 60))
    c.alpha_composite(h2, (185, 60))
    d = ImageDraw.Draw(c)
    # Red X badge
    cx, cy, r = 200, 110, 26
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(239, 68, 68, 255))
    d.line([(cx-12, cy-12), (cx+12, cy+12)], fill=(255, 255, 255, 255), width=5)
    d.line([(cx+12, cy-12), (cx-12, cy+12)], fill=(255, 255, 255, 255), width=5)
    return c

# 29. sama-sama (two open hands in reciprocal greeting)
def make_sama_sama():
    c = create_card()
    h1 = load_hand("B", scale=1.05, flip_h=True, rotate_deg=20)
    h2 = load_hand("B", scale=1.05, rotate_deg=-20)
    c.alpha_composite(h1, (50, 70))
    c.alpha_composite(h2, (200, 70))
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(80, 60), (120, 40), (160, 55)], color=(59, 130, 246, 255), width=5)
    draw_curved_arrow(d, [(320, 60), (280, 40), (240, 55)], color=(59, 130, 246, 255), width=5)
    return c

# 31. semangat (two clenched fists with energetic downward arrows)
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

# 32. siapa (index finger near chin with circular question arrow)
def make_siapa():
    c = create_card()
    h = load_hand("D", scale=1.25)
    pos = ((c.width - h.width)//2 - 20, (c.height - h.height)//2)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    draw_curved_arrow(d, [(260, 100), (290, 80), (280, 50), (250, 60), (250, 85)], color=(59, 130, 246, 255), width=5)
    return c

# 34. terlambat (tap wrist watch then sweep backward)
def make_terlambat():
    c = create_card()
    h_arm = load_hand("B", scale=1.1, rotate_deg=90)
    h_tap = load_hand("D", scale=1.1, rotate_deg=140)
    c.alpha_composite(h_arm, (70, 125))
    c.alpha_composite(h_tap, (150, 40))
    d = ImageDraw.Draw(c)
    # Red backward sweep arrow
    draw_curved_arrow(d, [(180, 110), (240, 80), (300, 120)], color=(239, 68, 68, 255), width=6)
    return c

# 36. tunggu (flat palm facing down waving gently)
def make_tunggu():
    c = create_card()
    h = load_hand("B", scale=1.25, rotate_deg=90)
    pos = ((c.width - h.width)//2, (c.height - h.height)//2 + 10)
    c.alpha_composite(h, pos)
    d = ImageDraw.Draw(c)
    # Amber waving arrows
    color = (245, 158, 11, 255)
    draw_arrow(d, (130, 65), (130, 95), color=color, width=5)
    draw_arrow(d, (270, 95), (270, 65), color=color, width=5)
    return c

# 37. waktu (tap wristwatch with ripple circles)
def make_waktu():
    c = create_card()
    h_arm = load_hand("B", scale=1.1, rotate_deg=90)
    h_tap = load_hand("D", scale=1.1, rotate_deg=140)
    c.alpha_composite(h_arm, (70, 125))
    c.alpha_composite(h_tap, (150, 40))
    d = ImageDraw.Draw(c)
    # Blue wristwatch
    d.rounded_rectangle([(145, 150), (185, 180)], radius=6, fill=(2, 132, 199, 255), outline=(35, 24, 21, 255), width=2)
    # Ripple circles
    d.ellipse([(150, 135), (180, 165)], outline=(59, 130, 246, 255), width=3)
    d.ellipse([(140, 125), (190, 175)], outline=(59, 130, 246, 180), width=2)
    return c

# 38. ya (clenched fist nodding downward)
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
    "keren": make_keren,
    "melihat": make_melihat,
    "membaca": make_membaca,
    "menggambar": make_menggambar,
    "menulis": make_menulis,
    "minta": make_minta,
    "mulai": make_mulai,
    "paham": make_paham,
    "sabar": make_sabar,
    "salah": make_salah,
    "sama-sama": make_sama_sama,
    "semangat": make_semangat,
    "siapa": make_siapa,
    "terlambat": make_terlambat,
    "tunggu": make_tunggu,
    "waktu": make_waktu,
    "ya": make_ya
}

print(f"Building {len(generators)} authentic vocabulary cards...")
for name, gen_fn in generators.items():
    card = gen_fn()
    out_file = f"assets/kosakata/{name}.png"
    card.save(out_file)
    print(f"  [OK] Saved {out_file} ({card.width}x{card.height})")

print(f"\nAll {len(generators)} cards built successfully!")
