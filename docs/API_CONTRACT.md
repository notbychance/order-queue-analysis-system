# API Contract

Общий API-контракт между FastAPI-сервером, Vue web-клиентом и PySide6/QML desktop-клиентом.

## Базовый адрес

Для локальной разработки:

```text
http://localhost:8000/api/v1
```

Для Docker/nginx web-сценария web-клиент может использовать относительный путь:

```text
/api/v1
```

## Endpoint-ы

```text
GET  /health
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

Endpoint `/api/v1/queue/default` не используется.

---

## GET /health

Проверка состояния сервера.

### Пример ответа

```json
{
  "status": "ok",
  "service": "Queue Analysis API",
  "environment": "development"
}
```

---

## POST /api/v1/queue/analyze

Выполняет анализ системы массового обслуживания M/M/1.

### Request body

```json
{
  "lambda_rate": 6,
  "mu_rate": 8
}
```

### Поля запроса

| Поле | Тип | Ограничение | Описание |
|---|---:|---:|---|
| `lambda_rate` | number | `>= 0` | интенсивность поступления заказов λ, заказов/день |
| `mu_rate` | number | `> 0` | интенсивность обслуживания заказов μ, заказов/день |

### Response body для устойчивой системы

```json
{
  "lambda_rate": 6.0,
  "mu_rate": 8.0,
  "arrival_rate_unit": "заказов/день",
  "service_rate_unit": "заказов/день",
  "time_unit": "дней",
  "is_stable": true,
  "utilization": 0.75,
  "utilization_percent": 75.0,
  "average_orders_in_system": 3.0,
  "average_waiting_time": 0.375,
  "average_waiting_time_hours": 9.0,
  "average_time_in_system": 0.5,
  "average_time_in_system_hours": 12.0,
  "conclusion": "Система устойчива. Клерк загружен на 75.0%. Очередь не растет неограниченно."
}
```

### Response body для неустойчивой системы

```json
{
  "lambda_rate": 8.0,
  "mu_rate": 8.0,
  "arrival_rate_unit": "заказов/день",
  "service_rate_unit": "заказов/день",
  "time_unit": "дней",
  "is_stable": false,
  "utilization": 1.0,
  "utilization_percent": 100.0,
  "average_orders_in_system": null,
  "average_waiting_time": null,
  "average_waiting_time_hours": null,
  "average_time_in_system": null,
  "average_time_in_system_hours": null,
  "conclusion": "Система неустойчива: интенсивность поступления заказов больше или равна интенсивности обслуживания. Очередь будет расти неограниченно."
}
```

### Поля ответа

| Поле | Тип | Описание |
|---|---:|---|
| `lambda_rate` | number | интенсивность поступления заказов λ |
| `mu_rate` | number | интенсивность обслуживания заказов μ |
| `arrival_rate_unit` | string | единица измерения λ |
| `service_rate_unit` | string | единица измерения μ |
| `time_unit` | string | базовая единица времени |
| `is_stable` | boolean | выполняется ли условие устойчивости `λ < μ` |
| `utilization` | number | коэффициент загрузки `ρ = λ / μ` |
| `utilization_percent` | number | загрузка в процентах |
| `average_orders_in_system` | number/null | среднее число заказов в системе `L` |
| `average_waiting_time` | number/null | среднее время ожидания `Wq`, дней |
| `average_waiting_time_hours` | number/null | среднее время ожидания `Wq`, часов |
| `average_time_in_system` | number/null | среднее время пребывания в системе `W`, дней |
| `average_time_in_system_hours` | number/null | среднее время пребывания в системе `W`, часов |
| `conclusion` | string | текстовое заключение для отображения в клиентах |

---

## GET /api/v1/queue/formulas

Возвращает описание модели и используемые формулы.

### Response body

```json
{
  "model_name": "M/M/1",
  "description": "Одноканальная система массового обслуживания с пуассоновским потоком заявок и экспоненциальным временем обслуживания.",
  "stability_condition": "λ < μ",
  "formulas": {
    "utilization": "ρ = λ / μ",
    "average_orders_in_system": "L = λ / (μ - λ)",
    "average_waiting_time": "Wq = λ / (μ * (μ - λ))",
    "average_time_in_system": "W = 1 / (μ - λ)"
  }
}
```

## Расчетные формулы

Условие устойчивости:

```text
λ < μ
```

Коэффициент загрузки:

```text
ρ = λ / μ
```

Среднее число заказов в системе:

```text
L = λ / (μ - λ)
```

Среднее время ожидания начала обслуживания:

```text
Wq = λ / (μ * (μ - λ))
```

Среднее время пребывания заказа в системе:

```text
W = 1 / (μ - λ)
```

Если `λ >= μ`, система считается неустойчивой, а стационарные показатели `L`, `Wq`, `W` возвращаются как `null`.
