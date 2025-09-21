from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

BASE_DIR = Path(__file__).resolve().parent
CERTS_DIR = BASE_DIR / "certs"

CERTS_DIR.mkdir(parents=True, exist_ok=True)

private_key_path = CERTS_DIR / "jwt-private-key.pem"
public_key_path = CERTS_DIR / "jwt-public-key.pem"


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with open(private_key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    public_key = private_key.public_key()
    with open(public_key_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print(f"Приватный: {private_key_path}\nПубличный: {public_key_path}")


if __name__ == "__main__":
    generate_keys()