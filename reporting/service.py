"""
reporting/service.py — Clean service boundaries for Phase 6 API integration.

Provides:
  create_report(investigation_id, mode, agent_state) → SecurityAssessmentReport + PDF path
  get_report(report_id)                               → ReportRecord
  list_reports(investigation_id)                      → List[ReportRecord]
  get_findings(investigation_id)                      → List[FindingModel]
  get_evidence(investigation_id)                      → List[dict]
  get_investigation_status(investigation_id)          → dict

These service methods are thin orchestration wrappers around:
  ReportBuilder → PDFGenerator → ReportHasher → database.repository
"""

import uuid
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from database.repository import OperationalRepository
from reporting.builder import ReportBuilder
from reporting.hasher import ReportHasher
from reporting.models import (
    FindingModel, ReportMode, ReportRecord, SecurityAssessmentReport,
)
from reporting.pdf_generator import PDFGenerator


def _now() -> str:
    return datetime.now(UTC).isoformat()


class ReportService:
    """
    Orchestrates the full evidence → report → PDF → hash pipeline.
    Designed as a thin layer so Phase 6 can expose these as REST endpoints.
    """

    def __init__(self, output_dir: str = "reports"):
        self._pdf_gen = PDFGenerator(output_dir=output_dir)
        self._repo    = OperationalRepository()

    # ── Create ────────────────────────────────────────────────────────────────

    def create_report(
        self,
        investigation_id: str,
        scenario_id: str,
        mode: ReportMode,
        agent_state: Optional[Dict[str, Any]] = None,
        audit_events: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Runs the full pipeline:
          Build report → Generate PDF → Hash PDF → Persist metadata

        Returns a dict with:
          report_id, pdf_path, sha256, mode, investigation_id, generated_at
        """
        report = ReportBuilder.build(
            investigation_id=investigation_id,
            scenario_id=scenario_id,
            mode=mode,
            agent_state=agent_state,
            audit_events=audit_events,
        )

        # Generate PDF
        pdf_path = self._pdf_gen.generate(report)
        report.pdf_path = pdf_path

        # Hash the PDF
        sha256 = ReportHasher.hash_file(pdf_path)
        report.report_hash = sha256

        # Persist report record to operational DB
        record = ReportRecord(
            report_id=report.report_id,
            investigation_id=investigation_id,
            scenario_id=scenario_id,
            mode=mode.value,
            pdf_path=pdf_path,
            sha256=sha256,
            generated_at=report.generated_at,
        )
        self._repo.save_report(record)

        return {
            "report_id":        report.report_id,
            "pdf_path":         pdf_path,
            "sha256":           sha256,
            "mode":             mode.value,
            "investigation_id": investigation_id,
            "scenario_id":      scenario_id,
            "generated_at":     report.generated_at,
            "findings_count":   len(report.findings),
            "evidence_count":   len(report.evidence),
        }

    # ── Retrieve ──────────────────────────────────────────────────────────────

    def get_report(self, report_id: str) -> Optional[ReportRecord]:
        """Returns the stored ReportRecord metadata for a given report_id."""
        return self._repo.get_report_by_id(report_id)

    def list_reports(self, investigation_id: str) -> List[ReportRecord]:
        """Returns all report records for a given investigation."""
        return self._repo.list_reports_by_investigation(investigation_id)

    def get_findings(self, investigation_id: str) -> List[Dict]:
        """Returns finding records from the operational DB for a given investigation."""
        return self._repo.get_findings_by_investigation(investigation_id)

    def get_evidence(self, investigation_id: str) -> List[Dict]:
        """Returns evidence records from the operational DB for a given investigation."""
        return self._repo.get_evidence_by_investigation(investigation_id)

    def get_investigation_status(self, investigation_id: str) -> Dict[str, Any]:
        """Returns current investigation status from the operational DB."""
        return self._repo.get_investigation_status(investigation_id)

    # ── Verify ────────────────────────────────────────────────────────────────

    def verify_report(self, report_id: str) -> Dict[str, Any]:
        """
        Verifies the SHA-256 hash of a stored report PDF.
        Returns:
          {report_id, verified, expected_hash, actual_hash, pdf_path, status}
        """
        record = self.get_report(report_id)
        if not record:
            return {"report_id": report_id, "verified": False, "status": "REPORT_NOT_FOUND"}

        verified = ReportHasher.verify(record.pdf_path, record.sha256)
        actual   = ReportHasher.hash_file(record.pdf_path) if verified else "MISMATCH"
        is_pdf   = ReportHasher.is_valid_pdf(record.pdf_path)

        return {
            "report_id":     report_id,
            "pdf_path":      record.pdf_path,
            "expected_hash": record.sha256,
            "actual_hash":   actual if verified else ReportHasher.hash_file(record.pdf_path),
            "verified":      verified,
            "is_valid_pdf":  is_pdf,
            "status":        "VERIFIED" if verified else "HASH_MISMATCH",
        }
