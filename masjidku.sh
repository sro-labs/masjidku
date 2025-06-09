#!/bin/bash

BASE_DIR=`dirname $0`
if [ "${BASE_DIR}" == "." ]; then
    echo "Please use fullpath, eg./your/path/$0"
    exit 1
fi
# --- Configuration Variables ---
# Base directory of your application
APP_BASE_DIR="${BASE_DIR}"
# Path to your Python virtual environment
VENV_PATH="${APP_BASE_DIR}/.venv"
# Path to your Django project directory (where manage.py or wsgi.py is located)
PROJECT_DIR="${APP_BASE_DIR}/mysite"
# Gunicorn PID file path
PID_FILE="${PROJECT_DIR}/app.id"
# Gunicorn access log file path
ACCESS_LOG="${PROJECT_DIR}/access.log"
# Gunicorn error log file path
ERROR_LOG="${PROJECT_DIR}/error.log"
# Gunicorn bind address and port
BIND_ADDRESS="127.0.0.1:9980"
# Number of Gunicorn workers
NUM_WORKERS=1
# WSGI application module
WSGI_APP="mysite.wsgi"

# --- Function to start Gunicorn ---
start_gunicorn() {
    echo "Attempting to start Gunicorn..."

    # Check if PID file exists, indicating Gunicorn might already be running
    if [ -f "$PID_FILE" ]; then
        if kill -0 $(< "$PID_FILE") 2>/dev/null; then
            echo "Gunicorn appears to be already running with PID: $(< "$PID_FILE")."
            exit 1
        else
            # PID file exists but process is not running, clean up old PID file
            echo "Old PID file found but process not running. Cleaning up..."
            rm -f "$PID_FILE"
        fi
    fi

    # Activate the virtual environment
    echo "Activating virtual environment: ${VENV_PATH}/bin/activate"
    source "${VENV_PATH}/bin/activate"

    # Change to the project directory
    echo "Changing directory to: ${PROJECT_DIR}"
    cd "$PROJECT_DIR" || { echo "Error: Could not change to project directory. Exiting."; exit 1; }

    # Start Gunicorn in daemon mode
    echo "Starting Gunicorn..."
    gunicorn -w "$NUM_WORKERS" \
             -D \
             --bind "$BIND_ADDRESS" \
             --access-logfile "$ACCESS_LOG" \
             --error-logfile "$ERROR_LOG" \
             --pid "$PID_FILE" \
             "$WSGI_APP"

    # Deactivate the virtual environment (optional, as Gunicorn runs in background)
    deactivate
    sleep 3

    # Verify if Gunicorn started successfully
    if [ -f "$PID_FILE" ]; then
        PID=$(< "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Gunicorn started successfully with PID: $PID"
            echo "Access log: $ACCESS_LOG"
            echo "Error log: $ERROR_LOG"
        else
            echo "Gunicorn failed to start. Check logs for errors."
            exit 1
        fi
    else
        echo "Gunicorn failed to create PID file. Check logs for errors."
        exit 1
    fi
}

# --- Function to stop Gunicorn ---
stop_gunicorn() {
    echo "Attempting to stop Gunicorn..."

    if [ -f "$PID_FILE" ]; then
        PID=$(< "$PID_FILE")
        echo "Found Gunicorn PID: $PID"
        # Check if the process is actually running
        if kill -0 "$PID" 2>/dev/null; then
            echo "Killing Gunicorn process..."
            kill "$PID" # Send SIGTERM (graceful shutdown)
            # Optionally, wait for the process to die
            for i in {1..10}; do
                if ! kill -0 "$PID" 2>/dev/null; then
                    echo "Gunicorn stopped successfully."
                    break
                fi
                sleep 1
            done
            if kill -0 "$PID" 2>/dev/null; then
                echo "Gunicorn process did not terminate gracefully. Forcing kill..."
                kill -9 "$PID" # Send SIGKILL (forceful shutdown)
            fi
        else
            echo "Gunicorn process (PID $PID) not found or already stopped."
        fi
        echo "Removing PID file: $PID_FILE"
        rm -f "$PID_FILE"
    else
        echo "Gunicorn PID file ($PID_FILE) not found. Gunicorn might not be running."
    fi
}

# --- Main script logic ---
case "$1" in
    start)
        start_gunicorn
        ;;
    stop)
        stop_gunicorn
        ;;
    restart)
        stop_gunicorn
        sleep 2 # Give some time for the process to fully stop
        start_gunicorn
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(< "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "Gunicorn is running with PID: $PID"
            else
                echo "Gunicorn PID file exists ($PID_FILE), but process ($PID) is not running. Consider 'stop' to clean up."
            fi
        else
            echo "Gunicorn is not running (PID file $PID_FILE not found)."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0

