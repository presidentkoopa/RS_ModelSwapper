"""Support-hand placement: the off hand on the front of each two-handed gun,
wrapped round the gun hand on pistols. Computes the hook (translation, rotation)
RSQ_Hands.ModifyBobLayer3D returns for the support layer, whose MODELDEF block
is the hand mesh mirrored (Scale -0.75 0.75 0.75: a left hand), and renders checks.

All positions are the weapon controller's frame in cm: F forward, L left, U up.
"""
import sys, math, json
import numpy as np
sys.path.insert(0, 'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit/melee')
import guns, gunview, hudrender

S = 'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit'
HAND = S + '/tool/vrmelee/models/rsq/hand.md3'
GRIP_FRAME = 1                      # stripped hand.md3: 1 = the fist round a grip
H0 = np.array([0, -14.7, -34.7])    # gun hand hook (measured on the pistol grip)
K = np.array([0, 5, 30])            # RenderHUDModel's fixed translate (cm)
SC = 0.75

def flu_to_local(p):
    f, l, u = p
    return np.array([-l, u, -f], float)

def local_to_flu(x):
    return np.array([-x[2], -x[0], x[1]])

# the gun hand's grip: centre and axes (local x right, y up, z back)
C0 = flu_to_local((-5.5, 0, -8.5))
_ax = np.array([-0.41, 0, -0.91])                      # F, L, U: down the grip, leaning back
A_GRIP = flu_to_local(_ax)                             # index -> little finger
F_GRIP = flu_to_local((0.91, 0, -0.41))                # toward the finger pads

def frame(a, f):
    a = a / np.linalg.norm(a); f = f - a * (f @ a); f /= np.linalg.norm(f)
    return np.stack([a, f, np.cross(a, f)], 1)

def euler_yxz(R):
    """R = Ry(yaw) Rx(pitch) Rz(roll), hudrender's rot_y/rot_x/rot_z"""
    pitch = math.degrees(math.asin(max(-1, min(1, -R[1, 2]))))
    yaw = math.degrees(math.atan2(R[0, 2], R[2, 2]))
    roll = math.degrees(math.atan2(R[1, 0], R[1, 1]))
    return [yaw, pitch, roll]

def rot(ypr):
    y, p, r = ypr
    return hudrender.rot_y(y) @ hudrender.rot_x(p) @ hudrender.rot_z(r)

def solve(target_flu, a_real_flu, f_real_flu):
    """hook and rotation that put the mirrored fist's grip centre at target,
    its index->little-finger axis along a_real and its finger pads toward f_real
    (all real-world directions, F L U)"""
    M = np.diag([-1.0, 1, 1])
    a_pre = M @ flu_to_local(a_real_flu)
    f_pre = M @ flu_to_local(f_real_flu)
    Q = frame(a_pre, f_pre) @ frame(A_GRIP, F_GRIP).T
    ypr = euler_yxz(Q)
    Q = rot(ypr)
    t = flu_to_local(target_flu)
    hook = H0 + (K - C0) / SC + Q.T @ (M @ (t - K)) / SC
    return [round(float(x), 2) for x in hook], [round(float(x), 2) for x in ypr]

def gun_verts(c):
    it = guns.item(c)
    return np.concatenate([gunview.to_fl(hudrender.to_local(raw, it)) for _, raw in gunview.item_mesh(it)])

def section(c, f):
    """points where the gun's surface crosses the plane F = f (F, L, U cm)"""
    it = guns.item(c)
    pts = []
    for tris, raw in gunview.item_mesh(it):
        v = gunview.to_fl(hudrender.to_local(raw, it))
        a, b, d = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
        for p, q in ((a, b), (b, d), (d, a)):
            s = (p[:, 0] - f) * (q[:, 0] - f)
            m = s < 0
            if m.any():
                w = (f - p[m, 0]) / (q[m, 0] - p[m, 0])
                pts.append(p[m] + (q[m] - p[m]) * w[:, None])
    return np.concatenate(pts) if pts else np.zeros((0, 3))

def front_point(c, f, lmax=4.0):
    """the support point on the front at F = f: the cross-section's middle if it
    is thin enough to wrap, else 2.5 cm above its underside"""
    v = section(c, f)
    m = abs(v[:, 1]) < lmax
    if not m.any():
        raise SystemExit('%s: nothing at F %s' % (c, f))
    lo = v[m, 2].min()
    # the lowest connected run of the section (stop at a 2 cm gap)
    us = np.sort(v[m, 2])
    hi = lo
    for u in us:
        if u - hi > 2.0:
            break
        hi = u
    u = lo + min(2.5, (hi - lo) / 2)
    return [f, 0.0, round(float(u), 2)], (float(lo), float(hi))

def hand_item(hook, ypr, mirror=True, color=(225, 170, 135)):
    return dict(path=HAND, frame=GRIP_FRAME, scale=[-SC if mirror else SC, SC, SC], hook=hook, rot=ypr, color=list(color))
