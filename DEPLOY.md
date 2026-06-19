# Deploying Pigeon Maze (GitHub Pages + Telegram)

The game is a static site (Python compiled to WebAssembly by pygbag). Pushing to
`main` builds and publishes it to GitHub Pages via `.github/workflows/deploy.yml`.

## One-time setup

1. **Create a GitHub repo** (must be **public** for free GitHub Pages):
   open <https://github.com/new>, name it e.g. `pigeon-maze`, leave it empty
   (do not add a README/.gitignore).

2. **Push this project's `main` branch:**
   ```bash
   git remote add origin https://github.com/<YOUR_USER>/pigeon-maze.git
   git push -u origin main
   ```

3. **Turn on Pages via Actions:** repo **Settings → Pages → Build and deployment
   → Source: "GitHub Actions"**.

4. The **Deploy** workflow runs automatically on each push to `main` (watch the
   **Actions** tab). When it goes green, your game is live at:
   ```
   https://<YOUR_USER>.github.io/pigeon-maze/
   ```
   Open that URL in a normal browser first to confirm it loads.

## Hook it up to a Telegram bot

1. In Telegram, talk to **@BotFather**.
   - New bot: `/newbot` → follow prompts → save the token. (Or reuse an existing bot.)
2. Point it at the game (either works):
   - **Menu button:** `/mybots` → pick the bot → **Bot Settings → Menu Button →**
     set the URL to your Pages URL.
   - **Mini App:** `/newapp` → pick the bot → provide title/description/photo and
     the Pages URL.
3. Open the bot in Telegram and tap the menu button / launch the Mini App. The
   game expands to fill the screen, adopts the Telegram theme background, and
   buzzes a success haptic when you reach the seeds.

## Notes

- GitHub Pages serves over HTTPS (required by Telegram) and from a real domain,
  so the pygbag runtime loads the pygame-ce wheel from the public CDN correctly.
  (The local `localhost` gotcha does **not** apply here — see the dev notes.)
- Updating the game: just `git push` to `main`; the workflow rebuilds and
  redeploys. Hard-refresh in the browser to bypass cache.
- Scores persist per-device via the browser's `localStorage` (works inside the
  Telegram webview). Cross-device sync via Telegram CloudStorage is a possible
  future add-on.
