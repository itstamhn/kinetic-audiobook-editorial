#!/usr/bin/env bash
set -e

MAC_MINI_HOST="tambot"
REMOTE_DIR="~/kinetic-text-video"

echo "📡 Checking connection to Mac Mini ($MAC_MINI_HOST)..."
if ! ssh -o ConnectTimeout=5 "$MAC_MINI_HOST" "echo '✅ Connected to:' \$(hostname)"; then
    echo "❌ Could not connect to $MAC_MINI_HOST. Please make sure the Mac Mini is awake and Tailscale is running."
    exit 1
fi

echo "📦 Syncing project to Mac Mini..."
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'out/chapters/*.mp4' ./ "$MAC_MINI_HOST:$REMOTE_DIR/"

echo "🔑 Syncing youtube-uploader credentials..."
ssh "$MAC_MINI_HOST" "mkdir -p ~/.config/youtube-uploader"
rsync -avz ~/.config/youtube-uploader/ "$MAC_MINI_HOST:~/.config/youtube-uploader/"

echo "🚀 Starting Full Audiobook Daemon on Mac Mini..."
ssh "$MAC_MINI_HOST" "bash -l -c 'cd $REMOTE_DIR && npm install && nohup python3 batch_render_and_publish_all.py > render.log 2>&1 &'"

echo "🎉 Daemon launched on Mac Mini! You can monitor logs with:"
echo "   ssh $MAC_MINI_HOST \"tail -f $REMOTE_DIR/render.log\""
