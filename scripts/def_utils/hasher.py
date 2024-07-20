import hashlib


patient = "test-psw"

hasher = hashlib.sha256()
hasher.update(patient.encode())
print(hasher.hexdigest())
