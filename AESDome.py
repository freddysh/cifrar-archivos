import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad
import hashlib
import binascii

import base64

class AESDome:
    def __init__(self, key,iv): 
        self.key=key
        self.iv=iv
    
    def generar_clave(self,key):
        try:
            self.key = hashlib.sha256(key.encode()).digest()
            return self.key
        except Exception as ex:
            print(ex.args)
            return {"status": "error", "message": "handler.AESDome.generarKey", "messageDetail":"Error al generar el hash con la clave"}

    def encritar(self,data):
        try:
            iv = get_random_bytes(16)
            cipher = AES.new(key= self.key, mode= AES.MODE_CFB,iv= iv)
            data=cipher.encrypt(pad(data, AES.block_size))
            self.iv = iv
            return data
        except Exception as ex:
            print("a{}a".format(ex.args))
            return {"status": "error", "message": "handler.AESDome.encritar", "messageDetail":U"El archivo esta corrupto o contraseña invalida"}

    def desencritar(self,ciphertext):
        try:
            cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
            return unpad(cipher.decrypt(ciphertext),AES.block_size)
        except  Exception as ex:
            print(ex.args)
            return {"status": "error", "message": "handler.AESDome.desencritar", "messageDetail":U"El archivo esta corrupto o contraseña invalida"}
