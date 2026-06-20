/* Pigeon Maze — HTML5 Canvas port of the pygame-ce game.
 *
 * A single, build-free script: open index.html (or serve the folder) and it
 * runs. Drawing happens in a fixed virtual coordinate space (VW x VH) that is
 * scaled to the device's backing store for crisp text + pixel-art sprites.
 *
 * Layout, palette, timings and sprite frames mirror game/config.py (the S=2
 * supersampled values are used directly as the virtual resolution).
 */
"use strict";

/* ----------------------------------------------------------------- config */
const S = 2;
const N = 15;                              // maze is N x N cells
const CELL = 22 * S;                       // 44 px per cell
const WALL_T = Math.max(3, Math.floor(CELL / 6)); // 7 px walls
const HUD_H = 96 * S;                      // 192 px HUD band
const VW = N * CELL;                       // 660 virtual px wide
const VH = N * CELL + HUD_H;               // 852 virtual px tall

const STEP_MS = 75;                       // glide time across one cell
const WALK_FPS = 14;
const PECK_FPS = 8;
const WALK_FRAME = [32, 32];
const PECK_FRAME = [48, 32];

const PLAY_SCALE = (CELL / WALK_FRAME[0]) * 1.3; // pigeon size in-maze
const MENU_PIGEON_SCALE = 3 * S;
const PECK_SCALE = 3 * S;

const F_TITLE = 40 * S, F_BIG = 24 * S, F_HUD = 24 * S, F_UI = 20 * S, F_SMALL = 18 * S;

const COL = {
  BG: "rgb(21,17,15)",
  WALL: "rgb(63,107,57)",
  PATH: "rgb(217,196,154)",
  PATH_ALT: "rgb(205,183,140)",
  SEED: "rgb(244,180,0)",
  TEXT: "rgb(236,229,218)",
  TEXT_DIM: "rgb(169,159,147)",
  BUTTON: "rgb(81,145,69)",
  BUTTON_TEXT: "rgb(21,17,15)",
};

/* directions (compared by reference, so always reuse these constants) */
const UP = [0, -1], DOWN = [0, 1], LEFT = [-1, 0], RIGHT = [1, 0];
const DIRS = [UP, DOWN, LEFT, RIGHT];
const KEYDIR = {
  ArrowUp: UP, ArrowDown: DOWN, ArrowLeft: LEFT, ArrowRight: RIGHT,
  w: UP, s: DOWN, a: LEFT, d: RIGHT, W: UP, S: DOWN, A: LEFT, D: RIGHT,
};

const now = () => performance.now();

/* ------------------------------------------------------------------- maze */
function generate(n) {
  const size = 2 * n + 1;
  const walls = [];
  for (let i = 0; i < size; i++) walls.push(new Uint8Array(size).fill(1));
  const visited = Array.from({ length: n }, () => new Array(n).fill(false));
  const stack = [[0, 0]];
  visited[0][0] = true;
  walls[1][1] = 0;
  while (stack.length) {
    const [cx, cy] = stack[stack.length - 1];
    const nb = [];
    for (const [dx, dy] of DIRS) {
      const nx = cx + dx, ny = cy + dy;
      if (nx >= 0 && nx < n && ny >= 0 && ny < n && !visited[ny][nx]) nb.push([dx, dy, nx, ny]);
    }
    if (!nb.length) { stack.pop(); continue; }
    const [dx, dy, nx, ny] = nb[(Math.random() * nb.length) | 0];
    visited[ny][nx] = true;
    walls[2 * cy + 1 + dy][2 * cx + 1 + dx] = 0; // wall between cells
    walls[2 * ny + 1][2 * nx + 1] = 0;           // neighbour cell centre
    stack.push([nx, ny]);
  }
  return { n, walls };
}

function canMove(maze, cx, cy, dx, dy) {
  const nx = cx + dx, ny = cy + dy;
  if (!(nx >= 0 && nx < maze.n && ny >= 0 && ny < maze.n)) return false;
  return maze.walls[2 * cy + 1 + dy][2 * cx + 1 + dx] === 0;
}

function bfs(maze, start) {
  const key = (x, y) => x + "," + y;
  const dist = new Map([[key(start[0], start[1]), 0]]);
  const queue = [start];
  let head = 0;
  while (head < queue.length) {
    const [cx, cy] = queue[head++];
    const base = dist.get(key(cx, cy));
    for (const [dx, dy] of DIRS) {
      if (canMove(maze, cx, cy, dx, dy)) {
        const nx = cx + dx, ny = cy + dy, k = key(nx, ny);
        if (!dist.has(k)) { dist.set(k, base + 1); queue.push([nx, ny]); }
      }
    }
  }
  return dist;
}

function farthestCell(maze, start) {
  const dist = bfs(maze, start);
  let bestK = null, bestV = -1;
  for (const [k, v] of dist) if (v > bestV) { bestV = v; bestK = k; }
  return bestK.split(",").map(Number);
}

function optimalSteps(maze, start, goal) {
  const dist = bfs(maze, start);
  const k = goal[0] + "," + goal[1];
  return dist.has(k) ? dist.get(k) : null; // shortest path length in steps
}

function solvePath(maze, start, goal) {
  const key = (x, y) => x + "," + y;
  const prev = new Map([[key(start[0], start[1]), null]]);
  const queue = [start];
  let head = 0;
  while (head < queue.length) {
    const [cx, cy] = queue[head++];
    if (cx === goal[0] && cy === goal[1]) break;
    for (const [dx, dy] of DIRS) {
      if (canMove(maze, cx, cy, dx, dy)) {
        const nx = cx + dx, ny = cy + dy, k = key(nx, ny);
        if (!prev.has(k)) { prev.set(k, [cx, cy]); queue.push([nx, ny]); }
      }
    }
  }
  const gk = key(goal[0], goal[1]);
  if (!prev.has(gk)) return null;
  const path = [];
  let cur = goal;
  while (cur) { path.push(cur); cur = prev.get(key(cur[0], cur[1])); }
  return path.reverse();
}

/* ------------------------------------------------------------------ model */
class PlayModel {
  constructor(maze, start, goal) {
    this.maze = maze; this.cell = start.slice(); this.goal = goal;
    this.steps = 0; this.won = false; this.startTime = null; this.endTime = null;
  }
  tryStep(dir, t) {
    if (this.won) return false;
    const [dx, dy] = dir;
    if (!canMove(this.maze, this.cell[0], this.cell[1], dx, dy)) return false;
    if (this.startTime === null) this.startTime = t;
    this.cell = [this.cell[0] + dx, this.cell[1] + dy];
    this.steps++;
    if (this.cell[0] === this.goal[0] && this.cell[1] === this.goal[1]) {
      this.won = true; this.endTime = t;
    }
    return true;
  }
  elapsed(t) {
    if (this.startTime === null) return 0;
    return (this.endTime !== null ? this.endTime : t) - this.startTime;
  }
}

/* ----------------------------------------------------------------- stats */
function efficiency(optimal, steps) {
  if (steps <= 0) return 0;
  return Math.min(1, optimal / steps);
}

function formatTime(ms) {
  const total = ms / 1000;
  const minutes = Math.floor(total / 60);
  const seconds = total - 60 * minutes;
  return minutes + ":" + seconds.toFixed(2).padStart(5, "0");
}

/* --------------------------------------------------------------- storage */
const KEY_TIME = "best_time_ms", KEY_EFF = "best_efficiency";
const best = {
  _get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  _set(k, v) { try { localStorage.setItem(k, String(v)); } catch (e) {} },
  bestTime() { const v = this._get(KEY_TIME); return v != null ? parseInt(v, 10) : null; },
  bestEff() { const v = this._get(KEY_EFF); return v != null ? parseFloat(v) : null; },
  record(timeMs, eff) {
    let it = false, ie = false;
    const bt = this.bestTime();
    if (bt === null || timeMs < bt) { this._set(KEY_TIME, Math.round(timeMs)); it = true; }
    const be = this.bestEff();
    if (be === null || eff > be) { this._set(KEY_EFF, eff); ie = true; }
    return [it, ie];
  },
  summary() {
    const bt = this.bestTime(), be = this.bestEff();
    if (bt === null && be === null) return "";
    return "BEST " + formatTime(bt) + "  ·  " + Math.round((be || 0) * 100) + "%";
  },
};

/* -------------------------------------------------------------- telegram */
const TG = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : null;
function tgInit() {
  if (!TG) return;
  const tries = [
    () => TG.ready(),
    () => TG.expand(),
    () => TG.disableVerticalSwipes && TG.disableVerticalSwipes(),
    () => TG.setBackgroundColor && TG.setBackgroundColor("#15110f"),
    () => TG.setHeaderColor && TG.setHeaderColor("#15110f"),
  ];
  for (const fn of tries) { try { fn(); } catch (e) {} }
}
function hapticSuccess() {
  if (!TG) return;
  try { TG.HapticFeedback.notificationOccurred("success"); } catch (e) {}
}

/* --------------------------------------------------------------- sprites */
function sliceSheet(img, fw, fh) {
  const cols = Math.floor(img.width / fw);
  const frames = [];
  for (let i = 0; i < cols; i++) frames.push({ img, sx: i * fw, sy: 0, sw: fw, sh: fh });
  return frames;
}

class Anim {
  constructor(frames, fps, loop = true) {
    this.frames = frames; this.frameMs = 1000 / fps; this.loop = loop; this.t = 0; this.i = 0;
  }
  update(dt) {
    this.t += dt;
    while (this.t >= this.frameMs) {
      this.t -= this.frameMs; this.i++;
      if (this.i >= this.frames.length) {
        if (this.loop) { this.i = 0; }
        else { this.i = this.frames.length - 1; this.t = 0; break; }
      }
    }
  }
  current() { return this.frames[this.i]; }
}

function shouldFlip(dir, lastHorizontal) {
  if (dir === LEFT) return true;          // sheet faces right; flip to face left
  if (dir === RIGHT) return false;
  return lastHorizontal === LEFT;         // vertical/idle keeps last facing
}

function tapDirection(px, tap) {
  const dx = tap[0] - px[0], dy = tap[1] - px[1];
  if (dx === 0 && dy === 0) return null;
  if (Math.abs(dx) >= Math.abs(dy)) return dx > 0 ? RIGHT : LEFT;
  return dy > 0 ? DOWN : UP;
}

let WALK_FRAMES = null, PECK_FRAMES = null;

/* --------------------------------------------------------------- drawing */
let ctx = null;

function clear(col) { ctx.fillStyle = col; ctx.fillRect(0, 0, VW, VH); }

function fontStr(px) { return "bold " + px + 'px "Courier New", ui-monospace, monospace'; }

function text(str, x, y, px, col, align = "left", baseline = "top") {
  ctx.fillStyle = col; ctx.font = fontStr(px);
  ctx.textAlign = align; ctx.textBaseline = baseline;
  ctx.fillText(str, x, y);
}

function rectCenter(cx, cy, w, h) { return { x: cx - w / 2, y: cy - h / 2, w, h }; }
function inRect(r, x, y) { return x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h; }

function roundRectPath(x, y, w, h, r) {
  if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); return; }
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function drawButton(r, label) {
  ctx.fillStyle = COL.BUTTON;
  roundRectPath(r.x, r.y, r.w, r.h, 12);
  ctx.fill();
  text(label, r.x + r.w / 2, r.y + r.h / 2, F_UI, COL.BUTTON_TEXT, "center", "middle");
}

function drawFrame(f, cx, cy, scale, flip) {
  const w = f.sw * scale, h = f.sh * scale;
  ctx.save();
  ctx.translate(cx, cy);
  if (flip) ctx.scale(-1, 1);
  ctx.drawImage(f.img, f.sx, f.sy, f.sw, f.sh, -w / 2, -h / 2, w, h);
  ctx.restore();
}

/* ---------------------------------------------------------------- states */
class MenuState {
  constructor(app) {
    this.app = app;
    this.pigeon = WALK_FRAMES[0];
    this.playRect = rectCenter(VW / 2, VH / 2 + 120 * S, 200 * S, 56 * S);
  }
  handle(e) {
    if (e.type === "pointerdown" && inRect(this.playRect, e.x, e.y)) {
      this.app.setState(new PlayState(this.app));
    }
  }
  update(_dt) {}
  draw() {
    clear(COL.BG);
    text("PIGEON MAZE", VW / 2, 140 * S, F_TITLE, COL.TEXT, "center", "middle");
    drawFrame(this.pigeon, VW / 2, 240 * S, MENU_PIGEON_SCALE, false);
    drawButton(this.playRect, "PLAY");
    const b = this.app.best.summary();
    if (b) text(b, VW / 2, VH - 60 * S, F_UI, COL.TEXT_DIM, "center", "middle");
  }
}

class PlayState {
  constructor(app) {
    this.app = app;
    this.maze = generate(N);
    this.start = [0, 0];
    this.goal = farthestCell(this.maze, this.start);
    this.model = new PlayModel(this.maze, this.start, this.goal);
    this.optimal = optimalSteps(this.maze, this.start, this.goal);
    this.walk = new Anim(WALK_FRAMES, WALK_FPS);
    this.standing = WALK_FRAMES[0];
    this.scale = PLAY_SCALE;
    this.heldDir = null;
    this.lastHorizontal = RIGHT;
    this.moving = false;
    this.glideT = 0;
    this.mazeOrigin = [0, HUD_H];
    this.fromPx = this.cellCenter(this.model.cell);
    this.toPx = this.fromPx;
  }
  cellCenter(cell) {
    const [ox, oy] = this.mazeOrigin;
    return [ox + cell[0] * CELL + CELL / 2, oy + cell[1] * CELL + CELL / 2];
  }
  pigeonPx() {
    if (this.moving) {
      const f = this.glideT / STEP_MS;
      return [this.fromPx[0] + (this.toPx[0] - this.fromPx[0]) * f,
              this.fromPx[1] + (this.toPx[1] - this.fromPx[1]) * f];
    }
    return this.toPx;
  }
  handle(e) {
    if (e.type === "pointerdown") {
      this.heldDir = tapDirection(this.pigeonPx(), [e.x, e.y]);
      this.tryBegin();
    } else if (e.type === "pointerup") {
      this.heldDir = null;
    } else if (e.type === "keydown") {
      const d = KEYDIR[e.key];
      if (d) { this.heldDir = d; this.tryBegin(); }
    } else if (e.type === "keyup") {
      this.heldDir = null;
    }
  }
  tryBegin() {
    if (this.moving || this.heldDir === null || this.model.won) return;
    const before = this.model.cell;
    if (!this.model.tryStep(this.heldDir, now())) return;
    if (this.heldDir === LEFT || this.heldDir === RIGHT) this.lastHorizontal = this.heldDir;
    this.fromPx = this.cellCenter(before);
    this.toPx = this.cellCenter(this.model.cell);
    this.moving = true;
    this.glideT = 0;
  }
  update(dt) {
    if (!this.moving) return;
    this.glideT += dt;
    this.walk.update(dt);
    if (this.glideT >= STEP_MS) {
      this.moving = false;
      this.glideT = 0;
      if (this.model.won) {
        this.app.setState(new WinState(this.app, this.model, this.optimal));
        return;
      }
      this.tryBegin(); // continue if a direction is still held
    }
  }
  draw() {
    clear(COL.BG);
    this.drawMaze();
    this.drawSeeds();
    this.drawPigeon();
    this.drawHud();
  }
  drawMaze() {
    const [ox, oy] = this.mazeOrigin, c = CELL, t = WALL_T;
    for (let cy = 0; cy < this.maze.n; cy++) {
      for (let cx = 0; cx < this.maze.n; cx++) {
        ctx.fillStyle = (cx + cy) % 2 === 0 ? COL.PATH : COL.PATH_ALT;
        ctx.fillRect(ox + cx * c, oy + cy * c, c, c);
      }
    }
    ctx.fillStyle = COL.WALL;
    for (let cy = 0; cy < this.maze.n; cy++) {
      for (let cx = 0; cx < this.maze.n; cx++) {
        const x = ox + cx * c, y = oy + cy * c;
        if (!canMove(this.maze, cx, cy, 1, 0)) ctx.fillRect(x + c - t, y, t, c);
        if (!canMove(this.maze, cx, cy, 0, 1)) ctx.fillRect(x, y + c - t, c, t);
        if (cx === 0 && !canMove(this.maze, cx, cy, -1, 0)) ctx.fillRect(x, y, t, c);
        if (cy === 0 && !canMove(this.maze, cx, cy, 0, -1)) ctx.fillRect(x, y, c, t);
      }
    }
  }
  drawSeeds() {
    const [cx, cy] = this.cellCenter(this.goal);
    ctx.fillStyle = COL.SEED;
    for (const [dx, dy] of [[-4, -2], [2, -4], [5, 0], [-2, 3], [3, 4], [0, 0]]) {
      ctx.fillRect(cx + dx * S, cy + dy * S, 3 * S, 3 * S);
    }
  }
  drawPigeon() {
    const f = this.moving ? this.walk.current() : this.standing;
    const [cx, cy] = this.pigeonPx();
    drawFrame(f, cx, cy, this.scale, shouldFlip(this.heldDir, this.lastHorizontal));
  }
  drawHud() {
    text(formatTime(this.model.elapsed(now())), 12 * S, 30 * S, F_HUD, COL.TEXT, "left", "top");
    const b = this.app.best.summary();
    if (b) text(b, VW - 12 * S, 36 * S, F_SMALL, COL.TEXT_DIM, "right", "top");
  }
}

class WinState {
  constructor(app, model, optimal) {
    this.app = app;
    this.peck = new Anim(PECK_FRAMES, PECK_FPS);
    const bw = 200 * S, bh = 50 * S;
    this.repeatRect = rectCenter(VW / 2, VH - 104 * S, bw, bh);
    this.menuRect = rectCenter(VW / 2, VH - 44 * S, bw, bh);
    this.elapsed = model.elapsed(now());
    this.eff = efficiency(optimal, model.steps);
    [this.improvedTime, this.improvedEff] = app.best.record(this.elapsed, this.eff);
    hapticSuccess();
    this.lines = [
      "Time   " + formatTime(this.elapsed),
      "Steps  " + model.steps + "  (best " + optimal + ")",
      "Route  " + Math.round(this.eff * 100) + "% efficient",
    ];
  }
  handle(e) {
    if (e.type !== "pointerdown") return;
    if (inRect(this.repeatRect, e.x, e.y)) this.app.setState(new PlayState(this.app));
    else if (inRect(this.menuRect, e.x, e.y)) this.app.setState(new MenuState(this.app));
  }
  update(dt) { this.peck.update(dt); }
  draw() {
    clear(COL.BG);
    drawFrame(this.peck.current(), VW / 2, 58 * S, PECK_SCALE, false);
    text("YOU GOT THE SEEDS!", VW / 2, 124 * S, F_BIG, COL.TEXT, "center", "middle");
    let y = 168 * S;
    for (const line of this.lines) {
      text(line, VW / 2, y, F_UI, COL.TEXT, "center", "middle");
      y += 26 * S;
    }
    if (this.improvedTime || this.improvedEff) {
      text("NEW BEST!", VW / 2, y + 6 * S, F_UI, COL.SEED, "center", "middle");
    }
    drawButton(this.repeatRect, "REPEAT");
    drawButton(this.menuRect, "MENU");
  }
}

/* ------------------------------------------------------------- app + loop */
const app = { best, state: null, setState(s) { this.state = s; } };

const canvas = document.getElementById("game");

function resize() {
  const scale = Math.min(window.innerWidth / VW, window.innerHeight / VH);
  const cssW = Math.max(1, Math.floor(VW * scale));
  const cssH = Math.max(1, Math.floor(VH * scale));
  const dpr = window.devicePixelRatio || 1;
  canvas.style.width = cssW + "px";
  canvas.style.height = cssH + "px";
  canvas.width = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);
  ctx.setTransform(canvas.width / VW, 0, 0, canvas.height / VH, 0, 0); // virtual -> backing px
  ctx.imageSmoothingEnabled = false;                                   // crisp pixel art
}

function toVirtual(clientX, clientY) {
  const r = canvas.getBoundingClientRect();
  return [(clientX - r.left) / r.width * VW, (clientY - r.top) / r.height * VH];
}

function bindInput() {
  canvas.addEventListener("pointerdown", (ev) => {
    ev.preventDefault();
    const [x, y] = toVirtual(ev.clientX, ev.clientY);
    app.state.handle({ type: "pointerdown", x, y });
  }, { passive: false });
  window.addEventListener("pointerup", () => app.state.handle({ type: "pointerup" }));
  window.addEventListener("keydown", (ev) => {
    if (KEYDIR[ev.key] !== undefined) ev.preventDefault();
    app.state.handle({ type: "keydown", key: ev.key });
  });
  window.addEventListener("keyup", (ev) => app.state.handle({ type: "keyup", key: ev.key }));
  window.addEventListener("resize", resize);
}

let last = 0;
function frame() {
  const t = now();
  let dt = t - last; last = t;
  if (dt > 100) dt = 100; // clamp after tab switch / first frame
  app.state.update(dt);
  app.state.draw();
  requestAnimationFrame(frame);
}

function loadImage(src) {
  return new Promise((res, rej) => {
    const img = new Image();
    img.onload = () => res(img);
    img.onerror = () => rej(new Error("failed to load " + src));
    img.src = src;
  });
}

async function boot() {
  ctx = canvas.getContext("2d");
  tgInit();
  const [walk, peck] = await Promise.all([
    loadImage("assets/pigeon_walking.png"),
    loadImage("assets/pigeon_pecking.png"),
  ]);
  WALK_FRAMES = sliceSheet(walk, WALK_FRAME[0], WALK_FRAME[1]);
  PECK_FRAMES = sliceSheet(peck, PECK_FRAME[0], PECK_FRAME[1]);
  resize();
  bindInput();
  app.setState(new MenuState(app));
  last = now();
  requestAnimationFrame(frame);
}

// test hooks (used by tools/cdp_check.js; harmless in production)
window.__pigeon = {
  app, canvas, VW, VH, DIRS, canMove, generate, bfs,
  farthestCell, optimalSteps, solvePath, PlayModel, PlayState, WinState, MenuState,
};
boot();
