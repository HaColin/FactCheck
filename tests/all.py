"""Run every offline test suite. No network, no credentials.

    python3 tests/all.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUITES = ["test_yamlish.py", "test_precedence.py", "test_render.py",
          "test_script.py", "test_issues.py"]

failed = 0
for name in SUITES:
    r = subprocess.run([sys.executable, os.path.join(HERE, name)],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    failed += r.returncode != 0
sys.exit(1 if failed else 0)
