# Project Rules: Kinetic Typography Pipeline

- **Remote Video Rendering**: ALWAYS offload Remotion video rendering tasks (single chapters, full books, batch videos) to the Mac Mini (`tambot` via Tailscale / `./render_remotely.sh`) instead of rendering on the local laptop.
- **YouTube Uploads**: ALWAYS use the CLI tool `youtube-uploader` (`/Users/tamhn/.local/bin/youtube-uploader`) with `--profile main` for all YouTube upload operations. Do not use generic browser automation or ad-hoc scripts unless explicitly asked.
