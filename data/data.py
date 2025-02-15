# system
import sys
import os
import math
import random
import binascii


# lib
import numpy as np
from keras.preprocessing.image import img_to_array, load_img

# self
from data.DES import des


def gen_symmetric_encryption_data(n, msg_len=16, key_len=16, center_zero=True):
    """
    generate data to allow the model to train for symmetric encryption.
    :param n: how much data
    :param msg_len: the length of the message
    :param key_len: the length of the key
    :return: the data as (messages, keys)
    """
    a, b = np.random.randint(0, 2, size=(n, msg_len)),\
           np.random.randint(0, 2, size=(n, key_len))

    if not center_zero:
        return a, b

    return a*2-1, b*2-1


def gen_xor_data(n, length, center_zero=True):
    """
    generate n samples of two random bit strings of
    the same length

    :param n: the number of samples
    :param length: the length of each bit string
    :return: input_1, input_2, xor result
    """
    a = np.random.randint(0, 2, size=(n, length))
    b = np.random.randint(0, 2, size=(n, length))
    xor = a ^ b

    if not center_zero:
        return a, b, xor

    return (a*2-1,
            b*2-1,
            xor*2-1)


def gen_broken_otp_data(n, length, key):
    """
    generate n samples of a broken one time pad
    encryption

    :param n: the number of samples
    :param length: the length of each bit string
    :param key: The key. len(key) == length
    :return: messages, encryptions
    """
    a = np.random.randint(0, 2, size=(n, length))
    print(a[0], type(a[0]))
    xor = a ^ key

    return (a*2-1,
            xor*2-1)


def gen_reduced_des_ecb_data(amt, n, length, key, rounds):
    """
    generate amt plaintext/DES ECB ciphertext pairs n times

    :param n: the number of samples
    :param length: the length of each bit string
    :param key: The key. len(key) == length
    :param rounds: The number of DES rounds to run
    :return: messages, encryptions
    """
    p = np.vstack([np.random.randint(2,size=(64)) for j in range(amt)] for i in range(int(n/amt)))
    d = des()
    c = np.vstack([d.encrypt(key, t, rounds=rounds)] for t in p)
    return (2 * p - 1, 2 * c - 1)


def gen_des_ecb_data(n, length, key, rounds):
    """
    generate n plaintext/DES ECB ciphertext pairs

    :param n: the number of samples
    :param length: the length of each bit string
    :param key: The key. len(key) == length
    :param rounds: The number of DES rounds to run
    :return: messages, encryptions
    """
    p = np.random.randint(2,size=(n, 64))
    d = des()
    c = np.vstack([d.encrypt(key, t, rounds=rounds)] for t in p)
    return (2 * p - 1, 2 * c - 1)


def gen_secure_otp_data(n, length):
    """
    generate n samples of two random bit strings of
    the same length

    :param n: the number of samples
    :param length: the length of each bit string
    :return: input_1, input_2, xor result
    """
    a = np.random.randint(0, 2, size=(n, length))
    b = np.random.randint(0, 2, size=(n, length))
    xor = a ^ b

    return (a*2-1,
            xor*2-1)


def load_image(number, path='./web/static/images', scale=1./255):
    print(number, os.path.join(path, "{:05}".format(number) + ".png"))
    img = load_img(os.path.join(path, "{:05}".format(number) + ".png"))
    x = np.array(img)
    x = x.astype(float) * scale
    return x


def load_images(path='./data/images/',
                shuffle=False,
                scale=1./255.):
    """
    load images into numpy array from /images directory

    :return: a 4d array of numpy images: (shape, height, width, channels=3)
    """
    images = []
    for file in os.listdir(path):
        if 'jpg' in file.lower() or 'png' in file.lower():
            img = load_img(os.path.join(path, file))
            image = img_to_array(img)
            images.append(image)

    x = np.array(images)

    if shuffle:
        x = x[np.random.permutation(len(x))]

    x = x.astype(float) * scale

    return x


DEFAULT_SECRET_SCALER = lambda x: x


def load_image_covers_and_random_bit_secrets(how_many,
                                             image_dir='./data/images',
                                             scale=1./255.,
                                             secret_modifier=DEFAULT_SECRET_SCALER,
                                             bit_channels=1):
    """
    load image covers and random bit secrets. The images
    will be a random section of the images in data/images

    :param how_many: how many covers/secrets
    :param image_dir: the image directory
    :param bit_channels: the number of channels in the bits
    :return: the covers and channels
    """

    covers = load_images(image_dir, shuffle=True, scale=scale)
    print(covers[0][0][0])

    if how_many > len(covers):
        covers = np.vstack([covers]*int(math.ceil(how_many/len(covers))))

    covers = covers[:how_many]
    covers = covers[np.random.permutation(len(covers))]

    secret_shape = covers.shape[:-1]
    secrets = np.random.randint(0, 2, size=(*secret_shape, bit_channels))

    return covers, secret_modifier(secrets)


def load_image_covers_and_image_secrets(how_many,
                                        image_dir='./data/images',
                                        scale=1./255.):

    covers = load_images(image_dir, shuffle=True, scale=scale)
    p = np.random.permutation(len(covers))
    secrets = covers[p]

    if how_many > len(covers):
        covers = np.vstack([covers] * int(math.ceil(how_many / len(covers))))
        secrets = np.vstack([secrets] * int(math.ceil(how_many / len(secrets))))

    covers = covers[:how_many]
    secrets = secrets[:how_many]

    p1 = np.random.permutation(len(covers))
    p2 = np.random.permutation(len(secrets))

    covers = covers[p1]
    secrets = secrets[p2]

    return covers, secrets


def load_image_covers_and_ascii_bit_secrets(how_many,
                                            image_dir='./data/images',
                                            secret_modifier=DEFAULT_SECRET_SCALER,
                                            scale=1./255.,
                                            bit_channels=3):
    """
    load image covers from the data directory and generate secrets
    that are drawn from the ascii encryption of a string drawn
    from english words. The bits are returned 1 channel deep by
    default.

    :param how_many: how many covers/secrets
    :param image_dir: the image directory
    :param secret_modifier: the function to modify the secret
                            (scale or alter it)
    :param bit_channels: the number of bit chanels
    :return:
    """
    covers = load_images(image_dir, shuffle=True, scale=scale)

    if how_many > len(covers):
        covers = np.vstack([covers] * int(math.ceil(how_many / len(covers))))

    covers = covers[:how_many]
    covers = covers[np.random.permutation(len(covers))]

    width, height = covers.shape[1], covers.shape[2]
    num_characters_for_secret = int(((width*height)/8))*bit_channels

    with open('./data/words.txt') as f:
        words = f.read().splitlines()

    secrets = []
    for i in range(how_many):

        _str = ''  # string to encrypt
        while len(_str) < num_characters_for_secret:
            _str += (' ' + random.choice(words)) if len(_str) > 0 else random.choice(words)

        _str = _str[:num_characters_for_secret]
        bit_str = [0] + [int(e) for e in list(bin(int.from_bytes(_str.encode(), 'big'))[2:])]

        secret = np.array(bit_str)
        secret = secret.reshape((height, width, bit_channels))

        secrets.append(
            secret
        )

    secrets = np.array(secrets)

    return covers, secret_modifier(secrets)


class LsbSteganography:

    @staticmethod
    def encode(how_many,
               image_dir='./data/images',
               scale=1./255.,
               return_secrets=False):
        """
        draw random images and gernate ascii bit secrest, then
        return images with those ascii secrets hidden with LSB
        Steganographhy

        :param how_many: how many samples
        :return: new covers of shape (how_many, height, width, 3)
        """

        covers, secrets = load_image_covers_and_ascii_bit_secrets(how_many,
                                                                  image_dir=image_dir,
                                                                  scale=1,
                                                                  bit_channels=3)

        return LsbSteganography.encode(covers, secrets, return_secrets=return_secrets, scale=scale)

    @staticmethod
    def encode(covers,
               secrets,
               scale=1./255.,
               return_secrets=False):

        covers_mod2 = (covers % 2).astype(int)
        secret_changes = covers_mod2 ^ secrets

        np.set_printoptions(edgeitems=10)

        new_covers = covers + secret_changes
        new_covers[new_covers == 256] = 254

        if return_secrets:
            return new_covers, secrets

        new_covers *= scale

        return new_covers

    @staticmethod
    def decode(covers,
               scale=1./255.):
        """
        decode lsb steganography

        :param covers: the covers (with secret)
        :return: the secrets with shape covers.shape
        """
        return (covers * (1/scale)) % 2

    @staticmethod
    def _verify(how_many):
        covers, secrets = LsbSteganography.encode(how_many, return_secrets=True)
        return np.all(secrets == LsbSteganography.decode(covers))



