---
name: game-design-feel
description: Design and build games that are readable, fair and satisfying to control, judged by the conventions of their own genre. Use when specifying or building any playable game.
---

A game is judged in the hands, not in the code. It must be reachable, readable and responsive before anything else matters. Judge it against the genre the project declares, never against standards imported from another genre.

**Core loop first**
- State the loop in one sentence: what the player does, what resists them, what they get. Build that loop until it is fun with placeholder art before adding content.
- Teach through play: the first screen of the first level introduces one verb in a safe space, then tests it, then combines it. No wall of instructions.
- Difficulty rises in steps with rests between them. A new mechanic arrives alone before it is mixed with others.

**Controls and game feel**
- Input responds on the same frame. Movement has a tuned curve: short acceleration, quick stop, a top speed that suits the level scale.
- For jumping games: variable jump height on release, coyote time (about 80 to 120 ms after leaving a ledge), jump buffering (about 100 ms before landing), faster fall than rise, and a forgiving hitbox slightly smaller than the sprite for hazards and slightly larger for pickups.
- Tune numbers against the level geometry: jump apex and distance must clear every required gap and platform with margin. Prove reachability with the real movement code, not by eye.
- The camera leads the player in the direction of travel, smooths without lagging, and never hides what is about to hurt them.

**Readability**
- The player character, hazards, pickups and solid ground are distinguishable at a glance by silhouette, value contrast and motion. Background art sits lower in contrast and saturation than the play layer.
- Sprites are big enough to read on a phone. The playfield fills the screen; no postage stamp game in a sea of empty page.
- Every state the player needs is visible: health, score, objective, what is interactive. Text is legible at the smallest supported viewport.
- Art is coherent across stages: same character proportions, palette logic, line weight and light direction. Use the committed asset pack; do not mix styles.

**Feedback (juice) in service of clarity**
- Every player action and every consequence gets a response in at least two channels: animation, sound, particles, a short screen shake or hit pause, a number or flash.
- Squash and stretch on jump and land, anticipation before big moves, a clear hurt and death read, a rewarding pickup and goal moment.
- Depth is shown, not claimed: parallax layers move at visibly different rates.
- Sound matters: distinct, short effects for jump, land, hit, pickup, win and lose, plus music that can be muted. Audio starts only after a user gesture.

**Fairness**
- The player can always see a threat in time to react. No blind jumps, no hits from off screen, no death without a visible cause.
- Failure is cheap: fast restart, sensible checkpoints, no long unskippable sequences.
- Every level is completable. Every platform and the goal are reachable with the shipped movement values.

**Platform basics**
- Keyboard, touch and (where relevant) gamepad all work. Touch controls are at least 44 px, placed for thumbs, and never select text, scroll the page or trigger browser gestures during play.
- Pause exists on every input method, survives the tab being hidden and restored, and stops time and audio.
- Title, play, pause, win and lose screens all exist and all lead somewhere.

**Before you hand off, check**
- Play it start to finish on the final tree, on a desktop and at a phone viewport. Note anything that felt unfair, unclear or sluggish and fix or report it.
- Capture real gameplay frames as evidence; a title screen alone proves nothing about play.
