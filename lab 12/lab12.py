s
import random
import time
import math
import csv
import os
import statistics
import threading
import platform
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt


# ==========================================================
# ЛАБОРАТОРНАЯ РАБОТА №12
# Разработка и запуск воспроизводимого benchmark-сценария
# Вариант 1: Каталог курсов
# Python local storage (моделирование MongoDB)
# ==========================================================

SEED = 42
DOCUMENTS_COUNT = 5000
QUERIES_PER_RUN = 400
WARMUP_COUNT = 40
REPEATS = 3
CLIENTS = [1, 4, 8]

random.seed(SEED)

os.makedirs("graphs", exist_ok=True)

# ==========================================================
# 1. ГЕНЕРАЦИЯ СИНТЕТИЧЕСКИХ ДАННЫХ
# ==========================================================

print("=" * 60)
print("ЛАБОРАТОРНАЯ РАБОТА №12")
print("Benchmark: Каталог курсов")
print("=" * 60)

print("\n1. Создание синтетических данных...")

courses = []

for i in range(DOCUMENTS_COUNT):
    courses.append({
        "courseId": i + 1,
        "departmentId": random.randint(1, 20),
        "semester": random.randint(1, 8),
        "title": f"Course {i + 1}",
        "credits": random.randint(2, 6),
        "teacherId": random.randint(1, 150)
    })

print("Документов создано:", len(courses))
print("Seed генератора:", SEED)
print("Хранилище: локальное Python-хранилище")

# ==========================================================
# 2. ACCESS PATTERNS
# ==========================================================

print("\n2. Access Patterns:")

print("AP-01: Поиск курсов по departmentId и semester")
print("AP-02: Поиск курса по идентификатору")
print("AP-03: Подсчёт курсов подразделения")

QUERY = {
    "departmentId": 10,
    "semester": 5
}

# ==========================================================
# 3. ПОИСК БЕЗ ИНДЕКСА
# ==========================================================

def find_without_index(query):
    result = []

    for course in courses:
        if (
            course["departmentId"] == query["departmentId"]
            and course["semester"] == query["semester"]
        ):
            result.append(course)

    return result[:100]


# ==========================================================
# 4. СОЗДАНИЕ СОСТАВНОГО ИНДЕКСА
# ==========================================================

print("\n3. Создание составного индекса...")

course_index = defaultdict(list)

for course in courses:
    key = (
        course["departmentId"],
        course["semester"]
    )
    course_index[key].append(course)

print("Индекс создан:")
print("{departmentId: 1, semester: 1}")


def find_with_index(query):
    key = (
        query["departmentId"],
        query["semester"]
    )

    return course_index.get(key, [])[:100]


# ==========================================================
# 5. АНАЛИЗ ПЛАНА ЗАПРОСА
# ==========================================================

def explain_without_index():
    matched = find_without_index(QUERY)

    return {
        "winningPlan": "COLLSCAN",
        "totalDocsExamined": DOCUMENTS_COUNT,
        "totalKeysExamined": 0,
        "nReturned": len(matched)
    }


def explain_with_index():
    matched = find_with_index(QUERY)

    key = (
        QUERY["departmentId"],
        QUERY["semester"]
    )

    return {
        "winningPlan": "INDEX_SCAN (Python dictionary)",
        "totalDocsExamined": len(course_index.get(key, [])),
        "totalKeysExamined": 1,
        "nReturned": len(matched)
    }


# ==========================================================
# 6. РАСЧЁТ ПРОЦЕНТИЛЕЙ
# ==========================================================

def percentile(values, p):
    values = sorted(values)

    if not values:
        return float("nan")

    index = (len(values) - 1) * p / 100

    low = math.floor(index)
    high = math.ceil(index)

    return (
        values[low]
        + (values[high] - values[low]) * (index - low)
    )


# ==========================================================
# 7. ВЫПОЛНЕНИЕ ОДНОГО ЗАПРОСА
# ==========================================================

def one_query(use_index):
    start = time.perf_counter()

    try:
        if use_index:
            find_with_index(QUERY)
        else:
            find_without_index(QUERY)

        elapsed = (time.perf_counter() - start) * 1000

        return elapsed, True

    except Exception:
        elapsed = (time.perf_counter() - start) * 1000

        return elapsed, False


# ==========================================================
# 8. BENCHMARK
# ==========================================================

def run_benchmark(workers, use_index):

    # Прогрев
    for _ in range(WARMUP_COUNT):
        one_query(use_index)

    latencies = []
    errors = 0

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:

        results = list(
            executor.map(
                lambda _: one_query(use_index),
                range(QUERIES_PER_RUN)
            )
        )

    total_time = time.perf_counter() - start_time

    for latency, success in results:

        if success:
            latencies.append(latency)
        else:
            errors += 1

    success_count = len(latencies)

    rps = (
        success_count / total_time
        if total_time > 0 else 0
    )

    return {
        "workers": workers,
        "success": success_count,
        "errors": errors,
        "rps": rps,
        "p50": percentile(latencies, 50),
        "p95": percentile(latencies, 95),
        "p99": percentile(latencies, 99),
        "duration": total_time
    }


# ==========================================================
# 9. ПРОВЕДЕНИЕ ЭКСПЕРИМЕНТОВ
# ==========================================================

all_results = []

for use_index in [False, True]:

    mode = "С индексом" if use_index else "Без индекса"

    print("\n" + "=" * 60)
    print("РЕЖИМ:", mode)
    print("=" * 60)

    for workers in CLIENTS:

        for repeat in range(1, REPEATS + 1):

            result = run_benchmark(workers, use_index)

            result["mode"] = mode
            result["repeat"] = repeat

            all_results.append(result)

            print(
                f"Клиенты: {workers} | "
                f"Повтор: {repeat} | "
                f"RPS: {result['rps']:.2f} | "
                f"P50: {result['p50']:.4f} ms | "
                f"P95: {result['p95']:.4f} ms | "
                f"P99: {result['p99']:.4f} ms | "
                f"Ошибки: {result['errors']}"
            )


# ==========================================================
# 10. СОХРАНЕНИЕ РЕЗУЛЬТАТОВ В CSV
# ==========================================================

df = pd.DataFrame(all_results)

df.to_csv(
    "results.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nРезультаты сохранены в results.csv")


# ==========================================================
# 11. ТАБЛИЦА РЕЗУЛЬТАТОВ
# ==========================================================

print("\n" + "=" * 60)
print("СВОДНАЯ ТАБЛИЦА")
print("=" * 60)

summary = df.groupby(
    ["mode", "workers"]
)[["rps", "p50", "p95", "p99", "errors"]].median().round(4)

print(summary.to_string())


# ==========================================================
# 12. РАСЧЁТ УЛУЧШЕНИЯ P95
# ==========================================================

print("\n" + "=" * 60)
print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
print("=" * 60)

for workers in CLIENTS:

    before = df[
        (df["mode"] == "Без индекса")
        & (df["workers"] == workers)
    ]["p95"].median()

    after = df[
        (df["mode"] == "С индексом")
        & (df["workers"] == workers)
    ]["p95"].median()

    if before > 0:
        improvement = ((before - after) / before) * 100
    else:
        improvement = 0

    print(
        f"{workers} клиентов: "
        f"P95 до = {before:.4f} ms | "
        f"P95 после = {after:.4f} ms | "
        f"Улучшение = {improvement:.2f}%"
    )


# ==========================================================
# 13. РАСЧЁТ ДОЛИ ОШИБОК
# ==========================================================

print("\nДОЛЯ ОШИБОК:")

for mode in ["Без индекса", "С индексом"]:

    mode_data = df[df["mode"] == mode]

    errors = mode_data["errors"].sum()

    attempts = len(mode_data) * QUERIES_PER_RUN

    error_percent = errors / attempts * 100

    print(
        f"{mode}: {error_percent:.2f}% "
        f"({errors}/{attempts})"
    )


# ==========================================================
# 14. EXPLAIN ДО И ПОСЛЕ ИНДЕКСА
# ==========================================================

print("\n" + "=" * 60)
print("АНАЛИЗ ПЛАНА ЗАПРОСА")
print("=" * 60)

print("\nДо индекса:")

print(explain_without_index())

print("\nПосле индекса:")

print(explain_with_index())


# ==========================================================
# 15. ГРАФИК P95
# ==========================================================

plt.figure(figsize=(10, 6))

for mode in ["Без индекса", "С индексом"]:

    data = df[df["mode"] == mode]

    grouped = data.groupby("workers")["p95"].median()

    plt.plot(
        grouped.index,
        grouped.values,
        marker="o",
        linewidth=2,
        label=mode
    )

plt.title("Сравнение P95 до и после индексации")
plt.xlabel("Количество параллельных клиентов")
plt.ylabel("P95 (ms)")
plt.xticks(CLIENTS)
plt.grid(True)
plt.legend()

plt.savefig("graphs/p95_comparison.png", dpi=300)
plt.show()


# ==========================================================
# 16. ГРАФИК THROUGHPUT
# ==========================================================

plt.figure(figsize=(10, 6))

for mode in ["Без индекса", "С индексом"]:

    data = df[df["mode"] == mode]

    grouped = data.groupby("workers")["rps"].median()

    plt.plot(
        grouped.index,
        grouped.values,
        marker="o",
        linewidth=2,
        label=mode
    )

plt.title("Сравнение Throughput (RPS)")
plt.xlabel("Количество параллельных клиентов")
plt.ylabel("Запросов в секунду")
plt.xticks(CLIENTS)
plt.grid(True)
plt.legend()

plt.savefig("graphs/throughput_comparison.png", dpi=300)
plt.show()


# ==========================================================
# 17. ИНФОРМАЦИЯ О СИСТЕМЕ
# ==========================================================

print("\n" + "=" * 60)
print("ИНФОРМАЦИЯ ОБ ЭКСПЕРИМЕНТЕ")
print("=" * 60)

print("Python:", platform.python_version())
print("Операционная система:", platform.system())
print("Количество документов:", DOCUMENTS_COUNT)
print("Seed:", SEED)
print("Количество запросов на повтор:", QUERIES_PER_RUN)
print("Прогрев:", WARMUP_COUNT)
print("Повторов:", REPEATS)
print("Клиенты:", CLIENTS)
print("Хранилище: Python local storage")
print("MongoDB: не используется")

# ==========================================================
# 18. ЗАВЕРШЕНИЕ
# ==========================================================

print("\n" + "=" * 60)
print("ЛАБОРАТОРНАЯ РАБОТА №12 ЗАВЕРШЕНА")
print("=" * 60)

print("Созданы файлы:")
print("1. results.csv")
print("2. graphs/p95_comparison.png")
print("3. graphs/throughput_comparison.png")

print("\nВсе результаты получены в ходе локального эксперимента.")
