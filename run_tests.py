import os
import subprocess
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Run tests with optional test selection."
    )
    parser.add_argument(
        "test",
        nargs="?",
        default=None,
        help="Optional specific test to run (e.g., 'test_module.TestClass.test_method').",
    )
    args = parser.parse_args()

    os.environ["LL_TESTING"] = "1"

    try:
        command = [sys.executable, "-m", "unittest"]
        if args.test:
            command.append(args.test)

        subprocess.run(command, check=True)
    finally:
        os.environ.pop("LL_TESTING", None)


if __name__ == "__main__":
    main()
