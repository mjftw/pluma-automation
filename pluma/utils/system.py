import string
import random


def random_dir_name():
    '''Return a random directory name'''
    characters = string.ascii_letters + string.digits
    return 'pluma-' + ''.join(random.choice(characters) for i in range(10))
