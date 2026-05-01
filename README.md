# switchgear-v67-rev

Utility scripts for inspecting `com.rldv1.switchgear` (v67).

## Layout
- `hooks/`: Frida scripts for runtime key/string extraction.
- `tools/`: Python scripts for offline decryption and CSV parsing.
- `output/`: Processed data (JSON/TXT).
- `logic/`: Decoded game data (CSVs).
- `assets/`: App fingerprints and config.

## Usage
1. **Keys**: Capture runtime keys using `frida -U -f com.rldv1.switchgear -l hooks/hook_string_loader.js`.
2. **Decrypt**: Run `python tools/lbts_decrypt.py` (requires keys).
3. **Extract**: Run `python tools/extract_all.py` to rebuild gameplay stats.

## Data
Results are stored in `output/`.
- `v67_extracted_data.json`: Comprehensive brawler and projectile data.
- `string_xrefs.json`: Mapping of native string indices to Java/Smali calls.

*Note: Large binaries and decompiled folders are excluded.*
