import os

P = 179769313486231590770839156793787453197860296048756011706444423684197180216158519368947833795864925541502180565485980503646440548199239100050792877003355816639229553136239076508735759914822574862575007425302077447712589550957937778424442426617334727629299387668709205606050270810842907692932019128194467627007
g = 2

def power_modulo(m : int, c : int, N : int) -> int:
    s = 1
    while c > 1:
        if c % 2:
            # print(f"c = {c}")
            s = (s*m)%N
        m = (m * m) % N
        c //= 2
    return (m * s)%N

def generate_private_key():
    random_bytes = os.urandom(128)
    return int.from_bytes(random_bytes, 'little')

def generate_public_key(private_key):
    return power_modulo(g, private_key, P)

def generate_keypair():
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    return private_key, public_key

def get_shared_secret(other_public_key, my_private_key):
    return power_modulo(other_public_key, my_private_key, P)

def get_key_from_shared_secret(shared_secret):
    mask = (1 << 128) - 1
    key = shared_secret & mask
    key |= (1 << 127)
    key = key.to_bytes(16, 'big')
    return key