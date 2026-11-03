# pk3/

Built packages. Make them with `python tools_build_pk3.py` (Linux / any OS; the same contents and gates as
`build.ps1 -Static`), not by hand.

- **ProjBrut_MS.pk3**: the Project Brutality set. Load order: **Project Brutality 0.4.1, the PB VR offhand patch
  (ModelSwapper-PB-0.4.1-VR-Offhand-Patch.pk3, its own pk3; not baked in), then ProjBrut_MS.pk3**.
  The Quest build cut down to the 29 models the PB profile uses, plus Options > "Project Brutality VR".
  Rebuild: `python tools_build_pk3.py --pb`.
- **ModelSwapper-QUEST.pk3** (when built): the whole shelf, `python tools_build_pk3.py`.
