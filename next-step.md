# Next Step: Интеграция Kafka в микросервисы

## Этап 1: Подготовка

| # | Задача | Файлы |
|---|--------|-------|
| 1.1 | Создать kafka_helper.py | `src/kafka_helper.py` |
| 1.2 | Обновить requirements.txt | `src/*/requirements.txt` |

---

## Этап 2: date-server

| # | Задача | Файл |
|---|--------|------|
| 2.1 | Переписать с HTTP на Kafka consumer | `src/date-server/date_server.py` |
| 2.2 | Добавить Kafka producer | `src/date-server/date_server.py` |

**Логика:**
```
1. Подключиться к Kafka как Consumer (topic: date-requests)
2. Подключиться к Kafka как Producer
3. Слушать сообщения из date-requests
4. При получении { "job_id": "xxx", "reply_to": "date-responses" }:
   - Сгенерировать текущую дату в формате ISO
   - Отправить в topic из reply_to: { "job_id": "xxx", "date": "...", "status": "success" }
```

---

## Этап 3: timezone-converter

| # | Задача | Файл |
|---|--------|------|
| 3.1 | Переписать с HTTP на 2 Kafka consumer | `src/timezone-converter/timezone_converter.py` |
| 3.2 | Добавить 2 Kafka producer | `src/timezone-converter/timezone_converter.py` |
| 3.3 | Добавить job_id mapping | `src/timezone-converter/timezone_converter.py` |

**Логика:**
```
1. Подключиться к Kafka как Consumer (topic: converter-requests)
2. Подключиться к Kafka как 2 Producer'а (date-requests, converter-responses)
3. Подключиться к Kafka как Consumer (topic: date-responses)

4. При получении { "job_id": "xxx", "reply_to": "..." } из converter-requests:
   - Отправить сообщение в date-requests: { "job_id": "yyy", "reply_to": "date-responses" }
   - Сохранить mapping: yyy → xxx (orig job_id)

5. При получении { "job_id": "yyy", "date": "...", "status": "success" } из date-responses:
   - Найти orig job_id по маппингу yyy → xxx
   - Конвертировать дату в Moscow time
   - Отправить в converter-responses: { "job_id": "xxx", "moscow_time": "...", "status": "success" }
```

---

## Этап 4: public-endpoint

| # | Задача | Файл |
|---|--------|------|
| 4.1 | Переписать с HTTP на Kafka producer | `src/public-endpoint/public_endpoint.py` |
| 4.2 | Добавить Kafka consumer | `src/public-endpoint/public_endpoint.py` |
| 4.3 | Сохранить HTTP endpoint `/public-date` | `src/public-endpoint/public_endpoint.py` |

**Логика:**
```
1. Подключиться к Kafka как Producer (topic: converter-requests)
2. Подключиться к Kafka как Consumer (topic: converter-responses)

3. При HTTP GET /public-date:
   - Сгенерировать job_id (uuid)
   - Отправить в converter-requests: { "job_id": "xxx", "reply_to": "converter-responses" }
   - Ждать сообщение с job_id=xxx из converter-responses
   - Вернуть { "converted_date": "moscow_time" }
```

---

## Этап 5: Тесты

| # | Задача | Файл |
|---|--------|-------|
| 5.1 | Переписать тесты на Kafka | `tests/test_*.py` |

---

## Kafka Topics

| Topic | Назначение |
|-------|------------|
| `date-requests` | Запросы: converter → date-server |
| `date-responses` | Ответы: date-server → converter |
| `converter-requests` | Запросы: public-endpoint → converter |
| `converter-responses` | Ответы: converter → public-endpoint |

---

## Формат сообщений (JSON)

**date-requests:**
```json
{ "job_id": "uuid-1", "reply_to": "date-responses" }
```

**date-responses:**
```json
{ "job_id": "uuid-1", "date": "2024-01-20T15:30:00+07:00", "status": "success" }
```

**converter-requests:**
```json
{ "job_id": "uuid-2", "reply_to": "converter-responses" }
```

**converter-responses:**
```json
{ "job_id": "uuid-2", "moscow_time": "2024-01-20T13:30:00+03:00", "status": "success" }
```

---

## Обработка ошибок

| Ситуация | Действие |
|----------|----------|
| Kafka недоступен | Логировать ошибку, вернуть 503 |
| Таймаут ожидания (>5 сек) | Вернуть 504 Gateway Timeout |
| Retry при ошибке | Повторять попытку |

---

## Библиотека

`confluent-kafka`

---

## Архитектура

```
┌─────────────────┐     converter-requests      ┌─────────────────┐
│  public-endpoint │ ─────────────────────────► │ timezone-converter│
│   (Producer)     │                            │   (Consumer)     │
└─────────────────┘                            └────────┬─────────┘
        ▲                                                 │
        │              converter-responses                │
        │◄────────────────────────────────────────────────┘
        │                                                  │
        │              date-requests                       │
        │                                                  ▼
        │              date-responses              ┌─────────────────┐
        │◄──────────────────────────────────────── │   date-server   │
                                                │   (Consumer)     │
                                                └─────────────────┘
```
