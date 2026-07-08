#!/usr/bin/env python3
"""Integration test: run local services and verify event chain."""

import subprocess
import sys


def main():
    # Run local services (start controller + worker, issue directives, process them)
    rc = subprocess.call([sys.executable, 'simulator/run_local.py'])
    if rc != 0:
        print('run_local failed', rc)
        return rc

    # Verify chain
    rc = subprocess.call([sys.executable, 'tests/verify_chain.py'])
    if rc != 0:
        print('verify_chain failed', rc)
        return rc

    print('Integration test passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
