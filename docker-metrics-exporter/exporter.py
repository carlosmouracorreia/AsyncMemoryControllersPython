from flask import Flask, Response, request
import docker
import logging

app = Flask(__name__)
client = docker.DockerClient(base_url='unix://var/run/docker.sock')


# Enable request logging
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request():
    print(f"Request: {request.method} {request.path}")

def generate_metrics():
    lines = []
    for container in client.containers.list():
        stats = container.stats(stream=False)
        name = container.name.replace("-", "_")
        mem_usage = stats['memory_stats']['usage']
        cpu_total = stats['cpu_stats']['cpu_usage']['total_usage']

        lines.append(f'docker_container_memory_bytes{{container="{name}"}} {
            mem_usage}')
        lines.append(f'docker_container_cpu_total{{container="{name}"}} {cpu_total}')
    return "\n".join(lines)

@app.route("/metrics")
def metrics():
    return Response(generate_metrics(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)