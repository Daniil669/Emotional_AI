import uuid, hashlib

def new_uuid() -> str:
    return str(uuid.uuid4())

def sha256_of(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()
