from flask import Flask, request, Response, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import json

QUEUE_FILE = "/tmp/memory_queue.log"


app = Flask(__name__)

# Expose application metrics on /metrics for Prometheus scrapes.
metrics = PrometheusMetrics(app, path=None)  # Disable auto-registering
metrics.info("app_info", "Application info", app_name="flask-app", version="1.0.0")

# Add a simple request counter grouped by path so the app has an easy-to-query
# business-level metric alongside the exporter defaults.
metrics.register_default(
    metrics.counter(
        "by_path_counter",
        "Request count by request paths",
        labels={"path": lambda: request.path},
    )
)


def enqueue(action):
    with open(QUEUE_FILE, "a") as f:
        f.write(json.dumps({"action": action}) + "\n")

@app.route("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
@metrics.do_not_track()
def healthz():
    return {"status": "ok"}


@app.post("/route1")
def postroute1():
    return "Route 1 Post call"


@app.get("/route1")
def getroute1():
    return "Route 1 Get call"


@app.post("/route2")
def postroute2():
    return "Route 2 Post call"


@app.get("/route2")
def getroute2():
    return "Route 2 Get call"


@app.get("/memory")
def memory_control():
    action = request.args.get("action", "").upper()
    if action not in ["ALLOCATE", "CLEAR", "STOP", "KEEP_ALLOCATING_CYCLE"]:
        return jsonify({"error": "invalid action"}), 400

    enqueue(action)
    return jsonify({"status": "queued", "action": action})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, use_reloader=True, debug=True)