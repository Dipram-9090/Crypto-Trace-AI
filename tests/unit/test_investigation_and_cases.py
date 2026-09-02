"""
Unit tests for investigation case management and forensic intelligence report generation.
"""

import os
import shutil
from src.cryptotrace.investigation.case_manager import CaseManager
from src.cryptotrace.investigation.report_generator import ForensicReportGenerator
from src.cryptotrace.blockchain.analysis.engine import BlockchainAnalysisEngine
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxInput, TxOutput


def test_case_management_and_reporting():
    test_dir = "reports/test_cases"
    os.makedirs(test_dir, exist_ok=True)

    cm = CaseManager(storage_dir=test_dir)
    case = cm.create_case("Operation CyberTrace Test", "Investigating suspicious fanout")
    
    assert case.status == "OPEN"
    cm.add_evidence_address(case.case_id, "1TestEvidenceAddr1111111111111")
    cm.add_evidence_transaction(case.case_id, "tx_evidence_0001")
    cm.add_note(case.case_id, "Analyst Smith", "Observed rapid movement through intermediary hop")

    updated_case = cm.get_case(case.case_id)
    assert len(updated_case.selected_addresses) == 1
    assert len(updated_case.selected_transactions) == 1
    assert len(updated_case.notes) == 1

    # Report Generator
    rg = ForensicReportGenerator()
    report_md = rg.generate_markdown_report(updated_case)
    assert "CRYPTOTRACE AI — BLOCKCHAIN FORENSIC INTELLIGENCE REPORT" in report_md
    assert "OBSERVED FACTS" in report_md
    assert "HEURISTIC INFERENCES" in report_md
    assert "MANDATORY FORENSIC DISCLAIMERS" in report_md

    # Clean up test dir
    shutil.rmtree(test_dir, ignore_errors=True)
