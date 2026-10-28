"""Build step for the "Hand Skin Tone" option (zscript/rsq/handtone.zs). Called by build.py on every MODELDEF lump.

Every MODELDEF block that wears the FBX hands' skin (Skin 0 "fbx_hand.png", the hand mesh as Model 0) is
re-indexed to model slot HAND_SLOT in the BUILT pk3: Model 0 -> Model 7, Skin 0 -> Skin 7, and its
FrameIndex lines' model 0 -> 7. The mesh, frames, scale and offsets are untouched, so it draws exactly
the same. What it buys: the FBX hand is then the only thing in model slot 7 on ANY actor, so
A_ChangeModel's skin override on slot 7 re-skins the FBX hand and nothing else -- not a gun hung on
the same actor (dual-wield RSQ_Off_*, the rsqdual and Purist weapon classes), and never Ermac's hands,
which stay in slot 0. Slot 7 is free: no MODELDEF here uses a model index above 1 (checked by build).

src/ is never rewritten: the hand rows other lanes edit stay as they are, and every build re-derives
the slot from whatever rows exist.
"""
import re

HAND_SLOT = 7
_BLOCK = re.compile(r'(Model\s+\w+\s*\{)(.*?)(\})', re.S | re.I)
_SKIN = re.compile(r'(\bSkin\s+)0(\s+"fbx_hand\.png")', re.I)

def transform(text):
    """-> (new text, number of blocks re-indexed). Raises if slot HAND_SLOT is already used."""
    for m in re.finditer(r'^\s*Model\s+(\d+)\s', re.sub(r'//[^\n]*', '', text), re.M | re.I):
        if int(m.group(1)) == HAND_SLOT:
            raise SystemExit('handtone_build: a MODELDEF already uses model index %d' % HAND_SLOT)
    n = [0]
    def one(m):
        body = m.group(2)
        code = re.sub(r'//[^\n]*', '', body)
        if not _SKIN.search(code) or not re.search(r'^\s*Model\s+0\s', code, re.M | re.I):
            return m.group(0)
        n[0] += 1
        body = re.sub(r'(^\s*Model\s+)0(\s)', r'\g<1>%d\2' % HAND_SLOT, body, flags=re.M | re.I)
        body = _SKIN.sub(r'\g<1>%d\2' % HAND_SLOT, body)
        body = re.sub(r'(^\s*FrameIndex\s+\S+\s+\S+\s+)0(\s+\d+)', r'\g<1>%d\2' % HAND_SLOT, body, flags=re.M | re.I)
        return m.group(1) + body + m.group(3)
    return _BLOCK.sub(one, text), n[0]
