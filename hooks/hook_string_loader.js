var sentry = Module.findBaseAddress("libsentry-android.so");

Interceptor.attach(sentry.add(0x3db348), {
    onEnter: function(args) {
        this.fd = args[0].toInt32();
        this.cfg = args[1];
        console.log("[loader] fd=" + this.fd);
        console.log("[loader] cfg struct @ " + this.cfg);
        console.log("[loader] key1 (+0x18):", hexdump(this.cfg.add(0x18), {length: 32}));
        console.log("[loader] key2 (+0x30):", hexdump(this.cfg.add(0x30), {length: 32}));
        console.log("[loader] flag (+0x48):", this.cfg.add(0x48).readU8());
        console.log("[loader] version (+0x50):", this.cfg.add(0x50).readU32());
    },
    onLeave: function(ret) {
        console.log("[loader] returned");
    }
});

Interceptor.attach(sentry.add(0x3dfc0c), {
    onEnter: function(args) {
        console.log("[key_setup] x0:", hexdump(args[0], {length: 32}));
        console.log("[key_setup] x1:", hexdump(args[1], {length: 32}));
        console.log("[key_setup] x2:", args[2]);
        console.log("[key_setup] x3:", args[3]);
        console.log("[key_setup] x4:", args[4]);
    }
});

var decrypted_count = 0;
Interceptor.attach(sentry.add(0x3dae0c), {
    onEnter: function(args) {
        this.outbuf = args[0];
        this.inbuf = args[1];
        this.len = args[2].toInt32();
    },
    onLeave: function(ret) {
        if (this.len > 0 && this.len < 4096) {
            decrypted_count++;
            if (decrypted_count <= 20) {
                try {
                    var s = this.outbuf.readUtf8String(Math.min(this.len, 200));
                    console.log("[chacha] #" + decrypted_count + " len=" + this.len + " -> " + s);
                } catch(e) {
                    console.log("[chacha] #" + decrypted_count + " len=" + this.len + " (binary)");
                }
            }
        }
    }
});

Interceptor.attach(sentry.add(0x3dbab0), {
    onEnter: function(args) {
        var ctx = this.context;
        var str_ptr = ctx.x9;
        var idx = ctx.x11.toInt32();
        try {
            var s = str_ptr.readUtf8String(200);
            console.log("[table] [" + idx + "] = " + JSON.stringify(s));
        } catch(e) {
            console.log("[table] [" + idx + "] = <binary>");
        }
    }
});

console.log("[*] hooks installed on libsentry-android.so @ " + sentry);
