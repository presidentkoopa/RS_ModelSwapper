"""Generate the FBX hands' skin tones (owner 2026-10-27 20:05): pre-tinted copies of
src/models/rsq/fbx/fbx_hand.png, one per step of the "Hand Skin Tone" option.

    python3 tools/handtones.py            # writes src/models/rsq/fbx/tones/fbx_hand_tNN.png
    python3 tools/handtones.py --sheet X  # also a swatch sheet of every tone at X.png

Never hand-painted. Each texel is recoloured in CIE Lab against the texture's own mean:
  L' = L * Lt / Lm          lightness scaled, so every shadow, crease and highlight keeps its
                            place and its ratio to the rest (shading survives)
  a' = at + (a - am) * K    hue moved to the tone, with the texture's own colour variation
  b' = bt + (b - bm) * K    (redder knuckles, paler nails) kept at K of its strength
Lt, at, bt are the tone's average colour; Lm, am, bm the texture's (measured, not typed).
Tone 0 is the texture as drawn and is not written: MODELDEF's own fbx_hand.png.
"""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'src', 'models', 'rsq', 'fbx', 'fbx_hand.png')
OUT = os.path.join(HERE, '..', 'src', 'models', 'rsq', 'fbx', 'tones')
K = 0.6

# (name, average sRGB of the tone). Index = the option's value; 0 is the texture as drawn.
TONES = [
    ('As drawn', None),
    ('Porcelain', (236, 206, 190)),
    ('Fair', (225, 184, 160)),
    ('Light', (210, 165, 130)),
    ('Olive', (190, 145, 105)),
    ('Tan', (170, 120, 85)),
    ('Medium brown', (145, 95, 62)),
    ('Brown', (120, 76, 48)),
    ('Dark brown', (95, 58, 36)),
    ('Deep brown', (70, 42, 27)),
    ('Ebony', (50, 30, 20)),
    ('Undead grey', (130, 130, 125)),
    ('Green', (95, 145, 80)),
    ('Blue', (70, 110, 190)),
    ('Purple', (135, 85, 175)),
    ('Demon red', (175, 55, 45)),
    ('Gold', (210, 170, 60)),
    ('Black glove', (38, 38, 42)),
]

def srgb_to_lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def lab_to_srgb(lab):
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1.0, 1.08883])
    Mi = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])
    c = np.clip(xyz @ Mi.T, 0, 1)
    c = np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)
    return np.clip(np.round(c * 255), 0, 255).astype(np.uint8)

def main():
    img = Image.open(SRC).convert('RGB')
    lab = srgb_to_lab(np.asarray(img, dtype=np.float64))
    mean = lab.reshape(-1, 3).mean(0)
    os.makedirs(OUT, exist_ok=True)
    made = []
    for i, (name, rgb) in enumerate(TONES):
        if rgb is None:
            made.append((name, img))
            continue
        t = srgb_to_lab(np.array(rgb, dtype=np.float64))
        out = np.empty_like(lab)
        out[..., 0] = np.clip(lab[..., 0] * t[0] / mean[0], 0, 100)
        out[..., 1] = t[1] + (lab[..., 1] - mean[1]) * K
        out[..., 2] = t[2] + (lab[..., 2] - mean[2]) * K
        im = Image.fromarray(lab_to_srgb(out))
        im.save(os.path.join(OUT, 'fbx_hand_t%02d.png' % i), optimize=True)
        made.append((name, im))
    print('texture mean Lab %.1f %.1f %.1f; wrote %d tones to %s' % (tuple(mean) + (len(TONES) - 1, OUT)))
    if '--sheet' in sys.argv:
        from PIL import ImageDraw
        S = Image.new('RGB', (6 * 160, 3 * 176), (16, 16, 16))
        for i, (name, im) in enumerate(made):
            x, y = (i % 6) * 160, (i // 6) * 176
            S.paste(im.resize((160, 160)), (x, y))
            ImageDraw.Draw(S).text((x + 3, y + 162), '%d %s' % (i, name), fill=(255, 255, 0))
        S.save(sys.argv[sys.argv.index('--sheet') + 1])

if __name__ == '__main__':
    main()
