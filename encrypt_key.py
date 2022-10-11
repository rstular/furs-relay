import json
import sys
from base64 import b64encode

from Crypto.Cipher import ChaCha20_Poly1305


def main(key: str, cert_key: str) -> int:
    key = bytes.fromhex(key)
    cert_key = cert_key.encode("utf-8")

    cipher = ChaCha20_Poly1305.new(key=key)
    ciphertext, tag = cipher.encrypt_and_digest(cert_key)

    jk = ["nonce", "ciphertext", "tag"]
    jv = [b64encode(x).decode("utf-8") for x in (cipher.nonce, ciphertext, tag)]

    print(json.dumps(dict(zip(jk, jv)), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <key (hex)> <cert-key>")
        sys.exit(-1)
    else:
        sys.exit(main(sys.argv[1], sys.argv[2]))
