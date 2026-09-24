# -*- coding: utf-8 -*-
"""QADAM — PDF fix: WeasyPrint -> xhtml2pdf (Docker kerak emas)."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. requirements.txt — WeasyPrint o'chirish, xhtml2pdf qo'shish
# ═══════════════════════════════════════════════════════════
REQ = Path("qadam/requirements.txt")
req = REQ.read_text(encoding="utf-8")

# WeasyPrint va jinja2 qatorlarini olib tashlash
lines = []
for line in req.split("\n"):
    if "weasyprint" in line.lower() or "jinja2" in line.lower():
        continue
    lines.append(line)

req = "\n".join(lines).rstrip()

# xhtml2pdf qo'shish
if "xhtml2pdf" not in req:
    req += "\nxhtml2pdf==0.2.16\n"

REQ.write_text(req + "\n", encoding="utf-8")
print("[OK] requirements.txt — WeasyPrint -> xhtml2pdf")


# ═══════════════════════════════════════════════════════════
# 2. backend/pdf_report.py — xhtml2pdf versiyasiga o'tkazish
# ═══════════════════════════════════════════════════════════
PDF_GEN = Path("qadam/backend/pdf_report.py")

PDF_GEN.write_text(r'''"""PDF Report generator — xhtml2pdf (pure Python, no system deps)."""
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4;
    margin: 12mm 14mm;
  }
  body {
    font-family: Helvetica, Arial, sans-serif;
    color: #0a0a0f;
    font-size: 10pt;
    line-height: 1.5;
  }
  h1 { font-size: 20pt; margin: 0 0 4pt; color: #0a0a0f; }
  h2 { font-size: 14pt; margin: 12pt 0 6pt; color: #4f46e5; }
  h3 { font-size: 11pt; margin: 8pt 0 4pt; color: #0a0a0f; }
  h4 { font-size: 10pt; margin: 6pt 0 3pt; color: #0a0a0f; }
  p { font-size: 10pt; margin: 3pt 0; color: #1f2937; }
  ul, ol { padding-left: 16pt; margin: 3pt 0; }
  li { margin: 2pt 0; color: #1f2937; font-size: 9.5pt; }
  .muted { color: #6b7280; font-size: 9pt; }
  .card {
    border: 1pt solid #e5e7eb;
    padding: 8pt 10pt;
    margin-bottom: 8pt;
    background: #f9fafb;
  }
  .card-indigo { border-color: #c7d2fe; background: #eef2ff; }
  .card-emerald { border-color: #a7f3d0; background: #ecfdf5; }
  .card-amber { border-color: #fde68a; background: #fffbeb; }
  .badge {
    padding: 1pt 4pt;
    font-size: 8pt;
    font-weight: bold;
  }
  .badge-indigo { background: #e0e7ff; color: #3730a3; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-red { background: #fee2e2; color: #991b1b; }
  .badge-green { background: #d1fae5; color: #065f46; }
  .stage {
    border-left: 3pt solid #6366f1;
    padding: 6pt 0 6pt 8pt;
    margin-bottom: 8pt;
  }
  .stage-num {
    background: #6366f1;
    color: white;
    font-weight: bold;
    padding: 2pt 6pt;
    font-size: 10pt;
  }
  .section-title {
    font-size: 12pt;
    font-weight: bold;
    color: #4f46e5;
    border-bottom: 1pt solid #e5e7eb;
    padding-bottom: 3pt;
    margin: 14pt 0 6pt;
  }
  .fit-big { font-size: 16pt; font-weight: bold; color: #059669; }
  .row { margin-bottom: 4pt; }
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
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td>
        <h3 style="margin:0">
          <span class="badge badge-indigo">#{{ loop.index }}</span>
          {{ c.career.uz }}
        </h3>
        <p class="muted" style="margin:2pt 0 0 0">{{ c.career.cluster_uz }}</p>
      </td>
      <td align="right" valign="top">
        <span class="fit-big">{{ c.fit }}%</span><br>
        <span class="muted" style="font-size:8pt">FIT</span><br>
        <span class="muted">Ready: {{ c.readiness }}%</span>
      </td>
    </tr>
  </table>
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
    <p class="muted">Kuchli signallaringiz:</p>
    <ul>
    {% for s in c.roadmap.a_point.signal_summary.top_5 %}
      <li><b>{{ s.key }}</b> — {{ (s.score*100)|round|int }}%</li>
    {% endfor %}
    </ul>
  {% endif %}
  {% if c.roadmap.a_point.constraints %}
    <h4>To'siqlar va yechim</h4>
    <ul>
    {% for cc in c.roadmap.a_point.constraints %}
      <li><b>[{{ cc.level|upper }}]</b> {{ cc.problem or cc.type }} — {{ cc.solution }}</li>
    {% endfor %}
    </ul>
  {% endif %}
</div>
{% endif %}

{% if c.roadmap.path and c.roadmap.path.stages %}
<div class="card card-amber">
  <h4 style="margin:0">YO'L — {{ c.roadmap.path.total_weeks }} hafta ({{ c.roadmap.path.stages|length }} stage)</h4>
</div>

{% for s in c.roadmap.path.stages %}
<div class="stage">
  <h4 style="margin:0">
    <span class="stage-num">{{ s.n }}</span>
    &nbsp;{{ s.name_uz }}
  </h4>
  <p class="muted" style="margin:2pt 0 4pt 0">
    {{ s.weeks }} hafta • {{ s.daily_hours }} • Rol: {{ s.role }}
  </p>

  {% if s.daily_focus %}
    <p><b>Har kun nima qilish:</b></p>
    <ul>
    {% for d in s.daily_focus %}<li>{{ d }}</li>{% endfor %}
    </ul>
  {% endif %}

  {% if s.constraints %}
    <p><b>To'siq va yechim:</b></p>
    <ul>
    {% for cc in s.constraints %}
      <li>{{ cc.problem }} → <b>{{ cc.solution }}</b></li>
    {% endfor %}
    </ul>
  {% endif %}

  {% if s.graduate_criteria %}
    <p><b>Keyingi stage'ga shart:</b></p>
    <ul>
    {% for gc in s.graduate_criteria %}<li>{{ gc }}</li>{% endfor %}
    </ul>
  {% endif %}

  {% if s.skills_gained %}
    <p class="muted"><b>Ko'nikmalar:</b> {{ s.skills_gained|join(", ") }}</p>
  {% endif %}
</div>
{% endfor %}
{% endif %}

{% if c.roadmap.b_point %}
<div class="card card-emerald">
  <h4>B NUQTA — Erishishingiz mumkin</h4>
  <table width="100%">
    <tr>
      {% if c.roadmap.b_point.junior_salary_uzs %}
      <td width="50%">
        <p class="muted" style="margin:0">Junior UZ</p>
        <p style="font-size:13pt;font-weight:bold;color:#059669;margin:2pt 0">{{ c.roadmap.b_point.junior_salary_uzs }}</p>
      </td>
      {% endif %}
      {% if c.roadmap.b_point.remote_salary_usd %}
      <td width="50%">
        <p class="muted" style="margin:0">Remote</p>
        <p style="font-size:13pt;font-weight:bold;color:#0891b2;margin:2pt 0">{{ c.roadmap.b_point.remote_salary_usd }}</p>
      </td>
      {% endif %}
    </tr>
  </table>
  {% if c.roadmap.b_point.outcomes %}
    <ul>
    {% for o in c.roadmap.b_point.outcomes %}<li>{{ o }}</li>{% endfor %}
    </ul>
  {% endif %}
  {% if c.roadmap.b_point.next_step %}
    <p class="muted">Keyingi qadam: {{ c.roadmap.b_point.next_step }}</p>
  {% endif %}
</div>
{% endif %}

{% if c.roadmap.first_3_actions %}
<div class="card card-amber">
  <h4>Birinchi 3 qadam — bugun boshlang</h4>
  <ol>
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
    {% for d in w.days %}<li>{{ d }}</li>{% endfor %}
    </ul>
  {% endfor %}
</div>
{% endif %}

{% if c.roadmap.milestones %}
<div class="card">
  <h4>Muhim nuqtalar</h4>
  <ul>
  {% for m in c.roadmap.milestones %}
    <li><b>{{ m.week }}h</b> — {{ m.milestone }}</li>
  {% endfor %}
  </ul>
</div>
{% endif %}

{% if c.roadmap.resources %}
<div class="card">
  <h4>Resurslar</h4>
  <ul>
  {% for r in c.roadmap.resources %}
    <li>{{ r.name }} — {{ r.url }}</li>
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
  @kelajakkailkqadam_bot
</p>

</body>
</html>
"""


def _render_template(report):
    """Jinja uslubidagi minimal template (xhtml2pdf ichida yo'q, o'zimiz)."""
    # xhtml2pdf Jinja2'ni qo'llab-quvvatlamaydi — biz o'zimiz render qilamiz
    # Oddiy formatlangan string almashtirish
    from jinja2 import Template
    template = Template(HTML_TEMPLATE)
    date_str = datetime.utcnow().strftime("%d.%m.%Y")
    return template.render(
        date=date_str,
        ai=report.get("ai") or {},
        careers=(report.get("roadmap") or {}).get("careers", []),
    )


def generate_pdf(report, theme="light"):
    """Report dict -> PDF bytes."""
    html = _render_template(report)
    output = BytesIO()
    pisa.CreatePDF(html, dest=output, encoding="utf-8")
    return output.getvalue()
''', encoding="utf-8")
print("[OK] backend/pdf_report.py — xhtml2pdf versiyasi")


# ═══════════════════════════════════════════════════════════
# 3. diagnostic.py — import yangilash (weasyprint emas)
# ═══════════════════════════════════════════════════════════
DIAG = Path("qadam/backend/api/diagnostic.py")
diag = DIAG.read_text(encoding="utf-8")
# Bu faylda o'zgartirish kerak emas — import dinamik: `from backend.pdf_report import generate_pdf`
# Faqat generate_pdf nomi bir xil
print("[OK] diagnostic.py — o'zgartirish kerak emas (dinamik import)")

print()
print("=" * 60)
print("PDF fix — tayyor!")
print("=" * 60)
print()
print("MUHIM: Render Build Command'ni ESKI holatga qaytaring!")
print()
print("Yangi Build Command:")
print("  pip install --upgrade pip && pip install -r requirements.txt")
print()
print("(apt-get qismi KERAK EMAS — o'chirib tashlang!)")
print()
print("Keyingi qadam:")
print("  1. git add -A")
print('  2. git commit -m "PDF: WeasyPrint -> xhtml2pdf (no Docker)"')
print("  3. git push")
print("  4. Render Build Command yangilash (apt-get olib tashlash)")
print("  5. Manual Deploy")