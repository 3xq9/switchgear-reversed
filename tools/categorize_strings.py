import os, re, json

jadx_src = 'jadx_out/sources'
results = {}

patterns = [
    (r'setContentType\(C0009ad\.a\((\d+)\)', 'content-type'),
    (r'setRequestProperty\(C0009ad\.a\((\d+)\)', 'http-header'),
    (r'Intent\(C0009ad\.a\((\d+)\)', 'intent-action'),
    (r'SharedPreferences.*C0009ad\.a\((\d+)\)', 'pref-key'),
    (r'Log\.\w\(C0009ad\.a\((\d+)\)', 'log-tag'),
    (r'new Exception\(C0009ad\.a\((\d+)\)', 'exception-msg'),
    (r'throw.*C0009ad\.a\((\d+)\)', 'exception-msg'),
    (r'equals\(C0009ad\.a\((\d+)\)', 'comparison'),
    (r'startsWith\(C0009ad\.a\((\d+)\)', 'prefix'),
    (r'endsWith\(C0009ad\.a\((\d+)\)', 'suffix'),
    (r'contains\(C0009ad\.a\((\d+)\)', 'substring'),
    (r'getSystemService\(C0009ad\.a\((\d+)\)', 'system-service'),
    (r'setAction\(C0009ad\.a\((\d+)\)', 'intent-action'),
    (r'Cipher\.getInstance\(C0009ad\.a\((\d+)\)', 'cipher-algo'),
    (r'MessageDigest\.getInstance\(C0009ad\.a\((\d+)\)', 'digest-algo'),
    (r'KeyGenerator\.getInstance\(C0009ad\.a\((\d+)\)', 'keygen-algo'),
    (r'SecretKeySpec.*C0009ad\.a\((\d+)\)', 'key-algo'),
    (r'getBytes\(C0009ad\.a\((\d+)\)', 'charset'),
    (r'new String\(.*C0009ad\.a\((\d+)\)', 'charset'),
    (r'URLEncoder\.encode\(.*C0009ad\.a\((\d+)\)', 'charset'),
    (r'System\.getProperty\(C0009ad\.a\((\d+)\)', 'sys-property'),
    (r'getExternalFilesDir\(C0009ad\.a\((\d+)\)', 'dir-type'),
    (r'checkNotNullParameter.*C0009ad\.a\((\d+)\)', 'param-name'),
    (r'JSONObject.*C0009ad\.a\((\d+)\)', 'json-key'),
    (r'getString\(C0009ad\.a\((\d+)\)', 'json-or-bundle-key'),
    (r'putString\(C0009ad\.a\((\d+)\)', 'pref-or-bundle-key'),
    (r'putExtra\(C0009ad\.a\((\d+)\)', 'intent-extra'),
]

for root, dirs, files in os.walk(jadx_src):
    for fname in files:
        if not fname.endswith('.java'):
            continue
        path = os.path.join(root, fname)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            continue

        for pat, category in patterns:
            for m in re.finditer(pat, content):
                idx = int(m.group(1))
                start = max(0, m.start() - 60)
                end = min(len(content), m.end() + 60)
                ctx = content[start:end].replace('\n', ' ').strip()
                results.setdefault(idx, []).append({
                    'cat': category,
                    'file': os.path.relpath(path, jadx_src),
                    'ctx': ctx[:150]
                })

print(f"categorized {len(results)} string indices")

for idx in sorted(results.keys()):
    entries = results[idx]
    cats = ", ".join(set(e['cat'] for e in entries))
    sample = entries[0]['ctx'][:90]
    print(f"  [{idx:4d}] [{cats}] {sample}")

with open('string_categories.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)
