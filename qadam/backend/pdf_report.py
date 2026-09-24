"""PDF Report generator - xhtml2pdf, jinja2 yo'q."""
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa


SIGNAL_UZ = {
    "logical_thinking": "Mantiq",
    "problem_solving": "Muammo hal",
    "technical_interest": "Texnika",
    "creative_design": "Ijodiy dizayn",
    "visual_logic": "Vizual mantiq",
    "user_empathy": "Empatiya",
    "system_design": "Tizim",
    "analytical": "Tahlil",
    "persistence": "Qatiyat",
    "math_logic": "Matematika",
    "attention_to_detail": "Detal",
    "business_sense": "Biznes",
    "innovation": "Innovatsiya",
}


STYLE = """
@page { size: A4; margin: 12mm 14mm; }
body { font-family: Helvetica, Arial, sans-serif; color: #0a0a0f; font-size: 10pt; line-height: 1.5; }
h1 { font-size: 20pt; margin: 0 0 4pt; color: #0a0a0f; }
h2 { font-size: 14pt; margin: 12pt 0 6pt; color: #4f46e5; }
h3 { font-size: 11pt; margin: 8pt 0 4pt; color: #0a0a0f; }
h4 { font-size: 10pt; margin: 6pt 0 3pt; color: #0a0a0f; }
p { font-size: 10pt; margin: 3pt 0; color: #1f2937; }
ul, ol { padding-left: 16pt; margin: 3pt 0; }
li { margin: 2pt 0; color: #1f2937; font-size: 9.5pt; }
.muted { color: #6b7280; font-size: 9pt; }
.card { border: 1pt solid #e5e7eb; padding: 8pt 10pt; margin-bottom: 8pt; background: #f9fafb; }
.card-indigo { border-color: #c7d2fe; background: #eef2ff; }
.card-emerald { border-color: #a7f3d0; background: #ecfdf5; }
.card-amber { border-color: #fde68a; background: #fffbeb; }
.badge { padding: 1pt 4pt; font-size: 8pt; font-weight: bold; }
.badge-indigo { background: #e0e7ff; color: #3730a3; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-red { background: #fee2e2; color: #991b1b; }
.stage { border-left: 3pt solid #6366f1; padding: 6pt 0 6pt 8pt; margin-bottom: 8pt; }
.stage-num { background: #6366f1; color: white; font-weight: bold; padding: 2pt 6pt; font-size: 10pt; }
.section-title { font-size: 12pt; font-weight: bold; color: #4f46e5; border-bottom: 1pt solid #e5e7eb; padding-bottom: 3pt; margin: 14pt 0 6pt; }
.fit-big { font-size: 16pt; font-weight: bold; color: #059669; }
"""


def _esc(s):
    """HTML escape."""
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _build_career_html(c):
    """Bitta career uchun HTML."""
    career = c.get("career", {})
    roadmap = c.get("roadmap", {})
    html = []

    # Career header
    html.append('<div class="card">')
    html.append("<table width=\"100%\"><tr>")
    html.append(f'<td><h3 style="margin:0"><span class="badge badge-indigo">#{_esc(c.get("_idx", ""))}</span> {_esc(career.get("uz", ""))}</h3>')
    html.append(f'<p class="muted" style="margin:2pt 0 0 0">{_esc(career.get("cluster_uz", ""))}</p></td>')
    html.append(f'<td align="right" valign="top"><span class="fit-big">{_esc(c.get("fit", 0))}%</span><br><span class="muted" style="font-size:8pt">FIT</span><br><span class="muted">Ready: {_esc(c.get("readiness", 0))}%</span></td>')
    html.append("</tr></table></div>")

    # Placeholder bo'lsa — o'tkazib yuborish
    if not roadmap or roadmap.get("is_placeholder"):
        return "\n".join(html)

    html.append(f'<div class="section-title">{_esc(career.get("uz", ""))} — Roadmap</div>')

    # Nega mos
    if roadmap.get("why_this_path"):
        html.append('<div class="card"><h4>Nega bu sizga mos</h4>')
        html.append(f'<p>{_esc(roadmap["why_this_path"])}</p></div>')

    # A NUQTA
    a_point = roadmap.get("a_point", {})
    if a_point:
        html.append('<div class="card"><h4>A NUQTA — Hozirgi holatingiz</h4>')
        sig = a_point.get("signal_summary", {})
        if sig and sig.get("top_5"):
            html.append('<p class="muted">Kuchli signallaringiz:</p><ul>')
            for s in sig["top_5"]:
                name = SIGNAL_UZ.get(s["key"], s["key"])
                pct = round(s["score"] * 100)
                html.append(f'<li><b>{_esc(name)}</b> — {pct}%</li>')
            html.append("</ul>")
        if a_point.get("constraints"):
            html.append("<h4>To'siqlar va yechim</h4><ul>")
            for cc in a_point["constraints"]:
                level = (cc.get("level") or "").upper()
                problem = cc.get("problem") or cc.get("type") or ""
                solution = cc.get("solution") or ""
                html.append(f'<li><b>[{_esc(level)}]</b> {_esc(problem)} — {_esc(solution)}</li>')
            html.append("</ul>")
        html.append("</div>")

    # YO'L
    path = roadmap.get("path", {})
    stages = path.get("stages", []) if path else []
    if stages:
        total_w = path.get("total_weeks", 0)
        html.append(f'<div class="card card-amber"><h4 style="margin:0">YO\'L — {total_w} hafta ({len(stages)} stage)</h4></div>')

        for s in stages:
            html.append('<div class="stage">')
            html.append(f'<h4 style="margin:0"><span class="stage-num">{_esc(s.get("n", ""))}</span> &nbsp;{_esc(s.get("name_uz", ""))}</h4>')
            html.append(f'<p class="muted" style="margin:2pt 0 4pt 0">{_esc(s.get("weeks", ""))} hafta • {_esc(s.get("daily_hours", ""))} • Rol: {_esc(s.get("role", ""))}</p>')

            if s.get("daily_focus"):
                html.append("<p><b>Har kun nima qilish:</b></p><ul>")
                for d in s["daily_focus"]:
                    html.append(f"<li>{_esc(d)}</li>")
                html.append("</ul>")

            if s.get("constraints"):
                html.append("<p><b>To'siq va yechim:</b></p><ul>")
                for cc in s["constraints"]:
                    html.append(f'<li>{_esc(cc.get("problem", ""))} → <b>{_esc(cc.get("solution", ""))}</b></li>')
                html.append("</ul>")

            if s.get("graduate_criteria"):
                html.append("<p><b>Keyingi stage'ga shart:</b></p><ul>")
                for gc in s["graduate_criteria"]:
                    html.append(f"<li>{_esc(gc)}</li>")
                html.append("</ul>")

            if s.get("skills_gained"):
                skills = ", ".join(_esc(x) for x in s["skills_gained"])
                html.append(f'<p class="muted"><b>Konikmalar:</b> {skills}</p>')

            html.append("</div>")

    # B NUQTA
    b_point = roadmap.get("b_point", {})
    if b_point:
        html.append('<div class="card card-emerald"><h4>B NUQTA — Erishishingiz mumkin</h4>')
        html.append('<table width="100%"><tr>')
        if b_point.get("junior_salary_uzs"):
            html.append(f'<td width="50%"><p class="muted" style="margin:0">Junior UZ</p><p style="font-size:13pt;font-weight:bold;color:#059669;margin:2pt 0">{_esc(b_point["junior_salary_uzs"])}</p></td>')
        if b_point.get("remote_salary_usd"):
            html.append(f'<td width="50%"><p class="muted" style="margin:0">Remote</p><p style="font-size:13pt;font-weight:bold;color:#0891b2;margin:2pt 0">{_esc(b_point["remote_salary_usd"])}</p></td>')
        html.append("</tr></table>")
        if b_point.get("outcomes"):
            html.append("<ul>")
            for o in b_point["outcomes"]:
                html.append(f"<li>{_esc(o)}</li>")
            html.append("</ul>")
        if b_point.get("next_step"):
            html.append(f'<p class="muted">Keyingi qadam: {_esc(b_point["next_step"])}</p>')
        html.append("</div>")

    # Birinchi 3 qadam
    if roadmap.get("first_3_actions"):
        html.append('<div class="card card-amber"><h4>Birinchi 3 qadam — bugun boshlang</h4><ol>')
        for a in roadmap["first_3_actions"]:
            html.append(f"<li>{_esc(a)}</li>")
        html.append("</ol></div>")

    # Calendar
    if roadmap.get("calendar_30d"):
        html.append('<div class="card"><h4>30 kunlik kalendar</h4>')
        for w in roadmap["calendar_30d"]:
            html.append(f'<p style="margin:6pt 0 2pt 0"><b>{_esc(w.get("w", ""))}-hafta: {_esc(w.get("theme", ""))}</b></p><ul style="margin:0">')
            for d in w.get("days", []):
                html.append(f"<li>{_esc(d)}</li>")
            html.append("</ul>")
        html.append("</div>")

    # Milestones
    if roadmap.get("milestones"):
        html.append('<div class="card"><h4>Muhim nuqtalar</h4><ul>')
        for m in roadmap["milestones"]:
            html.append(f'<li><b>{_esc(m.get("week", ""))}h</b> — {_esc(m.get("milestone", ""))}</li>')
        html.append("</ul></div>")

    # Resources
    if roadmap.get("resources"):
        html.append('<div class="card"><h4>Resurslar</h4><ul>')
        for r in roadmap["resources"]:
            html.append(f'<li>{_esc(r.get("name", ""))} — {_esc(r.get("url", ""))}</li>')
        html.append("</ul></div>")

    return "\n".join(html)


def generate_pdf(report, theme="light"):
    """Report dict -> PDF bytes."""
    date_str = datetime.utcnow().strftime("%d.%m.%Y")
    ai = report.get("ai") or {}
    careers = (report.get("roadmap") or {}).get("careers", [])

    parts = []
    parts.append('<!DOCTYPE html><html><head><meta charset="UTF-8">')
    parts.append(f"<style>{STYLE}</style></head><body>")
    parts.append("<h1>Sizning natijangiz</h1>")
    parts.append(f'<p class="muted">{date_str} • Qadam.io diagnostikasi</p>')

    if ai.get("summary"):
        parts.append('<div class="card card-indigo"><h3>Umumiy xulosa</h3>')
        parts.append(f'<p>{_esc(ai["summary"])}</p></div>')

    parts.append(f'<h2>Top-{len(careers)} mos yonalish</h2>')

    for idx, c in enumerate(careers, 1):
        c["_idx"] = idx
        parts.append(_build_career_html(c))

    if ai.get("risks"):
        parts.append('<div class="card card-amber"><h4>Umumiy ogohlantirishlar</h4><ul>')
        for r in ai["risks"]:
            parts.append(f"<li>{_esc(r)}</li>")
        parts.append("</ul></div>")

    if ai.get("next_step_emphasis"):
        parts.append('<div class="card card-indigo"><h4>Eng muhim qadam</h4>')
        parts.append(f'<p>{_esc(ai["next_step_emphasis"])}</p></div>')

    parts.append('<p class="muted" style="text-align:center;margin-top:20pt">')
    parts.append("Qadam.io — Halol tahlil, manipulyatsiyasiz<br>")
    parts.append("@kelajakkailkqadam_bot</p>")
    parts.append("</body></html>")

    html = "\n".join(parts)

    output = BytesIO()
    pisa.CreatePDF(html, dest=output, encoding="utf-8")
    return output.getvalue()
