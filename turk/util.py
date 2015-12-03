
import hashlib

def hash_task_phdr(id, pkh, tstamp):
    md = hashlib.sha256()
    md.update(id.encode('utf-8'))
    md.update(pkh.encode('utf-8'))
    md.update(str(tstamp).encode('utf-8'))
    return md.hexdigest()

