import random

class A3Encryption():
    def __init__(self):
        self.encrypted_data = ''
        self.randomKey = random.randint(1, 65536)

    def start_encryption(self, text, key):
        self.encrypted_data = ''
        totalKey = 0
        key_lst = [i for i in key]
        random.shuffle(key_lst)
        key = "".join(key_lst)
        for i in key:
            totalKey += ord(i)

        key = int(bin(totalKey)[2:])
        
        for i in text:
            # encryption goes here
            # make the first xor operation for two steps

            # first step : xor with ascii value of each text and total ascii value of key
            encrypted_ord = ord(i) ^ totalKey
            # second step : xor with random value and result ascii value from first step
            doubleEncrypted_rod = encrypted_ord ^ self.randomKey

            # final step -> get the result encrypted data by changing the ascii into hexadecimal and concat with 'X'
            self.encrypted_data += str(hex(doubleEncrypted_rod)) + 'X'
        # concat again the result encrypted data  with 'x' sign : user key and random data
        # so that we can decrypt easily
        self.encrypted_data += str(hex(totalKey)) + 'X' + str(hex(self.randomKey))
        return self.encrypted_data


class A3Decryption():

    def __init__(self):
        self.dataList: list = []
        self.decrypted_data: str=''

    def startDecryption(self, encrypted_data: str):
        self.dataList = encrypted_data.split('X')
        keyList = self.dataList[-2:]
        key = int(keyList[0], 16) # get the ascii value of user key
        rKey = int(keyList[1], 16) # get the ascii value of random key
        # print("user key:", key, ": random key:", rKey)
        self.decrypted_data = ""
        for i in range(len(self.dataList)-2):
            # change each hexa value to int and xor with the random key
            # xor again with the user key
            dDecrypt: int = int(self.dataList[i], 16) ^ rKey
            decrypted_int = dDecrypt ^ key
            # change the resulted ascii value into character
            self.decrypted_data += chr(decrypted_int)

        # return back the decrypted result
        return self.decrypted_data
    
if __name__ == '__main__':
    decr = A3Decryption()
    print(decr.startDecryption("0xbd59X0xbd2eX0xbd59X0xbd36X0xbd23X0xbd0eX0xbd20X0xbd5cX0xbd3bX0xbd5dX0xbd16X0xbd06X0xbd0aX0xbd01X0xbd18X0xbd20X0xbd18X0xbd24X0x434X0xb95b"))