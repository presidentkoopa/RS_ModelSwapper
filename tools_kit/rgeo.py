"""Reload geometry: where a gun's magazine, magazine well and charging handle are
in the weapon controller's frame, and the ModifyBobLayer3D hooks that move a
piece of the gun's own mesh (into the off hand, down the well, back along the
handle's track).

Frame for every number: the controller's, centimetres, F forward, L left, U up
(the same as tool/hands/gunview.py). The chain is models.cpp RenderHUDModel:

    local = 0.01 * ( ((q + hook) R^T) * S + off + (0, 5, 30) )      (x right, y up, z back, m)
    q     = Ry90(swap_yz(v)) * vr_weaponScale

with R = Ry(rot.x) Rx(rot.y) Rz(rot.z) (the hook rotation, pivot 0) and S the
MODELDEF Scale (x, z, y order in local axes).
"""
import struct, math, json, sys
import numpy as np

WS = 1.02            # vr_weaponScale (the pack's tests and the hand fits use 1.02)
K = np.array([0.0, 5.0, 30.0])


def load_md3(path):
    d = open(path, 'rb').read()
    nfr, ntag, nsurf, nskin, ofr, otag, osurf, oeof = struct.unpack_from('<8i', d, 76)
    out = []
    off = osurf
    for s in range(nsurf):
        name = d[off + 4:off + 68].split(b'\0')[0].decode('latin1')
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        tris = np.frombuffer(d, dtype='<i4', count=nt * 3, offset=off + otri).reshape(nt, 3)
        xyz = np.frombuffer(d, dtype='<i2', count=snfr * nv * 4, offset=off + oxyz).reshape(snfr, nv, 4)[:, :, :3] / 64.0
        out.append(dict(name=name, tris=tris, xyz=xyz.astype(float)))
        off += oend
    return out


def rot_y(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rot_x(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def rot_z(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def rot(ypr):
    return rot_y(ypr[0]) @ rot_x(ypr[1]) @ rot_z(ypr[2])
def euler_yxz(R):
    pitch = math.degrees(math.asin(max(-1, min(1, -R[1, 2]))))
    yaw = math.degrees(math.atan2(R[0, 2], R[2, 2]))
    roll = math.degrees(math.atan2(R[1, 0], R[1, 1]))
    return [yaw, pitch, roll]


def Smat(scale):
    xs, ys, zs = scale
    return np.diag([xs, zs, ys])


def pre(v):
    """md3 vertex -> the hook's space (after the jDoom turn, before the hook)"""
    r = np.stack([v[:, 0], v[:, 2], v[:, 1]], 1) * WS
    return np.stack([r[:, 2], r[:, 1], -r[:, 0]], 1)


def to_flu(v, scale, off, hook=(0, 0, 0), ypr=(0, 0, 0)):
    """md3 vertices -> controller frame F, L, U (cm)"""
    p = pre(v) + np.array(hook, float)
    p = p @ rot(ypr).T
    xs, ys, zs = scale
    xo, yo, zo = off
    p = p * np.array([xs, zs, ys]) + np.array([xo, zo, yo]) + K       # local cm, x right y up z back
    return np.stack([-p[:, 2], -p[:, 0], p[:, 1]], 1)


def flu_to_loc(p):
    f, l, u = p
    return np.array([-l, u, -f], float)


def loc_to_flu(x):
    return np.array([-x[2], -x[0], x[1]], float)


def hook_for(scale, Rl_flu, c_from, c_to):
    """the hook (translation, yaw/pitch/roll) that turns the layer's mesh by
    Rl_flu (a rotation in the controller frame) about c_from and puts c_from
    on c_to (all F L U cm). Same MODELDEF placement as the gun."""
    P = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], float)     # flu = P @ loc
    Rl = P.T @ Rl_flu @ P                                         # in local axes
    S = Smat(scale)
    Rh = np.linalg.inv(S) @ Rl @ S                                # hook rotation (pre-scale)
    ypr = euler_yxz(Rh)
    Rh = rot(ypr)
    c0 = flu_to_loc(c_from) - K        # local cm without the fixed offset: c0 = q S + off
    c1 = flu_to_loc(c_to) - K
    # local(q) = ((q + h) Rh^T) S + off  ;  want  Rl (q S + off - c0) + c1  (column form)
    # => h Rh^T S = (off - c0) Rl^T + c1 - off  ->  needs off; off is folded in by the caller
    return Rh, ypr


def solve_hook(scale, off, Rl_flu, c_from, c_to):
    P = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], float)
    Rl = P.T @ Rl_flu @ P
    S = Smat(scale)
    Rh = np.linalg.inv(S) @ Rl @ S
    ypr = euler_yxz(Rh)
    Rh = rot(ypr)
    o = np.array([off[0], off[2], off[1]], float)                 # local x, y(=z off), z(=y off)
    c0 = flu_to_loc(c_from) - K
    c1 = flu_to_loc(c_to) - K
    w = (o - c0) @ Rl.T + c1 - o
    h = w @ np.linalg.inv(S) @ Rh
    return h, ypr


def shift_hook(scale, dflu):
    """a pure move (F L U cm) -> hook translation"""
    loc = flu_to_loc(dflu)
    xs, ys, zs = scale
    return loc / np.array([xs, zs, ys])


def surf_flu(md3, si, frame, scale, off, **kw):
    return to_flu(md3[si]['xyz'][frame], scale, off, **kw)


def pca(pts):
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c)
    return c, vt, s


if __name__ == '__main__':
    pass
