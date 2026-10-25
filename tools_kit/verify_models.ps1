# verify_all.ps1 -- one engine launch per model, the other lane's discipline:
# a marker per gun, and the gun's OWN reload phases counted, never a clean log.
#
# One launch each because rs_fm_picks is read once at startup: RS_ForeignModelHandler
# does `if (!mPicks) mPicks.Load()`, and Rescan() restores pinned rows from memory,
# so setting the cvar mid-run changes nothing. Rather than put a test-only path into
# shipping code, each model gets its own engine.
#
# The host weapon is Doomablo's rwPistol, which reloads: the host supplies the reload
# states, our mesh supplies the geometry. That is the whole point -- any mesh on any
# reloading gun.
param([string] $ModelsJson, [string] $Out, [string] $Host_ = 'rwPistol', [int] $Limit = 0)

$sp   = 'C:\Users\Command\AppData\Local\Temp\claude\E--DOOMWork-UZDXREMA\41c253b2-0e7e-44c4-807f-185f9dc7e0d1\scratchpad\rtest'
$boot = 'E:\DOOMWork\tools\main_boottest\main_boottest.ps1'
$pk3  = 'E:\DOOMWork\RS_ModelSwapper\ModelSwapper-QUEST.pk3'
$mod  = 'E:\DOOMWork\doomablo_0.9.1a.pk3'
$ovl  = Join-Path $sp 'ms_rtest_overlay.pk3'
$zdl  = Join-Path $sp 'empty.zdl'

$models = Get-Content -Raw $ModelsJson | ConvertFrom-Json
if ($Limit -gt 0) { $models = $models | Select-Object -First $Limit }

"model,archetype,index,slot,took_slot,empty,carry,insert,seated,done,parsed,verdict" | Set-Content -Encoding utf8 $Out

foreach ($m in $models) {
    $name = $m[0]; $arch = $m[1]; $idx = $m[2]; $slot = $m[3]
    $ammo = if ($m.Count -gt 4 -and $m[4]) { $m[4] } else { 'Clip' }
    $picks = '"' + $Host_ + ':' + $arch + ':' + $idx + ':' + $idx + '"'
    # GIVE THE GUN ITS OWN RESERVE. Without this the off hand has nothing to reach for:
    # a reload starts, the magazine leaves the gun, and the grab never happens because no
    # spare exists. Every non-Clip gun "failed" on the first pass for exactly this, and the
    # reserve class is in our own table (RSR_Guns.Reserve), not guessed.
    $chain = '+"wait 40; give ' + $ammo + ' 400"'
    $extra = "+set rs_fm_picks $picks +rsrtest_script 1 +rsr_debug 1 +rsr_grab_with 1 $chain"
    $res = & $boot -TimeoutSec 200 -Tics 900 -Zdl $zdl -ExtraArgs $extra `
                   -ExtraFiles @($mod, $pk3, $ovl) 2>&1 | Out-String
    $logPath = ($res -split "`n" | Where-Object { $_ -match 'full output: (.+)' } |
                ForEach-Object { $Matches[1].Trim() } | Select-Object -Last 1)
    $took = ''; $e=0; $c=0; $i=0; $s=0; $d=0; $parsed=0
    if ($logPath -and (Test-Path $logPath)) {
        $log = Get-Content -Raw $logPath
        if ($log -match 'took \w+ \(slot (\d+)\)') { $took = $Matches[1] }
        $e = ([regex]::Matches($log, 'IDLE -> EMPTY')).Count
        $c = ([regex]::Matches($log, 'EMPTY -> CARRY')).Count
        $i = ([regex]::Matches($log, 'CARRY -> INSERT')).Count
        $s = ([regex]::Matches($log, 'INSERT -> SEATED')).Count
        $d = ([regex]::Matches($log, 'SEATED -> DONE')).Count
        if ($log -match 'script parsing took') { $parsed = 1 }
    }
    $verdict = if ($parsed -eq 0) { 'NO COMPILE' }
               elseif ($took -ne "$slot") { "WRONG SLOT ($took)" }
               elseif ($s -gt 0 -and $d -gt 0) { 'RELOADS' }
               elseif ($e -gt 0) { 'STARTS ONLY' }
               else { 'NOTHING' }
    "$name,$arch,$idx,$slot,$took,$e,$c,$i,$s,$d,$parsed,$verdict" | Add-Content -Encoding utf8 $Out
    Write-Output ("{0,-28} slot {1,-3} -> {2}" -f $name, $slot, $verdict)
}
Write-Output "done -> $Out"
