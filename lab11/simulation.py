
import random
import hashlib
import csv
from collections import Counter
from pathlib import Path

# ============================================================
# LABORATORY WORK №11
# Sharding Strategy Design and Distribution Test
# Variant №7: Banking Demo Service
# ============================================================

SEED = 42
N = 12000
Q = 30000
SHARDS = 3

random.seed(SEED)

OUTPUT_DIR = Path("lab11_results")
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. GENERATE TEST DATA
# ============================================================

def generate_data(skew=False):
    """Generate 12,000 synthetic banking events."""

    rows = []

    for i in range(N):

        if skew:
            # 80% of documents belong to branch 0
            if random.random() < 0.8:
                branch_id = 0
            else:
                branch_id = random.randint(1, 4)
        else:
            branch_id = i % 5

        rows.append({
            "accountId": i % 2500,
            "branchId": branch_id,
            "event_id": i,
            "amount": random.randint(100, 100000),
            "event_type": random.choice(
                ["deposit", "withdrawal", "transfer"]
            )
        })

    return rows


# ============================================================
# 2. SHARDING STRATEGIES
# ============================================================

def stable_hash(value):
    """Stable SHA-256 hash for reproducible simulation."""

    digest = hashlib.sha256(str(value).encode()).digest()

    return int.from_bytes(digest[:8], "big")


def shard_by_branch(row):
    """Strategy A: Low-cardinality branchId."""

    return row["branchId"] % SHARDS


def shard_by_account(row):
    """Strategy B: Hashed accountId."""

    return stable_hash(row["accountId"]) % SHARDS


def shard_by_event(row):
    """Strategy C: Ranged event_id."""

    return min(
        row["event_id"] // (N // SHARDS),
        SHARDS - 1
    )


STRATEGIES = {
    "branchId (low-cardinality)": shard_by_branch,
    "accountId (hashed)": shard_by_account,
    "event_id (ranged)": shard_by_event
}


# ============================================================
# 3. GENERATE QUERIES
# ============================================================

def generate_queries(rows, hot=False):
    """Generate 30,000 queries."""

    queries = []

    branch_zero = [
        row for row in rows
        if row["branchId"] == 0
    ]

    for _ in range(Q):

        # 60% of requests target branch 0
        if hot and random.random() < 0.6:
            query = random.choice(branch_zero)
        else:
            query = random.choice(rows)

        queries.append(query)

    return queries


# ============================================================
# 4. CALCULATE DISTRIBUTION METRICS
# ============================================================

def calculate_metrics(rows, queries, shard_function):

    documents = Counter(
        shard_function(row) for row in rows
    )

    requests = Counter(
        shard_function(query) for query in queries
    )

    doc_counts = [
        documents[i] for i in range(SHARDS)
    ]

    request_counts = [
        requests[i] for i in range(SHARDS)
    ]

    doc_mean = sum(doc_counts) / SHARDS
    request_mean = sum(request_counts) / SHARDS

    doc_max_mean = max(doc_counts) / doc_mean
    request_max_mean = max(request_counts) / request_mean

    doc_max_min = (
        max(doc_counts) / min(doc_counts)
        if min(doc_counts) > 0 else float("inf")
    )

    request_max_min = (
        max(request_counts) / min(request_counts)
        if min(request_counts) > 0 else float("inf")
    )

    return {
        "documents": doc_counts,
        "requests": request_counts,
        "doc_percent": [
            round(x / N * 100, 2) for x in doc_counts
        ],
        "request_percent": [
            round(x / Q * 100, 2) for x in request_counts
        ],
        "doc_max_mean": round(doc_max_mean, 2),
        "request_max_mean": round(request_max_mean, 2),
        "doc_max_min": round(doc_max_min, 2),
        "request_max_min": round(request_max_min, 2)
    }


# ============================================================
# 5. PRINT RESULTS
# ============================================================

def run_experiment(rows, mode):

    hot = mode == "hot"

    queries = generate_queries(rows, hot)

    print("\n" + "=" * 75)
    print("LOAD MODE:", mode.upper())
    print("=" * 75)

    results = {}

    for name, function in STRATEGIES.items():

        result = calculate_metrics(
            rows,
            queries,
            function
        )

        results[name] = result

        print("\nShard key:", name)

        print("Documents per shard:", result["documents"])
        print("Document distribution (%):", result["doc_percent"])

        print("Queries per shard:", result["requests"])
        print("Query distribution (%):", result["request_percent"])

        print("Document Max/Mean:", result["doc_max_mean"])
        print("Query Max/Mean:", result["request_max_mean"])

        print("Document Max/Min:", result["doc_max_min"])
        print("Query Max/Min:", result["request_max_min"])

    return results


# ============================================================
# 6. SAVE RESULTS TO CSV
# ============================================================

def save_csv(all_results):

    filename = OUTPUT_DIR / "sharding_results.csv"

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:

        writer = csv.writer(file, delimiter=";")

        writer.writerow([
            "Load mode",
            "Shard key",
            "Documents",
            "Document distribution (%)",
            "Queries",
            "Query distribution (%)",
            "Document Max/Mean",
            "Query Max/Mean",
            "Document Max/Min",
            "Query Max/Min"
        ])

        for mode, results in all_results.items():

            for name, result in results.items():

                writer.writerow([
                    mode,
                    name,
                    result["documents"],
                    result["doc_percent"],
                    result["requests"],
                    result["request_percent"],
                    result["doc_max_mean"],
                    result["request_max_mean"],
                    result["doc_max_min"],
                    result["request_max_min"]
                ])

    print("\nCSV saved:", filename)


# ============================================================
# 7. CREATE DISTRIBUTION GRAPH (SVG)
# Uses only Python standard library
# ============================================================

def create_graph(all_results):

    width = 1100
    height = 650

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="550" y="35" text-anchor="middle" '
        'font-size="23" font-weight="bold">'
        'Query Distribution Across Shards</text>'
    ]

    colors = ["#4285F4", "#34A853", "#FBBC05"]

    modes = list(all_results.keys())
    strategies = list(STRATEGIES.keys())

    for panel, mode in enumerate(modes):

        panel_x = 60 + panel * 530
        panel_y = 90

        svg.append(
            f'<text x="{panel_x + 230}" y="{panel_y}" '
            f'text-anchor="middle" font-size="19" '
            f'font-weight="bold">{mode.upper()}</text>'
        )

        for index, strategy in enumerate(strategies):

            result = all_results[mode][strategy]
            values = result["request_percent"]

            group_x = panel_x + index * 165
            base_y = 500

            svg.append(
                f'<text x="{group_x + 55}" y="135" '
                f'text-anchor="middle" font-size="12">'
                f'{strategy.split(" ")[0]}</text>'
            )

            for shard, value in enumerate(values):

                bar_height = value * 3.1
                x = group_x + shard * 37
                y = base_y - bar_height

                svg.append(
                    f'<rect x="{x}" y="{y}" width="30" '
                    f'height="{bar_height}" '
                    f'fill="{colors[shard]}"/>'
                )

                svg.append(
                    f'<text x="{x + 15}" y="{y - 7}" '
                    f'text-anchor="middle" font-size="10">'
                    f'{value}%</text>'
                )

                svg.append(
                    f'<text x="{x + 15}" y="520" '
                    f'text-anchor="middle" font-size="11">'
                    f'S{shard + 1}</text>'
                )

    svg.append(
        '<text x="550" y="590" text-anchor="middle" '
        'font-size="14">S1, S2, S3 - Shards</text>'
    )

    svg.append('</svg>')

    filename = OUTPUT_DIR / "distribution_graph.svg"

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(svg))

    print("Graph saved:", filename)


# ============================================================
# 8. ADDITIONAL EXPERIMENT: 80% DOCUMENT SKEW
# ============================================================

def run_skew_experiment():

    print("\n" + "=" * 75)
    print("ADDITIONAL EXPERIMENT: 80% DOCUMENT SKEW")
    print("=" * 75)

    rows = generate_data(skew=True)
    queries = generate_queries(rows, hot=True)

    for name, function in STRATEGIES.items():

        result = calculate_metrics(
            rows,
            queries,
            function
        )

        print("\nShard key:", name)
        print("Documents:", result["documents"])
        print("Document distribution:", result["doc_percent"])
        print("Queries:", result["requests"])
        print("Query distribution:", result["request_percent"])
        print("Query Max/Mean:", result["request_max_mean"])
        print("Query Max/Min:", result["request_max_min"])


# ============================================================
# 9. ACCESS PATTERNS ANALYSIS
# ============================================================

def access_patterns():

    print("\n" + "=" * 75)
    print("ACCESS PATTERNS ANALYSIS")
    print("=" * 75)

    patterns = [
        (
            "AP-01",
            "Get account transaction history",
            "accountId",
            "Hashed accountId",
            "Targeted",
            "Very high"
        ),
        (
            "AP-02",
            "Get transactions by branch",
            "branchId",
            "branchId",
            "Targeted / Scatter-gather",
            "High"
        ),
        (
            "AP-03",
            "Find events in a time interval",
            "event_id range",
            "event_id",
            "Targeted / Scatter-gather",
            "High"
        ),
        (
            "AP-04",
            "Aggregate transactions by branch",
            "branchId",
            "branchId",
            "Scatter-gather",
            "Medium"
        ),
        (
            "AP-05",
            "Insert a new banking event",
            "event_id",
            "event_id",
            "Depends on shard key",
            "Very high"
        ),
        (
            "AP-06",
            "Find large transactions of an account",
            "accountId + amount",
            "accountId",
            "Targeted",
            "Medium"
        )
    ]

    for pattern in patterns:

        print("\n", pattern[0])
        print("Operation:", pattern[1])
        print("Filter:", pattern[2])
        print("Relevant key:", pattern[3])
        print("Routing:", pattern[4])
        print("Frequency:", pattern[5])


# ============================================================
# 10. ARCHITECTURE DESCRIPTION
# ============================================================

def architecture():

    print("\n" + "=" * 75)
    print("SHARDED CLUSTER ARCHITECTURE")
    print("=" * 75)

    print("""
                    CLIENT APPLICATION
                           |
                           v
                         mongos
                           |
              +------------+------------+
              |            |            |
              v            v            v
           SHARD 1      SHARD 2      SHARD 3
              |            |            |
              v            v            v
          Documents    Documents    Documents

    Config Servers store cluster metadata.
    mongos routes client requests to the required shard(s).
    """)


# ============================================================
# 11. MAIN PROGRAM
# ============================================================

def main():

    print("=" * 75)
    print("LABORATORY WORK №11 - SHARDING SIMULATION")
    print("Variant №7 - Banking Demo Service")
    print("=" * 75)

    print("\nConfiguration:")
    print("Random seed:", SEED)
    print("Documents:", N)
    print("Queries:", Q)
    print("Number of shards:", SHARDS)

    # Generate normal dataset
    rows = generate_data()

    # Run uniform and hot load experiments
    uniform_results = run_experiment(rows, "uniform")
    hot_results = run_experiment(rows, "hot")

    all_results = {
        "uniform": uniform_results,
        "hot": hot_results
    }

    # Save CSV and graph
    save_csv(all_results)
    create_graph(all_results)

    # Additional 80% skew experiment
    run_skew_experiment()

    # Access patterns
    access_patterns()

    # Architecture
    architecture()

    print("\n" + "=" * 75)
    print("EXPERIMENT COMPLETED SUCCESSFULLY")
    print("=" * 75)

    print("\nFiles created in lab11_results:")
    print("1. sharding_results.csv")
    print("2. distribution_graph.svg")

    print("\nRun the program again to verify reproducibility.")


if __name__ == "__main__":
    main()
