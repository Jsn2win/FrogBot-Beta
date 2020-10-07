import hashlib
from blake3 import blake3

def MD5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def BLAKE2(fname):
    hash_blake2 = hashlib.blake2b()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_blake2.update(chunk)
    return hash_blake2.hexdigest()

def BLAKE3(fname):
    hash_blake3 = blake3()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_blake3.update(chunk)
    return hash_blake3.hexdigest()



