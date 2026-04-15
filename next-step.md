# Next Step: Интеграция Kafka в микросервисы

## Решения
- **Библиотека**: `confluent-kafka`
- **Инфраструктура**: Strimzi operator в Kubernetes
- **DLQ**: Нет (можно добавить позже)
- **Тесты**: Моки (не testcontainers)

---

## Этап 1: Подготовка

| # | Задача | Файлы |
|---|--------|-------|
| 1.1 | Создать `kafka_helper.py` | `src/kafka_helper.py` |
| 1.2 | Обновить requirements.txt | `src/*/requirements.txt` |

---

## Этап 2: date-server

| # | Задача | Файл |
|---|--------|------|
| 2.1 | Создать Kafka consumer | `src/date-server/date_server.py` |
| 2.2 | Создать Kafka producer | `src/date-server/date_server.py` |

**Логика:**
```
1. Consumer (topic: date-requests)
2. Producer
3. При { "job_id": "xxx", "reply_to": "..." }:
   - Дата в ISO → { "job_id": "xxx", "date": "...", "status": "success" }
```

---

## Этап 3: timezone-converter

| # | Задача | Файл |
|---|--------|------|
| 3.1 | Consumer + Producer | `src/timezone-converter/timezone_converter.py` |
| 3.2 | Consumer на date-responses | `src/timezone-converter/timezone_converter.py` |
| 3.3 | job_id mapping | `src/timezone-converter/timezone_converter.py` |

**Логика:**
```
converter-requests → отправить в date-requests → получить из date-responses → converter-responses
```

---

## Этап 4: public-endpoint

| # | Задача | Файл |
|---|--------|------|
| 4.1 | Producer в converter-requests | `src/public-endpoint/public_endpoint.py` |
| 4.2 | Consumer converter-responses | `src/public-endpoint/public_endpoint.py` |
| 4.3 | HTTP endpoint `/public-date` | `src/public-endpoint/public_endpoint.py` |

**Логика:**
```
HTTP GET /public-date → converter-requests → converter-responses → HTTP response
```

---

## Этап 5: Тесты

| # | Задача | Файл |
|---|--------|-------|
| 5.1 | Моки для Kafka | `tests/test_*.py` |

---

## Этап 6: Kubernetes

| # | Задача | Файл |
|---|--------|-------|
| 6.1 | Strimzi KafkaTopic CR | `k8s/strimzi-topics.yaml` |

---

## Kafka Topics

| Topic | Назначение |
|-------|------------|
| `date-requests` | converter → date-server |
| `date-responses` | date-server → converter |
| `converter-requests` | public-endpoint → converter |
| `converter-responses` | converter → public-endpoint |

---

## Формат сообщений

```json
// date-requests
{ "job_id": "uuid-1", "reply_to": "date-responses" }

// date-responses
{ "job_id": "uuid-1", "date": "2024-01-20T15:30:00+07:00", "status": "success" }

// converter-requests
{ "job_id": "uuid-2", "reply_to": "converter-responses" }

// converter-responses
{ "job_id": "uuid-2", "moscow_time": "2024-01-20T13:30:00+03:00", "status": "success" }
```

---

## Обработка ошибок

| Ситуация | Действие |
|----------|----------|
| Kafka недоступен | Логировать, вернуть 503 |
| Таймаут (>5 сек) | Вернуть 504 |
| Retry | Повторять попытку |

---

## Архитектура

```
┌─────────────────┐   converter-requests   ┌─────────────────┐
│  public-endpoint│ ──────────────────────► │timezone-converter│
│  HTTP+Producer  │                         │ 2 Consumer+Prod │
└───────┬─────────┘                         └────────┬────────┘
        │          converter-responses              │
        │◄───────────────────────────────────────────┘
        │                                             
        │          date-requests                      
        │◄─────────────────────────────────────────── 
        │                                             
        │          date-responses              ┌─────────────┐
        │◄──────────────────────────────────── │ date-server │
                                              │ Consumer+Prod│
                                              └─────────────┘
```

---

## Структура файлов после миграции

```
src/
├── kafka_helper.py          # NEW: общий модуль
├── date-server/
│   ├── date_server.py       # Kafka consumer + producer
│   ├── requirements.txt     # + confluent-kafka
│   └── Dockerfile
├── timezone-converter/
│   ├── timezone_converter.py
│   ├── requirements.txt
│   └── Dockerfile
└── public-endpoint/
    ├── public_endpoint.py
    ├── requirements.txt
    └── Dockerfile

k8s/
├── base/
│   ├── date-server.yaml
│   ├── public-endpoint.yaml
│   └── timezone-converter.yaml
└── strimzi-topics.yaml      # NEW: Strimzi CR
```
