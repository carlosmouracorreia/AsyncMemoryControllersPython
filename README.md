# AsyncMemoryControlPlane — memory-control simulator with observability

A compact setup to simulate memory pressure inside a container and observe its effects via Prometheus and Grafana.

## Summary

- A Flask control API to enqueue memory commands and expose HTTP metrics.
- A worker (in the same container) that performs spiked allocations according to queued commands.
- A `docker-stats-exporter` that exposes container memory and CPU as Prometheus metrics.

## How it works

1. Send a command to the control API (the action is appended to a queue).
2. A worker reads the queue and performs the requested action (allocate, clear, stop, exit).
3. The separate exporter polls Docker stats and exposes `docker_container_memory_bytes` and `docker_container_cpu_total`.

## Queue commands (control API)

Endpoint: `/memory?action=<ACTION>`

- `ALLOCATE` — begin allocating memory in a spike ( ~ every half second adds 20 mega-bytes)
- `CLEAR` — frees allocated memory
- `STOP` — stop the allocation loop (keeps current allocated memory)
- `EXIT` — stop the worker process entirely

Examples:

```bash
curl "http://localhost:8081/memory?action=ALLOCATE"
curl "http://localhost:8081/memory?action=STOP"
curl "http://localhost:8081/memory?action=CLEAR"
curl "http://localhost:8081/memory?action=EXIT"
```

## Metrics

- Container memory & CPU (docker-stats-exporter): `docker_container_memory_bytes`, `docker_container_cpu_total`.
- Flask HTTP (control API): request counts, durations, status codes, plus `by_path_counter` and `app_info`.

## Run the stack

```bash
docker compose up --build
```

## Verify memory usage metrics (quick)

1. Trigger spike allocation:
   - `curl "http://localhost:8081/memory?action=ALLOCATE"` 
2. Inspect exporter metrics:
   - `http://localhost:8000/metrics` — verify `docker_container_memory_bytes` and `docker_container_cpu_total` are present
3. Confirm Prometheus and Grafana:
   - Prometheus: `http://localhost:9090/targets` (both `control-center-flask-api` and `docker-stats-exporter` should be UP)
   - Grafana: `http://localhost:3000` — see the provisioned dashboard for memory trends

### Quick metric queries
- Container memory: `docker_container_memory_bytes`
- Container CPU: `docker_container_cpu_total`
- Flask HTTP Control Center: `flask_http_request_total`, `flask_http_request_duration_seconds_bucket`, `by_path_counter`

## Quick Grafana access

1. Open: `http://localhost:3000`
2. Default credentials: `admin` / `admin` (you'll be prompted to change them on first login)
3. Go to "Dashboards" → look for the provisioned dashboard (e.g., "Flask App Metrics" or "AsyncMemoryControls")
4. Use the Explore view or the dashboard panels to inspect `docker_container_memory_bytes` over time.

## Next steps

- Create documentation/CLI to integrate the parallel_processing_scripts programs.
- Generate and collect data from a csv in a multithreaded way.
- Use async python features / syntax
- Maybe test simple Redis/RabbitMQ/Kafka setup
- If reasonable, integrate Orchestration with Kubernetes/Helm setup here.
