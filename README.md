# AsyncUtils Python - Showcase

Simple webserver with increasing on-demand charge and metrics control simulator

What this app does now:
- Allocates memory via http request in flask-server container - with a simple queue worker
- Exposes Flask Server HTTP request metrics
- Keeps track of container memory usage on docker stats via a container in loop that collects them via a docker client with access to host docker socket and exposes them with a flask server to prometheus metrics service.
- Keeps Grafana dashboards to track webserver metrics and container memory usage

next steps:
- Create documentation/CLI to integrate the parallel_processing_scripts programs.
- Generate and collect data from a csv in a multithreaded way.
- Maybe test simple Redis/RabbitMQ/Kafka setup

### What is collected

- Default HTTP metrics for the main webserver, including request count, latency, and response codes for the Flask app

- Container memory metrics are collected separately by the `docker-exporter` service that fetches data from Docker directly and are exposed to Prometheus through its own `/metrics` endpoint.

### Run the stack

```bash
docker compose up --build
```

### Verify metrics

#### Flask HTTP metrics

1. Open `http://localhost:8081/route1` or `http://localhost:8081/route2` a few times.
2. Open `http://localhost:8081/metrics` and confirm Prometheus-formatted metrics are returned.

#### Container memory metrics (main focus)

3. Allocate memory by calling `http://localhost:8081/memory?action=ALLOCATE` a few times.
4. Open `http://localhost:8000/metrics` and confirm Docker container metrics are returned (look for `docker_container_memory_bytes` and `docker_container_cpu_total`).

#### Check both in Prometheus & Grafana

5. Open Prometheus at `http://localhost:9090/targets` and verify both `flask-app` and `docker-exporter` targets are `UP`.
6. Open Grafana at `http://localhost:3000` and use the provisioned `Flask App Metrics` dashboard.
7. Manually query metrics:
   - Flask HTTP: `flask_http_request_total`, `flask_http_request_duration_seconds_bucket`, `by_path_counter`
   - Container memory: `docker_container_memory_bytes`, `docker_container_cpu_total`
