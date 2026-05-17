# AsyncMemoryControls With Python and Observability Showcase

Simple containerized webserver and observability setup with increasing on-demand memory allocation and metrics control - e.g a memory control simulator

What this app does now:
- Has a container with a Python Flask API control center and simple queue process - using sync python
- Has a container that exposes Docker Stats via another Flask web-server
- Has a container with Grafana Observability Tools and another with Prometheus Metrics Server

- Request memory allocation commands to the queue from the API control center
- Allocates memory via a simple queue worker process that keeps allocating memory or stops completely. (in the same container)

- Keeps track of the container memory usage (that holds the queue) via docker stats
- Keeps Grafana dashboards to track container memory periodic usage via Prometheus Metrics ssks to the Control Center APIs

next steps:
- Create documentation/CLI to integrate the parallel_processing_scripts programs.
- Generate and collect data from a csv in a multithreaded way.
- Use async python features / syntax
- Maybe test simple Redis/RabbitMQ/Kafka setup
- If reasonable, integrate Orchestration with Kubernetes/Helm setup here.

### What is collected

- Container memory metrics are collected separately by the `docker-stats-exporter` service that interacts with Docker host CLI directly -> exposed on the `/metrics` endpoint.

- Default HTTP metrics for the main control simulator webserver, including request count, latency, and response codes for the Flask app -> collected by the Control Center API - `control-center-flask-api` on it's on `/metrics` endpoint


### Run the stack

```bash
docker compose up --build
```

### Verify Memory Usage Metrics - Docker-Stats-Exporter

1. Allocate memory by calling `http://localhost:8081/memory?action=ALLOCATE` a few times.
2. Open `http://localhost:8000/metrics` and confirm Docker container metrics are returned (look for `docker_container_memory_bytes` and `docker_container_cpu_total`).


#### Check both in Prometheus & Grafana

5. Open Prometheus at `http://localhost:9090/targets` and verify both `control-center-flask-api` and `docker-stats-exporter` targets are `UP`.
6. Open Grafana at `http://localhost:3000` and use the provisioned `Flask App Metrics` dashboard.
7. Manually query metrics:
   - Container memory: `docker_container_memory_bytes`, `docker_container_cpu_total`
   - Flask HTTP (For Main Control Center): `flask_http_request_total`, `flask_http_request_duration_seconds_bucket`, `by_path_counter`
