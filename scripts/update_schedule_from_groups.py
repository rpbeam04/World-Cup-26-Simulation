import csv
from collections import defaultdict

BASE_CSV = r"c:\Users\rpbea\Documents\World Cup\data\schedule.csv"
OUT_CSV = BASE_CSV

# Mapping stadium city -> FIFA metro area (major metro associated with stadium)
stadium_metro = {
    'Estadio Azteca': 'Mexico City',
    'Estadio Akron': 'Guadalajara',
    'Mercedes-Benz Stadium': 'Atlanta',
    'Estadio BBVA': 'Monterrey',
    'BMO Field': 'Toronto',
    "Levi's Stadium": 'San Francisco',
    'SoFi Stadium': 'Los Angeles',
    'BC Place': 'Vancouver',
    'BC Place Stadium': 'Vancouver',
    'Gillette Stadium': 'Boston',
    'MetLife Stadium': 'New York',
    'Hard Rock Stadium': 'Miami',
    'AT&T Stadium': 'Dallas',
    'NRG Stadium': 'Houston',
    'Arrowhead Stadium': 'Kansas City',
    'Lumen Field': 'Seattle',
    'Lincoln Financial Field': 'Philadelphia',
}

# Convenience: map known named teams to group slots
team_to_slot = {
    'Mexico': 'A1',
    'Canada': 'B1',
    'United States': 'D1',
}

# Group matchup rules for matchdays when teams aren't listed
# For each group, match numbers are provided; use these templates:
# Matchday1: match_a = 1v2, match_b = 3v4
# Matchday2: match_c = 4v2, match_d = 1v3
# Matchday3: match_e = 4v1, match_f = 2v3

def slot(group, n):
    return f"{group}{n}"

groups = {
    'A': [
        # (date, matchnum, home, away, stadium)
        ('2026-06-11', 1, 'Mexico', 'A2', 'Estadio Azteca'),
        ('2026-06-11', 2, 'A3', 'A4', 'Estadio Akron'),
        ('2026-06-18', 25, 'A4', 'A2', "Mercedes-Benz Stadium"),
        ('2026-06-18', 28, 'Mexico', 'A3', 'Estadio Akron'),
        ('2026-06-24', 53, 'A4', 'Mexico', 'Estadio Azteca'),
        ('2026-06-24', 54, 'A2', 'A3', 'Estadio BBVA'),
    ],
    'B': [
        ('2026-06-12', 3, 'Canada', 'B2', 'BMO Field'),
        ('2026-06-13', 8, 'B3', 'B4', "Levi's Stadium"),
        ('2026-06-18', 26, 'B4', 'B2', 'SoFi Stadium'),
        ('2026-06-18', 27, 'Canada', 'B3', 'BC Place'),
        ('2026-06-24', 51, 'B4', 'Canada', 'BC Place'),
        ('2026-06-24', 52, 'B2', 'B3', 'Lumen Field'),
    ],
    'C': [
        ('2026-06-13', 5, None, None, 'Gillette Stadium'),
        ('2026-06-13', 7, None, None, 'MetLife Stadium'),
        ('2026-06-19', 29, None, None, 'Lincoln Financial Field'),
        ('2026-06-19', 30, None, None, 'Gillette Stadium'),
        ('2026-06-24', 49, None, None, 'Hard Rock Stadium'),
        ('2026-06-24', 50, None, None, 'Mercedes-Benz Stadium'),
    ],
    'D': [
        ('2026-06-12', 4, 'United States', 'D2', 'SoFi Stadium'),
        ('2026-06-13', 6, 'D3', 'D4', 'BC Place'),
        ('2026-06-19', 31, 'D4', 'D2', "Levi's Stadium"),
        ('2026-06-19', 32, 'United States', 'D3', 'Lumen Field'),
        ('2026-06-25', 59, 'D4', 'United States', 'SoFi Stadium'),
        ('2026-06-25', 60, 'D2', 'D3', "Levi's Stadium"),
    ],
    'E': [
        ('2026-06-14', 9, None, None, 'Lincoln Financial Field'),
        ('2026-06-14', 10, None, None, 'NRG Stadium'),
        ('2026-06-20', 33, None, None, 'BMO Field'),
        ('2026-06-20', 34, None, None, 'Arrowhead Stadium'),
        ('2026-06-25', 55, None, None, 'Lincoln Financial Field'),
        ('2026-06-25', 56, None, None, 'MetLife Stadium'),
    ],
    'F': [
        ('2026-06-14', 11, None, None, 'AT&T Stadium'),
        ('2026-06-14', 12, None, None, 'Estadio BBVA'),
        ('2026-06-20', 35, None, None, 'NRG Stadium'),
        ('2026-06-20', 36, None, None, 'Estadio BBVA'),
        ('2026-06-25', 57, None, None, 'AT&T Stadium'),
        ('2026-06-25', 58, None, None, 'Arrowhead Stadium'),
    ],
    'G': [
        ('2026-06-15', 15, None, None, 'SoFi Stadium'),
        ('2026-06-15', 16, None, None, 'Lumen Field'),
        ('2026-06-21', 39, None, None, 'SoFi Stadium'),
        ('2026-06-21', 40, None, None, 'BC Place'),
        ('2026-06-26', 63, None, None, 'Lumen Field'),
        ('2026-06-26', 64, None, None, 'BC Place'),
    ],
    'H': [
        ('2026-06-15', 13, None, None, 'Hard Rock Stadium'),
        ('2026-06-15', 14, None, None, "Mercedes-Benz Stadium"),
        ('2026-06-21', 37, None, None, 'Hard Rock Stadium'),
        ('2026-06-21', 38, None, None, 'Mercedes-Benz Stadium'),
        ('2026-06-26', 65, None, None, 'NRG Stadium'),
        ('2026-06-26', 66, None, None, 'Estadio Akron'),
    ],
    'I': [
        ('2026-06-16', 17, None, None, 'MetLife Stadium'),
        ('2026-06-16', 18, None, None, 'Gillette Stadium'),
        ('2026-06-22', 41, None, None, 'MetLife Stadium'),
        ('2026-06-22', 42, None, None, 'Lincoln Financial Field'),
        ('2026-06-26', 61, None, None, 'Gillette Stadium'),
        ('2026-06-26', 62, None, None, 'BMO Field'),
    ],
    'J': [
        ('2026-06-16', 19, None, None, 'Arrowhead Stadium'),
        ('2026-06-16', 20, None, None, "Levi's Stadium"),
        ('2026-06-22', 43, None, None, 'AT&T Stadium'),
        ('2026-06-22', 44, None, None, "Levi's Stadium"),
        ('2026-06-27', 69, None, None, 'Arrowhead Stadium'),
        ('2026-06-27', 70, None, None, 'AT&T Stadium'),
    ],
    'K': [
        ('2026-06-17', 23, None, None, 'NRG Stadium'),
        ('2026-06-17', 24, None, None, 'Estadio Azteca'),
        ('2026-06-23', 47, None, None, 'NRG Stadium'),
        ('2026-06-23', 48, None, None, 'Estadio Akron'),
        ('2026-06-27', 71, None, None, 'Hard Rock Stadium'),
        ('2026-06-27', 72, None, None, 'Mercedes-Benz Stadium'),
    ],
    'L': [
        ('2026-06-17', 21, None, None, 'BMO Field'),
        ('2026-06-17', 22, None, None, 'AT&T Stadium'),
        ('2026-06-23', 45, None, None, 'Gillette Stadium'),
        ('2026-06-23', 46, None, None, 'BMO Field'),
        ('2026-06-27', 67, None, None, 'MetLife Stadium'),
        ('2026-06-27', 68, None, None, 'Lincoln Financial Field'),
    ],
}

# Build match entries
matches = {}
for g, entries in groups.items():
    for date, mnum, home, away, stadium in entries:
        # determine home/away placeholders
        if home is None and away is None:
            # Determine which of the 6 match templates this mnum corresponds to for the group
            # Find index in group's entries to know which matchday it is (0..5)
            idx = next(i for i,e in enumerate(entries) if e[1]==mnum)
            # idx 0,1 -> matchday1; 2,3 -> matchday2; 4,5 -> matchday3
            if idx == 0:
                home_slot = slot(g,1)
                away_slot = slot(g,2)
            elif idx == 1:
                home_slot = slot(g,3)
                away_slot = slot(g,4)
            elif idx == 2:
                home_slot = slot(g,4)
                away_slot = slot(g,2)
            elif idx == 3:
                home_slot = slot(g,1)
                away_slot = slot(g,3)
            elif idx == 4:
                home_slot = slot(g,4)
                away_slot = slot(g,1)
            elif idx == 5:
                home_slot = slot(g,2)
                away_slot = slot(g,3)
            home = home_slot
            away = away_slot
        else:
            # translate named teams like 'Mexico' to slot if necessary
            if home in team_to_slot:
                home = team_to_slot[home]
            if away in team_to_slot:
                away = team_to_slot[away]
        metro = stadium_metro.get(stadium, None)
        matches[mnum] = {
            'match': str(mnum),
            'home': home,
            'away': away,
            'date': date,
            'time (est)': '',
            'stadium': stadium,
            'location': metro if metro else '',
        }

# Load existing CSV to preserve entries (like initial matches 1-8 which have times)
existing = {}
with open(BASE_CSV, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        existing[int(row['match'])] = row

# Merge: existing rows preserved, matches from groups override or fill
for mnum, info in matches.items():
    if int(mnum) in existing:
        # update existing entry fields (preserve time if present)
        row = existing[int(mnum)]
        row['home'] = info['home']
        row['away'] = info['away']
        row['date'] = info['date']
        if not row.get('time (est)'):
            row['time (est)'] = info['time (est)']
        row['stadium'] = info['stadium']
        row['location'] = info['location']
        matches[mnum] = row

# Add/replace into a single dict keyed by match number
all_matches = {}
all_matches.update({k: existing[k] for k in existing})
for mnum, info in matches.items():
    all_matches[int(mnum)] = info

# Determine times per date using your rules
by_date = defaultdict(list)
for m in all_matches.values():
    by_date[m['date']].append(m)

for date, lst in by_date.items():
    # sort by match number
    lst.sort(key=lambda x: int(x['match']))
    cnt = len(lst)
    if cnt == 4:
        times = ['12:00', '15:00', '18:00', '21:00']
    elif cnt == 6:
        times = ['12:00', '12:00', '15:00', '15:00', '18:00', '18:00']
    elif cnt == 2:
        # preserve any existing times; otherwise assign 15 and 18
        times = [lst[0].get('time (est)') or '15:00', lst[1].get('time (est)') or '18:00']
    else:
        # fallback: assign afternoons progressively
        base = ['12:00','15:00','18:00','21:00']
        times = [base[i%4] for i in range(cnt)]

    for i, row in enumerate(lst):
        if not row.get('time (est)'):
            row['time (est)'] = times[i]

# Write out CSV sorted by match number
fieldnames = ['match','home','away','date','time (est)','stadium','location']
with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for mnum in sorted(all_matches.keys()):
        row = all_matches[mnum]
        # ensure all fields present
        out = {k: row.get(k, '') for k in fieldnames}
        w.writerow(out)

print(f"Wrote schedule with {len(all_matches)} matches to {OUT_CSV}")
