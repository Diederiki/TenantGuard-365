"""Password hashing for local auth.

Uses bcrypt with the library default work factor (12). We store the hash as
raw bytes in ``platform_users.password_hash`` (LargeBinary column).
"""

from __future__ import annotations

import bcrypt


def hash_password(plaintext: str) -> bytes:
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt())


def verify_password(plaintext: str, hashed: bytes) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), hashed)
    except ValueError:
        return False
