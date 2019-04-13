from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes, hmac
from cryptography.hazmat.primitives.asymmetric import padding as paddings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from os import urandom
from os import path

folderPath = "/Users/SadiqSarwar/Desktop/Lake.jpg"
encPath = "/Users/SadiqSarwar/Desktop/Lake[Encrypted].enc"
decPath = "/Users/SadiqSarwar/Desktop/Lake[Decypted].jpg"
RSA_publicKey_filepath = "/Users/SadiqSarwar/Desktop/RSA_Public_Key.pem"
RSA_privateKey_filepath = "/Users/SadiqSarwar/Desktop/RSA_Private_Key.pem"
ext = ".jpg"
ivLen = 16
keyLen = 32
padLen = 128
hmacLen = 256


def menu():
    print(" --[Menu]-- ")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Exit")
    
    '''
    #Generate key
    #public_exponent = Fermat Prime # to use as exponent for new key. Recommended: 65537
    #key_size = Bit length of key
    #backend = Implements RSABackend
    '''
def retrieveRSAKeys():
    PrivateKeyExists = path.isfile(RSA_privateKey_filepath)
    PublicKeyExists = path.isfile(RSA_publicKey_filepath)
    
    if PrivateKeyExists and PublicKeyExists:
        print("[File was found in path - Keys have been loaded]")
        with open(RSA_privateKey_filepath, "rb") as key_file:
            privateKey = serialization.load_pem_private_key(key_file.read(),
                                                             password=None,
                                                             backend=default_backend())
        with open(RSA_publicKey_filepath, "rb") as key_file:
            publicKey = serialization.load_pem_public_key(key_file.read(),
                                                             backend=default_backend())    
            
        return publicKey, privateKey
    
    else:
        print("[File was not found in path - Generating new keys]")
        #Generate Private Key
        privateKey = rsa.generate_private_key(public_exponent = 65537,
                                              key_size = 4096,
                                              backend = default_backend())
        #Encode Private Key into PEM File
        pem = privateKey.private_bytes(encoding = serialization.Encoding.PEM,
                                       format = serialization.PrivateFormat.TraditionalOpenSSL,
                                       encryption_algorithm = serialization.NoEncryption())
        pem.splitlines()[0]
        
        #Open File Path for Private Key
        privateKeySave = open(RSA_privateKey_filepath, "wb")
        #Save Private Key to Path
        privateKeySave.write(pem)
        #Close File
        privateKeySave.close()
        
        
        #Generate Public Key
        publicKey = privateKey.public_key()
        #Enclode Public Key into PEM file
        pem = publicKey.public_bytes(encoding = serialization.Encoding.PEM,
                                     format = serialization.PublicFormat.SubjectPublicKeyInfo)
        pem.splitlines()[0]
        
        #Open File Path for Private Key
        publicKeySave = open(RSA_publicKey_filepath, "wb")
        #Save Private Key to Path
        publicKeySave.write(pem)
        #Close File
        publicKeySave.close()
        
        return publicKey, privateKey
        
    
    
    
def myRSAEncrypt():
    
    #Load Encryption Information
    encrypInfo = myFileEncryptMAC()
    
    #Load from RSA Keys from File Path
    RSA_KeyInfo = retrieveRSAKeys()
    publicKey = RSA_KeyInfo[0]
    privateKey = RSA_KeyInfo[1]
    
    #Encrypting Key Variable
    key = encrypInfo[3] + encrypInfo[4]
    RSA_CipherText = publicKey.encrypt(key, paddings.OAEP(
            mgf = paddings.MGF1(algorithm = hashes.SHA256()),
            algorithm = hashes.SHA256(),
            label = None))
    print("Complete")
    return RSA_CipherText, encrypInfo[0], encrypInfo[1], encrypInfo[5]


def read(filepath):
    return open(filepath, "rb").read()

def myEncryptMAC(file, key, hkey):
    iv = urandom(ivLen)
    backend = default_backend()
    padder = padding.PKCS7(padLen).padder()
    paddedFile = padder.update(file)
    paddedFile += padder.finalize()
    encryption = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = encryption.encryptor()
    cipherText = encryptor.update(paddedFile) + encryptor.finalize()
    hashfunc = hmac.HMAC(hkey, hashes.SHA256(), backend = default_backend())
    tag = hashfunc.update(cipherText)
    tag = hashfunc.finalize()
    enc = open(encPath, "wb")
    enc.write(cipherText)
    return cipherText, iv, tag

def myFileEncryptMAC():
    filePath = folderPath
    file = read(filePath)
    key = urandom(keyLen)
    hkey = urandom(hmacLen)
    encryptedSet = myEncryptMAC(file, key, hkey)
    return encryptedSet[0], encryptedSet[1], encryptedSet[2], key, hkey, ext

def myDecryptMAC(file, key, iv, tag, hkey):
    backend = default_backend()
    hashfunc = hmac.HMAC(hkey, hashes.SHA256(), backend = default_backend())
    revMes = hashfunc.update(file)
    revMes = hashfunc.verify(tag)
    if(revMes == None):
        print("[Verification has proceeded successfully]")
    else:
        print("[Error: " + revMes + "]")
    decryption = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = decryption.decryptor()
    paddedFile = decryptor.update(file) + decryptor.finalize()
    unpadder = padding.PKCS7(padLen).unpadder()
    plainText = unpadder.update(paddedFile)
    plainText += unpadder.finalize()
    return plainText

def myFileDecryptMAC(encrypInfo):
    file = read(encPath)
    decryptedSet = myDecryptMAC(file, encrypInfo[3],encrypInfo[1],encrypInfo[2],encrypInfo[4])
    dec = open(decPath, "wb")
    dec.write(decryptedSet)
    
### BELOW AES METHOD WITHOUT HASH

def myEncrypt(file, key):
    iv = urandom(ivLen)
    backend = default_backend()
    padder = padding.PKCS7(padLen).padder()
    paddedFile = padder.update(file)
    paddedFile += padder.finalize()
    encryption = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = encryption.encryptor()
    cipherText = encryptor.update(paddedFile) + encryptor.finalize()
    enc = open(encPath, "wb")
    enc.write(cipherText)
    return cipherText, iv

def myFileEncrypt():
    filePath = folderPath
    file = read(filePath)
    key = urandom(keyLen)
    encryptedSet = myEncrypt(file, key)
    return encryptedSet[0], encryptedSet[1], key, ext

def myDecrypt(file, key, iv):
    backend = default_backend()
    decryption = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = decryption.decryptor()
    paddedFile = decryptor.update(file) + decryptor.finalize()
    unpadder = padding.PKCS7(padLen).unpadder()
    plainText = unpadder.update(paddedFile)
    plainText += unpadder.finalize()
    return plainText


def myFileDecrypt(encrypInfo):
    file = read(encPath)
    decryptedSet = myDecrypt(file, encrypInfo[2],encrypInfo[1])
    dec = open(decPath, "wb")
    dec.write(decryptedSet)

def main():
    myRSAEncrypt()
    '''
    encrypInfo = None
    cont = True
    while cont:
        menu()
        choice = int(input("Please Enter Menu Option: "))
        if choice == 1:
            encrypInfo = myFileEncryptMAC()
            print("[File has been encypted]")
            print("--------------------------------\n")
        elif choice == 2:
            myFileDecryptMAC(encrypInfo)
            print("[File has been decrypted]")
            print("--------------------------------\n")
        elif choice == 3:
            print("[Program Terminated]")
            print("--------------------------------\n")
            cont = False
        else:
            print("Invalid Input")
    '''

main()