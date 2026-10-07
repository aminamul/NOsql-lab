# Лабораторная работа №3: Выполнение операций Insert, Find, Update и Delete в MongoDB

* **Дисциплина:** Нереляционные базы данных (NoSQL)
* **Вариант:** №2 (Интернет-магазин)
* **База данных:** `shopDB`
* **Коллекция:** `products`
* **Среда выполнения:** MongoDB Compass / mongosh

---

## 1. Цель работы
Освоить практический цикл операций CRUD (Create, Read, Update, Delete) в MongoDB. Научиться работать с BSON-типами, фильтрацией, операторами сравнения, вложенными документами (dot notation), массивами, проекцией, сортировкой и точечным изменением/удалением документов.

---

## 2. Структура документа
Каждый документ коллекции `products` содержит следующие поля:
* `productId` (Number) — уникальный идентификатор товара;
* `name` (String) — наименование товара;
* `brand` (String) — бренд;
* `price` (Number) — цена;
* `stock` (Number) — остаток на складе;
* `rating` (Number) — рейтинг товара;
* `active` (Boolean) — доступность для продажи;
* `tags` (Array) — список категорий/тегов;
* `specifications` (Object) — вложенный объект с техническими характеристиками.

---

## 3. Ход выполнения работы

### 3.1. Создание БД и вставка данных (Create / Insert)
Переключение на базу данных `shopDB`, создание коллекции `products` и заполнение исходными данными (10+ документов):

use shopDB
db.createCollection("products")

// Вставка единичного документа
db.products.insertOne({
  productId: 101,
  name: "Laptop Pro 15",
  brand: "TechCorp",
  price: 1200,
  stock: 15,
  rating: 4.8,
  active: true,
  tags: ["electronics", "laptops", "bestseller"],
  specifications: { ram: "16GB", storage: "512GB SSD", color: "Space Gray" }
})

// Массовая вставка
db.products.insertMany([
  { productId: 102, name: "Wireless Mouse", brand: "TechCorp", price: 25, stock: 50, rating: 4.2, active: true, tags: ["electronics", "accessories"], specifications: { color: "Black", weight: "90g" } },
  { productId: 103, name: "Mechanical Keyboard", brand: "KeyMaster", price: 90, stock: 20, rating: 4.7, active: true, tags: ["gaming", "accessories"], specifications: { color: "RGB", switchType: "Red" } },
  { productId: 104, name: "4K Monitor 27", brand: "Vision", price: 350, stock: 8, rating: 4.6, active: true, tags: ["electronics", "monitors"], specifications: { color: "Black", resolution: "4K" } },
  { productId: 105, name: "USB-C Hub", brand: "TechCorp", price: 40, stock: 35, rating: 4.1, active: true, tags: ["accessories"], specifications: { ports: 6, color: "Silver" } },
  { productId: 106, name: "Gaming Headset", brand: "SoundPro", price: 80, stock: 0, rating: 3.9, active: false, tags: ["gaming", "audio"], specifications: { color: "Red", connection: "Wireless" } },
  { productId: 107, name: "Smartphone X", brand: "MobileOne", price: 950, stock: 12, rating: 4.9, active: true, tags: ["electronics", "phones", "bestseller"], specifications: { ram: "8GB", color: "Blue" } },
  { productId: 108, name: "Webcam Full HD", brand: "Vision", price: 60, stock: 18, rating: 4.3, active: true, tags: ["electronics", "accessories"], specifications: { resolution: "1080p", color: "Black" } },
  { productId: 109, name: "External SSD 1TB", brand: "DataStore", price: 110, stock: 25, rating: 4.5, active: true, tags: ["storage", "accessories"], specifications: { speed: "1050MB/s", color: "Gray" } },
  { productId: 110, name: "Old Trackpad", brand: "LegacyTech", price: 15, stock: 0, rating: 2.5, active: false, tags: ["accessories", "outlet"], specifications: { color: "White" } }
])
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/f40758ac-188b-4c2e-80a5-a908fd558ecc" />

db.products.countDocuments()
<img width="580" height="543" alt="image" src="https://github.com/user-attachments/assets/1e5247e4-9f9e-47cb-8d13-791acb380b75" />


3.2. Выборка и фильтрация данных (Read / Find)
Выполнение поиска с использованием операторов сравнения, dot notation для вложенных объектов, условий по массивам, а также проекции и сортировки:

// Фильтрация и сравнение ($gt,$gte, диапозоны)
db.products.find({ brand: "TechCorp" })
db.products.find({ price: { $gt: 100 } })
db.products.find({ rating: { $gte: 4.5 } })
db.products.find({ price: { $gte: 30,$lte: 100 } })

// Вложенные документы (dot notation) и массивы ($all)
db.products.find({ "specifications.color": "Black" })
db.products.find({ tags: { $all: ["electronics", "bestseller"] } })

// Проекция, сортировка и лимит
db.products.find({}, { _id: 0, name: 1, price: 1, rating: 1 }).sort({ rating: -1 }).limit(3)
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/36177735-396a-450a-acf0-61da60a45b70" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/59e62b56-6ca9-4387-828a-93dba587e8e3" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/93d8825d-7ef7-4573-9d25-22137190d912" />


3.3. Обновление документов (Update)
Изменение полей с использованием модификаторов $set, $inc и $push:
// Изменение цены ($set)
db.products.updateOne({ productId: 101 }, { $set: { price: 1150 } })
<img width="654" height="195" alt="image" src="https://github.com/user-attachments/assets/3b1951c9-2a3a-40c8-a720-3efc6ab1a53d" />

// Увеличение остатка на складе ($inc)
db.products.updateOne({ productId: 102 }, { $inc: { stock: 10 } })
<img width="552" height="213" alt="image" src="https://github.com/user-attachments/assets/febadef1-5e40-4a81-be21-22046255a476" />

// Добавление тега в массив ($push)
db.products.updateOne({ productId: 101 }, { $push: { tags: "discount" } })

3.4. Удаление документов (Delete)
Удаление единичных и группы документов по критерию:
<img width="400" height="254" alt="image" src="https://github.com/user-attachments/assets/f5420ee5-3c0d-43b3-aea8-77b8a08b9e9d" />

// Точечное удаление
db.products.deleteOne({ productId: 110 })

// Массовое удаление неактивных товаров
db.products.deleteMany({ active: false })

// Проверка остатка документов
db.products.countDocuments()

4. Контрольные вопросы
Что означает CRUD?
Это аббревиатура базовых операций работы с данными: Create (Создание), Read (Чтение), Update (Обновление), Delete (Удаление).

Для чего используются insertOne() и insertMany()?
insertOne() добавляет один документ, а insertMany() — массив документов за один запрос.

Чем findOne() отличается от find()?
findOne() возвращает один документ в виде объекта, а find() — курсор с коллекцией совпавших документов.

Что означают $gt, $gte, $lt и $lte?
Операторы сравнения: $gt (>), $gte (>=), $lt (<), $lte (<=).

Что такое dot notation?
Синтаксис обращения к вложенным полям и объектам через точку (например, "specifications.color").

Как найти документ по элементу массива?
Передать имя массива и искомое значение: db.products.find({ tags: "gaming" }).

Для чего используется $all?
Чтобы фильтровать документы, у которых массив содержит все указанные элементы одновременно.

Что такое проекция?
Указание конкретных полей, которые нужно включить (1) или исключить (0) из итоговой выборки.

Для чего нужны sort() и limit()?
sort() сортирует выдачу (1 — по возрастанию, -1 — по убыванию), а limit() ограничивает число возвращаемых документов.

Чем updateMany() отличается от updateOne()?
updateOne() обновляет только первый найденный документ, updateMany() — все документы, подходящие под условие.

Что делают $set, $inc и $push?
$set устанавливает новое значение поля, $inc увеличивает/уменьшает числовое поле, $push добавляет элемент в конец массива.

Чем deleteOne() отличается от deleteMany()?
deleteOne() удаляет первый найденный документ, deleteMany() — все документы, соответствующие критерию.

Почему перед deleteMany() полезно выполнить find()?
Чтобы визуально убедиться в правильности условия фильтрации и не удалить нужные данные случайно.

Как определить количество документов?
С помощью метода db.collection.countDocuments().

Почему важны BSON-типы?
BSON — бинарное расширение JSON. Оно поддерживает дополнительные типы данных (ObjectId, Date, 64-bit int) и обеспечивает высокую скорость чтения и фильтрации.

5. Вывод
В ходе выполнения лабораторной работы были успешно освоены базовые операции CRUD в СУБД MongoDB. На примере базы данных shopDB и коллекции products были отработаны навыки создания, чтения, изменения и удаления полуструктурированных данных. Использование операторов сравнения ($gt, $gte, $lte), вложенных полей (dot notation) и условий поиска по массивам ($all) позволило реализовать гибкие выборки товаров. Применение точечных обновлений ($set, $inc, $push) продемонстрировало эффективное изменение отдельных полей документов без их полной перезаписи. Очистка и удаление записей с помощью deleteOne и deleteMany подтвердили корректность работы механизмов фильтрации перед массовыми операциями. Работа с BSON-форматом доказала удобство и высокую скорость обработки данных без жесткой фиксированной схемы.
