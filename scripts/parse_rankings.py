import csv

INPUT = r"c:\Users\rpbea\Documents\World Cup\data\rankings.csv"
OUTPUT = r"c:\Users\rpbea\Documents\World Cup\data\rankings_simple.csv"

lines = []
with open(INPUT, encoding='utf-8') as f:
    for ln in f:
        lines.append(ln.rstrip('\n'))

results = []
i = 0
while i < len(lines):
    s = lines[i].strip()
    if s.isdigit():
        rank = s
        # find next non-empty, non-digit line for team name
        j = i + 1
        while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().isdigit()):
            j += 1
        if j < len(lines):
            team = lines[j].strip()
            # skip rows where team looks like header or empty
            if team and not team.lower().startswith('team'):
                results.append((team, rank))
            i = j + 1
        else:
            i += 1
    else:
        i += 1

# write CSV
with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['team','rank'])
    for team, rank in results:
        w.writerow([team, rank])

print(f"Wrote {len(results)} teams to {OUTPUT}")
