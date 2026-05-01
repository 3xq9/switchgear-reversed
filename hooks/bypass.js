Java.perform(() => {
    const File = Java.use("java.io.File");
    const SystemProperties = Java.use("android.os.SystemProperties");
    const PackageManager = Java.use("android.app.ApplicationPackageManager");

    // Anti-Root
    File.exists.implementation = function() {
        const name = this.getName();
        if (["su", "magisk", "busybox"].includes(name)) return false;
        return this.exists();
    };

    PackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pkg, flags) {
        if (pkg.includes("magisk") || pkg.includes("supersu")) {
            throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new(pkg);
        }
        return this.getPackageInfo(pkg, flags);
    };

    // Anti-Emulator
    SystemProperties.get.overload('java.lang.String').implementation = function(key) {
        if (key === "ro.build.tags") return "release-keys";
        if (key === "ro.debuggable") return "0";
        return this.get(key);
    };

    // Hide Frida
    const strstrPtr = Module.findExportByName(null, 'strstr');
    if (strstrPtr) {
        Interceptor.attach(strstrPtr, {
            onEnter(args) { this.needle = args[1].readUtf8String(); },
            onLeave(retval) {
                if (this.needle && (this.needle.includes("frida") || this.needle.includes("gum-js"))) {
                    retval.replace(ptr(0));
                }
            }
        });
    }

    // License Bypass
    const libsentry = Module.findBaseAddress("libsentry-android.so");
    if (libsentry) {
        // v.b() -> License Check
        Interceptor.replace(libsentry.add(0x1a03c8), new NativeCallback(() => 1, 'int', []));
    }
});
