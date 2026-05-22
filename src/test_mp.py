#!/usr/bin/env python3
import multiprocessing

def test_func(x):
    return x * x

def main():
    with multiprocessing.Pool() as pool:
        results = pool.map(test_func, range(10))
    print("Results:", results)

if __name__ == "__main__":
    main()
