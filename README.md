# hombreimaginario.com

Retro works — progress notes on retro game ports. Plain static HTML served by GitHub Pages, no database.

## Publishing a post

1. Add an entry to `content/posts.json` (`slug`, `date`, `title`, `summary`, `platforms`, optional `project`, `cover`, `cover_pixel`).
2. Write the post body as an HTML fragment in `content/posts/<slug>.html`.
3. Put images in `img/` (PNG for screenshots and pixel art; add `class="pixel"` to keep hard edges when scaled).
4. Run `python3 tools/build.py` and commit everything, including the generated pages.

Platforms: `mega-drive`, `saturn`, `dreamcast`, `neo-geo` (edit `PLATFORMS` in `tools/build.py` to add more).

Fonts: IBM Plex Sans and JetBrains Mono (SIL Open Font License), self-hosted. Icons: Simple Icons (CC0).
