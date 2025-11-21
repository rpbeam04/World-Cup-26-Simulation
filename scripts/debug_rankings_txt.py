INPUT = r"c:\Users\rpbea\Documents\World Cup\data\rankings.txt"
with open(INPUT, encoding='utf-8') as f:
    for i, ln in enumerate(f, start=1):
        if i <= 120:
            s = ln.rstrip('\n')
            print(i, repr(s), 'isdigit=', s.strip().isdigit())
        else:
            break
