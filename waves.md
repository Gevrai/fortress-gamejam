# Wave Design — Difficulty Curve & Implementation Plan

## Difficulty Philosophy

A medium-skill player (decent maze, some turrets, occasional princess shots) should clear **Nights 1–4** with effort. **Night 5** requires deliberate money management, strong maze routing, and good kill-priority — it should feel like a wall.

Difficulty levers available in the current engine:
- Enemy count, type mix, and spawn order
- Spawn delay (time between enemies)
- HP and speed (scaled by `nightNum` in `spawnEnemy`)
- Gold reward per night (currently flat +15g)
- Number of active portals (1 added per night cleared, starts with 3)

---

## Mechanical Baseline (from code)

| Stat | Value |
|---|---|
| Starting gold | 50g |
| Wall cost | 5g (refund 2g) |
| Turret cost | 15 + 5×(existing turrets) g (refund 5g) |
| Pit cost | 10g (refund 3g) |
| Turret range | 3.5 tiles |
| Turret cooldown | 0.5s |
| Turret damage | `2 + floor(nightNum/2)` |
| Princess damage | same as turret |
| Princess cooldown | 1s |
| Normal HP (night N) | N=1: 2 HP, else `3 + N*2` |
| Tank HP (night N) | `10 + N*5` |
| Flyer HP (night N) | `2 + N` |
| Kill gold | Normal=1g, Flyer=3g, Tank=5g |

---

## Proposed Wave Structure (5 Nights)

### Night 1 — "The First Scouts"
**Goal:** Tutorial wave. Player learns enemies pathfind through the maze. Very forgiving.

- **Enemies:** 24 normals only
- **Spawn delay:** 1.5s between each
- **Total duration:** ~36s of spawning
- **Difficulty:** Easy. A bare minimum maze + 1–2 turrets survives this.
- **Gold reward:** +25g (generous — let the player over-build for Night 2)

**Why this works:** Normal HP is only 2 on Night 1. A single turret does 2 damage per shot (0.5s CD = 4 DPS) and trivially deletes them. The slow spawn rate means no overlap pressure.

---

### Night 2 — "The Vanguard"
**Goal:** Introduce Tanks and Sprinters. Tanks punish thin mazes; Sprinters punish turret coverage gaps.

- **Enemies:** 28 normals, 8 tanks, 8 sprinters
- **Spawn order:** 4 normals → 1 sprinter → 4 normals → 1 tank → 3 normals → 1 sprinter → 1 tank → 1 sprinter → 1 tank → 1 sprinter → 1 tank → 4 normals → 1 sprinter → 4 normals → 1 tank → 3 normals → 1 sprinter → 1 tank → 1 sprinter → 1 tank → 1 sprinter → 1 tank → 3 normals
- **Spawn delay:** 1.0s
- **Difficulty:** Medium-easy. One portal source, slow enough to handle with 2–3 turrets.
- **Gold reward:** +20g

**Pressure points:**
- Tanks have 20 HP on Night 2 — a single turret (3 DPS) takes ~7s. Player must funnel them into multi-turret fire.
- Sprinters have 1 HP and 3× speed — a player who left a turret-gap near the princess will feel it.

**New enemy — Sprinter:**
- Color: bright yellow `#ff4`
- Speed: 3× normal (≈ 9 tiles/s on Night 2)
- HP: 1 — any hit kills it
- Grab: instant (no 1s timer)
- Spawn visual cue: plays before tank groups so player can see the threat type

---

### Night 3 — "Air Support"
**Goal:** Force wall-agnostic coverage. Flyers bypass the maze entirely; Sprinters demand reaction from the princess's own attack.

- **Enemies:** 30 normals, 20 flyers, 10 sprinters
- **Spawn order:** 2 normals → 1 flyer → 2 normals → 1 flyer → 1 sprinter → (repeat) — flyers every 3rd spawn, sprinters scattered
- **Spawn delay:** 0.7s
- **Difficulty:** Medium. Flyers are 5 HP on Night 3, fast. A player who only walled will be exposed. Two turrets in open sightlines handle flyers; princess shots cover sprinters.
- **Gold reward:** +20g

**Pressure points:**
- 20 flyers at 3g each = 60g income if killed, but only if turrets cover open areas.
- Sprinters now move at 3× Night 3 normal speed — harder to react to.
- Spawn delay drop to 0.7s creates some bunching for the first time.

---

### Night 4 — "The Mixed Assault"
**Goal:** Introduce Ghosts and Healers. Test full defense. Require kill-prioritization.

- **Enemies:** 32 normals, 12 tanks, 16 flyers, 10 ghosts, 6 healers
- **Structure:** Two groups of ~38 with a 4s pause between them
  - Group 1: 8 normals → 3 flyers → 2 tanks → 1 healer → 3 normals → 2 ghosts → 2 flyers → 2 tanks → 1 healer → 5 normals → 3 ghosts → 2 flyers → 1 sprinter → 4 normals
  - Group 2 (after 4s): 3 ghosts → 4 normals → 2 tanks → 3 flyers → 1 healer → 5 normals → 2 tanks → 3 flyers → 1 healer → 4 ghosts → 4 normals → 2 tanks → 3 flyers → 1 healer → 5 normals → 2 ghosts → 2 tanks
- **Spawn delay:** 0.5s within groups
- **Difficulty:** Medium-hard. A player with 4+ turrets, good maze, and active princess shots can clear it. Healers embedded mid-tank-cluster reward players who target them first.
- **Gold reward:** +25g

**New enemy — Ghost:**
- Color: translucent white `rgba(220,220,255,0.6)`
- Behavior: phases through 1 consecutive wall tile (ignores single walls; double walls block it)
- HP: 3 on Night 4
- Speed: 1.5× normal
- Design impact: forces players to double-wall critical chokepoints

**New enemy — Healer:**
- Color: green `#4f4`
- Behavior: pulses a heal aura — restores 1 HP/s to enemies within 1.5 tiles
- HP: 8 on Night 4
- Speed: 0.8× normal (walks behind the cluster)
- Design impact: tanks heal back to full if healer is ignored; introduces kill-order decisions

**Pressure points:**
- Night 4 tanks have 30 HP and turrets do 4 DPS. A healer can partially negate 1 turret's output.
- The 4s group pause gives just enough breathing room to not feel overwhelming — but not enough to fully reset.

---

### Night 5 — "The Siege"
**Goal:** Overwhelming final assault. Average play loses here. Requires optimized economy (walls turned into multi-turrets early, pits at chokepoints), a long maze path, and active princess micro.

- **Enemies:** 50 normals, 24 tanks, 24 flyers, 16 ghosts, 10 healers, 12 sprinters
- **Structure:** Two rushes with a 5s break
  - Rush 1 (0.3s spawn delay): 2 sprinters → 4 normals → 2 flyers → 1 healer → 3 tanks → 3 normals → 2 ghosts → 1 sprinter → 4 flyers → 2 tanks → 5 normals → 1 healer → 2 ghosts → 1 sprinter → 4 normals → 2 flyers → 1 healer → 3 tanks → 3 normals → 2 ghosts → 1 sprinter → 4 flyers → 2 tanks → 5 normals → 1 healer → 2 ghosts → 1 sprinter
  - [5s break — last chance to tap-shoot stragglers]
  - Rush 2 (0.2s spawn delay, faster): 2 sprinters → 5 normals → 3 ghosts → 3 tanks → 2 flyers → 1 healer → 4 normals → 2 ghosts → 3 tanks → 2 sprinters → 4 flyers → 3 normals → 1 healer → 2 tanks → 2 sprinters → 5 normals → 3 ghosts → 3 tanks → 2 flyers → 1 healer → 4 normals → 2 ghosts → 3 tanks → 2 sprinters → 4 flyers → 3 normals → 1 healer → 2 tanks
- **Difficulty:** Hard. Intended to defeat players who coasted through Night 4 without optimizing.
- **Gold reward:** none (final night)

**What defeats average players here:**
- Night 5 tanks have 35 HP, turrets do 4 DPS = ~9s per tank. With 24 tanks this is brutal without 6+ turrets stacked on one path. Turret cost by turret #5 is 35g — players who didn't manage gold won't have enough.
- 24 flyers bypass the maze entirely, requiring area coverage turrets placed off-path.
- 16 ghosts punish any single-wall chokepoints the player relied on in Nights 1–4.
- Rush 2's 0.2s spawn delay creates 5 enemies alive at once before the first one dies, overwhelming sparse turret setups.
- 5 healers embedded in the tank clusters mean tanks regenerate faster than a turret deals damage unless the healer is prioritized.

**What wins Night 5 (optimal strategy required):**
- Maze path of 20+ tiles so tanks take ~10s to traverse (giving turrets multiple shots)
- At least 6 turrets including 2 covering open ground for flyers
- Pits at maze entry points to slow tanks under turret fire
- Active princess shots used on sprinters and healers, not tanks
- Gold reserved from Night 4's +25g bonus to buy 2 extra turrets before Night 5

---

## Gold Economy Across 5 Nights

| Night | Starting gold | End-of-night bonus | Approx kill income | Total available | Notes |
|-------|--------------|-------------------|--------------------|-----------------|-------|
| 1 | 50g | +25g | ~24g | ~99g | Generous — build freely |
| 2 | ~99g | +20g | ~60g | ~179g | First turret costs spike here |
| 3 | ~179g | +20g | ~118g | ~317g | Flyer kills pay well (3g each) |
| 4 | ~317g | +25g | ~190g | ~532g | Save for Night 5 turret push |
| 5 | ~532g | — | up to ~240g | — | Must spend wisely pre-wave |

Kill income assumes ~60% enemy survival (enemies reaching the princess don't drop gold). Tank kills (5g each) significantly reward good mazes that let turrets fire multiple times.

---

## New Enemy Summary

| Type | Night+ | Color | HP | Speed | Special |
|------|--------|-------|----|-------|---------|
| Sprinter | 2 | `#ff4` yellow | 1 | 3× normal | Instant grab, no grab timer |
| Ghost | 4 | `rgba(220,220,255,0.6)` | 3 | 1.5× normal | Phases through single wall tiles |
| Healer | 4 | `#4f4` green | 8 | 0.8× normal | Aura heals 1 HP/s to nearby enemies |

---

## Implementation Notes

**`startNight()` replacement:** Replace the flat `total=(4+nightNum*3)*10` formula with a scripted `spawnQueue` built from the per-night arrays above. Each entry: `{x, y, delay, type}`.

**Sprinter in `spawnEnemy()`:**
```js
else if(type==='sprinter'){hp=1; speed=(2+nightNum*.3)*3; size=.28;}
```
Grabbing logic: check `e.type==='sprinter'` in the grabbing state and skip the 1s `grabTimer`.

**Ghost in `isWalkable()` / `moveAlongFlow()`:**
Track consecutive wall tiles the ghost has passed through. Reset on non-wall tile. Block after 2 consecutive walls.

**Healer in `stepEnemies()`:**
Each frame, healers scan nearby entities within 1.5 tile radius and increment `e.hp` (capped at `e.maxHp`) by `dt * 1`.

**Gold rewards:** Change the flat `gold+=15` in `stepWaves()` to a lookup:
```js
const nightBonus=[0,25,20,20,25,0];
gold+=nightBonus[nightNum]||0;
```
