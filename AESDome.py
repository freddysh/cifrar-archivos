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
            # # Choose a random, 16-byte IV.
            # iv = Random.new().read(AES.block_size)

            # # Convert the IV to a Python integer.
            # iv_int = int(binascii.hexlify(iv), 16) 

            # # Create a new Counter object with IV = iv_int.
            # ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
            # # Create AES-CTR cipher.
            # aes = AES.new(self.key, AES.MODE_CTR, counter=ctr)
            # # Encrypt and return IV and ciphertext.
            # ciphertext = aes.encrypt(data)
            # self.iv = iv
            # return ciphertext

            # cipher = AES.new(self.key, AES.MODE_CBC)
            # ct_bytes = cipher.encrypt(pad(data, AES.block_size))
            # self.iv = cipher.iv
            # return ct_bytes
            print("paso 1")
            BS = AES.block_size
            print("paso 2")
            # pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

            print("paso 3")
            # raw = base64.b64encode(pad(data).encode('utf8'))

            print("paso 4")
            iv = get_random_bytes(16)

            print("paso 5")
            cipher = AES.new(key= self.key, mode= AES.MODE_CFB,iv= iv)

            print("paso 6")
            data=cipher.encrypt(pad(data, AES.block_size))

            print("paso 7")
            print(type(iv).__name__)
            print(type(data).__name__)
            # return base64.b64encode(iv +data )
            
            self.iv = iv
            return data
        except Exception as ex:
            print("a{}a".format(ex.args))
            return {"status": "error", "message": "handler.AESDome.encritar", "messageDetail":U"El archivo esta corrupto o contraseña invalida"}

    def desencritar(self,ciphertext):
        try:
            # Initialize counter for decryption. iv should be the same as the output of
            # encrypt().
            # iv_int = int(self.iv.encode('hex'), 16) 
            # ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

            # # Create AES-CTR cipher.
            # aes = AES.new(self.key, AES.MODE_CTR, counter=ctr)

            # # Decrypt and return the plaintext.
            # plaintext = aes.decrypt(ciphertext)
            # return plaintext


            # cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            # content=cipher.decrypt(ciphertext)
            # pt = unpad(content, AES.block_size)
            # return pt

            # unpad = lambda s: s[:-ord(s[-1:])]
            # enc = base64.b64decode(ciphertext)
            # iv = ciphertext[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
            return unpad(cipher.decrypt(ciphertext),AES.block_size)
        except  Exception as ex:
            print(ex.args)
            return {"status": "error", "message": "handler.AESDome.desencritar", "messageDetail":U"El archivo esta corrupto o contraseña invalida"}
