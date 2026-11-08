# forwarder (2026-11-08): the one copy of this tool is tools/hqt/phase.py. ModelSwapper's tools_kit carried
# its own copy from 2026-10-24; its fixes are in the one copy now, and the regression gate for it is
# tools/hqt/recheck_cards.py. Importing or running this file is the same as the one copy.
import os, sys, runpy, importlib.util
_ONE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hqt', 'phase.py'))
if __name__ == '__main__':
    sys.argv[0] = _ONE; runpy.run_path(_ONE, run_name='__main__')
else:
    _d = os.path.dirname(_ONE)
    if _d not in sys.path: sys.path.insert(0, _d)
    _spec = importlib.util.spec_from_file_location('_one_phase', _ONE); _mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
    globals().update({k: v for k, v in vars(_mod).items() if not k.startswith('__')})
