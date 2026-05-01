import sys
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

def decrypt(data, key, nonce):
    cipher = ChaCha20Poly1305(key)
    return cipher.decrypt(nonce, data, b"SSv2")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: decrypt.py <file.dat> <key_hex>")
        sys.exit(1)
    
    with open(sys.argv[1], "rb") as f:
        raw = f.read()
    
    key = bytes.fromhex(sys.argv[2])
    nonce = raw[12:24]
    encrypted = raw[24:]
    
    try:
        print(decrypt(encrypted, key, nonce).decode())
    except Exception as e:
        print(f"Decryption failed: {e}")
