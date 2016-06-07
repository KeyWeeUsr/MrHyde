import os
import array
from Crypto.Cipher import AES


class Secret(object):
    def __init__(self, secret=None):
        if secret is None:
            secret = os.urandom(16)
        self.secret = secret
        self.reset()

    def counter(self):
        for i, c in enumerate(self.current):
            if c + 1 >= 255:
                self.current[i] = 0
            else:
                self.current[i] = c + 1
        return self.current.tostring()

    def reset(self):
        self.current = array.array('B', self.secret)


class Vial(object):
    def __init__(self, key):
        self.key = key

    def encrypt(self, text, counter_path):
        secret = Secret()
        with open(counter_path, 'wb') as f:
            f.write(secret.secret)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=secret.counter)
        encrypted = crypto.encrypt(text)
        return encrypted

    def decrypt(self, text, counter_path):
        with open(counter_path, 'rb') as f:
            load_secret = f.read()
        secret = Secret(load_secret)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=secret.counter)
        decrypted = crypto.decrypt(text)
        return decrypted

    def encrypt_stream(self, input, output):
        secret = Secret()
        counter_path = os.path.splitext(output.name)[0] + '.ctr'
        with open(counter_path, 'wb') as f:
            f.write(secret.secret)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=secret.counter)
        while True:
            data = input.read(4096)
            if not data:
                break
            data = crypto.encrypt(data)
            output.write(data)

    def decrypt_stream(self, input, output):
        counter_path = os.path.splitext(input.name)[0] + '.ctr'
        with open(counter_path, 'rb') as f:
            counter_read = f.read()
        secret = Secret(counter_read)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=secret.counter)
        while True:
            data = input.read(4096)
            if not data:
                break
            data = crypto.decrypt(data)
            output.write(data)


if __name__ == '__main__':
    root_path = os.path.abspath(os.path.dirname(__file__))
    key32 = '0123456789' * 3 + 'QW'
    vial = Vial(key32)
    path = root_path + '/vial_test.ctr'
    enc = vial.encrypt(16 * 'a', path)
    print 'enc: ', enc, len(enc)

    vial = Vial(key32)
    path = root_path + '/vial_test.ctr'
    dec = vial.decrypt(enc, path)
    print 'dec: ', dec, len(dec)

    vial = Vial(key32)
    finput = open(root_path + 'encrypt_me.png', 'rb')
    foutput = open(root_path + 'im_encrypted.png', 'wb')
    vial.encrypt_stream(finput, foutput)
    fin.close()
    fout.close()

    vial = Vial(key32)
    finput = open(root_path + 'im_encrypted.png', 'rb')
    foutput = open(root_path + 'im_decrypted.png', 'wb')
    vial.decrypt_stream(finput, foutput)
    fin.close()
    fout.close()