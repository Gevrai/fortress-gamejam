# Fortress Defense — CLAUDE.md

## Project Overview
A single-file browser tower defense game (`index.html`). No build system, no dependencies, no bundler. All game code is vanilla JS inside a `<script>` tag. Deploy via GitHub Pages.

## File Structure
- `index.html` — entire game (HTML + CSS + JS, ~730 lines)
- `waves.md` — detailed wave redesign proposals and new enemy type specs (Ghost, Healer, Sprinter)
- `serve.py` — local dev server (`python serve.py`)

## Architecture

### Constants & State (top of script)
- `COLS=20, ROWS=32, BASE_TILE=16` — grid dimensions
- `zoom, camX, camY` — camera state (pan + pinch-to-zoom)
- `grid[y][x]` — tile type string: `'empty'|'wall'|'turret'|'pit'|'princess'|'portal'|'tree'|'rock'|'water'`
- `entities[]` — all enemies
- `projectiles[]` — turret + princess bullets
- `floatingTexts[]` — damage/gold popups
- `phase` — `'day'|'night'`
- `nightNum` — current night (1–5)
- `princessAttackCooldown` — player tap-to-shoot cooldown (1s)

### Main Loop
`loop(time)` → calls `stepWaves`, `stepEnemies`, `stepTurrets`, `stepProjectiles`, `stepFloatingTexts`, `render`, `updateHUD` each frame.

### Flow Fields
Enemies navigate via BFS flow fields:
- `flowToPrincess` — all ground enemies use this
- `flowToPortals` — enemies carrying the princess use this
- `calcFlowFields()` — must be called after any grid change (wall placed/removed, princess grabbed)
- `isWalkable(x,y)` — walls, turrets, trees, rocks, water block movement

### Enemy Entity Shape
```js
{x, y, hp, maxHp, type, state, speed, grabTimer, slowTimer, pitCooldown, size, flyOffset}
```
- `state`: `'moving_to_princess' | 'grabbing' | 'carrying_to_portal'`
- `type`: `'normal' | 'tank' | 'flyer'` (more planned — see waves.md)

### Projectile Shape
```js
{x, y, tx, ty, timer, target, dmg, isPrincessShot?, tapX?, tapY?}
```
- Turret shots: `timer=0.2`, `target=entity ref`, yellow dot
- Princess shots: `timer=0.3`, `isPrincessShot=true`, `tapX/tapY=impact coords`, pink dot — hits nearest enemy within 1 tile of impact

### Turret Data
Stored on grid rows as `grid[y]._turrets[x] = {cd}`. Cooldown 0.5s, range 3.5 tiles, damage `2 + floor(nightNum/2)`.

### Princess Shoot (player mechanic)
- Tap anywhere during night → princess fires toward tap
- Same damage formula as turrets
- 1s cooldown shown as arc ring around princess (red draining arc = on cooldown, pulsing yellow ring = ready)

## Key Functions
| Function | Purpose |
|---|---|
| `initGrid()` | Reset grid, scatter terrain, place princess |
| `addPortal()` | Add an edge portal (one added per night cleared) |
| `canPlace(x,y)` | Checks wall placement won't trap princess from portals |
| `calcFlowFields()` | Recompute BFS — call after any grid change |
| `spawnEnemy(px,py,type)` | Create enemy at portal tile coords |
| `startNight()` | Transition to night, build `spawnQueue[]` |
| `placeTile(tx,ty)` | Handle tap-to-build logic |
| `screenToGrid(sx,sy)` | Convert screen coords to grid tile |
| `drawPrincess(cx,cy)` | Draws princess + cooldown ring |
| `showOverlay(title,msg,btn,cb)` | Win/lose/start screen |

## Planned Work (see waves.md)
- **Redesign wave spawning** — replace flat formula with scripted per-night waves
- **New enemy: Sprinter** — 3× speed, 1 HP, instant grab (Night 2+)
- **New enemy: Ghost** — phases through single walls (Night 4+)
- **New enemy: Healer** — heals nearby enemies (Night 4+)
- **Per-night gold bonuses** — replace flat +15g with night-specific rewards

## Conventions
- Tile coordinates: `(x, y)` integers. World coords: `x + 0.5` = center of tile.
- Enemy positions are in tile units (floats). Multiply by `BASE_TILE * zoom` to get screen pixels.
- Never call `calcFlowFields()` inside the game loop — only on grid changes.
- `floatingTexts` entries: `{x, y, text, timer, color}` where x/y are tile-space coords.
- Gold: wall costs 5g (refund 2g), turret costs `15 + turretCount*5g` (refund 5g), pit costs 10g (refund 3g).
