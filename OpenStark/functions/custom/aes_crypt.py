import base64

from Cryptodome.Cipher import AES

# 如果text不足16位的倍数就用空格补足为16位
class AESCrypt(object):
    def __init__(self, key='', iv='', mode='CBC'):
        self.key = 'cloudwisdomadjsn'.encode('utf-8')
        self.iv = b'5721678222017913'
        self.mode = mode
        self.mode = AES.MODE_CBC
    def add_to_16(self,text):
        if len(text.encode('utf-8')) % 16:
            add = 16 - (len(text.encode('utf-8')) % 16)
        else:
            add = 0
        text = text + ('\0' * add)
        return text.encode('utf-8')


    # 加密函数
    def aes_encode(self,text):
        text = self.add_to_16(text)
        cryptos = AES.new(self.key, self.mode, self.iv)
        cipher_text = cryptos.encrypt(text)
        return cipher_text


    # 解密后，去掉补足的空格用strip() 去掉
    def aes_decode(self,text):
        cryptos = AES.new(self.key, self.mode, self.iv)
        plain_text = base64.b64decode(text,'-_')
        plain_text = cryptos.decrypt(plain_text)
        return bytes.decode(plain_text).rstrip('\0')



if __name__ == '__main__':
    key = 'cloudwisdomadjsn'.encode('utf-8')
    iv = b'5721678222017913'
    mode = 'CBC'
    #e = AESCrypt(key=key,iv=iv,mode=mode).aes_encode('{"RQModel_CheckInfo":[{"Identity":"18611625312","ArrDate":"2020-02-26","DptDate":"2020-03-04","Status":"1","SearchFlg":"3","SearchMainAcct":"False","SearchLockFlag":"False"}],"grpcd":"lc","htlcd":"lc01","staffcd":"9897","token":"52138214DD7DC7A80073B3C2CF3D2AD5F0841C16","staffpassword":"sunwood","isformal":"True","mac":"6C-0B-84-08-06-78"}')  # 加密

    b = "gHlNqppn3Hd7B3UfUVwaid6SdFsnYAV53hv7C24YgObhiZUuYyq3FS8dyfgKkxl6KsVTa0gNwHdJbFaeOSPvlBEXfq6y06+KFYx2CSdr5ky/qyG5AQomq+AuGfBmaZWIhJ/KsjXfZwPctEzoxiP31A=="
    d = AESCrypt(key=key,iv=iv,mode=mode).aes_decode(b)  # 解密
    #print("加密:", type(b),e)
    print("解密:", d)