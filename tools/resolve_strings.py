import os, re, json

jadx = 'jadx_out/sources'
resolved = json.load(open('resolved_strings.json'))

def java_hash(s):
    h = 0
    for c in s:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h if h <= 0x7FFFFFFF else h - 0x100000000

unresolved = {}
for root, dirs, files in os.walk(jadx):
    for fname in files:
        if not fname.endswith('.java'): continue
        path = os.path.join(root, fname)
        try:
            content = open(path, 'r', errors='ignore').read()
        except: continue

        for m in re.finditer(r'C0009ad\.a\((\d+)\)', content):
            idx = m.group(1)
            if idx in resolved: continue
            start = max(0, m.start()-60)
            end = min(len(content), m.end()+60)
            ctx = content[start:end].replace('\n', ' ').strip()
            unresolved.setdefault(idx, []).append({
                'file': os.path.basename(path),
                'ctx': ctx[:200]
            })

auto = {}
for idx, refs in unresolved.items():
    for r in refs:
        ctx = r['ctx']

        if 'getSystemService' in ctx:
            if 'NotificationManager' in ctx or 'notification' in ctx.lower():
                auto[idx] = 'notification'
            elif 'ConnectivityManager' in ctx or 'connectivity' in ctx.lower():
                auto[idx] = 'connectivity'
            elif 'TelephonyManager' in ctx or 'telephony' in ctx.lower():
                auto[idx] = 'phone'
            elif 'AlarmManager' in ctx or 'alarm' in ctx.lower():
                auto[idx] = 'alarm'
            elif 'AudioManager' in ctx or 'audio' in ctx.lower():
                auto[idx] = 'audio'
            elif 'ClipboardManager' in ctx or 'clipboard' in ctx.lower():
                auto[idx] = 'clipboard'
            elif 'PowerManager' in ctx or 'power' in ctx.lower():
                auto[idx] = 'power'
            elif 'Vibrator' in ctx or 'vibrator' in ctx.lower():
                auto[idx] = 'vibrator'

        if 'checkNotNullParameter' in ctx:
            m2 = re.search(r'checkNotNullParameter\((\w+),\s*C0009ad', ctx)
            if m2:
                auto[idx] = m2.group(1)

        if 'getBytes(C0009ad' in ctx or 'new String(' in ctx and 'C0009ad' in ctx:
            if 'doFinal' in ctx or 'cipher' in ctx.lower() or 'digest' in ctx.lower():
                auto[idx] = 'UTF-8'

        if 'getInstance(C0009ad' in ctx:
            if 'Cipher' in ctx:
                auto[idx] = 'AES/CBC/PKCS5Padding'
            elif 'MessageDigest' in ctx:
                auto[idx] = 'SHA-256'
            elif 'KeyGenerator' in ctx:
                auto[idx] = 'AES'

        if 'NotificationChannel' in ctx and 'C0009ad' in ctx:
            pass

        if "getString(C0009ad" in ctx and ", C0009ad" in ctx:
            pass

        if 'setType(C0009ad' in ctx:
            auto[idx] = 'text/plain'

resolved.update(auto)

hash_map = {}
for root, dirs, files in os.walk(jadx):
    for fname in files:
        if not fname.endswith('.java'): continue
        path = os.path.join(root, fname)
        try:
            lines = open(path, 'r', errors='ignore').readlines()
        except: continue

        for i, line in enumerate(lines):
            m = re.search(r'case\s+(-?\d+):', line)
            if m:
                hc = int(m.group(1))
                block = ''.join(lines[i:i+3])
                m2 = re.search(r'equals\(C0009ad\.a\((\d+)\)\)', block)
                if m2:
                    idx = m2.group(1)
                    if idx not in resolved:
                        hash_map[idx] = hc

android_strings = [
    'android.intent.action.MAIN', 'android.intent.category.LAUNCHER',
    'android.intent.action.VIEW', 'android.intent.action.SEND',
    'android.intent.action.SENDTO', 'android.intent.action.PICK',
    'android.intent.action.DELETE', 'android.intent.action.EDIT',
    'android.intent.action.DIAL', 'android.intent.action.CALL',
    'android.intent.extra.TEXT', 'android.intent.extra.STREAM',
    'android.permission.CAMERA', 'android.permission.INTERNET',
    'android.provider.MediaStore', 'image/*', 'video/*',
    'application/json', 'application/octet-stream',
    'text/plain', 'text/html', 'multipart/form-data',
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH',
    'Content-Type', 'Accept', 'Authorization', 'User-Agent',
    'Bearer ', 'Basic ', 'true', 'false', 'null',
    'https', 'http', 'wss', 'ws',
    'com.google.firebase.messaging.RECEIVE',
    'google.delivered_priority', 'google.sent_time',
    'google.message_id', 'google.ttl',
    'from', 'collapse_key', 'message_type',
    'gcm', 'gcm.notification.title', 'gcm.notification.body',
    'supercell_id', 'scid', 'sc_id',
    'device_id', 'session_id', 'platform',
    'android', 'ios', 'version', 'build',
    'en', 'fi', 'ja', 'ko', 'zh', 'de', 'fr', 'es', 'pt', 'ru', 'tr', 'it', 'nl',
    'language', 'locale', 'country',
]

for idx, hc in hash_map.items():
    for s in android_strings:
        if java_hash(s) == hc:
            resolved[idx] = s

json.dump(dict(sorted(resolved.items(), key=lambda x: int(x[0]))), 
          open('resolved_strings.json', 'w'), indent=2, ensure_ascii=False)

remaining = len(unresolved) - len(auto)
print(f"resolved: {len(resolved)} / 770 ({remaining} still unknown)")
print(f"auto-resolved this pass: {len(auto)}")
print(f"hashcode matches: {len(hash_map)}")
