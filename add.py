import sys
args = sys.argv[1:]
if len(args) == 3:
    total = sum(map(int, args))
    print(f"Sum = {total}")
else:
    print("Please provide exactly 3 numbers.")

