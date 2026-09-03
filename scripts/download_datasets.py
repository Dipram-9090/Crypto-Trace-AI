"""
Dataset Download Script

Automated download of Elliptic and BitcoinHeist datasets.

Requirements:
- Kaggle CLI configured (for Elliptic dataset)
- Download credentials configured
"""

import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path
from urllib.request import urlretrieve

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DatasetDownloader:
    """Handles dataset downloads."""
    
    DATASETS = {
        "elliptic": {
            "description": "Elliptic Bitcoin Transaction Dataset (Kaggle)",
            "kaggle_dataset": "ellipticco/elliptic-data-set",
            "extract": True,
            "files": [
                "elliptic_txs_features.csv",
                "elliptic_txs_edgelist.csv",
                "elliptic_txs_classes.csv"
            ]
        },
        "bitcoinheist": {
            "description": "BitcoinHeist Ransomware Dataset (UCI Archive)",
            "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/bitcoin/",
            "extract": False,
            "files": [
                "bitcoinheist_addresses.csv",
                "bitcoinheist_labels.csv"
            ]
        }
    }
    
    def __init__(self, base_dir: str = "ai_ml/datasets/raw"):
        """
        Initialize downloader.
        
        Args:
            base_dir: Base directory for storing datasets
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def download_elliptic(self) -> bool:
        """
        Download Elliptic dataset using Kaggle CLI.
        
        Returns:
            True if successful
        """
        logger.info("=" * 70)
        logger.info("DOWNLOADING ELLIPTIC DATASET")
        logger.info("=" * 70)
        
        dataset_dir = self.base_dir / "elliptic"
        dataset_dir.mkdir(exist_ok=True)
        
        # Check if Kaggle CLI is configured
        kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
        if not kaggle_config.exists():
            logger.error(
                "Kaggle CLI not configured!\n"
                "Please follow these steps:\n"
                "1. Visit: https://www.kaggle.com/settings/account\n"
                "2. Click 'Create New API Token'\n"
                "3. Download kaggle.json\n"
                "4. Run: mkdir ~/.kaggle && cp kaggle.json ~/.kaggle/\n"
                "5. Run: chmod 600 ~/.kaggle/kaggle.json"
            )
            return False
        
        try:
            # Download using Kaggle CLI
            cmd = [
                "kaggle", "datasets", "download",
                "-d", self.DATASETS["elliptic"]["kaggle_dataset"],
                "-p", str(dataset_dir)
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Download failed: {result.stderr}")
                return False
            
            # Extract zip file
            import zipfile
            zip_files = list(dataset_dir.glob("*.zip"))
            if zip_files:
                logger.info(f"Extracting {zip_files[0]}")
                with zipfile.ZipFile(zip_files[0], 'r') as z:
                    z.extractall(dataset_dir)
                zip_files[0].unlink()
            
            # Verify files
            return self._verify_elliptic(dataset_dir)
        
        except Exception as e:
            logger.error(f"Error downloading Elliptic: {str(e)}")
            return False
    
    def download_bitcoinheist(self) -> bool:
        """
        Download BitcoinHeist dataset from UCI Archive.
        
        Returns:
            True if successful
        """
        logger.info("=" * 70)
        logger.info("DOWNLOADING BITCOINHEIST DATASET")
        logger.info("=" * 70)
        
        dataset_dir = self.base_dir / "bitcoinheist"
        dataset_dir.mkdir(exist_ok=True)
        
        base_url = self.DATASETS["bitcoinheist"]["url"]
        files = self.DATASETS["bitcoinheist"]["files"]
        
        try:
            for filename in files:
                file_url = f"{base_url}{filename}"
                file_path = dataset_dir / filename
                
                if file_path.exists():
                    logger.info(f"File already exists: {file_path}")
                    continue
                
                logger.info(f"Downloading: {file_url}")
                urlretrieve(file_url, file_path)
                logger.info(f"Saved to: {file_path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error downloading BitcoinHeist: {str(e)}")
            return False
    
    def _verify_elliptic(self, dataset_dir: Path) -> bool:
        """Verify Elliptic dataset files."""
        required_files = self.DATASETS["elliptic"]["files"]
        
        logger.info("Verifying Elliptic dataset files...")
        all_exist = True
        for filename in required_files:
            filepath = dataset_dir / filename
            if filepath.exists():
                size_mb = filepath.stat().st_size / (1024 * 1024)
                logger.info(f"✓ Found {filename} ({size_mb:.2f} MB)")
            else:
                logger.error(f"✗ Missing {filename}")
                all_exist = False
        
        return all_exist
    
    def _verify_bitcoinheist(self, dataset_dir: Path) -> bool:
        """Verify BitcoinHeist dataset files."""
        required_files = self.DATASETS["bitcoinheist"]["files"]
        
        logger.info("Verifying BitcoinHeist dataset files...")
        all_exist = True
        for filename in required_files:
            filepath = dataset_dir / filename
            if filepath.exists():
                size_mb = filepath.stat().st_size / (1024 * 1024)
                logger.info(f"✓ Found {filename} ({size_mb:.2f} MB)")
            else:
                logger.error(f"✗ Missing {filename}")
                all_exist = False
        
        return all_exist
    
    def download_all(self) -> bool:
        """Download all datasets."""
        logger.info("\n" + "=" * 70)
        logger.info("DOWNLOADING ALL DATASETS")
        logger.info("=" * 70 + "\n")
        
        results = {
            "elliptic": self.download_elliptic(),
            "bitcoinheist": self.download_bitcoinheist()
        }
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("=" * 70)
        
        for dataset_name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{dataset_name}: {status}")
        
        return all(results.values())


def main():
    parser = argparse.ArgumentParser(
        description="Download Elliptic and BitcoinHeist datasets"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["elliptic", "bitcoinheist", "all"],
        default="all",
        help="Dataset to download"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="ai_ml/datasets/raw",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    downloader = DatasetDownloader(args.output)
    
    if args.dataset == "all":
        success = downloader.download_all()
    elif args.dataset == "elliptic":
        success = downloader.download_elliptic()
    else:  # bitcoinheist
        success = downloader.download_bitcoinheist()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
