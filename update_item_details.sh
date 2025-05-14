#!/bin/bash

PIDFILE="/tmp/script.pid"

# Check if PID file exists
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Script is already running with PID $PID. Exiting."
        exit 1
    else
        echo "Stale PID file found. Removing."
        rm -f "$PIDFILE"
    fi
fi

# Write current PID to file
echo $$ > "$PIDFILE"

# Run the Python script
source /home/ec2-user/miniconda3/etc/profile.d/conda.sh && conda activate pokevision && python /home/ec2-user/pokevision/update_item_details.py >> /home/ec2-user/pokevision/logs/update.log 2>&1

# Clean up PID file after script ends
rm -f "$PIDFILE"
