from passlib.hash import bcrypt


def hash_password(password: str):
    # bcrypt.genconfig()
    return bcrypt.hash(password)


def verify_hash(password, hash):
    return bcrypt.verify(password, hash)
