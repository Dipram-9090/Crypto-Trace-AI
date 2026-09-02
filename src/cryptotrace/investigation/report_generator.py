"""
Forensic Intelligence Report Generation Engine.
Produces professional, auditable investigation reports in Markdown and JSON formats.
Strictly distinguishes Observed Facts, Heuristic Inferences, ML Anomalies, and Investigator Notes.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.cryptotrace.blockchain.models import InvestigationCase
from src.cryptotrace.blockchain.analysis.engine import BlockchainAnalysisEngine
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class ForensicReportGenerator:
    """Generates structured forensic intelligence reports with methodology and evidence taxonomy."""

    def __init__(self, analysis_engine: Optional[BlockchainAnalysisEngine] = None):
        self.analysis_engine = analysis_engine

    def generate_markdown_report(
        self,
        case: InvestigationCase,
        output_filepath: Optional[str] = None,
    ) -> str:
        """
        Generate a comprehensive, courtroom/audit-grade forensic report in Markdown.
        """
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        md_lines = [
            f"# CRYPTOTRACE AI — BLOCKCHAIN FORENSIC INTELLIGENCE REPORT",
            f"**Case Reference**: `{case.case_id}` | **Status**: `{case.status}` | **Generated**: {now_str}",
            "",
            "---",
            "",
            "## 1. EXECUTIVE SUMMARY & INVESTIGATION OBJECTIVE",
            f"**Case Title**: {case.title}",
            f"**Objective**: {case.description or 'Offline Bitcoin transaction forensics, entity clustering, and risk scoring analysis.'}",
            "",
            f"- **Target Addresses Under Review**: {len(case.selected_addresses)}",
            f"- **Target Transactions Under Review**: {len(case.selected_transactions)}",
            f"- **Associated Heuristic Clusters**: {len(case.selected_clusters)}",
            "",
            "---",
            "",
            "## 2. FORENSIC EVIDENCE TAXONOMY & METHODOLOGY",
            "In adherence to forensic intelligence standards, findings are categorized into four distinct evidential classes:",
            "",
            "1. **OBSERVED FACTS**: Cryptographically verified immutable on-chain data points (txids, block heights, timestamps, output values, scriptPubKey opcodes).",
            "2. **HEURISTIC INFERENCES**: Probabilistic behavioral linkages (e.g., Common-Input Ownership Clustering, Peel Chain identification, Change Address probability).",
            "3. **ML ANOMALY SIGNALS**: Statistical deviations flagged by unsupervised machine learning models (Isolation Forest).",
            "4. **INVESTIGATOR NOTES**: Qualitative annotations provided by human analysts.",
            "",
            "---",
            "",
            "## 3. IDENTIFIED SUSPICIOUS PATTERNS & RISK SIGNALS",
        ]

        # Populate transaction evidence if engine available
        if self.analysis_engine:
            md_lines.append("### Transaction Risk Breakdown")
            md_lines.append("| Transaction ID | Value (BTC) | Risk Score | Tier | Detected Heuristic Signals |")
            md_lines.append("|---|---|---|---|---|")

            for txid in case.selected_transactions:
                tx = self.analysis_engine.transactions.get(txid)
                risk = self.analysis_engine.tx_risk_evaluations.get(txid)
                if tx and risk:
                    signal_str = ", ".join([s.type for s in risk.signals]) or "None"
                    md_lines.append(
                        f"| `{tx.txid[:16]}...` | {tx.total_output_amount:.4f} | **{risk.risk_score:.1f}** | `{risk.risk_level}` | {signal_str} |"
                    )

            md_lines.append("")
            md_lines.append("### Address Intelligence & Cluster Profiles")
            md_lines.append("| Address | Encoding | Active Balance (BTC) | Tx Count | Cluster ID | Risk Tier |")
            md_lines.append("|---|---|---|---|---|---|")

            for addr in case.selected_addresses:
                prof = self.analysis_engine.address_profiles.get(addr)
                if prof:
                    md_lines.append(
                        f"| `{addr}` | {prof.encoding_type} | {prof.balance:.4f} | {prof.transaction_count} | `{prof.cluster_id or 'N/A'}` | `{prof.risk_level}` |"
                    )
        else:
            md_lines.append("*Detailed engine analysis was not attached during generation.*")

        # Timeline Section
        md_lines.extend([
            "",
            "---",
            "",
            "## 4. CHRONOLOGICAL FORENSIC TIMELINE",
        ])

        if self.analysis_engine and case.selected_addresses:
            for addr in case.selected_addresses[:3]:
                md_lines.append(f"#### Activity Timeline for Address `{addr}`")
                timeline = self.analysis_engine.generate_timeline(addr)
                if timeline:
                    for ev in timeline[:10]:
                        md_lines.append(f"- **{ev['timestamp']}** | `{ev['event_type']}` | {ev['description']} (Risk: `{ev['risk_level']}`)")
                else:
                    md_lines.append("- No recorded transactions in dataset.")
                md_lines.append("")

        # Investigator Notes
        md_lines.extend([
            "---",
            "",
            "## 5. INVESTIGATOR NOTES & EVIDENCE LOG",
        ])

        if case.notes:
            for note in case.notes:
                md_lines.append(f"- **[{note.get('timestamp')}] {note.get('author')}**: {note.get('text')}")
        else:
            md_lines.append("*No investigator notes recorded for this case.*")

        # Mandatory Disclaimers
        md_lines.extend([
            "",
            "---",
            "",
            "## 6. MANDATORY FORENSIC DISCLAIMERS & LIMITATIONS",
            "> **LEGAL & ANALYTICAL NOTICE**:",
            "> 1. **Pseudonymity**: Bitcoin addresses are cryptographic pseudonyms. An address does not inherently prove physical real-world identity or legal ownership.",
            "> 2. **Heuristic Nature**: Address clustering relies on the Common-Input Ownership heuristic and change detection algorithms. These are probabilistic models and do not constitute indisputable proof of common ownership.",
            "> 3. **Analytical Indicators**: Risk scores, mixing patterns, and velocity indicators represent analytical anomaly signals, not definitive legal determinations of illicit conduct.",
            "> 4. **Offline Integrity**: All computations were conducted strictly offline without external web scraping or third-party reputation trackers.",
            "",
            "---",
            f"*Report generated by CryptoTrace AI Offline Forensics Engine v2.0.*",
        ])

        report_content = "\n".join(md_lines)

        if output_filepath:
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"Report exported to {output_filepath}")

        return report_content
