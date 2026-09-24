# -*- coding: utf-8 -*-
"""QADAM — server-side PDF (WeasyPrint) + bot fayl yuborish."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. requirements.txt — WeasyPrint qo'shish
# ═══════════════════════════════════════════════════════════
REQ = Path("qadam/requirements.txt")
req = REQ.read_text(encoding="utf-8")

if "weasyprint" not in req:
    req += "\nweasyprint==62.3\njinja2==3.1.4\n"
    REQ.write_text(req, encoding="utf-8")
    print("[OK] requirements.txt — WeasyPrint qo'shildi")
else:
    print("[SKIP] requirements.txt — allaqachon bor")


# ═══════════════════════════════════════════════════════════
# 2. backend/pdf_report.py — PDF generator (r\"\"\" wrapper)
# ═══════════════════════════════════════════════════════════
PDF_GEN = Path("qadam/backend/pdf_report.py")

PDF_GEN.write_text(r"""# PDF Report generator - WeasyPrint
from datetime import datetime
from jinja2 import Template
from weasyprint import HTML


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4;
    margin: 12mm 14mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #0a0a0f;
    background: white;
    line-height: 1.5;
    font-size: 10pt;
  }
  h1 { font-size: 22pt; margin: 0 0 4pt; color: #0a0a0f; }
  h2 { font-size: 15pt; margin: 12pt 0 6pt; color: #4f46e5; }
  h3 { font-size: 12pt; margin: 10pt 0 5pt; color: #0a0a0f; }
  h4 { font-size: 10.5pt; margin: 6pt 0 3pt; color: #0a0a0f; }
  p, li { font-size: 10pt; margin: 3pt 0; color: #1f2937; }
  .muted { color: #6b7280; font-size: 9pt; }
  .card {
    border: 1px solid #e5e7eb;
    border-radius: 10pt;
    padding: 10pt 12pt;
    margin-bottom: 8pt;
    background: #f9fafb;
  }
  .card-indigo { border-color: #c7d2fe; background: #eef2ff; }
  .card-emerald { border-color: #a7f3d0; background: #ecfdf5; }
  .card-amber { border-color: #fde68a; background: #fffbeb; }
  .badge {
    display: inline-block;
    padding: 2pt 6pt;
    border-radius: 6pt;
    font-size: 8pt;
    font-weight: 600;
  }
  .badge-indigo { background: #e0e7ff; color: #3730a3; }
  .badge-emerald { background: #d1fae5; color: #065f46; }
  .badge-red { background: #fee2e2; color: #991b1b; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .row { display: flex; justify-content: space-between; margin-bottom: 6pt; }
  .stage {
    border-left: 3pt solid #6366f1;
    padding: 6pt 0 6pt 8pt;
    margin-bottom: 6pt;
  }
  .stage-num {
    display: inline-block;
    width: 22pt; height: 22pt;
    background: #6366f1; color: white;
    border-radius: 50%;
    text-align: center; line-height: 22pt;
    font-weight: 700; font-size: 11pt;
    margin-right: 6pt;
  }
  ul, ol { padding-left: 14pt; margin: 3pt 0; }
  li { margin: 1.5pt 0; }
  .tag {
    display: inline-block;
    padding: 1.5pt 5pt;
    border-radius: 8pt;
    background: #f3f4f6;
    font-size: 8pt;
    color: #374151;
    margin: 2pt 2pt 0 0;
  }
  .section-title {
    font-size: 12pt;
    font-weight: 700;
    color: #4f46e5;
    border-bottom: 1pt solid #e5e7eb;
    padding-bottom: 3pt;
    margin: 12pt 0 6pt;
  }
  .signal-row { margin-bottom: 3pt; }
  .signal-name { display: inline-block; width: 90pt; font-size: 9pt; }
  .signal-bar-bg {
    display: inline-block; width: 120pt; height: 5pt;
    background: #e5e7eb; border-radius: 3pt; vertical-align: middle;
  }
  .signal-bar-fill {
    height: 5pt; border-radius: 3pt;
    background: linear-gradient(90deg, #6366f1, #a855f7);
  }
  .signal-pct { font-size: 9pt; color: #6b7280; margin-left: 4pt; }
</style>
</head>
<body>

<h1>Sizning natijangiz</h1>
<p class="muted">{{ date }} • QADAM diagnostikasi</p>

{% if ai.summary %}
<div class="card card-indigo">
  <h3>Umumiy xulosa</h3>
  <p>{{ ai.summary }}</p>
</div>
{% endif %}

<h2>Top-{{ careers|length }} mos yonalish</h2>

{% for c in careers %}
<div class="card">
  <div class="row">
    <div>
      <h3 style="margin:0">
        <span class="badge badge-indigo">#{{ loop.index }}</span>
        {{ c.career.uz }}
      </h3>
      <p class="muted" style="margin:2pt 0 0 0">{{ c.career.cluster_uz }}</p>
    </div>
    <div style="text-align:right">
      <p style="margin:0"><b style="font-size:16pt;color:#059669">{{ c.fit }}%</b></p>
      <p class="muted" style="margin:0">FIT</p>
      <p style="margin:2pt 0 0 0;font-size:9pt">Ready: {{ c.readiness }}%</p>
    </div>
  </div>
</div>

{% if c.roadmap and not c.roadmap.is_placeholder %}
<div class="section-title">{{ c.career.uz }} — Roadmap</div>

{% if c.roadmap.why_this_path %}
<div class="card">
  <h4>Nega bu sizga mos</h4>
  <p>{{ c.roadmap.why_this_path }}</p>
</div>
{% endif %}

{% if c.roadmap.a_point %}
<div class="card">
  <h4>A NUQTA — Hozirgi holatingiz</h4>
  {% if c.roadmap.a_point.signal_summary and c.roadmap.a_point.signal_summary.top_5 %}
    <p class="muted" style="margin-bottom:4pt">Kuchli signallaringiz:</p>
    {% for s in c.roadmap.a_point.signal_summary.top_5 %}
      <div class="signal-row">
        <span class="signal-name">{{ s.key }}</span>
        <span class="signal-bar-bg">
          <span class="signal-bar-fill" style="width:{{ (s.score*100)|round|int }}%;display:block"></span>
        </span>
        <span class="signal-pct">{{ (s.score*100)|round|int }}%</span>
      </div>
    {% endfor %}
  {% endif %}
  {% if c.roadmap.a_point.constraints %}
    <h4 style="margin-top:8pt">To'siqlar va yechim</h4>
    {% for cc in c.roadmap.a_point.constraints %}
      <p style="margin:3pt 0">
        <span class="badge badge-{{ 'red' if cc.level == 'hard' else 'amber' }}">{{ cc.level }}</span>
        <b>{{ cc.problem or cc.type }}</b> — {{ cc.solution }}
      </p>
    {% endfor %}
  {% endif %}
</div>
{% endif %}

{% if c.roadmap.path and c.roadmap.path.stages %}
<div class="card card-amber">
  <div class="row">
    <h4 style="margin:0">YO'L — {{ c.roadmap.path.total_weeks }} hafta</h4>
    <span class="muted">{{ c.roadmap.path.stages|length }} stage</span>
  </div>
</div>

{% for s in c.roadmap.path.stages %}
<div class="stage">
  <h4 style="margin:0">
    <span class="stage-num">{{ s.n }}</span>
    {{ s.name_uz }}
  </h4>
  <p class="muted" style="margin:2pt 0 4pt 28pt">
    {{ s.weeks }} hafta • {{ s.daily_hours }} • Rol: {{ s.role }}
  </p>

  {% if s.daily_focus %}
    <p style="margin:4pt 0 2pt 28pt"><b>Har kun nima qilish:</b></p>
    <ul style="margin-left:28pt">
      {% for d in s.daily_focus %}<li>{{ d }}</li>{% endfor %}
    </ul>
  {% endif %}

  {% if s.constraints %}
    <p style="margin:4pt 0 2pt 28pt"><b>To'siq va yechim:</b></p>
    <ul style="margin-left:28pt">
      {% for cc in s.constraints %}
        <li>{{ cc.problem }} → <span style="color:#059669">{{ cc.solution }}</span></li>
      {% endfor %}
    </ul>
  {% endif %}

  {% if s.graduate_criteria %}
    <p style="margin:4pt 0 2pt 28pt"><b>Keyingi stage'ga shart:</b></p>
    <ul style="margin-left:28pt">
      {% for gc in s.graduate_criteria %}<li>{{ gc }}</li>{% endfor %}
    </ul>
  {% endif %}

  {% if s.skills_gained %}
    <div style="margin-left:28pt;margin-top:4pt">
      {% for sk in s.skills_gained %}<span class="tag">{{ sk }}</span>{% endfor %}
    </div>
  {% endif %}
</div>
{% endfor %}
{% endif %}

{% if c.roadmap.b_point %}
<div class="card card-emerald">
  <h4>B NUQTA — Erishishingiz mumkin</h4>
  <div class="row">
    {% if c.roadmap.b_point.junior_salary_uzs %}
    <div style="flex:1">
      <p class="muted" style="margin:0">Junior UZ</p>
      <p style="font-size:14pt;font-weight:700;margin:2pt 0;color:#059669">{{ c.roadmap.b_point.junior_salary_uzs }}</p>
    </div>
    {% endif %}
    {% if c.roadmap.b_point.remote_salary_usd %}
    <div style="flex:1">
      <p class="muted" style="margin:0">Remote</p>
      <p style="font-size:14pt;font-weight:700;margin:2pt 0;color:#0891b2">{{ c.roadmap.b_point.remote_salary_usd }}</p>
    </div>
    {% endif %}
  </div>
  {% if c.roadmap.b_point.outcomes %}
    <ul>
      {% for o in c.roadmap.b_point.outcomes %}<li>{{ o }}</li>{% endfor %}
    </ul>
  {% endif %}
  {% if c.roadmap.b_point.next_step %}
    <p class="muted" style="margin-top:4pt">Keyingi qadam: {{ c.roadmap.b_point.next_step }}</p>
  {% endif %}
</div>
{% endif %}

{% if c.roadmap.first_3_actions %}
<div class="card card-amber">
  <h4>Birinchi 3 qadam — bugun boshlang</h4>
  <ol style="padding-left:16pt">
    {% for a in c.roadmap.first_3_actions %}<li>{{ a }}</li>{% endfor %}
  </ol>
</div>
{% endif %}

{% if c.roadmap.calendar_30d %}
<div class="card">
  <h4>30 kunlik kalendar</h4>
  {% for w in c.roadmap.calendar_30d %}
    <p style="margin:6pt 0 2pt 0"><b>{{ w.w }}-hafta: {{ w.theme }}</b></p>
    <ul style="margin:0">
      {% for d in w.days %}<li style="font-size:9pt">{{ d }}</li>{% endfor %}
    </ul>
  {% endfor %}
</div>
{% endif %}

{% if c.roadmap.milestones %}
<div class="card">
  <h4>Muhim nuqtalar</h4>
  {% for m in c.roadmap.milestones %}
    <p style="margin:2pt 0">
      <span class="badge badge-indigo">{{ m.week }}h</span>
      {{ m.milestone }}
    </p>
  {% endfor %}
</div>
{% endif %}

{% if c.roadmap.resources %}
<div class="card">
  <h4>Resurslar</h4>
  <ul>
    {% for r in c.roadmap.resources %}
      <li>{{ r.name }} — <a href="{{ r.url }}">{{ r.url }}</a></li>
    {% endfor %}
  </ul>
</div>
{% endif %}

{% endif %}
{% endfor %}

{% if ai.risks %}
<div class="card card-amber">
  <h4>Umumiy ogohlantirishlar</h4>
  <ul>
    {% for r in ai.risks %}<li>{{ r }}</li>{% endfor %}
  </ul>
</div>
{% endif %}

{% if ai.next_step_emphasis %}
<div class="card card-indigo">
  <h4>Eng muhim qadam</h4>
  <p>{{ ai.next_step_emphasis }}</p>
</div>
{% endif %}

<p class="muted" style="text-align:center;margin-top:20pt">
  QADAM — Halol tahlil, manipulyatsiyasiz<br>
  qadam.uz • @kelajakkailkqadam_bot
</p>

</body>
</html>
'''


def generate_pdf(report, theme="light"):
    # Report dict -> PDF bytes
    template = Template(HTML_TEMPLATE)
    date_str = datetime.utcnow().strftime("%d.%m.%Y")
    html = template.render(
        date=date_str,
        ai=report.get("ai") or {},
        careers=(report.get("roadmap") or {}).get("careers", []),
    )
    pdf_bytes = HTML(string=html).write_pdf()
    return pdf_bytes
""", encoding="utf-8")
print("[OK] backend/pdf_report.py — PDF generator")


# ═══════════════════════════════════════════════════════════
# 3. diagnostic.py — /pdf endpoint qo'shish
# ═══════════════════════════════════════════════════════════
DIAG = Path("qadam/backend/api/diagnostic.py")
diag = DIAG.read_text(encoding="utf-8")

if "report_pdf" not in diag:
    PDF_ENDPOINT = r'''

# ═══════════════════════════════════════════════════════════════════
# PDF — Server-side PDF + bot orqali fayl yuborish
# ═══════════════════════════════════════════════════════════════════


class PdfRequestPayload(BaseModel):
    init_data: str
    theme: str = "light"


@router.post("/report/{report_id}/pdf")
async def report_pdf(report_id: int, payload: PdfRequestPayload):
    """PDF yaratadi va bot orqali foydalanuvchiga yuboradi."""
    user = _auth(payload.init_data)

    async with SessionLocal() as s:
        r = await s.get(TestResult, report_id)
        if not r or r.user_id != user["id"]:
            raise HTTPException(404, "Report topilmadi")

        report_data = {
            "id": r.id,
            "profile": r.profile,
            "roadmap": r.roadmap,
            "ai": r.ai_explanation,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }

    # PDF yaratish
    try:
        from backend.pdf_report import generate_pdf
        pdf_bytes = generate_pdf(report_data, theme=payload.theme)
    except Exception as e:
        log.error(f"PDF xatoligi: {e}")
        raise HTTPException(500, f"PDF xatolik: {str(e)[:100]}")

    # Bot orqali yuborish
    sent = False
    try:
        import os
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import BufferedInputFile

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "dostim"
        top_career = "sizga mos yonalish"
        careers = (r.roadmap or {}).get("careers", [])
        if careers:
            top_career = careers[0]["career"]["uz"]

        caption = (
            f"🎉 <b>Tabriklaymiz, {first_name}!</b>\n\n"
            f"QADAM diagnostikasi natijangiz va shaxsiy roadmap tayyor.\n\n"
            f"📌 <b>Asosiy yonalish:</b> {top_career}\n"
            f"📄 <b>Fayl:</b> QADAM-report-{report_id}.pdf\n\n"
            f"Reja boyicha bugun birinchi qadamni boshlang!\n"
            f"Savollar bolsa — @qadam_support\n\n"
            f"<i>Sizning muvaffaqiyatingiz — bizning maqsadimiz.</i>\n"
            f"— QADAM jamoasi"
        )

        file = BufferedInputFile(pdf_bytes, filename=f"QADAM-report-{report_id}.pdf")
        await bot.send_document(user["id"], document=file, caption=caption)
        await bot.session.close()
        sent = True
    except Exception as e:
        log.error(f"Bot PDF yuborishda xato: {e}")

    return {"ok": True, "report_id": report_id, "sent_to_telegram": sent}
'''
    diag = diag.rstrip() + PDF_ENDPOINT
    DIAG.write_text(diag, encoding="utf-8")
    print("[OK] diagnostic.py — /pdf endpoint")
else:
    print("[SKIP] diagnostic.py — /pdf allaqachon bor")


# ═══════════════════════════════════════════════════════════
# 4. api.ts — requestPdf
# ═══════════════════════════════════════════════════════════
API = Path("qadam-miniapp/lib/api.ts")
api = API.read_text(encoding="utf-8")

if "requestPdf" not in api:
    api += r'''

export async function requestPdf(report_id: number, theme: string = "light") {
  const r = await api.post(`/diagnostic/report/${report_id}/pdf`, {
    init_data: getInitData(),
    theme,
  });
  return r.data;
}
'''
    API.write_text(api, encoding="utf-8")
    print("[OK] api.ts — requestPdf")
else:
    print("[SKIP] api.ts — requestPdf allaqachon bor")


print()
print("=" * 60)
print("Server-side PDF — tayyor!")
print("=" * 60)
print()
print("KEYINGI:")
print("  1. Render Build Command'ni yangilash")
print("  2. git push + Render Manual Deploy")