# Running a weapon set through the engine, and reading what comes back

**For a lane building any set in this depot.** This is how the bd22q work was checked: the game
is launched, it plays itself, and the log is read. No automation framework, no input faking.

    sh gate/run_set.sh gate/<yourset>.gate dist/<yourset>.pk3

Copy `gate/bd22q.gate`, change the paths, the parent files, the guns and their ammo. That file
is the whole per-set part.

---

## 1. How it works, in one paragraph

GZDoom's console takes commands chained with `;`, and it has a `wait N` that pauses N tics.
`+attack`, `-attack` and `+reload` are the same commands your keybinds fire. So one
`+"wait 40; god; give Rifle; use Rifle; wait 40; +attack; wait 25; -attack; +reload; ... quit"`
argument makes the engine give itself the guns, switch to each, hold the trigger, reload, and
quit. `+logfile` writes everything to a file you then grep. That is the entire trick.

---

## 2. What it proves, and what it cannot

**Proves:** the pack parses; the map starts; each gun can be selected, fired and reloaded; the
run reached the end instead of dying in the middle.

**Cannot prove:**

- **Anything in VR.** It runs `+vr_mode 0`. Hands, melee, grabs and any pose code return early
  outside a headset and never execute at all. A clean gate says nothing about them.
- **Anything about how it looks.** It has no eyes. It can tell you a thing *ran*; never that it
  is in the right place, the right size or the right colour.
- **That a gun fired.** The per-gun marker proves the SCRIPT reached that gun. It does not prove
  the class name was real, that the gun was given, that it had ammo, or that a shot came out.
  For that, see §4.

---

## 3. Every way this thing passes while testing nothing

All of these happened on bd22q. Each one cost at least a session, and each one ends with a green
run. **Assume you have one of these until you have proved you do not.**

| The hole | What it looks like | The fix |
|---|---|---|
| **The pk3 is never loaded.** A relative `-file` and the script `cd`s to the engine dir first. | Perfect run. Every marker. Exit 0. The engine loaded the parent mod and nothing else. | `run_set.sh` resolves every path to absolute before the `cd`, and refuses if one is missing. |
| **The gun has no ammo.** You gave `Shell`; the mod's `Weapon.AmmoType1` is `AmmoShell`. | The gun is there, selected, `+attack` does nothing. No casing, no flash, no impact — and nothing in the log says so. | Read each gun's `AmmoType1` out of its own DECORATE and give that. |
| **The gun never raised.** `use X; wait 10; +attack` and the mod's select animation is 30 tics. | Marker present, gun never fires. | `RAISE=40` in the config. If a gun shows a marker and produces no effect, suspect this first. |
| **A fatal script error does not reach stdout.** | The redirected log just... stops, looking clean. | `+logfile` as well as the redirect. Read `<log>.engine`. |
| **`echo "exit $?"` after a grep** reports the GREP's status. | "exit 0" on a crashed run, as long as the grep found nothing. | Capture `rc` immediately after the run. |
| **"No errors found" is not "it ran".** | A silent early death looks identical to a clean pass. | Count markers. `run_set.sh` prints one per gun and warns on any zero. |
| **A stale pk3 somewhere else.** | You gate `dist/x.pk3` and launch a copy from your Desktop. | The runner prints size, mtime and lump count; the engine prints `adding …, N lumps`. Match them. |
| **`xvfb-run` is not installed.** | `timeout` says "failed to run command" and the line still reports exit 0. | Used only where it exists. |
| **An EventHandler that is not registered** compiles, ships, and never runs. | Everything passes. The feature does nothing. | It must be in MAPINFO's `AddEventHandlers`. Prove it with §4. |

**Never run it fullscreen.** Standing rule. `-width 640 -height 480 +vid_fullscreen 0`.

---

## 4. Proving a thing actually fires

A clean compile is exactly what dead code looks like. When you need to know a code path
*executed* — not that it built — print from inside the running game:

1. Add a `Console.Printf` at the point in question, **in the built tree only**, never in the
   generator:

       Console.Printf("MYTAG %s -> %s", a, b);

2. Build a throwaway pk3: `python tools/bd22_plus.py pk3 dist/<set>_test.pk3`
3. Run the gate on it, then `grep MYTAG gate/<set>.log.engine`
4. Delete the test pk3, regenerate clean, and check the tag is gone before committing.

This is how every "N times" claim in this repo's commit messages was made, and it is what caught:

- a bullet flying **through** the wall it had just hit (`ttl 1`, `step 777`, a 400-unit shot)
- a pose handler that was **never registered** and printed zero of either half
- a casing model lend sitting behind a VR gate, so it could never run under the gate
- a whole gate leg firing nothing because of one wrong ammo class name

None of those is visible in a compile, and none would have been caught by reading the code.

---

## 5. The config

`gate/<set>.gate` is sourced as shell. The fields:

| field | meaning |
|---|---|
| `QZD` | the engine build directory (must contain `qzdoom` or `qzdoom.exe`) |
| `IWAD` | the iwad. Mind what your parent mod needs — BD22 needs doom2.wad, not Freedoom |
| `FILES` | parent mods, in load order, **before** the set under test |
| `PK3` | the set under test (overridable as argv 2) |
| `GUNS` | **class names** from the mod's DECORATE, not display names |
| `AMMO` | console `give` lines — read each gun's `AmmoType1` |
| `RAISE` `FIRE` `SETTLE` | tics to wait after `use`, while firing, and after reloading |
| `RELOAD` | 0 to skip the reload leg |
| `EXTRA` | any extra console commands before `quit` |
| `IGNORE` | a regex of faults from the parent mod that are not yours |
| `TIMEOUT` `WARP` `GOD` | wall-clock seconds, the map, and godmode (on by default) |

`god` is on by default because a gate that dies partway still prints its final marker and still
exits 0 — the `quit` runs either way. It just stops firing anything first.

---

## 6. A pass

    exit 0
    "script parsing took … ms"  in <log>.engine
    GATE_DONE present
    every gun in the list non-zero
    no faults outside IGNORE

Anything less is not a pass, however green it looks.
