from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import jwt
import binascii
import json
import base64
import os
import requests

student_id = "e237534"

one_time_password = """1FPpJzJEY5gPFURoWmkfqqMKUNpdSyFO"""

own_public_key = """MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQBcuKLjc+qTH57OKl6Mma7C
+/rlVfxWcLoY5L3fE2jsnycyu4SOvBD+S1RxXPoWySiJaD3VwyQnlaq08N/uHWom
bJOxINQ1xsnWKv+Bv/UY5N1DRnm68PVeNHP/nP9B/ctk+Df/Ab5g25Cq8LI6DYjW
SsNdEh8SBrM7FbkrEP08v3uABAigUaqn1gG7lGk2etxYc4ec6sX9EyYqUFxRcJQt
OHCQ0t2jTRWdVgAehhwFeQjJ+gorBvazUldtPAL3TfEGLMNEzx2ttkP6XiYXs6m3
r2tZtbsxSORxyjCtvFhRMoMBJ9oZtjLjS5CW3w+LW4ZxXG68GERNvE8yl3bxfjUZ
AgMBAAE="""

own_private_key = """MIIEoQIBAAKCAQBcuKLjc+qTH57OKl6Mma7C+/rlVfxWcLoY5L3fE2jsnycyu4SO
vBD+S1RxXPoWySiJaD3VwyQnlaq08N/uHWombJOxINQ1xsnWKv+Bv/UY5N1DRnm6
8PVeNHP/nP9B/ctk+Df/Ab5g25Cq8LI6DYjWSsNdEh8SBrM7FbkrEP08v3uABAig
Uaqn1gG7lGk2etxYc4ec6sX9EyYqUFxRcJQtOHCQ0t2jTRWdVgAehhwFeQjJ+gor
BvazUldtPAL3TfEGLMNEzx2ttkP6XiYXs6m3r2tZtbsxSORxyjCtvFhRMoMBJ9oZ
tjLjS5CW3w+LW4ZxXG68GERNvE8yl3bxfjUZAgMBAAECggEAFJNIWi7r2/AFXnya
dJrZ5BzkhSW6lDf5o/KGi80T2IZMvX5NIRtsrfFrcKiQOqQy4aMHLbta94nH0tUs
6/sNBi/L6l99l91gBq2N+23sZrTKwNYPx0MXP+tl3lApeKxoCSTn0CfD5lxy0uwM
sMM2HU+D4NBXorln5nGgoITpnSQf3Q1aC8VuFCdmYTfhQE/2QxcYBUa+dhYftlY4
iTs9ffUiyrcfVrDXjPI6LvO57d2h9HcqWaZGA3TkIfjjTO4ICPI7GcqS5SPWZPAh
oG4e8t0FHI6sBgjtGGXWM1Z7dPQ3BUDrOOL4PMTifkX94O+sV6mDOnHbeyKLdjTJ
4XJTgQKBgQCtHLmWgFw1iS1sLi3amQYtgfuMPdoya+Irl8NNrGB05WeigYBo/+ZU
hjKUtLCX/OY7jP3t2HCL1D2hBFVA27M1TpbMlqySqYktpkn7+YdsK3kffpj6Szgs
kuwv9tIYWLvf41mul98FJfDgB0lXbjh+XxNA3+kKp7rkiSwOI0SqCQKBgQCJHfdt
r81KSA1jEuEeSYDjqdI/fQL005jXAaB+PVmnmC4EXh1PsWR/MEeA3kd/QK6MEf8J
NYObFzfs+zwKMfjSX19kwE6S1ko18oOL0nMD6nV9zY/U3Zliqp9uacRNLsY8/kwO
2lzM9o/PkxRMqqMtHqnNxCeoP4DDfaL2fNw2kQKBgBSj5iThrRzc/EN3xhPYRvpK
EzoHbeqxHkhgUfMC6IVHjPG9Sxg52radQY6ldKDKkJDtIKGpOtIRPj/iil+vUlC6
zBQcqvrZp/d/ajbW66SkEk8FAyxkp4/4/JxDa41nlw78xoagqQCuI2gytjXseGPo
5hzIFbslgI0bJduRrPAxAoGANMwAIREneCnEVdjILBRbd85FMcMeJ01utaNfvBw9
cGYNmgrvOGdy7fKWJc3xM9OhIjgvvskHUume1DZtCPPy/nZQ0gemea3fx2QJOQag
2OonsXg8oNdvH2nZl/dL6fhPxt6YRMPaJeXuvBvDHj46NL5w3dVg+8zv9NZksIql
dLECgYBMWRArq/47pELxbqU6l8nNcKQvL+1jlViHDUfRCH8Q2MnpwPhEu4JcsdTn
ZjogPmcgib4DsVMCqow3lIuMhW+qq0O3wO9Z/snCRgk9Re6B2Ec26zTLgKi5VoQe
9DMghQ2uGDcnaPtSHRDc4jOaG01Uue0q/b2/wlOTVeolHoUBvQ=="""

gradecoin_public_key = """MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1xyT0V8EA2PT5xSJ/eB8
1RokfotJERIjEZe3x+PCJOuwzn3K+/kYRXdEGS3bXJ01MMhKXnCvu6nWyQHcc01g
0OfvHQ5FfdFHQ8QApoHfgqlo/DYnPgSN1rJxAWYFPo0+JQb97RAV15c1IWSdJYhH
nyboPl5Y6gcvXhJorSoi9mOKeLvUDOtDb4EdxaUcGXQy/AIubhhTR1Vf0ZEWWD29
ri22pVTGzWUs1JCK8ixbuOSgTO/FSlLgRLyFowO67H/zhvRWIxdzFn7CTiqbAGxo
HjAmpZtTmHmgNrzQCKcJ0NYSMwuar16O6q0/affpDRHEmtSLvTMqUuu0GME+DKCn
gwIDAQAB
"""

def pad(m):
    return m+chr(16-len(m)%16)*(16-len(m)%16)

register_json = {
    "student_id" : student_id,
    "passwd" : one_time_password,
    "public_key" : own_public_key
}

register_str = json.dumps(register_json)

key = os.urandom(16)
IV = os.urandom(16)

print("Key:\n", base64.b64encode((key)).decode('ascii'))
print("IV:\n", base64.b64encode((IV)).decode('ascii'))

AES_encryptor = AES.new(key, AES.MODE_CBC, IV=IV)
register_str_ciphertext = AES_encryptor.encrypt(pad(register_str))


OAEP_encryptor = PKCS1_OAEP.new(key=gradecoin_public_key, hashAlgo=SHA256)
key_ciphertext = base64.b64encode(OAEP_encryptor.encrypt(key))
IV_b64 = base64.b64encode(IV)

print("register_str_ciphertext:\n", register_str_ciphertext.decode('ascii'))
print("key_ciphertext:\n", key_ciphertext.decode('ascii'))
print("IV_b64:\n", IV_b64.decode('ascii'))

json_payload = {
    "c": register_str_ciphertext,
    "iv": IV_b64,
    "key": key_ciphertext
}





