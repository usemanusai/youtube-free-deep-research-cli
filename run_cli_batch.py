import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Import CLI module (it loads .env explicitly on import)
from youtube_chat_cli_main import cli as cli_mod


def run_and_capture(argv):
    buf_out, buf_err = StringIO(), StringIO()
    old_argv = sys.argv[:]
    try:
        sys.argv = argv
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            rc = cli_mod.main()
    finally:
        sys.argv = old_argv
    return rc, buf_out.getvalue(), buf_err.getvalue()


results = {}

for cmd in (
    ["cli", "faq"],
    ["cli", "toc"],
):
    key = " ".join(cmd[1:])
    rc, out, err = run_and_capture(cmd)
    results[key] = {"rc": rc, "stdout": out, "stderr": err}

# Print a simple marker-delimited output
for key, data in results.items():
    print("=== BEGIN:", key, "===")
    print(data["stdout"])  # already includes any CLI prints
    if data["stderr"].strip():
        print("[stderr]\n" + data["stderr"])  # show errors if any
    print("=== END:", key, "(rc=", data["rc"], ") ===\n")

