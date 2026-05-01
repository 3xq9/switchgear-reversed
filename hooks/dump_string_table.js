var sentry = Module.findBaseAddress("libsentry-android.so");
var table_va = sentry.add(0x5f4438);
var count_va = sentry.add(0x5f4430);

function dumpTable() {
    var count = count_va.readS32();
    var table = table_va.readPointer();
    var out = {};
    for (var i = 0; i < count; i++) {
        var ptr = table.add(i * Process.pointerSize).readPointer();
        if (!ptr.isNull()) {
            try {
                out[i] = ptr.readUtf8String(500);
            } catch(e) {
                out[i] = "<binary>";
            }
        }
    }
    send({type: "table", count: count, strings: out});
    console.log("[*] dumped " + count + " strings");
}

Interceptor.attach(sentry.add(0x3db348), {
    onLeave: function(ret) {
        dumpTable();
    }
});

rpc.exports = {
    dump: function() {
        dumpTable();
        return count_va.readS32();
    }
};

setTimeout(function() {
    var count = count_va.readS32();
    if (count > 0) {
        console.log("[*] table already loaded, dumping " + count + " entries");
        dumpTable();
    } else {
        console.log("[*] table not yet loaded, waiting for loader hook");
    }
}, 2000);
