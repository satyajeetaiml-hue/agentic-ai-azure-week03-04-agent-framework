"""Verifies the memory stores.

The in-memory store is exercised via the API in test_app.py. Here we unit-test
the CosmosMemoryStore logic (upsert + COUNT query + ORDER BY ts) against a fake
container, so the Cosmos code path is verified without a live Cosmos account.
"""

import app.service as svc


class FakeContainer:
    """Minimal stand-in for a Cosmos container supporting the queries we issue."""

    def __init__(self):
        self.items = []

    def upsert_item(self, item):
        self.items.append(item)

    def query_items(self, query, parameters, partition_key):
        sid = parameters[0]["value"]
        rows = [i for i in self.items if i["sessionId"] == sid and i["sessionId"] == partition_key]
        if "COUNT(1)" in query:
            return [len(rows)]
        # emulate "ORDER BY c.ts DESC"
        return sorted(rows, key=lambda r: r["ts"], reverse=True)


def _cosmos_store_with_fake():
    store = svc.CosmosMemoryStore.__new__(svc.CosmosMemoryStore)  # bypass __init__/network
    store._container = FakeContainer()
    return store


def test_in_memory_store_roundtrip():
    s = svc.InMemoryStore()
    assert s.append("sess", "q1", "a1") == 1
    assert s.append("sess", "q2", "a2") == 2
    assert [t["query"] for t in s.recent("sess", n=2)] == ["q1", "q2"]


def test_cosmos_store_counts_per_partition():
    s = _cosmos_store_with_fake()
    assert s.append("alice", "q1", "a1") == 1
    assert s.append("alice", "q2", "a2") == 2
    assert s.append("bob", "qx", "ax") == 1  # different partition, independent count


def test_cosmos_store_recent_is_chronological():
    s = _cosmos_store_with_fake()
    s.append("alice", "q1", "a1")
    s.append("alice", "q2", "a2")
    s.append("alice", "q3", "a3")
    recent = s.recent("alice", n=2)
    assert [t["query"] for t in recent] == ["q2", "q3"]  # last two, oldest-first


def test_default_store_is_in_memory():
    svc.get_memory_store.cache_clear()
    assert svc.get_memory_store().backend == "in-memory"
