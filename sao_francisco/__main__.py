"""Support ``python -m sao_francisco`` and the bundled yt-dlp helper mode."""

from __future__ import annotations

import sys


def main() -> int:
    """Dispatch to the GUI or to the bundled yt-dlp command-line entry point."""

    if len(sys.argv) > 1 and sys.argv[1] == "--yt-dlp":
        from yt_dlp import main as ytdlp_main  # type: ignore[import-untyped]

        result = ytdlp_main(sys.argv[2:])
        return int(result or 0)

    from sao_francisco.app import main as app_main

    return app_main()


if __name__ == "__main__":
    raise SystemExit(main())
