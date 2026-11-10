---
name: game-engineering
description: Structure game code so simulation is deterministic, testable and smooth: fixed timestep, separated update and render, explicit state, and input and asset handling that works on desktop and mobile. Use when implementing or testing a game.
---

**The loop**
- Drive the game with `requestAnimationFrame` and a fixed simulation timestep (for example 1/60 s) using an accumulator. Step the simulation zero or more times per frame, then render, interpolating if needed.
- Clamp the frame delta (for example to 100 ms) so a background tab or a slow frame cannot produce a giant step that tunnels the player through the floor.
- Physics must give the same result at 30, 60 and 144 Hz. Never scale gameplay by raw frame count.

**Separate simulation from presentation**
- Keep game logic (movement, collision, rules, level data) in pure modules with no DOM, canvas or audio calls. Rendering and sound read state and never write it.
- This is what makes the game testable: tests step the simulation headless with scripted input and assert positions, collisions and outcomes.
- One source of truth for tunables (gravity, speeds, jump velocity, sizes) in a single constants module that both the game and the tests import.

**State**
- Use an explicit state machine for the game (title, playing, paused, won, lost) and for entities with modes (idle, run, jump, fall, hurt). Transitions are named and happen in one place.
- Reset is total: restarting a level rebuilds state from level data, with no leftovers from the previous attempt.
- Level data is data: declarative arrays or JSON, validated on load, not code scattered through the update function.

**Collision and movement**
- Resolve movement axis by axis against solids (move on x, resolve, move on y, resolve). Use swept or stepped checks for fast objects so nothing tunnels.
- Keep hitboxes explicit and separate from sprite size. Derive grounded state from collision, not from position guesses.
- Prove traversal in tests: with the real movement constants, compute jump apex and range and assert every required platform and the goal are reachable with margin.

**Input**
- Sample input into an action map (left, right, jump, pause) once per frame; game logic reads actions, not key codes. Track pressed, held and released so buffering and variable jump work.
- Support keyboard and touch from the same action map; add gamepad when the genre expects it. Call `preventDefault` on game keys and touches inside the playfield.
- On the playfield and controls set `touch-action: none`, `user-select: none` and suppress the context menu and tap highlight. Leave scrolling alone on menus and overlays that need it.
- Handle `visibilitychange` and `blur`: pause the simulation and audio, clear held keys, and resume only on an explicit action.

**Rendering and assets**
- Size the canvas to the display with `devicePixelRatio` handled, keep the design aspect ratio, and scale to fill the viewport. Pixel art uses integer scaling and `image-rendering: pixelated` with smoothing off.
- Preload every image and sound before play starts and show progress. A missing asset fails loudly with its path, never as an invisible sprite.
- Draw back to front in layers; cull what is off screen. Avoid allocations in the hot loop: reuse objects and pool particles.
- Create or resume the audio context on the first user gesture. Provide mute. Cap simultaneous sounds.

**Performance budget**
- Hold 60 fps on a mid range phone. Measure frame time; keep update plus render under about 12 ms.
- Batch draws from sprite sheets, prerender static layers to offscreen canvases, and keep particle counts bounded.

**Verify before handoff**
- Run the headless simulation tests and the project checks on the final tree.
- Play in a real browser at desktop and phone viewports, with touch emulation, and check the console is clean.
- Hide and restore the tab mid play: the game must still be paused, with time and audio stopped.
