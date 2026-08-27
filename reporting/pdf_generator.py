"""
reporting/pdf_generator.py — Professional PDF report generator using ReportLab Platypus.

Architecture:
  - BaseDocTemplate with PageTemplate for headers, footers, and page numbers
  - Platypus flowables: Paragraph, Table, Spacer, PageBreak, HRFlowable, KeepTogether
  - All 18 sections from the specification
  - Multi-page tables use repeatRows=1 (header on each page)
  - Unicode-safe: all strings sanitized before rendering
  - SYNTHETIC_DEMO mode: watermark "DEMONSTRATION REPORT — SYNTHETIC DATA" on every page

Does NOT print PDF bytes to terminal.
Output is written to a file only.
"""

import os
import textwrap
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    FrameBreak,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.frames import Frame

from reporting.models import ReportMode, SecurityAssessmentReport, ValidationStatus

# ─── Page dimensions ─────────────────────────────────────────────────────────

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 2 * cm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

# ─── Color palette ────────────────────────────────────────────────────────────

C_DARK   = colors.HexColor("#0D1117")
C_ACCENT = colors.HexColor("#1F6FEB")
C_WARN   = colors.HexColor("#E3B341")
C_CRIT   = colors.HexColor("#F85149")
C_GREEN  = colors.HexColor("#3FB950")
C_GRAY   = colors.HexColor("#8B949E")
C_BG     = colors.HexColor("#161B22")
C_WHITE  = colors.white

SEVERITY_COLORS = {
    "CRITICAL": C_CRIT,
    "HIGH":     colors.HexColor("#F0883E"),
    "MODERATE": C_WARN,
    "LOW":      C_GREEN,
}

VALIDATION_COLORS = {
    ValidationStatus.PASS:    C_GREEN,
    ValidationStatus.FAIL:    C_CRIT,
    ValidationStatus.BLOCKED: C_WARN,
}


# ─── Style sheet ─────────────────────────────────────────────────────────────

def _build_styles() -> dict:
    base = getSampleStyleSheet()
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", fontSize=22, textColor=C_WHITE,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=8,
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", fontSize=13, textColor=C_GRAY,
        alignment=TA_CENTER, fontName="Helvetica", spaceAfter=4,
    )
    styles["cover_warn"] = ParagraphStyle(
        "cover_warn", fontSize=11, textColor=C_WARN,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4,
    )
    styles["h1"] = ParagraphStyle(
        "h1", fontSize=16, textColor=C_ACCENT,
        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6,
    )
    styles["h2"] = ParagraphStyle(
        "h2", fontSize=12, textColor=C_WHITE,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body", fontSize=9, textColor=C_WHITE,
        fontName="Helvetica", spaceAfter=4, leading=14,
    )
    styles["body_gray"] = ParagraphStyle(
        "body_gray", fontSize=8, textColor=C_GRAY,
        fontName="Helvetica", spaceAfter=2, leading=12,
    )
    styles["label"] = ParagraphStyle(
        "label", fontSize=9, textColor=C_ACCENT,
        fontName="Helvetica-Bold", spaceAfter=2,
    )
    styles["mono"] = ParagraphStyle(
        "mono", fontSize=8, textColor=C_WHITE,
        fontName="Courier", spaceAfter=2, leading=11,
    )
    styles["warning"] = ParagraphStyle(
        "warning", fontSize=9, textColor=C_WARN,
        fontName="Helvetica-Bold", spaceAfter=4,
    )
    styles["blocked"] = ParagraphStyle(
        "blocked", fontSize=9, textColor=C_CRIT,
        fontName="Helvetica-Bold", spaceAfter=4,
    )
    styles["footer"] = ParagraphStyle(
        "footer", fontSize=7, textColor=C_GRAY,
        fontName="Helvetica", alignment=TA_CENTER,
    )
    styles["toc"] = ParagraphStyle(
        "toc", fontSize=9, textColor=C_WHITE,
        fontName="Helvetica", spaceAfter=2, leftIndent=10,
    )
    return styles


def _safe(text: Any, max_len: int = 2000) -> str:
    """Unicode-safe string truncation."""
    if text is None:
        return ""
    s = str(text)
    s = s.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
    return s[:max_len]


# ─── Page callbacks ───────────────────────────────────────────────────────────

class _PageCallbacks:
    def __init__(self, report: SecurityAssessmentReport, styles: dict):
        self.report  = report
        self.styles  = styles
        self.is_demo = (report.mode == ReportMode.SYNTHETIC_DEMO)

    def on_page(self, canvas, doc):
        canvas.saveState()
        # Dark background
        canvas.setFillColor(C_DARK)
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

        # Header stripe
        canvas.setFillColor(C_BG)
        canvas.rect(0, PAGE_HEIGHT - 1.2 * cm, PAGE_WIDTH, 1.2 * cm, fill=1, stroke=0)

        # Header text
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(MARGIN, PAGE_HEIGHT - 0.8 * cm, "PCCWIS — Security Assessment Report")
        canvas.drawRightString(
            PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 0.8 * cm,
            f"Report ID: {self.report.report_id[:16]}…"
        )

        # Footer stripe
        canvas.setFillColor(C_BG)
        canvas.rect(0, 0, PAGE_WIDTH, 1.2 * cm, fill=1, stroke=0)

        # Footer: page number + classification
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(C_GRAY)
        canvas.drawCentredString(
            PAGE_WIDTH / 2, 0.55 * cm,
            f"Page {doc.page}  |  CONFIDENTIAL  |  {self.report.generated_at[:10]}"
        )

        # Synthetic watermark
        if self.is_demo:
            canvas.setFont("Helvetica-Bold", 28)
            canvas.setFillColor(colors.Color(1, 0.85, 0, 0.12))
            canvas.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, "SYNTHETIC DATA")
            canvas.rotate(-35)
            canvas.translate(-PAGE_WIDTH / 2, -PAGE_HEIGHT / 2)

        canvas.restoreState()


# ─── Table helpers ────────────────────────────────────────────────────────────

def _make_table(data: List[List], col_widths=None, repeat_header=True) -> Table:
    t = Table(data, colWidths=col_widths, repeatRows=1 if repeat_header else 0)
    t.setStyle(TableStyle([
        # Header
        ("BACKGROUND",  (0, 0), (-1, 0),  C_BG),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  C_ACCENT),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        # Body
        ("BACKGROUND",  (0, 1), (-1, -1), C_DARK),
        ("TEXTCOLOR",   (0, 1), (-1, -1), C_WHITE),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_DARK, C_BG]),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID",        (0, 0), (-1, -1), 0.25, C_GRAY),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _hr(styles: dict) -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.5, color=C_GRAY, spaceAfter=6)


def _section_header(text: str, styles: dict):
    return [
        Spacer(1, 4 * mm),
        Paragraph(_safe(text), styles["h1"]),
        _hr(styles),
    ]


# ─── PDF Generator ────────────────────────────────────────────────────────────

class PDFGenerator:
    """Generates a real binary PDF from a SecurityAssessmentReport."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, report: SecurityAssessmentReport) -> str:
        """
        Generates the PDF. Returns the output file path.
        Does NOT print PDF bytes to terminal.
        """
        file_path = os.path.join(self.output_dir, f"report_{report.report_id[:8]}.pdf")
        styles = _build_styles()
        cb = _PageCallbacks(report, styles)

        doc = BaseDocTemplate(
            file_path,
            pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
            title=f"PCCWIS Report {report.report_id[:8]}",
            author="PCCWIS",
        )

        main_frame = Frame(
            MARGIN, 1.8 * cm,
            CONTENT_WIDTH, PAGE_HEIGHT - 3.6 * cm,
            id="main",
        )
        doc.addPageTemplates([
            PageTemplate(id="standard", frames=[main_frame], onPage=cb.on_page),
        ])

        story = []
        story += self._cover(report, styles)
        story += self._toc(styles)
        story += self._section_executive_summary(report, styles)
        story += self._section_scope(report, styles)
        story += self._section_methodology(report, styles)
        story += self._section_data_sources(report, styles)
        story += self._section_scenario(report, styles)
        story += self._section_entities(report, styles)
        story += self._section_transaction_analysis(report, styles)
        story += self._section_chain_analysis(report, styles)
        story += self._section_geographic(report, styles)
        story += self._section_indicators(report, styles)
        story += self._section_risk_assessment(report, styles)
        story += self._section_findings(report, styles)
        story += self._section_evidence(report, styles)
        story += self._section_recommendations(report, styles)
        story += self._section_limitations(report, styles)
        story += self._section_validation_status(report, styles)
        story += self._section_audit_trail(report, styles)

        doc.build(story)
        return file_path

    # ── Section 1: Cover ─────────────────────────────────────────────────────

    def _cover(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = []
        elems.append(Spacer(1, 3 * cm))
        elems.append(Paragraph("PREDICTIVE CYBERCRIME CASH WITHDRAWAL", styles["cover_title"]))
        elems.append(Paragraph("INTELLIGENCE SYSTEM", styles["cover_title"]))
        elems.append(Spacer(1, 6 * mm))
        elems.append(Paragraph("Security Assessment Report", styles["cover_sub"]))
        elems.append(Spacer(1, 1 * cm))

        if report.mode == ReportMode.SYNTHETIC_DEMO:
            elems.append(Paragraph("⚠  DEMONSTRATION REPORT", styles["cover_warn"]))
            elems.append(Paragraph("SYNTHETIC DATA — NOT REAL INVESTIGATION RESULTS", styles["cover_warn"]))
        elif report.mode == ReportMode.BLOCKED:
            elems.append(Paragraph("⚠  INVESTIGATION BLOCKED", styles["blocked"]))
            elems.append(Paragraph("Real data sources inaccessible — see Validation Status section.", styles["warning"]))

        elems.append(Spacer(1, 1 * cm))
        meta = [
            ["Report ID",        _safe(report.report_id)],
            ["Investigation ID", _safe(report.investigation_id)],
            ["Scenario ID",      _safe(report.scenario_id)],
            ["Mode",             report.mode.value],
            ["Generated",        _safe(report.generated_at[:19]) + " UTC"],
        ]
        t = Table([[Paragraph(k, styles["label"]), Paragraph(v, styles["body"])] for k, v in meta],
                  colWidths=[5 * cm, CONTENT_WIDTH - 5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_BG),
            ("TEXTCOLOR",  (0, 0), (-1, -1), C_WHITE),
            ("GRID",       (0, 0), (-1, -1), 0.25, C_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 6 * mm))
        elems.append(Paragraph(
            "CONFIDENTIAL — For authorised investigative use only. "
            "This document must not be distributed without appropriate authorisation.",
            styles["body_gray"]
        ))
        elems.append(PageBreak())
        return elems

    # ── TOC ──────────────────────────────────────────────────────────────────

    def _toc(self, styles: dict) -> list:
        sections = [
            "1. Executive Summary", "2. Investigation Scope", "3. Data Sources",
            "4. Methodology", "5. Scenario Overview", "6. Investigated Entities",
            "7. Transaction Analysis", "8. Transaction Chain Analysis",
            "9. Geographic Analysis", "10. Cybercrime Indicators", "11. Risk Assessment",
            "12. Findings", "13. Evidence & Provenance", "14. Recommendations",
            "15. Limitations", "16. Validation Status", "17. Audit Trail",
        ]
        elems = [Paragraph("Contents", styles["h1"]), _hr(styles)]
        for s in sections:
            elems.append(Paragraph(_safe(s), styles["toc"]))
        elems.append(PageBreak())
        return elems

    # ── Section 2: Executive Summary ─────────────────────────────────────────

    def _section_executive_summary(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("1. Executive Summary", styles)
        for line in report.executive_summary.split("\n"):
            elems.append(Paragraph(_safe(line) or " ", styles["body"]))
        return elems

    # ── Section 3: Scope ─────────────────────────────────────────────────────

    def _section_scope(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("2. Investigation Scope", styles)
        elems.append(Paragraph(_safe(report.scope) or "Not specified.", styles["body"]))
        return elems

    # ── Section 4: Methodology ───────────────────────────────────────────────

    def _section_methodology(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("4. Methodology", styles)
        elems.append(Paragraph(_safe(report.methodology), styles["body"]))
        return elems

    # ── Section 5: Data Sources ───────────────────────────────────────────────

    def _section_data_sources(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("3. Data Sources", styles)
        if not report.data_sources:
            elems.append(Paragraph("No data source information available.", styles["body_gray"]))
            return elems
        rows = [["Source", "Status", "Details"]]
        for ds in report.data_sources:
            status_color = VALIDATION_COLORS.get(ds.status, C_WHITE)
            rows.append([
                _safe(ds.source_name),
                Paragraph(f'<font color="#{status_color.hexval()[2:]}">{ds.status.value}</font>', styles["body"]),
                _safe(ds.reason or (f"{ds.row_count} rows" if ds.row_count else "OK")),
            ])
        t = _make_table(rows, col_widths=[5 * cm, 3 * cm, CONTENT_WIDTH - 8 * cm])
        elems.append(t)
        return elems

    # ── Section 6: Scenario ───────────────────────────────────────────────────

    def _section_scenario(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("5. Scenario Overview", styles)
        elems.append(Paragraph(f"Scenario ID: {_safe(report.scenario_id)}", styles["body"]))
        elems.append(Paragraph(f"Mode: {report.mode.value}", styles["body"]))
        elems.append(Paragraph(_safe(report.investigation_summary) or "No summary available.", styles["body"]))
        return elems

    # ── Section 7: Entities ───────────────────────────────────────────────────

    def _section_entities(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("6. Investigated Entities", styles)
        if not report.subjects:
            elems.append(Paragraph("No entities identified.", styles["body_gray"]))
            return elems
        rows = [["#", "Masked Account ID"]]
        for i, subj in enumerate(report.subjects, 1):
            rows.append([str(i), _safe(subj)])
        t = _make_table(rows, col_widths=[1.5 * cm, CONTENT_WIDTH - 1.5 * cm])
        elems.append(t)
        return elems

    # ── Section 8: Transaction Analysis ──────────────────────────────────────

    def _section_transaction_analysis(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("7. Transaction Analysis", styles)
        for line in report.transaction_analysis.split("\n"):
            elems.append(Paragraph(_safe(line) or " ", styles["body"]))
        return elems

    # ── Section 9: Chain Analysis ─────────────────────────────────────────────

    def _section_chain_analysis(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("8. Transaction Chain Analysis (Money Flow)", styles)
        
        chains = report.money_flow_chains
        if not chains:
            elems.append(Paragraph("No transaction chain data available.", styles["body_gray"]))
            return elems
            
        for cid_idx, chain in enumerate(chains[:5]):
            if isinstance(chain, dict) and "transactions" in chain:
                # Grouped chain format
                txns = chain["transactions"]
                cid = chain.get("chain_id", f"Chain {cid_idx+1}")
            else:
                # Flat list of txns (from fallback state)
                txns = [chain]
                cid = chain.get("chain_id", f"Chain {cid_idx+1}") if isinstance(chain, dict) else f"Chain {cid_idx+1}"

            elems.append(Paragraph(f"<b>CHAIN:</b> {_safe(cid)}", styles["body"]))
            
            rows = [["Hop", "From", "To", "Amount (INR)", "Flag"]]
            
            # Sort by hop_layer if available
            if isinstance(txns, list) and all(isinstance(t, dict) for t in txns):
                txns = sorted(txns, key=lambda t: t.get("hop_layer", 0))
                
            for i, t in enumerate(txns):
                if not isinstance(t, dict): continue
                hop = t.get("hop_layer", i)
                frm = t.get("from_account_id", "?")
                to  = t.get("to_account_id", "?")
                amt = t.get("amount_inr", 0)
                flag = "CASHOUT" if t.get("is_terminal_cashout") else "LAUNDERING" if t.get("is_laundering") else ""
                
                rows.append([
                    str(hop),
                    _safe(frm)[:12],
                    _safe(to)[:12],
                    f"₹{amt:,.0f}",
                    flag
                ])
                
            t = _make_table(rows, col_widths=[1.5 * cm, 3.5 * cm, 3.5 * cm, 3 * cm, 2.5 * cm])
            elems.append(t)
            elems.append(Spacer(1, 4 * mm))
            
        if len(chains) > 5:
            elems.append(Paragraph(f"... and {len(chains)-5} more chains omitted for brevity.", styles["body_gray"]))

        return elems

    # ── Section 10: Geographic ────────────────────────────────────────────────

    def _section_geographic(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("9. Geographic Analysis", styles)
        if getattr(report, "atm_analysis_status", "") == "BLOCKED":
            elems.append(Paragraph("⛔ GEOGRAPHIC DATA BLOCKED: Master database corruption prevents reading ATM tables.", styles["blocked"]))
        elems.append(Paragraph(_safe(report.geographic_analysis) or "No geographic data.", styles["body"]))
        return elems

    # ── Section 11: Indicators ────────────────────────────────────────────────

    def _section_indicators(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("10. Cybercrime Indicators", styles)
        if not report.indicators:
            elems.append(Paragraph("No indicators triggered.", styles["body_gray"]))
            return elems
        rows = [["Indicator", "Threshold", "Observed", "Conf."]]
        for ind in report.indicators:
            rows.append([
                _safe(ind.get("name", "?")),
                _safe(str(ind.get("threshold", ""))[:40]),
                _safe(str(ind.get("observed_value", ""))[:30]),
                f"{ind.get('confidence', 0):.2f}",
            ])
        t = _make_table(rows, col_widths=[5 * cm, 5 * cm, 4 * cm, 2 * cm])
        elems.append(t)
        return elems

    # ── Section 12: Risk Assessment ───────────────────────────────────────────

    def _section_risk_assessment(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("11. Risk Assessment", styles)
        ra = report.risk_assessment
        if not ra:
            elems.append(Paragraph("No risk assessment available.", styles["body_gray"]))
            return elems
        score   = ra.get("risk_score", 0)
        level   = ra.get("risk_level", "LOW")
        conf    = ra.get("confidence", 0)
        contra  = ra.get("contradictory_evidence", False)
        color   = SEVERITY_COLORS.get(level, C_WHITE)

        rows = [
            ["Risk Score",             f"{score:.1f} / 100"],
            ["Risk Level",             level],
            ["Confidence",             f"{conf:.2f}"],
            ["Contradictory Evidence", "YES — see Methodology" if contra else "No"],
        ]
        t = Table([[Paragraph(k, styles["label"]), Paragraph(_safe(v), styles["body"])] for k, v in rows],
                  colWidths=[6 * cm, CONTENT_WIDTH - 6 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_BG),
            ("GRID",       (0, 0), (-1, -1), 0.25, C_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 4 * mm))
        elems.append(Paragraph(
            "Note: Risk thresholds are PROJECT HEURISTICs and have not been statistically validated. "
            "This score does not constitute proof of criminal activity.",
            styles["body_gray"]
        ))
        if contra:
            elems.append(Paragraph(
                "CONTRADICTORY EVIDENCE DETECTED: Profile flagged as mule but transaction patterns "
                "do not exhibit laundering indicators. Score adjusted down by 15 pts; confidence down 0.20.",
                styles["warning"]
            ))
        return elems

    # ── Section 13: Findings ─────────────────────────────────────────────────

    def _section_findings(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("12. Findings", styles)
        if not report.findings:
            elems.append(Paragraph("No findings generated for this investigation.", styles["body_gray"]))
            return elems

        for i, finding in enumerate(report.findings, 1):
            sev_color = SEVERITY_COLORS.get(finding.severity, C_WHITE)
            block = [
                Paragraph(f"Finding {i}: {_safe(finding.title)}", styles["h2"]),
                _hr(styles),
            ]
            meta = [
                ["Severity",    finding.severity],
                ["Risk Score",  f"{finding.risk_score:.1f}/100"],
                ["Confidence",  f"{finding.confidence:.2f}"],
                ["Status",      finding.status.value],
                ["Category",    _safe(finding.category)],
            ]
            mt = Table([[Paragraph(k, styles["label"]), Paragraph(_safe(v), styles["body"])] for k, v in meta],
                       colWidths=[4 * cm, CONTENT_WIDTH - 4 * cm])
            mt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), C_BG),
                ("GRID",       (0, 0), (-1, -1), 0.25, C_GRAY),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            block.append(mt)
            block.append(Spacer(1, 3 * mm))

            # Indicators
            if finding.indicator_ids:
                block.append(Paragraph("Indicators:", styles["label"]))
                for iid in finding.indicator_ids:
                    block.append(Paragraph(f"  • {_safe(iid)}", styles["body"]))

            # Evidence references
            if finding.evidence_ids:
                block.append(Paragraph("Evidence:", styles["label"]))
                for eid in finding.evidence_ids[:10]:
                    block.append(Paragraph(f"  • {_safe(eid[:16])}…", styles["body"]))
                if len(finding.evidence_ids) > 10:
                    block.append(Paragraph(f"  … and {len(finding.evidence_ids)-10} more", styles["body_gray"]))

            # Description (prose explanation)
            block.append(Paragraph("Explanation:", styles["label"]))
            for line in (finding.description or "").split("\n")[:15]:
                block.append(Paragraph(_safe(line) or " ", styles["body"]))

            block.append(Spacer(1, 4 * mm))
            elems.append(KeepTogether(block[:8]))  # keep first chunk together
            elems += block[8:]

        return elems

    # ── Section 14: Evidence ──────────────────────────────────────────────────

    def _section_evidence(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("13. Evidence & Provenance", styles)
        if not report.evidence:
            elems.append(Paragraph("No evidence collected.", styles["body_gray"]))
            return elems

        elems.append(Paragraph(
            "Evidence items are classified as OBSERVED (direct field read), DERIVED (computed), "
            "INFERRED (logical), PREDICTED (forward), or SYNTHETIC (test fixture). "
            "INFERRED and PREDICTED items are never presented as OBSERVED.",
            styles["body_gray"]
        ))
        elems.append(Spacer(1, 3 * mm))

        rows = [["ID", "Source", "Field", "Value", "Class", "Conf."]]
        for ev in report.evidence:
            rows.append([
                _safe(ev.get("id", ""))[:12],
                _safe(ev.get("source", ""))[:20],
                _safe(ev.get("field", ""))[:20],
                _safe(ev.get("value", ""))[:25],
                _safe(ev.get("class", ""))[:12],
                _safe(ev.get("confidence", "")),
            ])
        t = _make_table(
            rows,
            col_widths=[2.5 * cm, 3.5 * cm, 3 * cm, 3.5 * cm, 2.5 * cm, 1.5 * cm],
        )
        elems.append(t)
        return elems

    # ── Section 15: Recommendations ───────────────────────────────────────────

    def _section_recommendations(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("14. Recommendations", styles)
        elems.append(Paragraph(
            "All items below are RECOMMENDATIONS. They are not confirmed facts or enforcement orders. "
            "Manual expert review is required before acting.",
            styles["warning"]
        ))
        elems.append(Spacer(1, 3 * mm))
        for rec in report.recommendations:
            block = [
                Paragraph(f"[{rec.get('label','RECOMMENDATION')}] [{rec.get('priority','?')}] {rec.get('code','')}", styles["label"]),
                Paragraph(_safe(rec.get("action", "")), styles["body"]),
                Paragraph(f"Rationale: {_safe(rec.get('rationale', ''))}", styles["body_gray"]),
                Spacer(1, 3 * mm),
            ]
            elems.append(KeepTogether(block))
        return elems

    # ── Section 16: Limitations ───────────────────────────────────────────────

    def _section_limitations(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("15. Limitations", styles)
        for line in report.limitations.split("\n"):
            elems.append(Paragraph(_safe(line) or " ", styles["body"]))
        return elems

    # ── Section 17: Validation Status ────────────────────────────────────────

    def _section_validation_status(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("16. Validation Status", styles)
        elems.append(Paragraph(
            "This section distinguishes IMPLEMENTATION STATUS (unit tests) "
            "from REAL DATA VALIDATION STATUS (master database access).",
            styles["body_gray"]
        ))
        elems.append(Spacer(1, 3 * mm))
        rows = [["Component", "Status"]]
        for component, status in report.validation_status.items():
            color = VALIDATION_COLORS.get(status, C_WHITE)
            rows.append([
                _safe(component).replace("_", " ").title(),
                Paragraph(
                    f'<font color="#{color.hexval()[2:]}">{status.value}</font>',
                    styles["body"]
                ),
            ])
        t = _make_table(rows, col_widths=[8 * cm, CONTENT_WIDTH - 8 * cm])
        elems.append(t)
        elems.append(Spacer(1, 3 * mm))

        if report.validation_status.get("master_db") == ValidationStatus.FAIL:
            elems.append(Paragraph(
                "Master Database Health: FAIL — B-tree index corruption on idx_atms_geo "
                "(root page 29). profiles and atms tables inaccessible.",
                styles["blocked"]
            ))
        if report.validation_status.get("real_e2e") == ValidationStatus.BLOCKED:
            elems.append(Paragraph(
                "Real Scenario E2E: BLOCKED — Required source tables (profiles, atms) "
                "are inaccessible due to database corruption. "
                "Do not interpret this as evidence of absence of risk.",
                styles["blocked"]
            ))
        return elems

    # ── Section 18: Audit Trail ───────────────────────────────────────────────

    def _section_audit_trail(self, report: SecurityAssessmentReport, styles: dict) -> list:
        elems = _section_header("17. Audit Trail", styles)
        if not report.audit_summary:
            elems.append(Paragraph("No audit events recorded.", styles["body_gray"]))
            return elems
        rows = [["Timestamp", "Event Type", "Component", "Status"]]
        for ev in report.audit_summary:
            rows.append([
                _safe(ev.timestamp[:19]),
                _safe(ev.event_type),
                _safe(ev.component),
                _safe(ev.status),
            ])
        t = _make_table(
            rows,
            col_widths=[4.5 * cm, 4.5 * cm, 4 * cm, 3.5 * cm],
        )
        elems.append(t)
        elems.append(Spacer(1, 3 * mm))
        elems.append(Paragraph(
            "Note: The audit trail records operational decisions only. "
            "No chain-of-thought, API keys, credentials, or raw PII are stored.",
            styles["body_gray"]
        ))
        return elems
