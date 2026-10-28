# Fit farm round 3: picks (2026-10-27)
Picked by index pad to trigger, then penetration, then palm gap, at the trigger pose (job.json metrics.curl.trigger; support = metrics.bake.sup_pen). cm.
- BFG10k <- BFG10k_fromMinigun (pad 0.00 [index solved to trigger], pen 0.58, palm 0.49, support 0.44; 66.95 min, batch r2b). Rejected: BFG10k 1.92 start (pad 6.86, pen 1.23).
- BIG_FUCKING_GUN <- BIG_FUCKING_GUN_fromMinigun (pad 0.00 [index solved to trigger], pen 0.60, palm 0.69, support 0.44; 74.98 min, batch r2b). Rejected: 1.92 start (pad 5.50, pen 0.59).
- IncendiaryLauncher <- IncendiaryLauncher_fromGrenadeLauncher (pad 0.44, pen 0.95, palm 0.62, support 0.43; 11.97 min, batch r3). Replaces the round-1 fit (pad 5.22, pen 1.30), kept aside as .old_IncendiaryLauncher_1546/.
  Judgement call: IncendiaryLauncher_fromMinigun has the lower pad (0.00 vs 0.44) but pen 1.53 (worse than round 1's 1.30); both pads are under the fitter's own 1 cm trigger threshold, so penetration decided. Pen 0.95 cm is still high: flag for a look.
- Devastator <- Devastator_fromRocket_Launcher (pad 1.32, pen 0.58, palm 0.02, support 0.49; 22.83 min, batch r3). Others: fromMinigun (pad 2.60, pen 0.79, palm 0.01; 21.79 min), 1.92 start (pad 3.09, pen 0.62).
  Weak: the index solve (both starts went M/R/P -> index solved) still leaves the pad 1.32 cm off the trigger, over the fitter's 1 cm threshold. Best of the three asked for; flag before porting.
