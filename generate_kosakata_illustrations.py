import os

os.makedirs("assets/kosakata", exist_ok=True)

# Helper function to generate standardized SVG wrapper
def svg_wrap(content):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 220" width="100%" height="100%">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#3b82f6" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#10b981" />
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000000" flood-opacity="0.08" />
    </filter>
  </defs>
  <!-- Background Card -->
  <rect width="296" height="216" x="2" y="2" rx="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2" />
  
  <!-- Illustration Elements -->
  <g filter="url(#shadow)">
    {content}
  </g>
</svg>"""

# SVG content generator dictionary
illustrations = {}

# 1. saya (pointing to own chest)
illustrations["saya"] = svg_wrap("""
  <!-- Hand pointing inward to chest -->
  <path d="M 175 165 C 170 145 160 125 150 115 C 138 105 110 85 90 95 C 80 100 85 115 95 115 L 125 125 C 115 130 115 145 128 145 L 140 145 C 130 152 135 165 145 162 L 160 180 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Extended Index Finger pointing to self -->
  <path d="M 148 115 L 90 70 C 82 64 72 74 78 82 L 128 122" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Inward motion arrow -->
  <path d="M 125 45 Q 85 45 60 70" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow)" />
  <circle cx="50" cy="80" r="4" fill="#3b82f6" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Menunjuk ke dada sendiri</text>
""")

# 2. kamu (pointing forward to conversational partner)
illustrations["kamu"] = svg_wrap("""
  <!-- Wrist & Forearm -->
  <path d="M 80 180 L 115 135 C 125 125 140 120 155 120 L 195 120 C 205 120 205 135 195 138 L 165 142 C 185 145 185 160 170 162 L 150 165 C 160 172 155 185 140 182 L 105 195 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Extended Index Finger pointing forward -->
  <path d="M 145 120 L 225 108 C 235 106 235 118 225 122 L 165 135" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Thumb folded -->
  <path d="M 125 120 C 135 105 150 110 155 122" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Forward motion arrow -->
  <path d="M 180 75 L 245 75" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Menunjuk ke arah lawan bicara</text>
""")

# 3. terima kasih (hand from chin forward)
illustrations["terima kasih"] = svg_wrap("""
  <!-- Open palm moving forward from chin -->
  <path d="M 110 175 L 135 130 C 140 120 155 115 170 105 L 180 60 C 182 52 192 52 194 60 L 190 95 L 202 62 C 204 54 214 54 215 62 L 205 100 L 217 70 C 220 62 230 64 228 72 L 215 115 C 210 135 195 155 175 165 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" />
  <!-- Thumb -->
  <path d="M 145 128 C 135 118 130 110 135 98 C 138 90 148 95 150 102 L 160 120" fill="#ea9f71" stroke="#231815" stroke-width="3.5" />
  <!-- Arc motion arrow: chin to forward -->
  <path d="M 90 85 C 90 50 140 35 175 42" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Dari depan dagu didorong ke depan</text>
""")

# 4. sama-sama (reciprocal greeting hands)
illustrations["sama-sama"] = svg_wrap("""
  <!-- Left hand -->
  <path d="M 60 170 L 95 125 C 105 110 125 105 135 90 L 142 55 C 144 48 152 48 154 55 L 148 95 L 140 130 C 130 150 110 165 85 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round" />
  <!-- Right hand meeting -->
  <path d="M 240 170 L 205 125 C 195 110 175 105 165 90 L 158 55 C 156 48 148 48 146 55 L 152 95 L 160 130 C 170 150 190 165 215 175 Z" fill="#df9266" stroke="#231815" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round" />
  <!-- Mutual greeting arrows -->
  <path d="M 90 55 C 120 40 180 40 210 55" fill="none" stroke="#3b82f6" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua tangan membalas salam</text>
""")

# 5. maaf (fist rubbing heart in circle)
illustrations["maaf"] = svg_wrap("""
  <!-- Closed fist over chest/heart area -->
  <path d="M 120 175 L 135 140 C 140 125 155 120 170 120 C 185 120 195 130 190 145 C 190 155 180 165 165 170 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Folded fingers (fist knuckles) -->
  <path d="M 150 120 C 152 110 165 110 168 120 L 170 142" fill="#ea9f71" stroke="#231815" stroke-width="3.5" />
  <path d="M 165 122 C 168 112 180 112 182 122 L 180 145" fill="#ea9f71" stroke="#231815" stroke-width="3.5" />
  <path d="M 140 125 C 135 115 145 110 150 122" fill="#ea9f71" stroke="#231815" stroke-width="3.5" />
  <!-- Thumb across fingers -->
  <path d="M 135 145 C 140 135 165 135 172 145" fill="#ea9f71" stroke="#231815" stroke-width="3.5" />
  <!-- Circular motion arrow -->
  <path d="M 185 85 C 215 105 210 155 185 170 C 165 180 135 180 120 165" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kepalan memutar perlahan di dada</text>
""")

# 6. tolong (left palm supporting right hand lifting up)
illustrations["tolong"] = svg_wrap("""
  <!-- Supporting bottom hand (left) -->
  <path d="M 75 145 L 125 145 C 145 145 170 145 195 140 C 205 138 205 152 195 155 L 125 165 L 75 165 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Top lifting hand (right) -->
  <path d="M 130 140 L 145 110 C 150 95 165 90 178 95 C 188 100 185 115 178 125 L 165 140 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Upward motion arrows -->
  <path d="M 155 80 L 155 35" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow-green)" />
  <path d="M 180 80 L 180 45" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow-green)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Satu tangan menopang tangan lain ke atas</text>
""")

# 7. bantu (similar support pushing forward)
illustrations["bantu"] = svg_wrap("""
  <!-- Base support hand -->
  <path d="M 80 150 L 140 150 C 160 150 185 145 205 140 C 215 138 215 152 205 155 L 135 168 L 80 168 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Resting fist on top pushing forward -->
  <path d="M 135 140 L 145 105 C 150 95 168 95 175 105 C 182 112 180 125 170 140 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Forward support arrow -->
  <path d="M 180 100 L 235 95" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Tangan menopang didorong ke depan</text>
""")

# 8. ya (fist nodding downward)
illustrations["ya"] = svg_wrap("""
  <!-- Fist hand -->
  <path d="M 120 165 L 135 130 C 140 115 155 110 170 110 C 185 110 195 120 190 135 L 175 165 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <path d="M 150 110 C 152 100 165 100 168 110 L 170 130" fill="#ea9f71" stroke="#231815" stroke-width="3" />
  <path d="M 165 112 C 168 102 178 102 180 112 L 180 135" fill="#ea9f71" stroke="#231815" stroke-width="3" />
  <!-- Nodding motion arrow (downward arc) -->
  <path d="M 195 90 C 215 110 215 140 205 160" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow-green)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kepalan tangan mengangguk ke bawah</text>
""")

# 9. jangan (index finger waving NO left-right)
illustrations["jangan"] = svg_wrap("""
  <!-- Fist with extended vertical index finger -->
  <path d="M 130 180 L 140 140 C 145 130 165 130 170 140 L 165 180 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Vertical index finger -->
  <path d="M 145 130 L 145 55 C 145 45 157 45 157 55 L 157 130" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Horizontal waving arrows -->
  <path d="M 115 50 Q 150 35 185 50" fill="none" stroke="#ef4444" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <path d="M 185 55 Q 150 70 115 55" fill="none" stroke="#ef4444" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Jari telunjuk menggeleng ke kiri-kanan</text>
""")

# 10. apa (both open palms facing up with question shrug)
illustrations["apa"] = svg_wrap("""
  <!-- Left open palm facing up -->
  <path d="M 65 165 L 85 135 C 95 120 115 120 125 125 L 135 145 L 85 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <!-- Right open palm facing up -->
  <path d="M 235 165 L 215 135 C 205 120 185 120 175 125 L 165 145 L 215 175 Z" fill="#df9266" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <!-- Question shrug arrows -->
  <path d="M 75 105 Q 60 90 45 100" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <path d="M 225 105 Q 240 90 255 100" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <text x="150" y="60" font-family="sans-serif" font-size="28" font-weight="bold" fill="#3b82f6" text-anchor="middle">?</text>
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua telapak terbuka menengadah ke atas</text>
""")

# 11. siapa (index finger near mouth/chin circling)
illustrations["siapa"] = svg_wrap("""
  <!-- Hand with index finger near chin -->
  <path d="M 125 175 L 140 135 C 145 120 160 120 165 135 L 160 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <path d="M 140 120 L 140 60 C 140 50 152 50 152 60 L 152 120" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Circular question arrow near chin -->
  <path d="M 165 65 C 185 65 195 85 185 100 C 175 110 155 105 155 95" fill="none" stroke="#3b82f6" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Jari telunjuk di depan dagu memutar</text>
""")

# 12. nama (two fingers touching in H/N shape)
illustrations["nama"] = svg_wrap("""
  <!-- Left hand 2 fingers -->
  <path d="M 80 150 L 120 120 L 160 100 C 168 95 172 105 165 112 L 125 135 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Right hand 2 fingers touching -->
  <path d="M 220 150 L 180 120 L 140 100 C 132 95 128 105 135 112 L 175 135 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Touch impact sparkle -->
  <circle cx="150" cy="106" r="8" fill="#10b981" opacity="0.4" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Dua jari kedua tangan saling mengetuk</text>
""")

# 13. perkenalkan (hands presenting forward)
illustrations["perkenalkan"] = svg_wrap("""
  <!-- Left presenting hand -->
  <path d="M 70 170 L 105 130 C 115 115 135 110 150 95 L 140 145 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Right presenting hand -->
  <path d="M 230 170 L 195 130 C 185 115 165 110 150 95 L 160 145 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Outward welcoming arrows -->
  <path d="M 120 85 L 80 55" fill="none" stroke="#3b82f6" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <path d="M 180 85 L 220 55" fill="none" stroke="#3b82f6" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua tangan membuka menyambut ke depan</text>
""")

# 14. betul (thumbs up / check confirmation)
illustrations["betul"] = svg_wrap("""
  <!-- Fist with thumbs up -->
  <path d="M 120 175 L 135 135 C 140 120 160 120 175 125 L 170 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Thumbs up pointing high -->
  <path d="M 135 135 C 135 105 132 65 142 55 C 150 48 160 55 158 75 L 155 125" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Green checkmark badge -->
  <path d="M 195 70 L 210 85 L 235 55" fill="none" stroke="#10b981" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Jempol tegak ke atas (Tanda Benar)</text>
""")

# 15. salah (crossed fingers forming X)
illustrations["salah"] = svg_wrap("""
  <!-- Crossed index fingers -->
  <path d="M 90 145 L 210 65" stroke="#ea9f71" stroke-width="16" stroke-linecap="round" />
  <path d="M 90 145 L 210 65" fill="none" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <path d="M 210 145 L 90 65" stroke="#df9266" stroke-width="16" stroke-linecap="round" />
  <path d="M 210 145 L 90 65" fill="none" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Red X indicator -->
  <circle cx="150" cy="105" r="16" fill="#ef4444" opacity="0.2" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua jari menyilang membentuk huruf X</text>
""")

# 16. waktu (tap left wrist watch)
illustrations["waktu"] = svg_wrap("""
  <!-- Left forearm / wrist -->
  <path d="M 50 140 L 160 140 C 175 140 190 135 200 125 L 200 160 L 50 160 Z" fill="#df9266" stroke="#231815" stroke-width="4" />
  <!-- Watch outline on wrist -->
  <rect x="110" y="132" width="28" height="22" rx="6" fill="#0284c7" stroke="#231815" stroke-width="2.5" />
  <!-- Right index finger tapping watch -->
  <path d="M 180 60 L 125 125 C 120 130 115 125 120 120 L 175 55 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Tap ripple waves -->
  <circle cx="124" cy="132" r="12" fill="none" stroke="#3b82f6" stroke-width="2" stroke-dasharray="3,2" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Jari mengetuk pergelangan tangan (jam)</text>
""")

# 17. berhenti (flat open hand STOP)
illustrations["berhenti"] = svg_wrap("""
  <!-- Flat open palm facing forward -->
  <path d="M 115 175 L 125 125 C 130 100 130 65 138 52 C 142 45 152 45 154 52 L 152 95 L 164 50 C 166 42 176 42 178 50 L 175 95 L 186 55 C 188 48 198 48 200 55 L 195 105 L 205 70 C 208 62 218 64 216 72 L 205 135 C 195 160 175 175 150 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" />
  <!-- Thumb extended -->
  <path d="M 125 125 C 110 115 95 110 98 98 C 102 88 115 92 120 105 L 128 125" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Red stop barrier icon -->
  <circle cx="235" cy="65" r="14" fill="#ef4444" />
  <rect x="227" y="62" width="16" height="6" fill="#ffffff" rx="2" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Telapak tangan terbuka tegak (Isyarat Stop)</text>
""")

# 18. berdoa (palms clasped together in prayer)
illustrations["berdoa"] = svg_wrap("""
  <!-- Left palm clasped -->
  <path d="M 125 175 L 138 120 L 146 55 C 148 48 152 48 152 55 L 152 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" stroke-linejoin="round" />
  <!-- Right palm clasped mirrored -->
  <path d="M 175 175 L 162 120 L 154 55 C 152 48 148 48 148 55 L 148 175 Z" fill="#df9266" stroke="#231815" stroke-width="3.5" stroke-linejoin="round" />
  <!-- Spiritual radiance aura -->
  <path d="M 150 25 L 150 15" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" />
  <path d="M 125 35 L 118 28" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" />
  <path d="M 175 35 L 182 28" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua telapak tangan dirapatkan di dada</text>
""")

# 19. membaca (left hand book, right scanning fingers)
illustrations["membaca"] = svg_wrap("""
  <!-- Left open palm as book -->
  <path d="M 60 140 L 135 140 C 150 140 160 135 170 120 L 170 155 L 60 160 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Right 2 fingers scanning across palm -->
  <path d="M 160 70 L 110 115 C 105 120 100 115 105 110 L 155 65" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <path d="M 175 75 L 125 120" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Scanning horizontal arrow -->
  <path d="M 95 95 L 145 95" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="4,2" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Dua jari menatap & menelusuri telapak</text>
""")

# 20. menulis (holding pen writing on left palm)
illustrations["menulis"] = svg_wrap("""
  <!-- Flat left palm as paper -->
  <path d="M 65 145 L 145 145 C 160 145 170 140 180 125 L 180 160 L 65 160 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Right hand holding pen -->
  <path d="M 175 60 L 130 125 C 128 130 120 125 125 120 L 170 55 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Pen body -->
  <line x1="185" y1="45" x2="130" y2="125" stroke="#3b82f6" stroke-width="5" stroke-linecap="round" />
  <!-- Writing scribble line -->
  <path d="M 90 135 Q 105 130 120 135" fill="none" stroke="#231815" stroke-width="2" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Gerakan memegang pena mencoret telapak</text>
""")

# 21. menggambar (painting strokes on palm)
illustrations["menggambar"] = svg_wrap("""
  <!-- Left palm palette/canvas -->
  <path d="M 65 150 L 145 150 C 160 150 170 145 180 130 L 180 165 L 65 165 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Right hand with brush sketching curves -->
  <path d="M 180 65 L 135 125 C 132 130 125 125 128 120 L 175 60 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Artistic wave curve -->
  <path d="M 90 125 Q 115 105 140 125 T 165 125" fill="none" stroke="#8b5cf6" stroke-width="3" stroke-linecap="round" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Gerakan melukis di depan telapak tangan</text>
""")

# 22. melihat (2 fingers pointing from eyes forward)
illustrations["melihat"] = svg_wrap("""
  <!-- Hand at eye level with index & middle pointing forward -->
  <path d="M 85 160 L 120 130 C 130 120 150 120 160 125 L 150 165 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Two fingers pointing forward -->
  <path d="M 145 120 L 225 105 C 235 102 235 115 225 118 L 160 130" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <path d="M 145 130 L 225 120 C 235 118 235 130 225 132 L 160 140" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Eye sight line arrows -->
  <path d="M 215 85 L 265 85" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Dua jari mengarah dari mata ke depan</text>
""")

# 23. berpikir (index finger at temple)
illustrations["berpikir"] = svg_wrap("""
  <!-- Hand with index tapping temple -->
  <path d="M 125 175 L 140 135 C 145 120 160 120 165 135 L 160 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Extended index finger -->
  <path d="M 142 120 L 142 55 C 142 45 155 45 155 55 L 155 120" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Thought sparkle near head -->
  <circle cx="185" cy="55" r="4" fill="#f59e0b" />
  <circle cx="205" cy="40" r="7" fill="#f59e0b" opacity="0.6" />
  <circle cx="225" cy="30" r="11" fill="#f59e0b" opacity="0.3" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Jari telunjuk menyentuh pelipis/kening</text>
""")

# 24. ingat (tap temple then thumb forward)
illustrations["ingat"] = svg_wrap("""
  <!-- Hand at temple with idea glow -->
  <path d="M 125 175 L 140 135 C 145 120 160 120 165 135 L 160 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <path d="M 142 120 L 142 60 C 142 50 155 50 155 60 L 155 120" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Lightbulb / Remember flash -->
  <path d="M 195 55 Q 210 35 225 55 Q 210 70 195 55 Z" fill="#facc15" stroke="#ca8a04" stroke-width="2" />
  <line x1="210" y1="25" x2="210" y2="15" stroke="#facc15" stroke-width="3" stroke-linecap="round" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Sentuh kening lalu buka tanda ingat</text>
""")

# 25. paham (hand opening from temple outwards)
illustrations["paham"] = svg_wrap("""
  <!-- Hand opening wide near temple -->
  <path d="M 115 170 L 130 130 C 135 110 145 95 155 75 L 165 110 L 175 70 L 185 115 L 195 80 L 185 155 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round" />
  <!-- Understanding expansion aura -->
  <path d="M 160 50 Q 200 40 225 65" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow-green)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Tangan membuka dari pelipis (Tanda Paham)</text>
""")

# 26. sabar (hand gently stroking chest downward)
illustrations["sabar"] = svg_wrap("""
  <!-- Flat open palm on chest -->
  <path d="M 120 155 L 135 115 C 140 100 155 95 170 95 C 185 95 195 105 190 120 L 175 165 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Downward calm stroke arrow -->
  <path d="M 155 75 L 155 125" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow-green)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Telapak tangan mengelus dada ke bawah perlahan</text>
""")

# 27. semangat (two clenched fists flexing down with power)
illustrations["semangat"] = svg_wrap("""
  <!-- Left clenched fist -->
  <path d="M 95 165 L 105 130 C 110 115 125 110 138 115 L 130 165 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" />
  <!-- Right clenched fist -->
  <path d="M 205 165 L 195 130 C 190 115 175 110 162 115 L 170 165 Z" fill="#df9266" stroke="#231815" stroke-width="3.5" />
  <!-- Energetic flex arrows -->
  <path d="M 115 85 L 115 115" fill="none" stroke="#ef4444" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <path d="M 185 85 L 185 115" fill="none" stroke="#ef4444" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua kepalan tangan dihentak mantap di dada</text>
""")

# 28. terlambat (tap wrist watch then sweep backward)
illustrations["terlambat"] = svg_wrap("""
  <!-- Left wrist -->
  <rect x="110" y="130" width="28" height="20" rx="4" fill="#0284c7" stroke="#231815" stroke-width="2.5" />
  <path d="M 60 140 L 180 140" stroke="#df9266" stroke-width="16" stroke-linecap="round" />
  <!-- Right hand sweeping backward over wrist -->
  <path d="M 180 80 L 125 125" stroke="#ea9f71" stroke-width="12" stroke-linecap="round" />
  <!-- Backward sweep arrow -->
  <path d="M 145 95 C 175 75 215 95 220 120" fill="none" stroke="#ef4444" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Ketuk jam lalu tangan digerakkan lewat belakang</text>
""")

# 29. tunggu (open palm down waving gently)
illustrations["tunggu"] = svg_wrap("""
  <!-- Flat palm facing down -->
  <path d="M 90 140 L 140 140 C 160 140 190 135 210 125 C 218 120 218 135 210 140 L 150 155 L 90 155 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Gentle wait wave arrows -->
  <path d="M 130 95 Q 160 85 190 95" fill="none" stroke="#f59e0b" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <path d="M 190 105 Q 160 115 130 105" fill="none" stroke="#f59e0b" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Telapak tangan menghadap bawah digerakkan pelan</text>
""")

# 30. ambil (open hand closing into grasp towards self)
illustrations["ambil"] = svg_wrap("""
  <!-- Hand grabbing / grasping inward -->
  <path d="M 180 160 L 160 125 C 150 105 130 100 110 105 C 100 110 105 125 120 125 L 145 135 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Grasping finger arcs -->
  <path d="M 140 100 Q 120 85 105 100" fill="none" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Inward pulling arrow -->
  <path d="M 175 75 L 115 75" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="6,4" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Tangan terbuka lalu menggenggam menarik ke dada</text>
""")

# 31. minta (cupped palms asking politely)
illustrations["minta"] = svg_wrap("""
  <!-- Cupped palms reaching forward -->
  <path d="M 110 165 L 130 135 C 140 120 160 120 170 135 L 190 165 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linejoin="round" />
  <!-- Gentle asking forward arrow -->
  <path d="M 150 95 L 150 120" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Telapak tangan menengadah ke depan meminta sopan</text>
""")

# 32. mulai (hands parting path forward)
illustrations["mulai"] = svg_wrap("""
  <!-- Left hand chopping path -->
  <path d="M 110 150 L 140 100 C 145 90 155 90 152 100 L 130 155 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Right hand opening path -->
  <path d="M 190 150 L 160 100 C 155 90 145 90 148 100 L 170 155 Z" fill="#df9266" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Parting arrows -->
  <path d="M 130 75 L 90 55" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow-green)" />
  <path d="M 170 75 L 210 55" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="5,3" marker-end="url(#arrow-green)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua telapak membuka membelah ke depan</text>
""")

# 33. hati-hati (two V-signs alternating forward)
illustrations["hati-hati"] = svg_wrap("""
  <!-- Left hand V-peace sign -->
  <path d="M 85 160 L 105 125 L 95 65 C 95 55 105 55 105 65 L 115 110 L 125 65 C 125 55 135 55 135 65 L 125 125 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <!-- Right hand V-peace sign -->
  <path d="M 215 160 L 195 125 L 185 65 C 185 55 175 55 175 65 L 165 110 L 155 65 C 155 55 145 55 145 65 L 155 125 Z" fill="#df9266" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Dua tangan membentuk huruf V bergantian ke depan</text>
""")

# 34. keren (shaka sign - thumb & pinky extended)
illustrations["keren"] = svg_wrap("""
  <!-- Fist with thumb and pinky extended (Shaka / Cool) -->
  <path d="M 125 170 L 140 135 C 145 120 160 120 165 135 L 160 170 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Extended thumb left -->
  <path d="M 135 130 C 115 125 90 120 85 110 C 80 100 95 95 105 105 L 140 125" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Extended pinky right -->
  <path d="M 160 130 C 180 125 205 120 210 110 C 215 100 200 95 190 105 L 155 125" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Cool sparkles -->
  <path d="M 150 40 L 150 60 M 140 50 L 160 50" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Jempol dan kelingking diacungkan (Isyarat Keren)</text>
""")

# 35. janji (pinky promise)
illustrations["janji"] = svg_wrap("""
  <!-- Hand with upright pinky finger -->
  <path d="M 125 175 L 140 140 C 145 125 165 125 170 140 L 160 175 Z" fill="#ea9f71" stroke="#231815" stroke-width="4" />
  <!-- Upright extended pinky finger -->
  <path d="M 165 135 L 165 65 C 165 55 175 55 175 65 L 175 135" fill="#ea9f71" stroke="#231815" stroke-width="4" stroke-linecap="round" />
  <!-- Promise sparkle ring -->
  <circle cx="170" cy="55" r="9" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="3,2" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Jari kelingking tegak ke atas (Janji)</text>
""")

# 36. buat (two fists rotating/tapping on each other)
illustrations["buat"] = svg_wrap("""
  <!-- Top fist tapping -->
  <path d="M 125 110 L 140 80 C 145 70 165 70 170 80 L 165 110 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" />
  <!-- Bottom fist base -->
  <path d="M 125 155 L 140 125 C 145 115 165 115 170 125 L 165 155 Z" fill="#df9266" stroke="#231815" stroke-width="3.5" />
  <!-- Tapping / building arrows -->
  <path d="M 110 95 C 100 115 100 135 110 145" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="4,2" marker-end="url(#arrow)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Kedua kepalan saling mengetuk/memutar membentuk</text>
""")

# 37. berjalan (index & middle fingers walking like legs)
illustrations["berjalan"] = svg_wrap("""
  <!-- Left palm surface -->
  <path d="M 60 165 L 170 165" stroke="#df9266" stroke-width="12" stroke-linecap="round" />
  <!-- Right hand walking fingers -->
  <path d="M 120 75 L 120 120 L 105 160" stroke="#ea9f71" stroke-width="12" stroke-linecap="round" />
  <path d="M 120 75 L 120 120 L 105 160" fill="none" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <path d="M 135 75 L 135 120 L 150 160" stroke="#ea9f71" stroke-width="12" stroke-linecap="round" />
  <path d="M 135 75 L 135 120 L 150 160" fill="none" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <!-- Walking step forward arrow -->
  <path d="M 160 135 L 205 135" fill="none" stroke="#10b981" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrow-green)" />
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Dua jari melangkah seperti kaki di atas telapak</text>
""")

# 38. bisindo (BISINDO - signing hands)
illustrations["bisindo"] = svg_wrap("""
  <!-- Left hand signing -->
  <path d="M 75 165 L 105 125 C 115 110 135 110 145 95 L 135 145 Z" fill="#ea9f71" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <!-- Right hand signing -->
  <path d="M 225 165 L 195 125 C 185 110 165 110 155 95 L 165 145 Z" fill="#df9266" stroke="#231815" stroke-width="3.5" stroke-linecap="round" />
  <!-- BISINDO Badge in center -->
  <rect x="100" y="45" width="100" height="30" rx="8" fill="#10b981" />
  <text x="150" y="66" font-family="sans-serif" font-size="14" font-weight="extrabold" fill="#ffffff" text-anchor="middle">BISINDO</text>
  <text x="150" y="200" font-family="sans-serif" font-size="12" font-weight="bold" fill="#64748b" text-anchor="middle">Bahasa Isyarat Indonesia</text>
""")

print(f"Total vocabulary illustrations defined: {len(illustrations)}")

for word, svg_code in illustrations.items():
    file_path = f"assets/kosakata/{word}.svg"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg_code.strip())
    print(f"  [OK] Saved {file_path}")

print("\nAll 38 vocabulary illustrations successfully generated!")
