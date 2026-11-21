"""Homework (Advanced): Graph v2 on the bundled data. A stored page vector stands in for the query, so no API calls."""

import sqlite3
import struct

import pytest

from app import retrieval
from app.config import GRAPH_V2_ADJACENT, GRAPH_V2_TERM, RAG_DB


def stored_vector(page_id: str) -> list[float]:
    with sqlite3.connect(RAG_DB) as db:
        (blob,) = db.execute("SELECT embedding FROM chunks WHERE page_id = ?", (page_id,)).fetchone()
    return list(struct.unpack(f"{len(blob) // 4}f", blob))


@pytest.fixture
def query_like(monkeypatch):
    """Use the vector of a page about constrained decoding (Lecture 03) as the query vector."""
    monkeypatch.setattr(retrieval, "embed_text", lambda *_: stored_vector("lec03-main-p035"))


def test_v2_keeps_the_seeds_and_trims_the_expansion(query_like):
    original = retrieval.search_graph("q")
    v2 = retrieval.search_graph_v2("q")
    assert [p["page_id"] for p in v2["seeds"]] == [p["page_id"] for p in original["seeds"]]
    assert len(v2["expanded"]) <= GRAPH_V2_ADJACENT + GRAPH_V2_TERM < len(original["expanded"])


def test_v2_ranks_graph_candidates_by_distance_without_cover_pages(query_like):
    pages, nodes, adjacent = retrieval._load_graph()
    seeds = retrieval.search_graph("q")["seeds"]
    _, pool = retrieval._expand(seeds, pages, nodes, adjacent)
    expanded = retrieval.search_graph_v2("q")["expanded"]
    assert {p["page_id"] for p in expanded} <= set(pool)  # only pages the graph reached
    assert not any(retrieval.is_cover_page(p) for p in expanded)
    distances = [p["distance"] for p in expanded]
    assert distances == sorted(distances)


def test_v2_gives_adjacent_pages_and_term_pages_their_own_slots(query_like):
    expanded = retrieval.search_graph_v2("q")["expanded"]
    hops = [p["hops"] for p in expanded]
    assert hops.count(1) == GRAPH_V2_ADJACENT  # adjacent slides (1 hop)
    assert hops.count(2) == GRAPH_V2_TERM      # pages reached through a shared term (2 hops)


def test_cover_page_rule():
    pages = {p["page_id"]: p for p in retrieval.load_pages()}
    assert retrieval.is_cover_page(pages["lec03-main-p033"])  # "Part 5 Structured output and tool calls"
    assert not retrieval.is_cover_page(pages["lec03-main-p034"])  # "Structured output"


def test_v2_rejects_an_empty_query():
    with pytest.raises(ValueError):
        retrieval.search_graph_v2("  ")
