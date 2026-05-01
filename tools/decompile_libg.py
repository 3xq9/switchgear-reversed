import struct, os, re, json
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

LIBG = "apktool_out/lib/arm64-v8a/libg.so"

with open(LIBG, "rb") as f:
    code = f.read()

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

e_shoff = struct.unpack_from("<Q", code, 40)[0]
e_shentsize = struct.unpack_from("<H", code, 58)[0]
e_shnum = struct.unpack_from("<H", code, 60)[0]
e_shstrndx = struct.unpack_from("<H", code, 62)[0]

shstr_off = struct.unpack_from("<Q", code, e_shoff + e_shstrndx * e_shentsize + 24)[0]
shstr_size = struct.unpack_from("<Q", code, e_shoff + e_shstrndx * e_shentsize + 32)[0]
shstrtab = code[shstr_off:shstr_off + shstr_size]

sections = {}
for i in range(e_shnum):
    sh_off = e_shoff + i * e_shentsize
    sh_name_idx = struct.unpack_from("<I", code, sh_off)[0]
    sh_type = struct.unpack_from("<I", code, sh_off + 4)[0]
    sh_addr = struct.unpack_from("<Q", code, sh_off + 16)[0]
    sh_offset = struct.unpack_from("<Q", code, sh_off + 24)[0]
    sh_size = struct.unpack_from("<Q", code, sh_off + 32)[0]
    name_end = shstrtab.find(b"\x00", sh_name_idx)
    name = shstrtab[sh_name_idx:name_end].decode("ascii", errors="replace")
    sections[name] = {"offset": sh_offset, "size": sh_size, "vaddr": sh_addr}
    if name in (".text", ".rodata", ".data", ".dynstr", ".dynsym", ".bss"):
        print(f"  {name:12s} offset=0x{sh_offset:08x} size=0x{sh_size:08x} vaddr=0x{sh_addr:08x}")

rodata = sections.get(".rodata", {})
ro_off = rodata.get("offset", 0)
ro_size = rodata.get("size", 0)
ro_data = code[ro_off:ro_off+ro_size]

game_keywords = [
    b"projectile", b"Projectile", b"bullet", b"Bullet",
    b"dodge", b"Dodge", b"autododge",
    b"aimbot", b"aim", b"Aim",
    b"attack", b"Attack", b"shoot", b"Shoot",
    b"movement", b"Movement", b"move", b"Move",
    b"joystick", b"Joystick", b"input", b"Input",
    b"physics", b"Physics", b"velocity", b"Velocity",
    b"position", b"Position", b"angle", b"Angle",
    b"collision", b"Collision", b"hitbox", b"Hitbox",
    b"damage", b"Damage", b"health", b"Health",
    b"super", b"Super", b"gadget", b"Gadget",
    b"brawler", b"Brawler", b"character", b"Character",
    b"player", b"Player", b"enemy", b"Enemy",
    b"target", b"Target", b"spawn", b"Spawn",
    b"tick", b"Tick", b"frame", b"Frame",
    b"LogicGameObject", b"LogicBattle", b"LogicProjectile",
    b"LogicCharacter", b"LogicPlayer", b"LogicAttack",
    b"GameMode", b"BattleLog",
    b"speed", b"Speed", b"range", b"Range",
    b"spread", b"Spread", b"knockback", b"Knockback",
    b"shield", b"Shield", b"heal", b"Heal",
    b"stun", b"Stun", b"slow", b"Slow",
    b"poison", b"Poison", b"burn", b"Burn",
    b"charge", b"Charge", b"reload", b"Reload",
    b"CLogic", b"CGame", b"CBattle",
    b"update", b"Update", b"simulate", b"Simulate",
    b"onTick", b"process", b"Process",
]

print(f"\nscanning .rodata ({ro_size} bytes) for game strings...")
found_strings = {}
for kw in game_keywords:
    idx = 0
    while True:
        idx = ro_data.find(kw, idx)
        if idx < 0:
            break
        end = ro_data.find(b"\x00", idx)
        if end < 0:
            end = idx + 200
        s = ro_data[idx:end]
        if len(s) > 2 and len(s) < 200:
            va = ro_off + idx + sections[".rodata"]["vaddr"] - sections[".rodata"]["offset"]
            file_off = ro_off + idx
            found_strings[file_off] = {"string": s.decode("ascii", errors="replace"), "vaddr": file_off, "file_offset": file_off}
        idx += 1

unique = sorted(found_strings.values(), key=lambda x: x["file_offset"])
print(f"found {len(unique)} game-related strings\n")

for entry in unique[:100]:
    print(f"  @0x{entry['file_offset']:08x}: {entry['string'][:80]}")

with open("libg_game_strings.json", "w") as f:
    json.dump(unique, f, indent=2, ensure_ascii=False)

print(f"\nfinding xrefs to game strings in .text...")
text = sections.get(".text", {})
text_off = text.get("offset", 0)
text_size = text.get("size", 0)
text_vaddr = text.get("vaddr", 0)

interesting_funcs = []
for entry in unique[:50]:
    target_addr = entry["file_offset"]
    target_page = target_addr & ~0xFFF
    target_offset = target_addr & 0xFFF

    for off in range(text_off, text_off + min(text_size, 2000000), 4):
        insn_bytes = code[off:off+4]
        if len(insn_bytes) < 4:
            break
        insn_word = struct.unpack_from("<I", insn_bytes)[0]
        if (insn_word & 0x9F000000) == 0x90000000:
            immhi = (insn_word >> 5) & 0x7FFFF
            immlo = (insn_word >> 29) & 0x3
            imm = (immhi << 2) | immlo
            if imm & 0x100000:
                imm -= 0x200000
            pc_page = off & ~0xFFF
            result_page = pc_page + (imm << 12)
            if result_page == target_page:
                if off + 4 < len(code):
                    next_word = struct.unpack_from("<I", code, off+4)[0]
                    if (next_word & 0xFFC00000) == 0x91000000:
                        add_imm = (next_word >> 10) & 0xFFF
                        shift = (next_word >> 22) & 0x3
                        if shift == 1:
                            add_imm <<= 12
                        if add_imm == target_offset:
                            func_addr = off
                            for back in range(off, max(off-256, text_off), -4):
                                w = struct.unpack_from("<I", code, back)[0]
                                if (w & 0xFFE00000) == 0xA9800000:
                                    func_addr = back
                                    break
                                if (w & 0xFF0003FF) == 0xD10003FF:
                                    func_addr = back
                                    break
                            interesting_funcs.append({
                                "string": entry["string"][:60],
                                "ref_at": off,
                                "func_start": func_addr,
                            })
                            break

print(f"found {len(interesting_funcs)} function references")

output = []
seen = set()
for func in interesting_funcs[:30]:
    start = func["func_start"]
    if start in seen:
        continue
    seen.add(start)

    lines = [f"\n--- {func['string']} (func @0x{start:08x}, ref @0x{func['ref_at']:08x}) ---"]
    block = code[start:start+512]
    for insn in md.disasm(block, start):
        lines.append(f"  0x{insn.address:08x}: {insn.mnemonic:8s} {insn.op_str}")
        if insn.mnemonic == "ret":
            break
    output.extend(lines)

with open("libg_game_functions.txt", "w") as f:
    f.write("\n".join(output))

print(f"disassembled {len(seen)} unique functions -> libg_game_functions.txt")
