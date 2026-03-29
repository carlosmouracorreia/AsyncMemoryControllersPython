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
is_allocating = False


def get_current_memory_mb():
    """Calculate current allocated memory in MB"""
    return len(memory_hog) * 20


def process_task(task):
    global running, is_allocating

    action = task.get("action")

    if action == "ALLOCATE":
        ceiling_mb = task.get("ceiling_mb", 1000)
        is_allocating = True
        logger.info(f"Starting allocation loop until {ceiling_mb}MB")

        while is_allocating and get_current_memory_mb() < ceiling_mb:
            memory_hog.append(bytearray(1024 * 1024 * 20))  # 20MB
            logger.info(f"Allocated 20MB, total: {get_current_memory_mb()}MB")

            # Check for interrupt tasks every 0.2 seconds (5 checks per second)
            for _ in range(5):
                time.sleep(0.2)
                pending = read_new_tasks()
                for pending_task in pending:
                    pa = pending_task.get("action")
                    if pa == "STOP":
                        logger.info("STOP received during allocating")
                        is_allocating = False
                    elif pa == "EXIT":
                        logger.info("EXIT received during allocating")
                        is_allocating = False
                        running = False
                    elif pa == "CLEAR":
                        memory_hog.clear()
                        logger.info("CLEAR received during allocating (memory cleared)")
                if not is_allocating or not running:
                    break

        is_allocating = False
        logger.info(f"Allocation stopped. Current: {get_current_memory_mb()}MB")

    elif action == "STOP":
        logger.info("Stopping allocation")
        is_allocating = False

    elif action == "EXIT":
        logger.info("Exiting worker")
        is_allocating = False
        running = False

    elif action == "CLEAR":
        memory_hog.clear()
        logger.info("Memory cleared")

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