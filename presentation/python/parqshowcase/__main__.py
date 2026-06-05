import sys

USAGE = "usage: python -m parqshowcase {stats|add|drop} ARGS..."

def main():
    if len(sys.argv) < 2:
        print(USAGE, file=sys.stderr)
        sys.exit(2)

    cmd = sys.argv.pop(1)
    if cmd == "stats":
        from .stats import main as f
    elif cmd == "add":
        from .add_column import main as f
    elif cmd == "drop":
        from .drop_column import main as f
    else:
        print(USAGE, file=sys.stderr)
        sys.exit(2)
    f()


if __name__ == "__main__":
    main()
