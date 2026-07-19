#!/bin/sh
set -e

if [ ! -d "/config" ] || [ ! -f "/config/config.py" ]; then
  echo "Error: /config/config.py not found. Mount your config folder with -v /path/to/config:/config"
  exit 1
fi

cp /config/config.py /app/config.py

# Copy spotify cache if provided
if [ -f "/config/spotify.cache" ]; then
  cp /config/spotify.cache /app/util/spotify.cache
fi

echo "Running Backup.py..."
python Backup.py

echo "Running LoFi.py..."
python LoFi.py
