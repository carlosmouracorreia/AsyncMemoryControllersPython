import time
import json
import logging
import os

QUEUE_FILE = "/tmp/memory_queue.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WORKER] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

memory_hog = []
file_position = 0
running = True


def process_task(task):
    global running

    action = task.get("action")

    if action == "ALLOCATE":
        memory_hog.append(bytearray(1024 * 1024))
        logger.info(f"Allocated 1MB, total blocks: {len(memory_hog)}")

    elif action == "CLEAR":
        memory_hog.clear()
        logger.info("Memory cleared")

    elif action == "STOP":
        logger.info("Stopping worker")
        running = False

    else:
        logger.warning(f"Unknown task: {task}")


def read_new_tasks():
    global file_position

    if not os.path.exists(QUEUE_FILE):
        return []

    tasks = []
    with open(QUEUE_FILE, "r") as f:
        f.seek(file_position)

        for line in f:
            try:
                tasks.append(json.loads(line.strip()))
            except Exception as e:
                logger.warning(f"Bad task line: {line}")

        file_position = f.tell()

    return tasks


def main():
    logger.info("Worker started")

    while running:
        tasks = read_new_tasks()

        for task in tasks:
            process_task(task)

        time.sleep(1)

    logger.info("Worker exiting")


if __name__ == "__main__":
    main()