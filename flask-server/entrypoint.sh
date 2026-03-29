#!/bin/sh

echo "Starting worker..."
python -u memory_worker.py &

echo "Starting flask app..."
python -u server.py