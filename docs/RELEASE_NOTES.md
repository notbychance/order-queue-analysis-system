# Order Queue Analysis System

## Summary

Release of the client-server system for analyzing an M/M/1 order queue.

## Included modules

- FastAPI server for queue analysis and formulas.
- Vue 3 web client with local browser history.
- PySide6/QML desktop client with local SQLite history.
- Docker Compose setup for server and web client.
- Windows EXE build for desktop client.

## Main features

- Queue analysis by `λ` and `μ`.
- Stability check by condition `λ < μ`.
- Utilization calculation.
- Average number of orders in system.
- Average waiting time.
- Average time in system.
- Sensitivity charts.
- Local history on clients.
- JSON import/export of history.
- Swagger/OpenAPI documentation.
- Unit and integration tests.
- CI pipeline.

## Artifacts

The release workflow attaches:

- `queue-analysis-web-dist.zip` — production web build.
- `QueueAnalysisDesktop-windows.zip` — Windows desktop application build.

## Notes

The FastAPI server does not store global calculation history.

History storage:

- web client: browser localStorage;
- desktop client: local SQLite database.
