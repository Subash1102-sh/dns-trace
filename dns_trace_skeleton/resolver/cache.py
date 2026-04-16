"""
DNS Cache — stores resolved records with TTL expiry.

Key insight: TTL (Time To Live) is the number of seconds a record
can be cached. After TTL seconds, the record must be re-fetched.

Cache key: (domain, qtype) — e.g. ("google.com", 1) for an A record.
Cache value: (records, expiry_timestamp)

Use time.time() to get current Unix timestamp in seconds.
"""

import time
from typing import List, Optional, Tuple
from dataclasses import dataclass

from dns.records import DNSRecord


class DNSCache:

    def __init__(self):
        # Internal store: {(name, qtype): (records, expiry_time)}
        self._store = {}

    def put(self, name: str, qtype: int, records: List[DNSRecord]) -> None:
        """
        Store records in cache.

        Use the minimum TTL across all records as the cache expiry.
        expiry = time.time() + min_ttl

        If records is empty, don't cache anything.

        TODO: implement this
        """
        raise NotImplementedError("You need to implement put()")

    def get(self, name: str, qtype: int) -> Optional[List[DNSRecord]]:
        """
        Retrieve records from cache if not expired.

        Steps:
        1. Look up (name, qtype) in self._store
        2. If not found: return None
        3. If found: check if time.time() < expiry_time
           - If still valid: return the records
           - If expired: delete from store, return None

        TODO: implement this
        """
        raise NotImplementedError("You need to implement get()")

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()

    def size(self) -> int:
        """Return number of cached entries (including possibly expired ones)."""
        return len(self._store)

    def __repr__(self):
        return f"DNSCache({self.size()} entries)"
