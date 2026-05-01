# switchgear-v67-rev

Technical documentation and research for inspecting `com.rldv1.switchgear` (v67).

## Layout
- `hooks/`: Frida scripts for runtime key/string extraction.
- `tools/`: Python scripts for offline decryption and binary analysis.
- `output/`: Processed data (JSON/TXT).
- `apktool_out/`: Decompiled Smali and resources.

## Technical Audit (Switchgear Internals)

### 1. Component Mapping
- **libkk.so (10.7 MB)**: Main Mod Engine. Handles Mod Menu rendering and function hooking. Contains the "switchgear" identity.
- **libsentry-android.so (6.2 MB)**: Security & Decryption Proxy. Heavily obfuscated (MBA/Flattening). Contains the String Table Resolver.
- **assets/kogcpfofggee.dat**: Encrypted master string table (ChaCha20-Poly1305, SSv2 prefix).

### 2. Native Offsets (ARM64)
| Offset | Target | Purpose |
|--------|--------|---------|
| `0x171508` | Resolver | String lookup by ID `(I)Ljava/lang/String;` |
| `0x3db348` | Init | Native string table population |
| `0x39c0` | Binding | JNINativeMethod array |
| `0xf485a` | Crypto | ChaCha20 constants in libkk.so |

### 3. Security & Anti-Detection
- **Root Detection**: Combined Smali (`RootChecker`) and Native (`v.d()`) validation.
- **Tool Detection**: Scans `/proc/self/maps` and uses `strstr` to detect "frida" or "gum-js".
- **Obfuscation**: LLVM-Obfuscator is used to hide logic in `libsentry-android.so`.

### 4. Known Data Points
- **Salt/Key material**: `fldsjfodasjifudslfjdsaofshaufihadsf`
- **Key IDs**: 157 (UTF-8), 160 (SecurePreferences), 167 (SHA-256).
- **Persistence**: License and settings stored in `SecurePreferences` (XML).

*Note: Large binaries and decompiled folders are excluded from version control.*
