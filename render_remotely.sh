#!/usr/bin/env bash
# Universal Remote Rendering & YouTube Publishing via Mac Mini (tambot)
set -e

MAC_MINI_HOST="tambot"
REMOTE_DIR="~/kinetic-text-video"

COMPOSITION="${1:-Honda-Editorial-Light}"
PROPS_FILE="${2:-chapters_data/brave_new_world_ch1_full_props.json}"
OUTPUT_FILE="${3:-out/brave_new_world_ch1_full_60fps.mp4}"
CONCURRENCY="${4:-8}"

echo "📡 Connecting to Mac Mini ($MAC_MINI_HOST)..."
if ! ssh -o ConnectTimeout=5 "$MAC_MINI_HOST" "echo '✅ Mac Mini online:' \$(hostname)"; then
    echo "❌ Error: Could not connect to $MAC_MINI_HOST via Tailscale."
    exit 1
fi

echo "📦 Syncing project & assets to Mac Mini..."
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'out/*.mp4' ./ "$MAC_MINI_HOST:$REMOTE_DIR/"

echo "🔑 Ensuring youtube-uploader credentials are synced..."
ssh "$MAC_MINI_HOST" "mkdir -p ~/.config/youtube-uploader"
rsync -avz ~/.config/youtube-uploader/ "$MAC_MINI_HOST:~/.config/youtube-uploader/"

echo "🎬 Starting Remotion render on Mac Mini ($COMPOSITION, concurrency: $CONCURRENCY)..."
ssh "$MAC_MINI_HOST" "bash -l -c '
    cd $REMOTE_DIR
    npm install --silent
    mkdir -p out
    echo \"Rendering $OUTPUT_FILE on Mac Mini...\"
    npx remotion render src/index.ts \"$COMPOSITION\" \"$OUTPUT_FILE\" --props=\"$PROPS_FILE\" --concurrency $CONCURRENCY
'"

echo "🚀 Rendering complete on Mac Mini! Triggering YouTube upload..."
ssh "$MAC_MINI_HOST" "bash -l -c '
    cd $REMOTE_DIR
    python3 -u auto_upload_when_done.py
'"

echo "🎉 All tasks completed successfully on Mac Mini ($MAC_MINI_HOST)!"
