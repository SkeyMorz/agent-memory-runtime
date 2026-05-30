"""Evaluation framework: Recall@K, MRR, Precision@K for memory retrieval."""

import time
from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever
from memory.ranking.ranker import MemoryRanker
from benchmarks.dataset import MEMORIES, QUERIES


def load_memories(store):
    for m in MEMORIES:
        store.add(m["content"], metadata={"category": m["category"]})


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    hits = len(set(retrieved_ids[:k]) & set(relevant_ids))
    return hits / len(relevant_ids)


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    if not retrieved_ids[:k]:
        return 0.0
    hits = len(set(retrieved_ids[:k]) & set(relevant_ids))
    return hits / k


def mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    for i, rid in enumerate(retrieved_ids, start=1):
        if rid in relevant_ids:
            return 1.0 / i
    return 0.0


def map_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    hits = 0
    score = 0.0
    for i, rid in enumerate(retrieved_ids[:k], start=1):
        if rid in relevant_ids:
            hits += 1
            score += hits / i
    return score / min(len(relevant_ids), k) if hits > 0 else 0.0


def build_id_map(store):
    """Map dataset memory IDs (m1..m25) to actual store UUIDs."""
    all_memories = store.get_all()
    id_map = {}
    for i, m in enumerate(all_memories):
        dataset_id = MEMORIES[i]["id"]
        id_map[dataset_id] = m["id"]
    return id_map


def run_benchmark(retriever_cls, ranker, name: str) -> dict:
    store = MemoryStore()
    load_memories(store)
    id_map = build_id_map(store)
    retriever = retriever_cls(store)

    metrics = {
        "recall@1": [], "recall@3": [], "recall@5": [], "recall@10": [],
        "precision@3": [], "precision@5": [], "precision@10": [],
        "mrr": [], "map@10": [],
    }

    for query, relevant_md_ids in QUERIES:
        relevant_store_ids = [id_map[mid] for mid in relevant_md_ids]

        results = retriever.search(query, top_k=10)
        ranked = ranker.rerank(results, strategy="hybrid")
        retrieved_ids = [r["id"] for r in ranked]

        metrics["recall@1"].append(recall_at_k(retrieved_ids, relevant_store_ids, 1))
        metrics["recall@3"].append(recall_at_k(retrieved_ids, relevant_store_ids, 3))
        metrics["recall@5"].append(recall_at_k(retrieved_ids, relevant_store_ids, 5))
        metrics["recall@10"].append(recall_at_k(retrieved_ids, relevant_store_ids, 10))
        metrics["precision@3"].append(precision_at_k(retrieved_ids, relevant_store_ids, 3))
        metrics["precision@5"].append(precision_at_k(retrieved_ids, relevant_store_ids, 5))
        metrics["precision@10"].append(precision_at_k(retrieved_ids, relevant_store_ids, 10))
        metrics["mrr"].append(mrr(retrieved_ids, relevant_store_ids))
        metrics["map@10"].append(map_at_k(retrieved_ids, relevant_store_ids, 10))

    return {k: round(sum(v) / len(v), 4) for k, v in metrics.items()}


def evaluate_consolidation() -> dict:
    """Benchmark consolidation accuracy: does it correctly merge near-duplicates?"""
    from memory.consolidation.consolidator import MemoryConsolidator

    test_cases = [
        {
            "name": "exact near-duplicate",
            "memories": [
                "User likes Japanese food, especially ramen and sushi",
                "User loves Japanese cuisine like ramen and sushi",
            ],
            "expected_kept": 1,
        },
        {
            "name": "different topics, no merge",
            "memories": [
                "User likes Japanese food",
                "User is a Python developer",
            ],
            "expected_kept": 2,
        },
        {
            "name": "three similar, two merge (conservative)",
            "memories": [
                "User likes ramen",
                "User really enjoys eating ramen, especially tonkotsu ramen at Ichiran",
                "User eats ramen",
            ],
            "expected_kept": 2,
        },
        {
            "name": "all distinct topics",
            "memories": [
                "User likes Japanese food",
                "User is a Python developer",
                "User lives in Tokyo",
                "User has a dog named Max",
            ],
            "expected_kept": 4,
        },
        {
            "name": "hiking similar, merges at low threshold",
            "memories": [
                "User enjoys hiking and outdoor activities",
                "User likes hiking outdoor nature walks",
            ],
            "expected_kept": 1,
        },
    ]

    results = []
    for case in test_cases:
        store = MemoryStore()
        for m in case["memories"]:
            store.add(m)
        consolidator = MemoryConsolidator(threshold=0.45)
        r = consolidator.consolidate(store)
        passed = r["kept"] == case["expected_kept"]
        results.append({
            "name": case["name"],
            "before": len(case["memories"]),
            "after": r["kept"],
            "expected": case["expected_kept"],
            "passed": passed,
        })

    accuracy = sum(1 for r in results if r["passed"]) / len(results)
    return {"accuracy": round(accuracy, 4), "details": results}


def main():
    ranker = MemoryRanker()

    print("=" * 60)
    print("agent-memory-runtime v1.0 — Performance Benchmarks")
    print("=" * 60)
    print(f"Dataset: {len(MEMORIES)} memories, {len(QUERIES)} queries")
    print()

    start = time.perf_counter()
    tfidf_metrics = run_benchmark(MemoryRetriever, ranker, "TF-IDF")
    elapsed = time.perf_counter() - start

    print("Retrieval Performance (TF-IDF + Hybrid Ranking)")
    print("-" * 40)
    print(f"  Recall@1:   {tfidf_metrics['recall@1']:.2%}")
    print(f"  Recall@3:   {tfidf_metrics['recall@3']:.2%}")
    print(f"  Recall@5:   {tfidf_metrics['recall@5']:.2%}")
    print(f"  Recall@10:  {tfidf_metrics['recall@10']:.2%}")
    print(f"  Precision@3: {tfidf_metrics['precision@3']:.2%}")
    print(f"  Precision@5: {tfidf_metrics['precision@5']:.2%}")
    print(f"  Precision@10:{tfidf_metrics['precision@10']:.2%}")
    print(f"  MRR:        {tfidf_metrics['mrr']:.4f}")
    print(f"  MAP@10:     {tfidf_metrics['map@10']:.4f}")
    print(f"  Avg time:   {elapsed/len(QUERIES)*1000:.1f}ms/query")
    print()

    print("Consolidation Accuracy")
    print("-" * 40)
    consolidation = evaluate_consolidation()
    print(f"  Accuracy: {consolidation['accuracy']:.0%}")
    for case in consolidation["details"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(f"  [{status}] {case['name']}: {case['before']}→{case['after']} (expected {case['expected']})")
    print()

    try:
        from memory.retrieval.embedding_retriever import EmbeddingRetriever

        start = time.perf_counter()
        emb_metrics = run_benchmark(EmbeddingRetriever, ranker, "Embedding")
        emb_elapsed = time.perf_counter() - start

        print("Retrieval Performance (Embedding + Hybrid Ranking)")
        print("-" * 40)
        print(f"  Recall@1:   {emb_metrics['recall@1']:.2%}")
        print(f"  Recall@3:   {emb_metrics['recall@3']:.2%}")
        print(f"  Recall@5:   {emb_metrics['recall@5']:.2%}")
        print(f"  Recall@10:  {emb_metrics['recall@10']:.2%}")
        print(f"  Precision@3: {emb_metrics['precision@3']:.2%}")
        print(f"  Precision@5: {emb_metrics['precision@5']:.2%}")
        print(f"  Precision@10:{emb_metrics['precision@10']:.2%}")
        print(f"  MRR:        {emb_metrics['mrr']:.4f}")
        print(f"  MAP@10:     {emb_metrics['map@10']:.4f}")
        print(f"  Avg time:   {emb_elapsed/len(QUERIES)*1000:.1f}ms/query")
    except Exception as e:
        print(f"Embedding retriever not available: {e}")

    print()
    print("=" * 60)

    results = {"tfidf": tfidf_metrics, "consolidation": consolidation}
    try:
        results["embedding"] = emb_metrics
    except Exception:
        pass
    return results


if __name__ == "__main__":
    main()
