def power_modulo(m : int, c : int, N : int) -> int:
    s = 1
    while c > 1:
        if c % 2:
            # print(f"c = {c}")
            s = (s*m)%N
        m = (m * m) % N
        c //= 2
    return (m * s)%N