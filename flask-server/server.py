from flask import Flask, request, Response, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

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

import threading
from queue import Queue
import time

task_queue = Queue()
memory_hog = []

import logging

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@app.get("/memory")
def memory_control():
    action = request.args.get("action", "").upper()
    if action in ["ALLOCATE", "CLEAR", "STOP"]:
        task_queue.put(action)
        logger.info(f"Enqueued {action} task via HTTP")
        return jsonify({"status": "ok", "action": action})
    else:
        logger.warning(f"Received unknown action via HTTP: {action}")
        return jsonify({"status": "error", "reason": "invalid action"}), 400

def memory_worker():
    """Worker that reacts to tasks from the queue, with logs."""
    while True:
        task = task_queue.get()
        if task == "STOP":
            logger.info("Stopping memory worker.")
            break
        elif task == "ALLOCATE":
            memory_hog.append(bytearray(1024 * 1024))  # allocate 1 MB
            logger.info(f"Allocated 1 MB, total blocks: {len(memory_hog)}")
        elif task == "CLEAR":
            memory_hog.clear()
            logger.info("Memory cleared")
        else:
            logger.warning(f"Unknown task: {task}")
        task_queue.task_done()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, use_reloader=True, debug=True)


    worker_thread = threading.Thread(target=memory_worker, daemon=True)
    worker_thread.start()
