"""After reproduce_bd22_r6.sh --resolve: each re-solved pose vector (work/results) vs the recorded one (reference/bd22_r6/fits)."""
import json, os, numpy as np
import paths
REF = os.path.join(paths.TOOL, 'reference', 'bd22_r6', 'fits')
for f, k in (('BrutalPistol_gunhand.json', 'K5'), ('BrutalPistol_support_R3c.json', None), ('Flamethrower2_under_D.json', None), ('Flamethrower2_pump_Z3.json', None)):
    a = json.load(open(os.path.join(REF, f))); b = json.load(open(os.path.join(paths.RESULTS, f)))
    a, b = (a[k], b[k]) if k else (a, b); xa, xb = np.array(a['x']), np.array(b['x'])
    print('%-32s %-3s x %s (max |diff| %.3g), cost %.6g -> %.6g' % (f, k or '', 'IDENTICAL' if np.array_equal(xa, xb) else 'differs', np.abs(xa - xb).max(), a.get('cost', a.get('m', {}).get('cost', float('nan'))), b.get('cost', b.get('m', {}).get('cost', float('nan')))))
