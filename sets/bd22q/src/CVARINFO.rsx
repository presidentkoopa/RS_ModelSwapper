// BD 2.0 (zscript/rsq/playerrounds.zs). Options: RSQ_Options in MENUDEF.rsq.

// "Player Ballistics: Hitscan / Bullet" (owner, 2026-10-27 11:21). 0 Hitscan = BD22 as it ships;
// 1 Bullet = the player's hitscans fly as real rounds. A server cvar: it decides where shots go.
server int sv_rsq_player_ballistics = 0;

// "Shot Tracers: Off / Dakka" (owner, 2026-10-27 20:02): Dakka's additive tracer from the drawn muzzle to the hit,
// and its impact sparks (zscript/rsq/shotfx.zs). Server: the sparks are real actors using playsim random numbers.
server int rsq_shot_tracers = 1;	// owner 21:2x: Dakka on by default; he judges the Quest cost in the headset

// "Pump Shotgun Spread: Stock / Enhanced" (owner's label, 2026-10-27 20:02). Stock = BD22's Shot_Gun spread;
// Enhanced = Dakka's shotgun pattern, 3 deg across x 2.5 deg up/down, same pellets and damage
// (actors/Weapons/Shotgun.dec). Server: it decides where shots go.
server int rsq_pump_spread = 0;

// "Hand Skin Tone" (owner, 2026-10-27 20:05): 0 = the FBX hands as drawn, 1..17 = tools/handtones.py's tones
// (zscript/rsq/handtone.zs). Local: your own hands.
user int rsq_hand_tone = 0;
