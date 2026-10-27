"""Compare the baked MD3s in work/out against a reference (default reference/bd22_r6/expected_md3.json): whole-file sha256
and each frame's vertex+normal block; with no argument also the round-6 result files (expected_results.json). usage: check_ref.py [expected.json]   exit 1 on any difference."""
import hashlib, json, os, sys
import paths, scene
exp = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(paths.TOOL, 'reference', 'bd22_r6', 'expected_md3.json')))
bad = 0
for name, e in exp.items():
    p = os.path.join(paths.OUT, name)
    if not os.path.exists(p): print('MISSING', p); bad += 1; continue
    b = open(p, 'rb').read(); S = scene.md3_full(p); n = int(S[0]['xyz'].shape[0])
    fs = [hashlib.sha256(b''.join(s['normal_raw'][i].tobytes() + (s['xyz'][i] * 64).astype('<i2').tobytes() for s in S)).hexdigest() for i in range(n)]
    same = hashlib.sha256(b).hexdigest() == e['sha256']
    fr = [a == c for a, c in zip(fs, e['frame_sha256'])] + [False] * abs(n - len(e['frame_sha256']))
    print('%s: file %s (%d bytes, sha %s); frames %s' % (name, 'IDENTICAL' if same else 'DIFFERS', len(b), hashlib.sha256(b).hexdigest()[:12],
          ' '.join('%d:%s' % (i, 'same' if f else 'DIFF') for i, f in enumerate(fr))))
    bad += (not same) + fr.count(False)
er = os.path.join(paths.TOOL, 'reference', 'bd22_r6', 'expected_results.json')
if len(sys.argv) < 2 and os.path.exists(er):   # the round-6 result files too (pose vectors, rules, gun move, spout tip)
    for name, h in json.load(open(er)).items():
        p = os.path.join(paths.RESULTS, name); got = hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else 'missing'
        print('results/%s: %s' % (name, 'IDENTICAL' if got == h else 'DIFFERS')); bad += got != h
print('check_ref:', 'byte-identical' if not bad else '%d difference(s)' % bad); sys.exit(1 if bad else 0)
