# Magazine strokes held back for review

These guns are measured and carded. The one number that is wrong is the
insertion stroke: it came from the card's mag_in phase, and on a gun whose
animation throws the spent magazine clear of the screen that phase catches
the throw, not the insertion.

The ceiling is the well depth (seat to mouth) plus the magazine's own
length along the insertion axis -- past that the magazine has left the gun.

gun                              stroke    well     mag  ceiling  reason
------------------------------------------------------------------------------------------------
MS_AE_Flamer                     182.51   10.82   28.27    39.09  stroke exceeds well depth + magazine length
MS_alien_flamer                  182.51   10.81   28.27    39.07  stroke exceeds well depth + magazine length
MS_alien_rifle                    72.08    8.43   13.10    21.53  stroke exceeds well depth + magazine length
MS_alien_pistol                   56.73   10.69   16.68    27.37  stroke exceeds well depth + magazine length
MS_chex_largezorcher              38.32    3.23    4.40     7.64  stroke exceeds well depth + magazine length
MS_chex_superlargezorcher         38.32    3.23    4.40     7.64  stroke exceeds well depth + magazine length
MS_qvplus_guns                    21.22    5.47   11.83    17.30  stroke exceeds well depth + magazine length
MS_vplus_guns                     21.22    5.47   11.83    17.30  stroke exceeds well depth + magazine length


## Two numbers worth your eye, both inside the ceiling

MS_brt_RPG / MS_d64_RPG / MS_hdvr_RPG / MS_vplus_RPG    stroke 1.64
    The shortest stroke on the shelf. The round seats shallow on this launcher
    and the ceiling is 10.61, so the mesh does support it, but 1.64 units is
    about 7cm of hand travel once scaled -- a push, not a load.

MS_brt_RailGun                                          not regenerated
    WMCARD.ww2 ships this gun at 8.82, measured by the old surface-name path.
    The new measure reads 28.64 over frames 16..28, which is OVER its 25.76
    ceiling. The two disagree, so WMCARD.ww2 was left exactly as it was committed
    rather than regenerated -- the shipping number is still 8.82. One of the two
    is wrong and the mesh has not told us which.
