# Лабораторная работа № 5
## Проектирование кэша/сессий и реализация операций Redis

**Дисциплина:** Проектирование и применение NoSQL-технологий  
**Вариант:** 9 -  Платформа онлайн-обучения
**Курс:** 3

---

## 1. Цель работы

Сформировать практические навыки проектирования Redis-хранилища для кэширования данных и управления пользовательскими сессиями с учётом паттернов доступа, времени жизни данных, стратегии формирования ключей и правил инвалидирования кэша, а также освоить основные операции Redis для создания, чтения, изменения и автоматического удаления временных данных.

---

## 2. Индивидуальный вариант

**Вариант 9. Платформа онлайн-обучения**

- Сущности: студент, курс, урок, преподаватель, сессия
- Поля: `user_id`, `course_id`, `lesson_id`, `language`, `role`

---

## 3. Описание предметной области

Рассматривается платформа онлайн-обучения, в которой студенты изучают курсы, состоящие из отдельных уроков, а преподаватели управляют содержимым. Система обслуживает тысячи одновременных пользователей. Значительная часть запросов приходится на повторное чтение одних и тех же данных: карточек курсов, описаний уроков, настроек интерфейса и состояния активной сессии.

Основная БД хранит постоянную информацию (профили, содержание уроков, оценки, прогресс). Redis используется как кэш и session store.

### 3.1. Пользователи системы

- **Студенты** — изучают курсы, просматривают уроки
- **Преподаватели** — создают и редактируют курсы и уроки
- **Администраторы** — управляют пользователями и настройками

---

## 4. Анализ требований

| Данные | Операция | Частота | Кэшировать? | TTL | Причина |
|--------|----------|---------|-------------|-----|---------|
| Карточка курса | чтение | высокая | да | 600 с | Редко изменяется |
| Карточка урока | чтение | высокая | да | 600 с | Редко изменяется |
| Сессия | чтение/запись | высокая | Redis как store | 1800 с | Временные данные |
| Последние уроки | чтение/запись | средняя | да | 3600 с | История просмотров |
| Онлайн на курсе | чтение/запись | средняя | да | 600 с | Временный статус |
| Счётчик просмотров | запись | высокая | да | без TTL | Аналитика |
| Оценки / прогресс | чтение/запись | средняя | нет | — | Требуется актуальность |

**Вывод:** в Redis размещаются часто читаемые и временные данные. Постоянные данные остаются в основной БД.

---

## 5. Обоснование применения Redis

1. Высокая скорость чтения/записи по ключу (данные в оперативной памяти)
2. Встроенный механизм TTL — автоматическое удаление устаревших сессий и кэша
3. Поддержка удобных структур: Hash, List, Set, String
4. Удобство централизованного хранения сессий
5. Простота инвалидирования кэша командой `DEL`

Redis **не заменяет** основную БД, а дополняет её как кэш и session store.

---

## 6. Проектирование пространства ключей

Соглашение: `<тип>:<сущность>:<идентификатор>`

| Ключ | Тип Redis | Назначение | TTL |
|------|-----------|------------|-----|
| `session:s001` | Hash | Сессия студента | 1800 с |
| `session:s002` | Hash | Сессия студента | 1800 с |
| `session:s003` | Hash | Сессия преподавателя | 900 с |
| `cache:course:CS305` | Hash | Кэш карточки курса | 600 с |
| `cache:course:WEB301` | Hash | Кэш карточки курса | 600 с |
| `cache:course:AI401` | Hash | Кэш карточки курса | 600 с |
| `cache:lesson:L101` | Hash | Кэш карточки урока | 600 с |
| `cache:lesson:L102` | Hash | Кэш карточки урока | 600 с |
| `cache:lesson:L205` | Hash | Кэш карточки урока | 600 с |
| `recent:student:1001` | List | Последние уроки студента | 3600 с |
| `course:CS305:online` | Set | Активные пользователи курса | 600 с |
| `course:WEB301:online` | Set | Активные пользователи курса | 600 с |
| `counter:course:CS305:views` | String | Счётчик просмотров | без TTL |
| `counter:course:WEB301:views` | String | Счётчик просмотров | без TTL |

### Обоснование структур

- **Hash** — удобно хранить объект с несколькими полями и изменять их независимо
- **List** — сохраняет порядок последних просмотренных уроков; `LTRIM` ограничивает размер
- **Set** — гарантирует уникальность элементов (один пользователь не дублируется)
- **String** — атомарный счётчик с командой `INCR`

---

## 7. Создание тестовых данных

### 7.1. Сессии пользователей

```redis
HSET session:s001 user_id "1001" role "student" language "ru" last_lesson "L101"
EXPIRE session:s001 1800

HSET session:s002 user_id "1002" role "student" language "kk" last_lesson "L205"
EXPIRE session:s002 1800

HSET session:s003 user_id "501" role "teacher" language "ru" last_lesson "L101"
EXPIRE session:s003 900

7.2. Кэш курсов
redisHSET cache:course:CS305 name "NoSQL Technologies" teacher "А. Преподаватель" lessons "12" level "intermediate"
EXPIRE cache:course:CS305 600

HSET cache:course:WEB301 name "Web Development" teacher "Б. Преподаватель" lessons "16" level "beginner"
EXPIRE cache:course:WEB301 600

HSET cache:course:AI401 name "Introduction to AI" teacher "В. Преподаватель" lessons "10" level "advanced"
EXPIRE cache:course:AI401 600

7.3. Кэш уроков
redisHSET cache:lesson:L101 title "Introduction to Redis" course "CS305" duration "45"
EXPIRE cache:lesson:L101 600

HSET cache:lesson:L102 title "Keys and TTL" course "CS305" duration "50"
EXPIRE cache:lesson:L102 600

HSET cache:lesson:L205 title "React Basics" course "WEB301" duration "40"
EXPIRE cache:lesson:L205 600

7.4. Последние просмотренные уроки
redisLPUSH recent:student:1001 "lesson:L101"
LPUSH recent:student:1001 "lesson:L102"
LPUSH recent:student:1001 "lesson:L205"
LTRIM recent:student:1001 0 4

7.5. Активные пользователи курсов
redisSADD course:CS305:online "student:1001" "student:1002" "teacher:501"
SADD course:WEB301:online "student:1001" "student:1003"

7.6. Счётчики просмотров
redisSET counter:course:CS305:views 0
INCR counter:course:CS305:views
INCR counter:course:CS305:views
INCR counter:course:CS305:views

SET counter:course:WEB301:views 0
INCR counter:course:WEB301:views

8. Выполнение основных операций
8.1. Операции чтения (5 запросов)
redis# 1. Получить кэш курса
HGETALL cache:course:CS305

# 2. Получить кэш урока
HGETALL cache:lesson:L101

# 3. Получить сессию
HGETALL session:s001

# 4. Получить последние уроки
LRANGE recent:student:1001 0 4

# 5. Получить число пользователей курса онлайн
SCARD course:CS305:online
SMEMBERS course:CS305:online

Ожидаемые результаты:

HGETALL cache:course:CS305 → name, teacher, lessons, level
HGETALL session:s001 → user_id=1001, role=student, language=ru, last_lesson=L101
LRANGE → список из 3 уроков
SCARD → 3

8.2. Изменение данных
redisHSET session:s001 last_lesson "L102"
HGETALL session:s001
Поле last_lesson изменяется на L102. TTL сессии сохраняется.

8.3. Удаление (завершение сессии)
redisDEL session:s002
EXISTS session:s002
Результат EXISTS: 0 — сессия удалена.

8.4. Аналитическое действие
redisGET counter:course:CS305:views
SCARD course:CS305:online
Счётчик просмотров = 3. Активных пользователей = 3.

9. Демонстрация TTL
redisSET cache:ttl-demo "temporary" EX 20
TTL cache:ttl-demo
# через несколько секунд
TTL cache:ttl-demo
# после истечения
GET cache:ttl-demo
Сразу TTL возвращает положительное число (≤ 20). После истечения GET возвращает (nil).
redisTTL session:s001
TTL cache:course:CS305
TTL cache:lesson:L101

10. Демонстрация инвалидирования кэша
Смоделировано изменение названия курса в основной БД:
redisDEL cache:course:CS305
EXISTS cache:course:CS305
Результат EXISTS: 0.

Ответы на вопросы:

При следующем запросе произойдёт cache miss
Приложение получит данные из основной БД
Да, данные нужно снова сохранить в Redis с новым TTL
Рекомендуемый TTL — 600 секунд
Без инвалидирования пользователи будут получать устаревшие данные до истечения TTL


11. Проверка результатов redis

TYPE session:s001                  # hash
TYPE cache:course:WEB301           # hash
TYPE cache:lesson:L101             # hash
TYPE recent:student:1001           # list
TYPE course:CS305:online           # set
TYPE counter:course:CS305:views    # string

HGETALL session:s001
HGETALL cache:course:WEB301
LRANGE recent:student:1001 0 -1
SMEMBERS course:CS305:online
GET counter:course:CS305:views

TTL session:s001
TTL cache:course:WEB301
EXISTS session:s002                # 0
EXISTS cache:course:CS305          # 0

12. Анализ разработанного решения

Почему Redis? — высокая скорость, встроенный TTL, удобные структуры данных.
Что в Redis? — сессии, кэш курсов/уроков, recent, online, счётчики.
Что в основной БД? — профили, содержание уроков, оценки, прогресс, регистрации.
Почему такие структуры? — Hash для объектов, List для истории, Set для уникальности, String для счётчика.
Как формируются ключи? — <тип>:<сущность>:<id> — читаемость и отсутствие конфликтов.
Почему такой TTL? — сессия 1800 с (30 мин), кэш 600 с (данные меняются редко).
Что может устареть? — кэш курса/урока при изменении в основной БД.
Стратегия инвалидирования? — explicit invalidation (DEL) + TTL как страховка.
Cache miss? — приложение идёт в основную БД, затем сохраняет результат в Redis.
Рост пользователей? — Redis Cluster, разгрузка основной БД за счёт cache hit.
Нельзя кэшировать надолго? — прогресс, оценки, персональные данные.
Неправильный TTL? — большой → устаревшие данные; маленький → частые cache miss.


13. Ответы на контрольные вопросы

Модель key-value — данные адресуются уникальным ключом. В Redis значение может быть String, Hash, List, Set и др.
TTL — время жизни ключа. Нужен для автоудаления устаревшего кэша и неактивных сессий.
Cache hit — данные найдены в Redis. Cache miss — данных нет, идём в основную БД.
GET читает String целиком. HGET читает одно поле из Hash.
EXPIRE key seconds — устанавливает TTL. TTL key — возвращает оставшееся время.
Ключ session:<id> понятен, предотвращает конфликты и упрощает отладку.
Hash удобнее, когда поля принадлежат одному объекту и часто читаются вместе.
TTL = -1 — ключ есть, но TTL не задан. Сессия никогда не удалится → расход памяти.
Пользователи будут получать устаревшие данные до истечения TTL или явного удаления.
Redis — хранилище в памяти, не предназначен для надёжного долговременного хранения. Он дополняет основную БД, но не заменяет её.


14. Вывод
В ходе лабораторной работы спроектировано пространство ключей Redis для платформы онлайн-обучения (Вариант 9). Использованы четыре структуры данных: Hash (сессии, кэш курсов и уроков), List (последние уроки), Set (активные пользователи) и String (счётчики).
Ключи организованы по соглашению <тип>:<сущность>:<идентификатор>. TTL применён к сессиям (1800/900 с) и кэшу (600 с). Реализованы создание, чтение, изменение и удаление данных. Продемонстрировано explicit-инвалидирование и автоматическое удаление по TTL.
Проблема устаревших данных решается комбинацией TTL и явного удаления кэша. Получены практические навыки проектирования Redis-модели, выбора структур данных и стратегии инвалидирования.

Приложение. Полный список команд
redisHSET session:s001 user_id "1001" role "student" language "ru" last_lesson "L101"
EXPIRE session:s001 1800
HSET session:s002 user_id "1002" role "student" language "kk" last_lesson "L205"
EXPIRE session:s002 1800
HSET session:s003 user_id "501" role "teacher" language "ru" last_lesson "L101"
EXPIRE session:s003 900
HSET cache:course:CS305 name "NoSQL Technologies" teacher "А. Преподаватель" lessons "12" level "intermediate"
EXPIRE cache:course:CS305 600
HSET cache:course:WEB301 name "Web Development" teacher "Б. Преподаватель" lessons "16" level "beginner"
EXPIRE cache:course:WEB301 600
HSET cache:course:AI401 name "Introduction to AI" teacher "В. Преподаватель" lessons "10" level "advanced"
EXPIRE cache:course:AI401 600
HSET cache:lesson:L101 title "Introduction to Redis" course "CS305" duration "45"
EXPIRE cache:lesson:L101 600
HSET cache:lesson:L102 title "Keys and TTL" course "CS305" duration "50"
EXPIRE cache:lesson:L102 600
HSET cache:lesson:L205 title "React Basics" course "WEB301" duration "40"
EXPIRE cache:lesson:L205 600
LPUSH recent:student:1001 "lesson:L101"
LPUSH recent:student:1001 "lesson:L102"
LPUSH recent:student:1001 "lesson:L205"
LTRIM recent:student:1001 0 4
SADD course:CS305:online "student:1001" "student:1002" "teacher:501"
SADD course:WEB301:online "student:1001" "student:1003"
SET counter:course:CS305:views 0
INCR counter:course:CS305:views
INCR counter:course:CS305:views
INCR counter:course:CS305:views
SET counter:course:WEB301:views 0
INCR counter:course:WEB301:views
