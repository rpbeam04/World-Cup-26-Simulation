INPUT = r"c:\Users\rpbea\Documents\World Cup\data\rankings.csv"
with open(INPUT, encoding='utf-8') as f:
    for i, ln in enumerate(f):
        if i < 120:
            print(i, repr(ln.rstrip('\n')))
        else:
            break
