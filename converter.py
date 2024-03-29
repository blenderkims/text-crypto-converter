import base64
import hashlib
from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.Util import Padding
from Cryptodome import Random

from enum import Enum

AES_DEFAULT_PASSWORD = 'abcdefghijklmnopqrstuvwxyz'
AES_DEFAULT_SALT = '1234567890'
AES_BLOCK_SIZE = AES.block_size
RSA_DEFAULT_PASSPHRASE = AES_DEFAULT_PASSWORD + AES_DEFAULT_SALT

class RSA_BIT(Enum):
    RSA_1024 = 1024
    RSA_2048 = 2048

class SHA_ALGORITHM(Enum):
    SHA_256 = 'sha_256'
    SHA_512 = 'sha_512'
    SHA3_256 = 'sha3_256'
    SHA3_512 = 'sha3_512'

class OUTPUT_FORMAT(Enum):
    HEX = 'hex'
    B64 = 'b64'

class AESEncrypt:
    def encrypt(self, text, password=AES_DEFAULT_PASSWORD, salt=AES_DEFAULT_SALT, format=OUTPUT_FORMAT.HEX):
        key = hashlib.pbkdf2_hmac('sha512', password.encode(), salt.encode(), 2048, 32)
        iv = Random.get_random_bytes(AES_BLOCK_SIZE)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypt = iv + cipher.encrypt(Padding.pad(text.encode(), AES_BLOCK_SIZE))
        return encrypt.hex() if format == OUTPUT_FORMAT.HEX else base64.b64encode(encrypt).decode()

    def decrypt(self, text, password=AES_DEFAULT_PASSWORD, salt=AES_DEFAULT_SALT, format=OUTPUT_FORMAT.HEX):
        key = hashlib.pbkdf2_hmac('sha512', password.encode(), salt.encode(), 2048, 32)
        encrypt = bytes.fromhex(text) if format == OUTPUT_FORMAT.HEX else base64.b64decode(text)
        iv = encrypt[:AES_BLOCK_SIZE]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return Padding.unpad(cipher.decrypt(encrypt[AES_BLOCK_SIZE:]), AES_BLOCK_SIZE).decode()

class RSAEncrypt:
    def generate(self, bit=RSA_BIT.RSA_1024, passphrase=''):
        key = RSA.generate(bit.value, Random.new().read)
        prkey = key.exportKey(format='PEM', passphrase=passphrase, pkcs=8, protection='PBKDF2WithHMAC-SHA512AndAES256-CBC') if bool(passphrase.strip()) else key.exportKey(format='PEM')
        pbkey = key.publickey().exportKey(format='PEM', passphrase=passphrase, pkcs=8, protection='PBKDF2WithHMAC-SHA512AndAES256-CBC') if bool(passphrase.strip()) else key.publickey().exportKey(format='PEM')
        return (prkey, pbkey)

    def encrypt(self, text, pbkey, passphrase='', format=OUTPUT_FORMAT.HEX):
        key = RSA.importKey(pbkey, passphrase) if bool(passphrase.strip())  else RSA.importKey(pbkey)
        cipher = PKCS1_v1_5.new(key)
        encrypt = cipher.encrypt(text.encode())
        return encrypt.hex() if format == OUTPUT_FORMAT.HEX else base64.b64encode(encrypt).decode()

    def decrypt(self, text, prkey, passphrase='', format=OUTPUT_FORMAT.HEX):
        key = RSA.importKey(prkey, passphrase) if bool(passphrase.strip())  else RSA.importKey(prkey)
        cipher = PKCS1_v1_5.new(key)
        encrypt = bytes.fromhex(text) if format == OUTPUT_FORMAT.HEX else base64.b64decode(text)
        return cipher.decrypt(encrypt, None).decode()


class SHAHash:
    def hash(self, text, algorithm=SHA_ALGORITHM.SHA_256, format=OUTPUT_FORMAT.HEX):
        if algorithm == SHA_ALGORITHM.SHA_256:
            hash = hashlib.sha256(text.encode())
        elif algorithm == SHA_ALGORITHM.SHA_512:
            hash = hashlib.sha512(text.encode())
        elif algorithm == SHA_ALGORITHM.SHA3_256:
            hash = hashlib.sha3_256(text.encode())
        else:
            hash = hashlib.sha3_512(text.encode())
        return hash.hexdigest() if format == OUTPUT_FORMAT.HEX else base64.b64encode(hash.digest()).decode()

class B64Encode:
    def encode(self, text):
        return base64.b64encode(text.encode()).decode()
    def decode(self, text):
        return base64.b64decode(text.encode()).decode()
    def b64ToHex(self, text):
        return base64.b64decode(text.encode()).hex()
    def hexToB64(self, text):
        return base64.b64encode(bytes.fromhex(text)).decode()