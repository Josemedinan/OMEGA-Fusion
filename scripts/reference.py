#!/usr/bin/env python3
"""Independent signed INT4/INT8 4x4 matrix multiplication reference model."""
import random

def decode(byte: int, int4: bool) -> int:
    val = (byte & 15) if int4 else (byte & 255)
    sign = 8 if int4 else 128
    return (val ^ sign) - sign

def matmul(a: list[int], b: list[int], int4: bool) -> list[int]:
    assert len(a) == len(b) == 16
    return [sum(decode(a[4*r+k], int4) * decode(b[4*k+c], int4)
                for k in range(4)) for r in range(4) for c in range(4)]

def run():
    rng = random.Random(0xF0510)
    count = 0
    for int4 in (False, True):
        for _ in range(2000):
            a = [rng.randrange(256) for _ in range(16)]
            b = [rng.randrange(256) for _ in range(16)]
            c = matmul(a, b, int4)
            bound = 4*(8*8 if int4 else 128*128)
            assert len(c) == 16 and all(-bound <= x <= bound for x in c)
            count += 1
    print(f"PASS reference arithmetic: {count} input tiles (software-only)")
if __name__ == '__main__':
    run()
