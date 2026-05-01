import re
import sys

def extract_strings(file_path, pattern):
    with open(file_path, 'rb') as f:
        content = f.read()

    matches = re.findall(rb'[a-zA-Z0-9_/]{4,}', content)

    results = []
    regex = re.compile(pattern.encode(), re.IGNORECASE)
    for m in matches:
        if regex.search(m):
            results.append(m.decode('ascii', errors='ignore'))

    return sorted(list(set(results)))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_strings.py <file> <pattern>")
        sys.exit(1)

    res = extract_strings(sys.argv[1], sys.argv[2])
    for r in res:
        print(r)
