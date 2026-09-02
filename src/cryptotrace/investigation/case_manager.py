"""
Investigation Case Management Engine.
Maintains forensic dossiers, evidence chains (addresses, transactions, clusters),
investigator notes, and case lifecycle status (OPEN, IN_PROGRESS, CLOSED, ESCALATED).
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.cryptotrace.blockchain.models import InvestigationCase
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class CaseManager:
    """Manages active and historical forensic investigation cases."""

    def __init__(self, storage_dir: str = "reports/cases"):
        self.storage_dir = storage_dir
        self.cases: Dict[str, InvestigationCase] = {}
        os.makedirs(self.storage_dir, exist_ok=True)
        self._load_existing_cases()

    def _load_existing_cases(self):
        """Load persisted case files if available."""
        if not os.path.exists(self.storage_dir):
            return
        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(self.storage_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        case = InvestigationCase(
                            case_id=data["case_id"],
                            title=data["title"],
                            description=data.get("description", ""),
                            status=data.get("status", "OPEN"),
                            created_at=data.get("created_at", datetime.utcnow().isoformat()),
                            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
                            selected_addresses=data.get("selected_addresses", []),
                            selected_transactions=data.get("selected_transactions", []),
                            selected_clusters=data.get("selected_clusters", []),
                            notes=data.get("notes", []),
                            risk_summary=data.get("risk_summary", {}),
                        )
                        self.cases[case.case_id] = case
                except Exception as e:
                    logger.warning(f"Failed to load case {fname}: {e}")

    def create_case(
        self,
        title: str,
        description: str = "",
        case_id: Optional[str] = None,
    ) -> InvestigationCase:
        """Create and persist a new investigation case."""
        cid = case_id or f"CASE_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        case = InvestigationCase(
            case_id=cid,
            title=title,
            description=description,
            status="OPEN",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        self.cases[cid] = case
        self.save_case(cid)
        return case

    def add_evidence_address(self, case_id: str, address: str) -> bool:
        if case_id not in self.cases:
            return False
        case = self.cases[case_id]
        if address not in case.selected_addresses:
            case.selected_addresses.append(address)
            case.updated_at = datetime.utcnow().isoformat()
            self.save_case(case_id)
        return True

    def add_evidence_transaction(self, case_id: str, txid: str) -> bool:
        if case_id not in self.cases:
            return False
        case = self.cases[case_id]
        if txid not in case.selected_transactions:
            case.selected_transactions.append(txid)
            case.updated_at = datetime.utcnow().isoformat()
            self.save_case(case_id)
        return True

    def add_evidence_cluster(self, case_id: str, cluster_id: str) -> bool:
        if case_id not in self.cases:
            return False
        case = self.cases[case_id]
        if cluster_id not in case.selected_clusters:
            case.selected_clusters.append(cluster_id)
            case.updated_at = datetime.utcnow().isoformat()
            self.save_case(case_id)
        return True

    def add_note(self, case_id: str, author: str, note_text: str) -> bool:
        if case_id not in self.cases:
            return False
        case = self.cases[case_id]
        case.notes.append({
            "author": author,
            "text": note_text,
            "timestamp": datetime.utcnow().isoformat(),
        })
        case.updated_at = datetime.utcnow().isoformat()
        self.save_case(case_id)
        return True

    def update_status(self, case_id: str, new_status: str) -> bool:
        if case_id not in self.cases:
            return False
        case = self.cases[case_id]
        case.status = new_status
        case.updated_at = datetime.utcnow().isoformat()
        self.save_case(case_id)
        return True

    def get_case(self, case_id: str) -> Optional[InvestigationCase]:
        return self.cases.get(case_id)

    def list_cases(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.cases.values()]

    def save_case(self, case_id: str):
        if case_id not in self.cases:
            return
        fpath = os.path.join(self.storage_dir, f"{case_id}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(self.cases[case_id].to_dict(), f, indent=2)
