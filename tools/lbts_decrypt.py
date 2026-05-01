import struct
import sys
import json
import hmac
import hashlib

DAT = "apktool_out/assets/kogcpfofggee.dat"
SENTRY = "apktool_out/lib/arm64-v8a/libsentry-android.so"

KEY1_HEX = ""
KEY2_HEX = ""

def hkdf_expand_sha256(prk, info, length):
    hash_len = 32
    n = (length + hash_len - 1) // hash_len
    okm = b""
    t = b""
    for i in range(1, n + 1):
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:length]

def derive_keys(key1, key2):
    with open(SENTRY, "rb") as f:
        sentry = f.read()

    combined = key1 + key2
    bss1 = sentry[0x5f6440:0x5f6440+8]
    bss2 = sentry[0x5f644c:0x5f644c+4]
    bss3 = sentry[0x5f6454:0x5f6454+10]

    block1 = combined + bss1
    block2 = combined + bss2
    block3 = combined + bss3

    info1 = sentry[0x6833:sentry.index(b'\x00', 0x6833)]
    info2 = sentry[0x683c:sentry.index(b'\x00', 0x683c)]
    info3 = sentry[0x6841:sentry.index(b'\x00', 0x6841)]

    subkey_enc = hkdf_expand_sha256(block1, info1, 32)
    subkey_auth = hkdf_expand_sha256(block2, info2, 32)
    subkey_nonce = hkdf_expand_sha256(block3, info3, 32)

    return subkey_enc, subkey_auth, subkey_nonce

def decrypt_stream(subkey_enc, subkey_auth, subkey_nonce):
    from Crypto.Cipher import ChaCha20_Poly1305

    with open(DAT, "rb") as f:
        dat = f.read()

    hdr_size = struct.unpack_from("<I", dat, 4)[0]
    ciphertext = dat[hdr_size:]

    nonce = subkey_nonce[:12]
    ct = ciphertext[:-16]
    tag = ciphertext[-16:]

    for aad in [b"SSv2", b""]:
        try:
            c = ChaCha20_Poly1305.new(key=subkey_enc, nonce=nonce)
            if aad:
                c.update(aad)
            pt = c.decrypt_and_verify(ct, tag)
            return pt
        except (ValueError, KeyError):
            pass
    return None

def parse_records(plaintext):
    off = 0
    records = []
    while off < len(plaintext):
        rtype = plaintext[off]
        off += 1

        if rtype == 2:
            flag = plaintext[off]
            key = plaintext[off+1:off+33]
            records.append({"type": 2, "flag": flag, "key": key.hex()})
            off += 33
        elif rtype == 4:
            count = struct.unpack_from("<I", plaintext, off)[0]
            records.append({"type": 4, "count": count})
            off += 4
        elif rtype == 6:
            size = struct.unpack_from("<I", plaintext, off)[0]
            data = plaintext[off+4:off+4+size]
            records.append({"type": 6, "size": size, "data": data})
            off += 4 + size
        else:
            records.append({"type": rtype, "offset": off-1})
            break

    return records

if __name__ == "__main__":
    if not KEY1_HEX or not KEY2_HEX:
        sys.exit(1)

    key1 = bytes.fromhex(KEY1_HEX)
    key2 = bytes.fromhex(KEY2_HEX)
    subkey_enc, subkey_auth, subkey_nonce = derive_keys(key1, key2)

    pt = decrypt_stream(subkey_enc, subkey_auth, subkey_nonce)
    if pt:
        records = parse_records(pt)
        strings = []
        for r in records:
            if r["type"] == 6 and "data" in r:
                try:
                    strings.append(r["data"].decode("utf-8"))
                except:
                    strings.append(r["data"].hex())

        with open("decrypted_strings_full.json", "w") as f:
            json.dump({"count": len(strings), "strings": strings}, f, indent=2, ensure_ascii=False)
