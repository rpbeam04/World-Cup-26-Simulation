import csv

INPUT = r"c:\Users\rpbea\Documents\World Cup\data\rankings.txt"
OUTPUT = r"c:\Users\rpbea\Documents\World Cup\data\rankings.csv"

teams = []
with open(INPUT, encoding='utf-8') as f:
    lines = [ln.rstrip('\n') for ln in f]

i = 0
while i < len(lines):
    s = lines[i].strip()
    # look for a rank line (pure digits)
    if s.isdigit():
        rank = s
        # find next non-empty, non-digit line for the team name
        j = i + 1
        team = None
        while j < len(lines):
            cand = lines[j].strip()
            if cand == '':
                j += 1
                continue
            # skip if the candidate is purely numeric (movement or extra numbers)
            if cand.isdigit():
                j += 1
                continue
            # otherwise we assume this is the team name
            team = cand
            break
        if team:
            teams.append((team, rank))
            print('Found:', rank, team)
        i = j + 1
    else:
        i += 1

with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['team','rank'])
    for team, rank in teams:
        w.writerow([team, rank])

print(f'Wrote {len(teams)} rows to {OUTPUT}')
