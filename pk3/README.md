# pk3/

Built packages. Make them with `python tools_build_pk3.py` (Linux / any OS; the same contents and gates as
`build.ps1 -Static`), not by hand.

- **ProjBrut_MS.pk3**: the Project Brutality set. Load order: **Project Brutality 0.4.1, then ProjBrut_MS.pk3**.
  The Quest build cut down to the 29 models the PB profile uses, plus PB's VR patch (guns in either hand, casings and
  smoke from the gun) and Options > "Project Brutality VR". Rebuild: `python tools_build_pk3.py --pb <PB zip or folder>`.
- **ModelSwapper-QUEST.pk3** (when built): the whole shelf, `python tools_build_pk3.py`.
