from Crypto.Cipher import AES
import bas64

class AESCipher(object):

    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = key

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = b'\0'*16 #Default zero based bytes[16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(cipher.encrypt(raw.encode()))

    def _pad(self, s):
        return m+chr(16-len(m)%16)*(16-len(m)%16)

a = AESCipher('1F61ECB5ED5D6BAF8D7A7068B28DCC8E')

