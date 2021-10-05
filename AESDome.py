import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad
import hashlib

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
            cipher = AES.new(self.key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(data, AES.block_size))
            self.iv = cipher.iv
            return ct_bytes
        except Exception as ex:
            print(ex.args)
            return {"status": "error", "message": "handler.AESDome.encritar", "messageDetail":U"El archivo esta corrupto o contraseña invalida"}

    def desencritar(self,ciphertext):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            content=cipher.decrypt(ciphertext)
            pt = unpad(content, AES.block_size)
            return pt
        except  Exception as ex:
            print(ex.args)
            return {"status": "error", "message": "handler.AESDome.desencritar", "messageDetail":U"El archivo esta corrupto o contraseña invalida"}
