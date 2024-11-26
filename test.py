import sys

print("Please enter your name:")
name = sys.stdin.readline()[0:-1]  # Use strip() to remove the newline character
print(f"Hello, {name}!")