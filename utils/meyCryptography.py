import hashlib
from Crypto.Cipher import DES
from Crypto.Hash import SHA256

def is_correct_password(password, hash):
    return get_hash(password) == hash

def get_hash(password):
    return SHA256.new(data=password.encode('utf-8')).hexdigest().encode('utf-8')

def padding(msg):
    return msg+' '*(8-len(msg)%8)

def unpadding(msg):
    while msg[-1] == ' ':
        msg = msg[:-1]
    return msg

def encrypt(password, msg):
    des = DES.new(padding(padding(password))[:8].encode('utf-8'), DES.MODE_ECB)
    return des.encrypt(padding(msg).encode('utf-8'))

def decrypt(password, msg):
    des = DES.new(padding(padding(password))[:8].encode('utf-8'), DES.MODE_ECB)
    return unpadding(des.decrypt(msg).decode())