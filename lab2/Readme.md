# Лабораторная работа №2 — Моделирование данных в MongoDB

## Вариант 6 — Турагентство

### Цель работы

Изучить моделирование данных в MongoDB с использованием:

- Embedded Documents;
- массивов;
- массивов Embedded Documents;
- References;
- Dot Notation;
- операторов `$all` и `$push`;
- агрегации `$lookup`.

---
<img width="1919" height="1073" alt="image" src="https://github.com/user-attachments/assets/a0b76ee5-294a-4479-9be3-515a55684633" />

## 1. Предметная область

Предметная область — **турагентство**.

Основные сущности:

1. **Tours** — туристические туры.
2. **Countries** — страны назначения.
3. **Tourists** — туристы (концептуальная сущность, в данной работе отдельная коллекция не требуется).

Основная реализованная связь:

**Countries 1 : N Tours**

Один документ страны может быть связан с несколькими турами.

Связь реализована через поле:

```text
tours.countryId → countries._id
```

---

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/da218550-dc3d-42b8-bbf9-6ddb1fef0e72" />


## 2. Структура документа `tours`

Пример документа:

```javascript
{
    tourId: 1001,
    name: "Almaty Mountains",
    price: 180000,
    duration: 5,
    countryId: 101,

    hotel: {
        name: "Alatau Resort",
        stars: 5
    },

    services: [
        "Breakfast",
        "Transfer",
        "Guide",
        "Insurance"
    ],

    excursions: [
        {
            name: "Mountain Trip",
            price: 25000
        },
        {
            name: "City Tour",
            price: 15000
        }
    ]
}
```

<img width="375" height="675" alt="image" src="https://github.com/user-attachments/assets/2d31d5d8-9e06-4f3c-8a1a-69c2fadab91e" />

### Использованные типы моделирования

- `hotel` — **Embedded Document**.
- `services` — **массив простых значений**.
- `excursions` — **массив Embedded Documents**.
- `countryId` — **Reference** на коллекцию `countries`.

---

## 3. Структура документа `countries`

Пример:

```javascript
{
    _id: 101,
    name: "Kazakhstan",
    capital: "Astana",
    currency: "Tenge"
}
```

Коллекция содержит 6 стран.

---

## 4. Создание базы данных

```javascript
use travelDB

db.createCollection("tours")
db.createCollection("countries")

show collections
```

Результат:

```text
countries
tours
```

---

## 5. Добавление 10 туров

В коллекцию `tours` были добавлены 10 документов.

Используемые поля:

- `tourId`
- `name`
- `price`
- `duration`
- `countryId`
- `hotel`
- `services`

Проверка:

```javascript
db.tours.find().pretty()
```

---

## 6. Массив Embedded Documents

Для тура `1001` добавлены экскурсии:

```javascript
db.tours.updateOne(
    { tourId: 1001 },
    {
        $set: {
            excursions: [
                {
                    name: "Mountain Trip",
                    price: 25000
                },
                {
                    name: "City Tour",
                    price: 15000
                }
            ]
        }
    }
)
```

Проверка:

```javascript
db.tours.find({ tourId: 1001 }).pretty()
```

---

## 7. Dot Notation

Поиск пятизвёздочных отелей:

```javascript
db.tours.find({
    "hotel.stars": 5
})
```

Dot Notation позволяет обращаться к полю, находящемуся внутри Embedded Document.

Пример:

```text
hotel.stars
```

означает обращение к полю `stars` внутри документа `hotel`.

### Dot Notation с дополнительным условием

```javascript
db.tours.find({
    "hotel.stars": 5,
    price: { $lte: 250000 }
})
```

Запрос возвращает туры с пятизвёздочным отелем и ценой не более 250000.

---

## 8. Работа с массивом `services`

### Поиск элемента массива

```javascript
db.tours.find({
    services: "Transfer"
})
```

MongoDB находит документы, в которых массив `services` содержит значение `Transfer`.

### Оператор `$all`

```javascript
db.tours.find({
    services: {
        $all: [
            "Breakfast",
            "Transfer"
        ]
    }
})
```

Запрос находит документы, где присутствуют одновременно `Breakfast` и `Transfer`.

### Оператор `$push`

Добавление нового элемента в массив:

```javascript
db.tours.updateOne(
    { tourId: 1001 },
    {
        $push: {
            services: "Insurance"
        }
    }
)
```

После выполнения:

```text
services: [
    "Breakfast",
    "Transfer",
    "Guide",
    "Insurance"
]
```

---

## 9. References

В документе тура хранится идентификатор страны:

```javascript
countryId: 101
```

В коллекции `countries` существует соответствующий документ:

```javascript
{
    _id: 101,
    name: "Kazakhstan",
    capital: "Astana",
    currency: "Tenge"
}
```

Таким образом:

```text
tours.countryId → countries._id
```

Это пример **Referencing**.

---

## 10. Оператор `$lookup`

Для объединения информации из двух коллекций используется:

```javascript
db.tours.aggregate([
    {
        $lookup: {
            from: "countries",
            localField: "countryId",
            foreignField: "_id",
            as: "countryInfo"
        }
    }
])
```

### Параметры `$lookup`

| Параметр | Назначение |
|---|---|
| `from` | коллекция, из которой берутся связанные документы |
| `localField` | поле текущей коллекции `tours` |
| `foreignField` | поле связанной коллекции `countries` |
| `as` | имя нового массива с найденными связанными документами |

В нашем случае:

```text
from = countries
localField = countryId
foreignField = _id
as = countryInfo
```

В результате к туру добавляется:

```javascript
countryInfo: [
    {
        _id: 101,
        name: "Kazakhstan",
        capital: "Astana",
        currency: "Tenge"
    }
]
```

---

## 11. Embedding vs Referencing

### Embedding

Вложенные данные хранятся непосредственно внутри документа.

В работе пример:

```javascript
hotel: {
    name: "Alatau Resort",
    stars: 5
}
```

Преимущества:

- данные находятся в одном документе;
- не требуется дополнительный запрос;
- удобно для небольших и тесно связанных данных.

Недостаток:

- при большом объёме вложенных данных документ может стать слишком большим.

### Referencing

В документе хранится ссылка на другой документ.

В работе:

```javascript
countryId: 101
```

Преимущества:

- данные не дублируются;
- удобно для общих объектов;
- подходит для связи 1:N и больших наборов данных.

Недостаток:

- для получения связанных данных может потребоваться `$lookup`.

---

## 12. Остальные скриншоты
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/01e35d2f-4c45-463a-be5e-d7c4ca5465d5" />
<img width="1910" height="1079" alt="image" src="https://github.com/user-attachments/assets/c132b61f-c13d-4deb-b64d-f444d3351191" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/7d12e432-235b-4cb7-8cb2-c9e303131116" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/6c90cbca-9356-4072-97ba-10a784573166" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/53811c2c-003f-4b85-a8f1-5c80220654ca" />

---

## 13. Что уже выполнено

- [x] Создана база `travelDB`
- [x] Созданы коллекции `tours` и `countries`
- [x] Добавлено 10 туров
- [x] Использован Embedded Document `hotel`
- [x] Создан массив `services`
- [x] Создан массив Embedded Documents `excursions`
- [x] Выполнены запросы Dot Notation
- [x] Использован `$all`
- [x] Использован `$push`
- [x] Добавлены страны
- [x] Реализован Reference через `countryId`
- [x] Выполнен `$lookup`

---

## 14. Контрольные вопросы

### Что такое BSON?

BSON — бинарное представление документов MongoDB. Оно поддерживает типы данных, используемые MongoDB, включая строки, числа, массивы, вложенные документы и даты.

### Что такое Embedded Document?

Embedded Document — документ, вложенный непосредственно внутрь другого документа.

### Что такое Embedding?

Embedding — способ моделирования, при котором связанные данные хранятся внутри одного документа.

### Что такое Referencing?

Referencing — способ моделирования, при котором вместо вложенного документа хранится ссылка на другой документ.

### Чем Embedding отличается от Referencing?

При Embedding данные находятся внутри одного документа. При Referencing данные находятся в отдельной коллекции и связываются идентификатором.

### Что такое Dot Notation?

Dot Notation — обращение к вложенному полю через точку, например:

```javascript
"hotel.stars"
```

### Для чего используется `$push`?

`$push` добавляет новый элемент в массив.

### Для чего используется `$all`?

`$all` проверяет наличие в массиве всех указанных значений.

### Что такое связи 1:1, 1:N и N:M?

- 1:1 — одному объекту соответствует один объект.
- 1:N — одному объекту соответствует много объектов.
- N:M — многим объектам соответствует много других объектов.

### Что такое unbounded array?

Unbounded array — массив, размер которого может постоянно расти без заранее установленного ограничения. Такие массивы внутри одного документа могут привести к чрезмерному размеру документа.

### Что такое денормализация?

Денормализация — намеренное дублирование или объединение данных для уменьшения количества обращений к разным документам и ускорения чтения.

### Когда использовать Embedding?

Embedding удобно использовать, когда связанные данные небольшие, часто читаются вместе с основным документом и не должны существовать отдельно.

### Когда использовать Referencing?

Referencing подходит для больших или общих данных, а также когда связанные объекты должны существовать независимо.

### Для чего нужен `$lookup`?

`$lookup` позволяет получить связанные документы из другой коллекции и объединить результат в рамках aggregation pipeline.

### Что такое query-driven modeling?

Query-driven modeling — проектирование структуры данных с учётом того, какие запросы и операции приложение будет выполнять чаще всего.

---

## 15. Вывод

В ходе лабораторной работы была разработана модель данных MongoDB для предметной области «Турагентство». Была создана база `travelDB` с коллекциями `tours` и `countries`. В документах `tours` были реализованы Embedded Documents, массивы и массивы вложенных документов. Для связи туров со странами был использован Referencing через поле `countryId`. Были выполнены запросы с Dot Notation, `$all` и `$push`. Для получения связанных данных из двух коллекций был применён оператор `$lookup`. В результате были изучены основные подходы к моделированию данных в MongoDB и различия между Embedding и Referencing.
