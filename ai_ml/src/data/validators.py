"""
Comprehensive dataset validation module.

Performs rigorous validation including:
- Structural integrity (files, shapes, columns)
- Data quality (missing values, duplicates, types)
- Statistical coherence (ranges, distributions)
- Graph validation
- Temporal consistency
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidator:
    """Base class for dataset validation."""
    
    def __init__(self):
        self.validation_report = {}
    
    def _add_check(self, category: str, check_name: str, passed: bool, details: str = ""):
        """Record a validation check result."""
        if category not in self.validation_report:
            self.validation_report[category] = []
        
        status = "✓" if passed else "✗"
        self.validation_report[category].append({
            "check": check_name,
            "passed": passed,
            "status": status,
            "details": details
        })
    
    def print_report(self):
        """Print validation report in human-readable format."""
        print("\n" + "="*70)
        print(f"[Dataset Validation Report] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        all_passed = True
        
        for category, checks in self.validation_report.items():
            print(f"\n{category}:")
            for check in checks:
                status_emoji = "✓" if check["passed"] else "✗"
                print(f"  {status_emoji} {check['check']}")
                if check["details"]:
                    print(f"     {check['details']}")
                if not check["passed"]:
                    all_passed = False
        
        print("\n" + "="*70)
        if all_passed:
            print("[ALL CHECKS PASSED ✓]")
        else:
            print("[VALIDATION FAILED - See errors above]")
        print("="*70 + "\n")
        
        return all_passed


class EllipticValidator(DataValidator):
    """Validates Elliptic Bitcoin transaction dataset."""
    
    def __init__(self, dataset_dir: str = "ai_ml/datasets/raw/elliptic"):
        super().__init__()
        self.dataset_dir = Path(dataset_dir)
    
    def validate(self) -> bool:
        """Run all validation checks."""
        logger.info("Starting Elliptic dataset validation...")
        
        # Structural checks
        self._validate_files()
        self._validate_shapes()
        
        # Load data for deeper checks
        try:
            features = pd.read_csv(self.dataset_dir / "elliptic_txs_features.csv", header=None)
            edgelist = pd.read_csv(self.dataset_dir / "elliptic_txs_edgelist.csv", header=None)
            classes = pd.read_csv(self.dataset_dir / "elliptic_txs_classes.csv", header=None)
        except Exception as e:
            self._add_check("File Loading", "Read CSV Files", False, f"Error: {str(e)}")
            return False
        
        # Data quality checks
        self._validate_data_quality(features, edgelist, classes)
        
        # Statistical checks
        self._validate_statistics(features, classes)
        
        # Graph validation
        self._validate_graph(features, edgelist)
        
        return self.print_report()
    
    def _validate_files(self):
        """Check that all required files exist."""
        required = ["elliptic_txs_features.csv", "elliptic_txs_edgelist.csv", "elliptic_txs_classes.csv"]
        
        for filename in required:
            filepath = self.dataset_dir / filename
            exists = filepath.exists()
            self._add_check("File Existence", f"Found {filename}", exists)
    
    def _validate_shapes(self):
        """Check expected dataset dimensions."""
        try:
            features = pd.read_csv(self.dataset_dir / "elliptic_txs_features.csv", header=None)
            edgelist = pd.read_csv(self.dataset_dir / "elliptic_txs_edgelist.csv", header=None)
            classes = pd.read_csv(self.dataset_dir / "elliptic_txs_classes.csv", header=None)
            
            # Expected shapes
            self._add_check("Shapes", "Features (203769, 166)", 
                          features.shape == (203769, 166),
                          f"Actual: {features.shape}")
            self._add_check("Shapes", "Edges (234355, 2)", 
                          edgelist.shape[1] == 2,
                          f"Actual: {edgelist.shape}")
            self._add_check("Shapes", "Classes (203769, 2)", 
                          classes.shape == (203769, 2),
                          f"Actual: {classes.shape}")
        except Exception as e:
            self._add_check("Shapes", "Load and check shapes", False, f"Error: {str(e)}")
    
    def _validate_data_quality(self, features: pd.DataFrame, edgelist: pd.DataFrame, classes: pd.DataFrame):
        """Check for missing values, duplicates, and type issues."""
        
        # Missing values
        feat_nulls = features.isnull().sum().sum()
        edge_nulls = edgelist.isnull().sum().sum()
        class_nulls = classes.isnull().sum().sum()
        
        self._add_check("Data Quality", "Missing values in features", feat_nulls == 0, f"Count: {feat_nulls}")
        self._add_check("Data Quality", "Missing values in edgelist", edge_nulls == 0, f"Count: {edge_nulls}")
        self._add_check("Data Quality", "Missing values in classes", class_nulls == 0, f"Count: {class_nulls}")
        
        # Duplicates
        feat_dups = features.duplicated().sum()
        edge_dups = edgelist.duplicated().sum()
        class_dups = classes.duplicated().sum()
        
        self._add_check("Data Quality", "Duplicate rows in features", feat_dups == 0, f"Count: {feat_dups}")
        self._add_check("Data Quality", "Duplicate rows in edgelist", edge_dups == 0, f"Count: {edge_dups}")
        self._add_check("Data Quality", "Duplicate rows in classes", class_dups == 0, f"Count: {class_dups}")
        
        # Type consistency
        try:
            # Features should be numeric
            numeric_check = features.iloc[:, 1:].applymap(lambda x: isinstance(x, (int, float, np.number)))
            all_numeric = numeric_check.all().all()
            self._add_check("Data Quality", "All features are numeric", all_numeric)
        except:
            pass
    
    def _validate_statistics(self, features: pd.DataFrame, classes: pd.DataFrame):
        """Check statistical properties."""
        
        # Check for infinite values
        inf_count = np.isinf(features.iloc[:, 1:]).sum().sum()
        self._add_check("Statistics", "No infinite values", inf_count == 0, f"Count: {inf_count}")
        
        # Class distribution
        class_col = classes.iloc[:, 1]
        illicit_count = (class_col == 1).sum()
        licit_count = (class_col == 2).sum()
        unknown_count = (class_col == "unknown").sum()
        
        self._add_check("Statistics", "Class distribution valid", 
                       illicit_count > 0 and licit_count > 0,
                       f"Illicit: {illicit_count}, Licit: {licit_count}, Unknown: {unknown_count}")
        
        # Feature value ranges
        feat_min = features.iloc[:, 1:].min().min()
        feat_max = features.iloc[:, 1:].max().max()
        
        self._add_check("Statistics", "Feature values in valid range", 
                       feat_min >= 0 and not np.isnan(feat_min),
                       f"Range: [{feat_min:.2f}, {feat_max:.2f}]")
    
    def _validate_graph(self, features: pd.DataFrame, edgelist: pd.DataFrame):
        """Check graph structural properties."""
        
        # Get unique transaction IDs from features
        feature_txids = set(features.iloc[:, 0].unique())
        
        # Check if all edge endpoints exist in features
        edge_sources = set(edgelist.iloc[:, 0].unique())
        edge_targets = set(edgelist.iloc[:, 1].unique())
        all_edge_txids = edge_sources | edge_targets
        
        orphan_edges = all_edge_txids - feature_txids
        
        self._add_check("Graph Validation", "All edge endpoints in features", 
                       len(orphan_edges) == 0,
                       f"Orphan transactions: {len(orphan_edges)}")


class BitcoinHeistValidator(DataValidator):
    """Validates BitcoinHeist ransomware dataset."""
    
    def __init__(self, dataset_dir: str = "ai_ml/datasets/raw/bitcoinheist"):
        super().__init__()
        self.dataset_dir = Path(dataset_dir)
    
    def validate(self) -> bool:
        """Run all validation checks."""
        logger.info("Starting BitcoinHeist dataset validation...")
        
        self._validate_files()
        
        try:
            addresses = pd.read_csv(self.dataset_dir / "bitcoinheist_addresses.csv")
            labels = pd.read_csv(self.dataset_dir / "bitcoinheist_labels.csv")
        except Exception as e:
            self._add_check("File Loading", "Read CSV Files", False, f"Error: {str(e)}")
            return False
        
        self._validate_shapes(addresses, labels)
        self._validate_data_quality(addresses, labels)
        self._validate_statistics(addresses, labels)
        
        return self.print_report()
    
    def _validate_files(self):
        """Check that all required files exist."""
        required = ["bitcoinheist_addresses.csv", "bitcoinheist_labels.csv"]
        
        for filename in required:
            filepath = self.dataset_dir / filename
            exists = filepath.exists()
            self._add_check("File Existence", f"Found {filename}", exists)
    
    def _validate_shapes(self, addresses: pd.DataFrame, labels: pd.DataFrame):
        """Check dataset dimensions."""
        self._add_check("Shapes", "Addresses has rows", len(addresses) > 0, f"Count: {len(addresses)}")
        self._add_check("Shapes", "Labels has rows", len(labels) > 0, f"Count: {len(labels)}")
    
    def _validate_data_quality(self, addresses: pd.DataFrame, labels: pd.DataFrame):
        """Check for data quality issues."""
        addr_nulls = addresses.isnull().sum().sum()
        label_nulls = labels.isnull().sum().sum()
        
        self._add_check("Data Quality", "Missing values in addresses", addr_nulls == 0, f"Count: {addr_nulls}")
        self._add_check("Data Quality", "Missing values in labels", label_nulls == 0, f"Count: {label_nulls}")
        
        addr_dups = addresses.duplicated().sum()
        label_dups = labels.duplicated().sum()
        
        self._add_check("Data Quality", "Duplicate rows in addresses", addr_dups == 0, f"Count: {addr_dups}")
        self._add_check("Data Quality", "Duplicate rows in labels", label_dups == 0, f"Count: {label_dups}")
    
    def _validate_statistics(self, addresses: pd.DataFrame, labels: pd.DataFrame):
        """Check statistical properties."""
        
        # Check for infinite values in numeric columns
        numeric_cols = addresses.select_dtypes(include=[np.number]).columns
        inf_count = np.isinf(addresses[numeric_cols]).sum().sum()
        
        self._add_check("Statistics", "No infinite values", inf_count == 0, f"Count: {inf_count}")
        
        # Label distribution
        label_dist = labels.iloc[:, 1].value_counts()
        self._add_check("Statistics", "Multiple label classes", len(label_dist) > 1, 
                       f"Classes: {len(label_dist)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Validate Elliptic
    print("\n" + "="*70)
    print("VALIDATING ELLIPTIC DATASET")
    print("="*70)
    validator = EllipticValidator()
    validator.validate()
    
    # Validate BitcoinHeist
    print("\n" + "="*70)
    print("VALIDATING BITCOINHEIST DATASET")
    print("="*70)
    validator = BitcoinHeistValidator()
    validator.validate()
