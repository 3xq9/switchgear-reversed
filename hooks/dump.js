const VA_RESOLVER = 0x171508;

function dump() {
    const base = Module.findBaseAddress("libsentry-android.so");
    if (!base) return setTimeout(dump, 500);

    const resolver = new NativeFunction(base.add(VA_RESOLVER), 'pointer', ['int']);
    const out = {};

    console.log("[*] Dumping string table...");
    for (let i = 0; i < 3000; i++) {
        try {
            const res = resolver(i);
            if (!res.isNull()) {
                const s = res.readUtf8String();
                if (s) out[i] = s;
            }
        } catch (e) {}
    }
    console.log(JSON.stringify(out, null, 2));
}

dump();
