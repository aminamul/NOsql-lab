# Лабораторная работа №1: Основы работы с MongoDB

**Дисциплина:** Проектирование и применение NoSQL-технологий  
**Тема:** Создание базы данных, коллекций и выполнение CRUD-операций в MongoDB  
**Вариант:** №9 — Онлайн-кинотеатр  
**Инструментарий:** MongoDB Community Server, MongoDB Compass (`mongosh`)

---

## 📌 Цель работы
Изучить документную модель MongoDB, получить практические навыки создания базы данных, коллекций и BSON-документов, выполнения базовых CRUD-операций, а также фильтрации, сортировки, проекции и работы с массивами и вложенными документами.

---

## 🗂️ Предметная область и структура документа

* **Предметная область:** Онлайн-кинотеатр (`cinema_db`)
* **Коллекция:** `movies`

### Схема BSON-документа:
* `movieId` *(Int)* — Уникальный идентификатор фильма
* `title` *(String)* — Название фильма
* `year` *(Int)* — Год выпуска
* `rating` *(Double)* — Рейтинг фильма
* `country` *(String)* — Страна производства
* `genres` *(Array of Strings)* — Массив жанров
* `details` *(Embedded Document)* — Вложенный документ с деталями (режиссер `director`, длительность `duration`)

Пример документа:
```json
{
  "movieId": 1,
  "title": "Inception",
  "year": 2010,
  "rating": 8.8,
  "country": "USA",
  "genres": ["Sci-Fi", "Action", "Thriller"],
  "details": {
    "director": "Christopher Nolan",
    "duration": 148
  }
}
🚀 Выполнение работы
1. Создание БД и вставка данных
JavaScript
// Выбор / создание базы данных
use cinema_db

// Заполнение коллекции 10 документами
db.movies.insertMany([
  { movieId: 1, title: "Inception", year: 2010, rating: 8.8, country: "USA", genres: ["Sci-Fi", "Action", "Thriller"], details: { director: "Christopher Nolan", duration: 148 } },
  { movieId: 2, title: "Interstellar", year: 2014, rating: 8.6, country: "USA", genres: ["Sci-Fi", "Drama", "Adventure"], details: { director: "Christopher Nolan", duration: 169 } },
  { movieId: 3, title: "Parasite", year: 2019, rating: 8.5, country: "South Korea", genres: ["Drama", "Thriller"], details: { director: "Bong Joon-ho", duration: 132 } },
  { movieId: 4, title: "The Dark Knight", year: 2008, rating: 9.0, country: "USA", genres: ["Action", "Crime", "Drama"], details: { director: "Christopher Nolan", duration: 152 } },
  { movieId: 5, title: "Spirited Away", year: 2001, rating: 8.6, country: "Japan", genres: ["Animation", "Adventure", "Family"], details: { director: "Hayao Miyazaki", duration: 125 } },
  { movieId: 6, title: "Pulp Fiction", year: 1994, rating: 8.9, country: "USA", genres: ["Crime", "Drama"], details: { director: "Quentin Tarantino", duration: 154 } },
  { movieId: 7, title: "Whiplash", year: 2014, rating: 8.5, country: "USA", genres: ["Drama", "Music"], details: { director: "Damien Chazelle", duration: 106 } },
  { movieId: 8, title: "The Intouchables", year: 2011, rating: 8.5, country: "France", genres: ["Biography", "Comedy", "Drama"], details: { director: "Olivier Nakache", duration: 112 } },
  { movieId: 9, title: "Coco", year: 2017, rating: 8.4, country: "USA", genres: ["Animation", "Adventure", "Comedy"], details: { director: "Lee Unkrich", duration: 105 } },
  { movieId: 10, title: "The Prestige", year: 2006, rating: 8.5, country: "USA", genres: ["Drama", "Mystery", "Sci-Fi"], details: { director: "Christopher Nolan", duration: 130 } }
])
2. Выполнение 18 обязательных задач
Получить все документы коллекции:

JavaScript
db.movies.find()
Найти документ по уникальному идентификатору:

JavaScript
db.movies.find({ movieId: 2 })
Выполнить поиск по строковому полю:

JavaScript
db.movies.find({ country: "USA" })
Выполнить поиск с $gte (рейтинг >= 8.8):

JavaScript
db.movies.find({ rating: { $gte: 8.8 } })
Выполнить поиск с $lt (фильмы до 2010 года):

JavaScript
db.movies.find({ year: { $lt: 2010 } })
Запрос одновременно по двум условиям:

JavaScript
db.movies.find({ country: "USA", rating: { $gte: 8.8 } })
Запрос с использованием $or:

JavaScript
db.movies.find({ $or: [ { country: "France" }, { country: "Japan" } ] })
Запрос с использованием $in:

JavaScript
db.movies.find({ movieId: { $in: [1, 3, 5] } })
Запрос к элементу массива:

JavaScript
db.movies.find({ genres: "Animation" })
Запрос к полю вложенного документа:

JavaScript
db.movies.find({ "details.director": "Christopher Nolan" })
Выполнить проекцию (только название и рейтинг, без _id):

JavaScript
db.movies.find({}, { title: 1, rating: 1, _id: 0 })
Выполнить сортировку (по убыванию рейтинга):

JavaScript
db.movies.find().sort({ rating: -1 })
Использовать limit() (первые 3 фильма):

JavaScript
db.movies.find().limit(3)
Изменить одно поле через $set:

JavaScript
db.movies.updateOne({ movieId: 1 }, { $set: { rating: 9.1 } })
Добавить новый элемент в массив через $push:

JavaScript
db.movies.updateOne({ movieId: 1 }, { $push: { genres: "Mind-Bending" } })
Обновить несколько документов через updateMany():

JavaScript
db.movies.updateMany({ country: "USA" }, { $inc: { rating: 0.1 } })
Удалить один документ через deleteOne():

JavaScript
db.movies.deleteOne({ movieId: 8 })
Продемонстрировать итоговое содержимое коллекции:

JavaScript
db.movies.find()
💡 Обоснование структуры данных
Массив (genres): Избавляет от необходимости создавать связующие таблицы типа many-to-many. Позволяет хранить список тегов или категорий прямо внутри сущности. MongoDB индексирует массивы, обеспечивая быстрый поиск по их элементам.

Вложенный документ (details): Группирует второстепенные или связанные атрибуты (например, режиссёр и длительность) в едином документе. Это исключает необходимость производить операции JOIN, обеспечивая высокую скорость чтения.

❓ Ответы на контрольные вопросы
Что такое документ и коллекция в MongoDB?

Документ — базовая единица хранения данных в BSON-формате (аналог строки в SQL).

Коллекция — группа BSON-документов (аналог таблицы в SQL).

Для чего используется поле _id?

Уникальный первичный ключ документа. При отсутствии генерируется автоматически алгоритмом ObjectId.

Чем insertOne() отличается от insertMany()?

insertOne() вставляет один документ, insertMany() принимает массив документов.

Для чего используются операторы $gt, $gte, $lt и $lte?

Это операторы сравнения: больше ($gt), больше или равно ($gte), меньше ($lt), меньше или равно ($lte).

Как выполнить запрос по вложенному полю?

Используется точечная нотация в кавычках: db.collection.find({ "nested.field": value }).

Как выполняется поиск значения внутри массива?

Путем прямого сопоставления с именем поля: db.collection.find({ arrayField: "value" }).

Для чего используются $set и $push?

$set меняет значение конкретного поля, а $push добавляет значение в конец массива.

Чем updateOne() отличается от updateMany()?

updateOne() меняет только первый найденный документ, подпадающий под фильтр, а updateMany() — все подходящие.

Как выполнить сортировку результатов?

Методом .sort({ field: 1 }) (по возрастанию) или .sort({ field: -1 }) (по убыванию).

Чем документная модель отличается от реляционной?

Гибкая схема (schema-less), хранение иерархических данных через встроенные документы и массивы, отсутствие жестких связей и вызовов JOIN, высокая масштабируемость.

🏁 Вывод
В ходе лабораторной работы были усвоены базовые принципы работы с документ-ориентированной БД MongoDB. Была создана БД cinema_db с коллекцией movies, освоены методы вставки, выборки, модификации и удаления данных через mongosh. Выявлены преимущества хранения агрегированных данных с использованием вложенных BSON-структур.
