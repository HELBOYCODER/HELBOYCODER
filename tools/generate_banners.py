import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import numpy as np

def generate_svg(dark=True):
    if dark:
        bg = "#0A101F"
        card_bg = "#0D1527"
        card_inner = "#070B14"
        border = "#1E293B"
        border_glow = "#38BDF8"
        chrome = "#22D3EE"
        chrome_dim = "#0E7490"
        portrait_color = "#A78BFA"
        accent = "#10B981"
        text_label = "#94A3B8"
        text_val = "#E2E8F0"
        dots_leader = "#334155"
        live_red = "#EF4444"
        pill_bg = "#1E1B4B"
        pill_text = "#A78BFA"
        scanline_op = "0.03"
    else:
        bg = "#F8FAFC"
        card_bg = "#FFFFFF"
        card_inner = "#F1F5F9"
        border = "#CBD5E1"
        border_glow = "#0284C7"
        chrome = "#0891B2"
        chrome_dim = "#06B6D4"
        portrait_color = "#7C3AED"
        accent = "#059669"
        text_label = "#475569"
        text_val = "#0F172A"
        dots_leader = "#94A3B8"
        live_red = "#DC2626"
        pill_bg = "#EDE9FE"
        pill_text = "#6D28D9"
        scanline_op = "0.015"

    img = Image.open('/var/minis/workspace/github-avatar.png').convert('RGB')
    target_w, target_h = 300, 340
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.35)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    gray = np.array(img.convert('L'), dtype=np.float32)

    h, w = gray.shape
    dithered = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        if y % 2 == 0:
            x_range = range(w)
            direction = 1
        else:
            x_range = range(w - 1, -1, -1)
            direction = -1
            
        for x in x_range:
            old_val = gray[y, x]
            new_val = 255 if old_val > 125 else 0
            if dark:
                dithered[y, x] = 1 if new_val == 255 else 0
            else:
                dithered[y, x] = 1 if new_val == 0 else 0
            err = old_val - new_val
            
            if direction == 1:
                if x + 1 < w:
                    gray[y, x + 1] += err * 7 / 16
                if y + 1 < h:
                    if x - 1 >= 0:
                        gray[y + 1, x - 1] += err * 3 / 16
                    gray[y + 1, x] += err * 5 / 16
                    if x + 1 < w:
                        gray[y + 1, x + 1] += err * 1 / 16
            else:
                if x - 1 >= 0:
                    gray[y, x - 1] += err * 7 / 16
                if y + 1 < h:
                    if x + 1 < w:
                        gray[y + 1, x + 1] += err * 3 / 16
                    gray[y + 1, x] += err * 5 / 16
                    if x - 1 >= 0:
                        gray[y + 1, x - 1] += err * 1 / 16

    random.seed(42)
    NUM_GROUPS = 45
    groups = [[] for _ in range(NUM_GROUPS)]

    dot_scale = 1.15
    ox = 65
    oy = 110

    for y in range(h):
        in_run = False
        start_x = 0
        for x in range(w):
            if dithered[y, x] == 1:
                if not in_run:
                    in_run = True
                    start_x = x
            else:
                if in_run:
                    in_run = False
                    run_len = x - start_x
                    grp_idx = random.randint(0, NUM_GROUPS - 1)
                    rx = round(ox + start_x * dot_scale, 2)
                    ry = round(oy + y * dot_scale, 2)
                    rw = round(run_len * dot_scale, 2)
                    rh = round(dot_scale * 0.92, 2)
                    groups[grp_idx].append(f"M{rx},{ry}h{rw}v{rh}h-{rw}Z")
        if in_run:
            run_len = w - start_x
            grp_idx = random.randint(0, NUM_GROUPS - 1)
            rx = round(ox + start_x * dot_scale, 2)
            ry = round(oy + y * dot_scale, 2)
            rw = round(run_len * dot_scale, 2)
            rh = round(dot_scale * 0.92, 2)
            groups[grp_idx].append(f"M{rx},{ry}h{rw}v{rh}h-{rw}Z")

    # Generate CSS animations for shimmer
    css_delays = []
    portrait_paths = []
    for i, g in enumerate(groups):
        if not g:
            continue
        d_str = " ".join(g)
        delay = round(i * 0.032, 3)
        css_delays.append(f".dg-{i} {{ animation: dotIn 0.7s cubic-bezier(0.16, 1, 0.3, 1) {delay}s both; }}")
        portrait_paths.append(f'<path class="dg-{i}" d="{d_str}" fill="{portrait_color}" shape-rendering="crispEdges"/>')

    css_classes = "\n      ".join(css_delays)
    portrait_svg = "\n".join(portrait_paths)

    rows = [
        ("Subject", "Hellboy Coder"),
        ("Role", "Mobile & Edge Systems Engineer"),
        ("Origin", "Tehran, Iran"),
        ("Status", "Building · Breaking Limits · Shipping"),
        ("ToolChain", "Android Studio · VS Code · Git · Linux"),
        ("Core.Lang", "Kotlin · Swift · Python · TS · Go"),
        ("Core.Mobile", "Jetpack Compose · Media3 · SwiftUI"),
        ("Core.Edge", "Cloudflare Workers · D1 · FastMCP"),
        ("Core.Network", "VpnService · tun2socks · SOCKS5"),
        ("Grid.X", "x.com/hellboy_code"),
        ("Grid.GitHub", "github.com/3krbkbkrbrbg"),
        ("Grid.Bot", "@netranew_bot · @tempmailersaz_bot")
    ]

    row_svg = []
    start_y = 140
    spacing = 34
    for idx, (label, val) in enumerate(rows):
        cy = start_y + idx * spacing
        label_w = len(label) * 9 + 10
        dot_start = 490 + label_w + 10
        dot_end = 1130 - len(val) * 8.2 - 10
        if dot_end > dot_start:
            dot_line = f'<line x1="{dot_start}" y1="{cy-4}" x2="{dot_end}" y2="{cy-4}" stroke="{dots_leader}" stroke-width="1.5" stroke-dasharray="2 6"/>'
        else:
            dot_line = ''
            
        row_svg.append(f'''
    <g>
      <text x="490" y="{cy}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="13.5" font-weight="600" fill="{text_label}">{label}</text>
      {dot_line}
      <text x="1130" y="{cy}" text-anchor="end" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="13" font-weight="500" fill="{text_val}" lengthAdjust="spacingAndGlyphs">{val}</text>
    </g>''')

    rows_markup = "\n".join(row_svg)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">
  <defs>
    <style>
      @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.35; transform: scale(1.2); }}
      }}
      @keyframes dotIn {{
        0% {{ opacity: 0; transform: translateY(1.5px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
      }}
      .pulse-dot {{
        transform-origin: 978px 84px;
        animation: pulse 1.8s ease-in-out infinite;
      }}
      {css_classes}
    </style>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1180" height="610" rx="14" ry="14" fill="{bg}" stroke="{border}" stroke-width="1.5"/>

  <!-- Titlebar -->
  <path d="M0 14 C0 6 6 0 14 0 L1166 0 C1174 0 1180 6 1180 14 L1180 44 L0 44 Z" fill="{card_bg}" stroke="{border}" stroke-width="1.5"/>
  <line x1="0" y1="44" x2="1180" y2="44" stroke="{border}" stroke-width="1.5"/>

  <!-- Window controls -->
  <circle cx="28" cy="22" r="6" fill="#EF4444"/>
  <circle cx="48" cy="22" r="6" fill="#F59E0B"/>
  <circle cx="68" cy="22" r="6" fill="#10B981"/>

  <!-- Title -->
  <text x="590" y="27" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="13" font-weight="600" fill="{chrome}">profile.sh --live</text>

  <!-- Left Frame: VISUAL.MAP -->
  <rect x="30" y="60" width="410" height="520" rx="10" fill="{card_inner}" stroke="{border}" stroke-width="1.2"/>
  <text x="45" y="86" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="{chrome}" letter-spacing="1">VISUAL.MAP // 300x340 DITHER</text>
  <line x1="30" y1="96" x2="440" y2="96" stroke="{border}" stroke-width="1"/>
  
  <!-- Dithered Portrait -->
  <g id="portrait">
{portrait_svg}
  </g>

  <!-- Right Frame: SYSTEM.INFO -->
  <rect x="460" y="60" width="690" height="520" rx="10" fill="{card_bg}" stroke="{border}" stroke-width="1.2"/>
  <text x="480" y="86" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="{chrome}" letter-spacing="1">SYSTEM.INFO // TELEMETRY</text>
  
  <!-- Live Badge -->
  <circle cx="978" cy="82" r="4.5" fill="{live_red}" class="pulse-dot" filter="url(#glow)"/>
  <text x="990" y="86" font-family="'JetBrains Mono', monospace" font-size="11.5" font-weight="700" fill="{live_red}" letter-spacing="0.5">LIVE</text>

  <!-- Handle Pill -->
  <rect x="1035" y="70" width="100" height="24" rx="12" fill="{pill_bg}" stroke="{portrait_color}" stroke-width="1"/>
  <text x="1085" y="86" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="{pill_text}">@3krbkbkrbrbg</text>
  
  <line x1="460" y1="96" x2="1150" y2="96" stroke="{border}" stroke-width="1"/>

  <!-- Readout Rows -->
{rows_markup}

  <!-- Footer -->
  <line x1="460" y1="545" x2="1150" y2="545" stroke="{border}" stroke-width="1"/>
  <text x="480" y="565" font-family="'JetBrains Mono', monospace" font-size="11.5" fill="{accent}">● SYSTEM ACTIVE</text>
  <text x="610" y="565" font-family="'JetBrains Mono', monospace" font-size="11" fill="{text_label}">HELLBOY-CORE // AARCH64 // PROOT SANDBOX</text>
  <text x="1130" y="565" text-anchor="end" font-family="'JetBrains Mono', monospace" font-size="11" fill="{chrome}">2026.09.07 ⚡</text>
</svg>
'''
    return svg_content

with open('/var/minis/workspace/banner-dark.svg', 'w') as f:
    f.write(generate_svg(dark=True))

with open('/var/minis/workspace/banner-light.svg', 'w') as f:
    f.write(generate_svg(dark=False))

print("Regenerated with CSS shimmer!")
