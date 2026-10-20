import random

def get_random_string(l=4):
    alphanumeric = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choices(alphanumeric, k=l))
