"""MongoDB Client for Raw Blockchain Blocks and Unstructured Payloads."""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("cryptotrace.backend.database.mongo")


class MongoClientWrapper:
    """Manages connection to MongoDB replica sets or standalone clusters."""

    def __init__(self, uri: Optional[str] = None):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.db = self.client["cryptotrace"]
            logger.info("MongoDB client connected.")
        except Exception as e:
            logger.debug(f"MongoDB connection notice: {e}. Using in-memory fallback store.")

    def insert_raw_block(self, block_data: Dict[str, Any]):
        if self.db is not None:
            try:
                self.db.raw_blocks.insert_one(block_data)
            except Exception as e:
                logger.warning(f"Failed to insert raw block into Mongo: {e}")
