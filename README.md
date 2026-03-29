# AsyncUtils Python - Showcase

Simple webserver with increasing on-demand charge and metrics control simulator

what this app does now:
- allocates memory via http request in flask-server container - with a simple queue worker
- exposes flask-server webserver metrics
- keeps track of container memory usage on docker stats via a container in loop that collects them via docker client with access to host docker socket and exposes them with a flask server to prometheus
- grafana dashboards to track webserver metrics and container memory usage

next steps:
- create better CLI to expose the parallel_processing_scripts
- generate and collect data via csv in a multithread way.
- test simple redis/rabbitMQ/kafka in memory

## Flask app metrics

The `flask-app` service now exposes Prometheus metrics on `http://localhost:8081/metrics`.

### What is collected

- Default HTTP metrics from `prometheus_flask_exporter`, including request count, latency, and response codes
- An `app_info` metric with the app name/version
- A `by_path_counter` metric labeled by request path

### Run the stack

```bash
docker compose up --build
```

### Verify metrics

1. Open `http://localhost:8081/route1` or `http://localhost:8081/route2` a few times.
2. Open `http://localhost:8081/metrics` and confirm Prometheus-formatted metrics are returned.
3. Open Prometheus at `http://localhost:9090/targets` and verify the `flask-app` target is `UP`.
4. Open Grafana at `http://localhost:3000` and use the provisioned `Flask App Metrics` dashboard.
5. If you want to explore manually in Grafana, query metrics like `flask_http_request_total`, `flask_http_request_duration_seconds_bucket`, or `by_path_counter`.
