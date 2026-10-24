# Package ModelSwapper.pk3.
#
# A pk3 is a zip, and zip entries must use forward slashes. Compress-Archive on
# Windows PowerShell writes BACKSLASHES, which GZDoom cannot read -- so this
# builds the archive entry by entry instead.

param(
    # Build the stock-GZDoom / QuestZDoom package instead of the desktop
    # one: zscript/static/RS_ForeignFork.zs is shipped in place of
    # zscript/RS_ForeignFork.zs, which is the ONLY file that differs.
    # Static models, no animation, no fork required.
    [switch]$Static
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = $PSScriptRoot
# The -REMAP suffix existed while the rebuilt engine lived in a second
# worktree beside the old one: two identically named pk3s in two folders is
# how a test session silently loads the wrong build and produces results that
# test nothing. That branch is now main and there is one tree, so the PCVR
# build takes the plain name again. The Quest build keeps a distinct one --
# it is a genuinely different artifact (static shim, no animation table) and
# must never be mistaken for the full build in a load order.
$out  = Join-Path $root $(if ($Static) { 'ModelSwapper-QUEST.pk3' } else { 'ModelSwapper.pk3' })

# Everything that belongs in the pk3. Anything else in the repo (README, this
# script, .git) stays out.
$include = @('zscript.txt', 'modeldef', 'MENUDEF', 'CVARINFO', 'MAPINFO', 'KEYCONF')
# Donors anchor on stock Doom sprite names, so this pk3 ships no sprite lumps
# at all.
$dirs    = @('zscript', 'models')
# -Static (Quest) additionally ships the VR reload / hands / melee code and the
# model cards. The desktop build does not: that code is QuestZDoom 17.3's, and the
# REMA version of it is a separate pass.
if ($Static) { $dirs += @('zscript_depot') }
# The model cards must be ROOT lumps, never a subfolder. GZDoom gives a pk3
# entry in an unrecognised subfolder Namespace ns_hidden and ZEROES its short
# name (filesystem.cpp, SetFromLump) -- so Wads.FindLump("WMCARD", ...), which
# is how the card reader finds them, would match nothing at all.
if ($Static) { $include += (Get-ChildItem $PSScriptRoot -Filter 'WMCARD.*' -File | ForEach-Object { $_.Name }) }
# SYNTAX CHECK BEFORE PACKING.
#
# build.ps1 only zips -- it never read the ZScript, and compile-testing
# meant launching the engine, which is no longer done. That gap shipped a
# trailing comma in an array initialiser and the first thing to notice was
# the game refusing to start. This closes it: cheap, no engine, and it
# fails the build rather than the user's next launch.
$lint = Join-Path $root 'tools_zs_lint.py'
if (Test-Path $lint) {
    & python $lint | Write-Host
    if ($LASTEXITCODE -ne 0) { throw "tools_zs_lint.py found problems -- not packing" }
}

$files = @()
foreach ($f in $include) {
    $p = Join-Path $root $f
    if (Test-Path $p) { $files += Get-Item $p } else { Write-Warning "missing: $f" }
}
foreach ($d in $dirs) {
    $p = Join-Path $root $d
    if (Test-Path $p) { $files += Get-ChildItem $p -Recurse -File } else { Write-Warning "missing: $d/" }
}

# zscript/static/ is the alternate fork shim, never shipped as itself --
# it is either substituted for zscript/RS_ForeignFork.zs (-Static) or
# left out entirely. Two RS_Fork classes in one pk3 would not compile.
$files = $files | Where-Object { $_.FullName -notmatch '\\zscript\\static\\' }
# quest/ holds -Static replacements for root lumps; never shipped at that path.
$files = $files | Where-Object { $_.FullName -notmatch '\\quest\\' }
# .pdn is Paint.NET's layered source for a skin -- the engine cannot read it, and
# the ones that came in beside the blend-file meshes were 26MB of dead weight.
# Keep them on disk next to the mesh they belong to; just never pack them.
$files = $files | Where-Object { $_.Extension -ne '.pdn' }
# models/blend/ is the blend re-export experiment: meshes rebuilt from the .blend
# sources, untextured, and referenced by no MODELDEF. The finished packages under
# models/wolf, models/hacx, models/meat and models/bd replaced them -- those arrived
# with their textures and their authors' MODELDEFs. Packing blend/ put 577MB of
# unreferenced geometry in the pk3 and took it from 30MB to 567MB.
$files = $files | Where-Object { $_.FullName -notmatch '\\models\\blend\\' }
# Pack only the model folders modeldef actually names. The imported weapon packages
# arrive whole -- weapons, pickups, ammo, decorations -- and a package nothing has
# been wired to yet is 177MB of geometry the engine will never ask for. This is
# derived, not a list, so a folder starts shipping the moment a Model block points
# at it. The asset-ref check below is what catches an over-exclusion.
$mdRefs = [regex]::Matches((Get-Content (Join-Path $root 'modeldef') -Raw), '(?i)Path\s+"models/([^/"]+)') |
          ForEach-Object { $_.Groups[1].Value.ToLower() } | Sort-Object -Unique
$files = $files | Where-Object {
    if ($_.FullName -notmatch '\\models\\([^\\]+)\\') { return $true }
    $mdRefs -contains $matches[1].ToLower()
}

$fs  = [System.IO.File]::Open($out, 'Create')
$zip = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Create)
foreach ($f in $files) {
    $rel = ($f.FullName.Substring($root.Length + 1)) -replace '\\', '/'
    $src = $f.FullName

    # The one substitution that makes the static build a build flag
    # rather than a second codebase.
    if ($Static -and $rel -eq 'zscript/RS_ForeignFork.zs') {
        $src = Join-Path $root 'zscript/static/RS_ForeignFork.zs'
    }

    # -Static overrides, generally: a root lump with a counterpart under quest/
    # ships that one instead. Additive and default-off -- with no quest/ directory,
    # or no counterpart for a lump, nothing changes for either build.
    $qp = Join-Path $root ('quest/' + $rel)
    if ($Static -and (Test-Path $qp)) { $src = $qp }

    $b = [System.IO.File]::ReadAllBytes($src)

    $e   = $zip.CreateEntry($rel, [System.IO.Compression.CompressionLevel]::Optimal)
    $st  = $e.Open()
    $st.Write($b, 0, $b.Length)
    $st.Close()
}
$zip.Dispose()
$fs.Close()

# Verify: forward slashes only, and every modeldef asset reference resolves.
$z     = [System.IO.Compression.ZipFile]::OpenRead($out)
$names = @{}
$z.Entries | ForEach-Object { $names[$_.FullName.ToLower()] = $true }

$bad = ($z.Entries | Where-Object { $_.FullName -match '\\' }).Count

$md = $z.Entries | Where-Object { $_.FullName -eq 'modeldef' }
$sr = New-Object System.IO.StreamReader($md.Open())
$txt = $sr.ReadToEnd(); $sr.Close()

$path = ''; $refs = 0; $miss = 0
foreach ($line in ($txt -split "`n")) {
    if ($line -match '^\s*Path\s+"([^"]+)"') {
        $path = $matches[1].Replace('\', '/').TrimEnd('/')
    }
    elseif ($line -match '^\s*(?:Model|Skin)\s+\d+\s+"([^"]+)"') {
        $refs++
        $key = ($path + '/' + $matches[1]).ToLower()
        if (-not $names.ContainsKey($key)) { Write-Warning "unresolved asset: $key"; $miss++ }
    }
}
# Donor consistency. A duplicate Model block shipped once as a duplicate
# ZScript stub and refused to compile at all; a donor named in the shelf but
# absent from modeldef is silently dropped instead, which is worse because it
# looks like it worked.
$md      = ($z.Entries | Where-Object { $_.FullName -eq 'modeldef' })
$sr2     = New-Object System.IO.StreamReader($md.Open())
$mdtxt   = $sr2.ReadToEnd(); $sr2.Close()
$donors  = [regex]::Matches($mdtxt, '(?m)^Model\s+(\S+)') | ForEach-Object { $_.Groups[1].Value }
$dupes   = $donors | Group-Object | Where-Object { $_.Count -gt 1 }

$zsE     = $z.Entries | Where-Object { $_.FullName -eq 'zscript.txt' }
$sr3     = New-Object System.IO.StreamReader($zsE.Open())
$zstxt   = $sr3.ReadToEnd(); $sr3.Close()
$stubs   = [regex]::Matches($zstxt, '(?m)^class\s+(\S+)\s*:') | ForEach-Object { $_.Groups[1].Value }
$stubdup = $stubs | Group-Object | Where-Object { $_.Count -gt 1 }
$nostub  = $donors | Where-Object { $stubs -notcontains $_ }

foreach ($d in $dupes)   { Write-Warning "duplicate Model block: $($d.Name)" }
foreach ($d in $stubdup) { Write-Warning "duplicate class stub: $($d.Name)" }
foreach ($d in $nostub)  { Write-Warning "donor with no class stub: $d" }

$mb = [math]::Round((Get-Item $out).Length / 1MB, 1)
$n  = $z.Entries.Count
$z.Dispose()

Write-Host "$(Split-Path $out -Leaf)  --  $n entries, $mb MB$(if ($Static) { '  [STATIC / stock GZDoom]' })"
Write-Host "  backslash entries : $bad"
Write-Host "  asset refs        : $refs checked, $miss unresolved"
Write-Host "  donors            : $($donors.Count), $($dupes.Count) duplicate, $($nostub.Count) unstubbed"
if ($bad -gt 0 -or $miss -gt 0 -or $dupes.Count -gt 0 -or $stubdup.Count -gt 0 -or $nostub.Count -gt 0) {
    throw "package verification failed"
}
