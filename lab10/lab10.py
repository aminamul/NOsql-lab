
from datetime import datetime
import json
import os
import shutil

# ЛАБОРАТОРНАЯ РАБОТА №10
# Моделирование отказа MongoDB Replica Set

DATABASE = "university_lab10"
BACKUP_DIR = "backup_lab10"
RESTORE_FILE = "university_restore10.json"

# 1. Исходное состояние Replica Set
nodes = {
    "Node1": "PRIMARY",
    "Node2": "SECONDARY",
    "Node3": "SECONDARY"
}

print("=" * 55)
print("ЛАБОРАТОРНАЯ РАБОТА №10")
print("Моделирование отказа MongoDB Replica Set")
print("=" * 55)

print("\n1. Исходное состояние кластера:")
for node, role in nodes.items():
    print(f"{node}: {role}")

# 2. Создание тестовых данных
events = [
    {"eventId": 1, "type": "login", "studentId": 1001},
    {"eventId": 2, "type": "view", "studentId": 1002},
    {"eventId": 3, "type": "logout", "studentId": 1001}
]

print("\n2. Тестовые данные:")
for event in events:
    print(event)

print(f"Количество документов: {len(events)}")
print("Write Concern: majority (модельное значение)")

# 3. Моделирование отказа PRIMARY
print("\n3. Моделирование отказа PRIMARY:")

t0 = datetime.now()
nodes["Node1"] = "DOWN"

print("Node1 остановлен.")
print("Node2 и Node3 продолжают работу.")

# 4. Выбор нового PRIMARY
nodes["Node2"] = "PRIMARY"
nodes["Node3"] = "SECONDARY"

t1 = datetime.now()
rto = (t1 - t0).total_seconds()

print("\n4. Результат выборов:")
for node, role in nodes.items():
    print(f"{node}: {role}")

print("Новый PRIMARY: Node2")
print(f"Модельное время переключения RTO: {rto:.6f} сек.")

# 5. Возвращение отказавшего узла
print("\n5. Восстановление Node1:")

nodes["Node1"] = "SECONDARY"

for node, role in nodes.items():
    print(f"{node}: {role}")

print("Node1 восстановлен и синхронизирован.")
print("Кластер снова содержит три доступных узла.")

# 6. Создание резервной копии
print("\n6. Создание резервной копии:")

os.makedirs(BACKUP_DIR, exist_ok=True)

backup_file = os.path.join(BACKUP_DIR, "events_backup.json")

with open(backup_file, "w", encoding="utf-8") as file:
    json.dump(events, file, ensure_ascii=False, indent=4)

print(f"Резервная копия создана: {backup_file}")

# 7. Восстановление данных в отдельную тестовую базу
print("\n7. Восстановление резервной копии:")

with open(backup_file, "r", encoding="utf-8") as file:
    restored_events = json.load(file)

with open(RESTORE_FILE, "w", encoding="utf-8") as file:
    json.dump(restored_events, file, ensure_ascii=False, indent=4)

print(f"Тестовая база восстановлена: {RESTORE_FILE}")

# 8. Проверка результатов
print("\n8. Проверка восстановленных данных:")

print(f"Исходное количество документов: {len(events)}")
print(f"Восстановленное количество документов: {len(restored_events)}")

original_ids = [event["eventId"] for event in events]
restored_ids = [event["eventId"] for event in restored_events]

print(f"Исходные eventId: {original_ids}")
print(f"Восстановленные eventId: {restored_ids}")

if events == restored_events:
    print("Результат проверки: УСПЕШНО")
    print("Все данные восстановлены корректно.")
else:
    print("Результат проверки: ОШИБКА")

# 9. Анализ RPO и RTO
rpo = 0 if events == restored_events else 1

print("\n9. Анализ RPO и RTO:")
print(f"Модельное RTO: {rto:.6f} сек.")
print(f"Модельное RPO: {rpo} потерянных документов")

print("\nЦелевые показатели:")
print("RTO: не более 60 секунд (проектное допущение)")
print("RPO: 0 подтвержденных записей (проектное допущение)")

print("\n10. Итог:")
print("Моделирование отказа завершено.")
print("Выбор нового PRIMARY выполнен.")
print("Резервная копия создана.")
print("Восстановление данных проверено.")

print("\n" + "=" * 55)
print("КОНЕЦ ЛАБОРАТОРНОЙ РАБОТЫ №10")
print("=" * 55)
