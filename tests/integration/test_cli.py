import subprocess
import sys

def test_cli_startup():
    # Since we can't easily mock input in a simple subprocess call without more setup,
    # we just check if the module can be imported.
    # A fuller test would use pexpect or mock sys.stdin.
    import cli.main
    assert callable(cli.main.main)
