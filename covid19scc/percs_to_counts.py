import sys


def main():
    with open(sys.argv[1]) as f:
        cases = int(sys.argv[2])
        lines = f.readlines()
        percs = lines[1].split(",")
        counts = []
        for s in percs:
            p = float(s) / 100
            counts.append(str(round(p * cases)))
        print(", ".join(counts))


if __name__ == '__main__':
    main()
