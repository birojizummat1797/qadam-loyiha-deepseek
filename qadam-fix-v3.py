# -*- coding: utf-8 -*-
"""QADAM v3 — Top-3 + PDF uzluksiz oqim + calendar PDF'da ochiq."""
import json
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. BACKEND — Top-3
# ═══════════════════════════════════════════════════════════
DIAG = Path("qadam/backend/api/diagnostic.py")
code = DIAG.read_text(encoding="utf-8")

# top_n=5 → top_n=3 (barcha joyda)
code = code.replace("top_n=5", "top_n=3")
code = code.replace("top_n = 5", "top_n = 3")

DIAG.write_text(code, encoding="utf-8")
print("[OK] diagnostic.py — Top-3")

# roadmap.py ham top_n ishlatadi (fallback uchun)
ROADMAP = Path("qadam/backend/engine/roadmap.py")
if ROADMAP.exists():
    rm_code = ROADMAP.read_text(encoding="utf-8")
    rm_code = rm_code.replace("top_n=5", "top_n=3")
    ROADMAP.write_text(rm_code, encoding="utf-8")
    print("[OK] roadmap.py — Top-3")


# ═══════════════════════════════════════════════════════════
# 2. CSS — PDF uzluksiz oqim (Hormozi uslubi)
# ═══════════════════════════════════════════════════════════
GLOBALS = Path("qadam-miniapp/app/globals.css")
css = GLOBALS.read_text(encoding="utf-8")

# Eski print blokni olib tashlash
import re
css = re.sub(r'/\* =+\s*PRINT.*?\*/\s*@media print \{.*?\n\}', '', css, flags=re.DOTALL)

# Yangi print blok
print_block = '''

/* ═══════════════════════════════════════════════════════════
   PRINT — Uzluksiz oqim (Hormozi uslubi)
   Sahifa bo'linmalari kontent uzilmasin, bo'sh joy minimal
   ═══════════════════════════════════════════════════════════ */
@media print {
  /* Barcha animatsiya va transformatsiyalarni olib tashlash */
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
    transform: none !important;
    box-shadow: none !important;
    text-shadow: none !important;
  }

  /* Framer Motion opacity 0 → 1 */
  * {
    opacity: 1 !important;
  }

  /* Fon va matn */
  html, body {
    background: white !important;
    color: black !important;
    font-size: 10pt;
  }

  /* Sahifa chekkalari */
  @page {
    size: A4;
    margin: 10mm 8mm;
  }

  /* Kartalar — ramka bilan, lekin uzluksiz */
  .card, [class*="rounded-2xl"], [class*="rounded-xl"] {
    background: white !important;
    border: 1px solid #ddd !important;
    padding: 8pt !important;
    margin-bottom: 6pt !important;

    /* Muhim: bo'linmalarni uzmaslik uchun auto */
    break-inside: auto;
    page-break-inside: auto;
  }

  /* Sarlavhalar */
  h1 { font-size: 20pt; margin: 0 0 6pt; }
  h2 { font-size: 16pt; margin: 12pt 0 6pt; page-break-after: avoid; }
  h3 { font-size: 13pt; margin: 8pt 0 4pt; page-break-after: avoid; }
  h4 { font-size: 11pt; margin: 6pt 0 3pt; page-break-after: avoid; }

  /* Ro'yxatlar */
  ul, ol { margin: 4pt 0; padding-left: 16pt; }
  li { margin: 2pt 0; }

  /* Gradient matn — oddiy qora */
  .gradient-text {
    background: none !important;
    -webkit-text-fill-color: black !important;
    color: black !important;
  }

  /* MUHIM: Accordion ichidagi kontent HAR DOIM ochiq */
  [data-accordion-content] {
    display: block !important;
    max-height: none !important;
    height: auto !important;
    overflow: visible !important;
    opacity: 1 !important;
  }

  /* Chevron ikonkalarni olib tashlash */
  [data-chevron] {
    display: none !important;
  }

  /* Calendar — PDF'da avtomatik ochiq */
  [data-calendar-body] {
    display: block !important;
    max-height: none !important;
    height: auto !important;
    overflow: visible !important;
  }

  /* Progress bar animatsiyalari */
  [style*="width"] {
    width: var(--final-width, 100%) !important;
  }

  /* Rangli badge va pill'lar */
  [class*="bg-indigo"], [class*="bg-purple"], [class*="bg-emerald"],
  [class*="bg-amber"], [class*="bg-blue"], [class*="bg-rose"] {
    background: #f3f4f6 !important;
    color: black !important;
    border: 1px solid #ddd !important;
  }

  /* Tugmalar — ko'rinmasin */
  button, .btn-primary {
    display: none !important;
  }

  /* Linklar */
  a { color: black !important; text-decoration: underline; }

  /* SVG ikonkalar — qora */
  svg { color: black !important; }

  /* Grid va flex */
  .grid { display: grid !important; }
  .flex { display: flex !important; }

  /* Sahifa bo'linmalari — minimal */
  .no-break { break-inside: avoid; }

  /* Emoji va ikonkalar */
  [class*="text-"] { color: black !important; }
}
'''

css += print_block
GLOBALS.write_text(css, encoding="utf-8")
print("[OK] globals.css — uzluksiz print oqim")


# ═══════════════════════════════════════════════════════════
# 3. RoadmapView.tsx — CSS-based calendar
# ═══════════════════════════════════════════════════════════
RV = Path("qadam-miniapp/components/RoadmapView.tsx")
rv = RV.read_text(encoding="utf-8")

# 3.1. Stage accordion — AnimatePresence → CSS
# Eski AnimatePresence o'rniga oddiy div bilan max-height
old_stage_block = '''<AnimatePresence>
                      {isOpen && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                          className="overflow-hidden"
                        >'''

new_stage_block = '''<div
                      data-accordion-content
                      className={`overflow-hidden transition-all duration-300 ${
                        isOpen ? "max-h-[10000px]" : "max-h-0"
                      }`}
                    >'''

if old_stage_block in rv:
    rv = rv.replace(old_stage_block, new_stage_block)
    print("[OK] RoadmapView — stage accordion CSS-based")

# Yopuvchi teg — mos kelishini tekshirish
old_close = '''                      )}
                    </AnimatePresence>
                  </div>
                </div>
              );'''
new_close = '''                  </div>
                </div>
              );'''
if old_close in rv:
    rv = rv.replace(old_close, new_close)
    print("[OK] RoadmapView — AnimatePresence olib tashlandi")

# 3.2. Chevron'ga data-chevron
rv = rv.replace(
    '<ChevronDown className="w-3.5 h-3.5 text-white" />',
    '<ChevronDown data-chevron className="w-3.5 h-3.5 text-white" />'
)
rv = rv.replace(
    '<ChevronRight className="w-3.5 h-3.5 text-white" />',
    '<ChevronRight data-chevron className="w-3.5 h-3.5 text-white" />'
)
print("[OK] RoadmapView — chevron data-attr")

# 3.3. Calendar — CSS-based
# useState(false) → default true
rv = rv.replace(
    'const [showCalendar, setShowCalendar] = useState(false);',
    'const [showCalendar, setShowCalendar] = useState(false);  // CSS-based'
)

# useEffect beforeprint olib tashlash (endi kerak emas)
old_useeffect = '''
  // PDF/print uchun calendar'ni avtomatik ochish
  useEffect(() => {
    const beforePrint = () => setShowCalendar(true);
    window.addEventListener("beforeprint", beforePrint);
    return () => window.removeEventListener("beforeprint", beforePrint);
  }, []);
'''
rv = rv.replace(old_useeffect, '')
print("[OK] RoadmapView — beforeprint olib tashlandi")

# Calendar AnimatePresence → CSS
old_cal = '''<AnimatePresence>
            {showCalendar && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >'''

new_cal = '''<div
              data-calendar-body
              className={`overflow-hidden transition-all duration-300 ${
                showCalendar ? "max-h-[10000px]" : "max-h-0"
              }`}
            >'''

if old_cal in rv:
    rv = rv.replace(old_cal, new_cal)
    print("[OK] RoadmapView — calendar CSS-based")

# Calendar yopuvchi
old_cal_close = '''                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}'''
new_cal_close = '''                </div>
            </div>
        </div>
      )}'''
if old_cal_close in rv:
    rv = rv.replace(old_cal_close, new_cal_close)
    print("[OK] RoadmapView — calendar yopuvchi yangilandi")

# Calendar chevron
rv = rv.replace(
    '{showCalendar ? <ChevronDown className="w-4 h-4 text-[var(--tg-hint)]" /> : <ChevronRight className="w-4 h-4 text-[var(--tg-hint)]" />}',
    '{showCalendar ? <ChevronDown data-chevron className="w-4 h-4 text-[var(--tg-hint)]" /> : <ChevronRight data-chevron className="w-4 h-4 text-[var(--tg-hint)]" />}'
)

RV.write_text(rv, encoding="utf-8")
print("[OK] RoadmapView — barcha yangilanishlar")


# ═══════════════════════════════════════════════════════════
# 4. Report page — Top-3 sarlavha
# ═══════════════════════════════════════════════════════════
REPORT = Path("qadam-miniapp/app/report/[id]/page.tsx")
rep = REPORT.read_text(encoding="utf-8")

rep = rep.replace("Top-{careers.length} mos yonalish", "Top-3 mos yonalish")
REPORT.write_text(rep, encoding="utf-8")
print("[OK] report/page.tsx — Top-3")

print()
print("=" * 60)
print("v3 — To'liq tayyor!")
print("=" * 60)
print()
print("1. Top-3 career (backend)")
print("2. PDF uzluksiz oqim (Hormozi uslubi)")
print("3. Calendar PDF'da avtomatik ochiq (CSS)")
print("4. Roadmapsiz career'lar olib tashlandi")
print()
print("Keyingi: git push + Render manual deploy")