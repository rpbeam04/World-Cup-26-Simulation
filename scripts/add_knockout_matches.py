import csv
from collections import defaultdict

BASE = r"c:\Users\rpbea\Documents\World Cup\data\schedule.csv"

# Helper to normalize team descriptions to placeholders
def normalize(team_desc):
    if not team_desc:
        return ''
    t = team_desc.strip()
    # Winner/Runner-up/3rd group patterns
    t = t.replace('Winner Group ', '1')
    t = t.replace('Runner-up Group ', '2')
    t = t.replace('Runner-up Group', '2')
    # replace '3rd Group ...' with 3X
    if t.startswith('3rd') or t.startswith('3rd '):
        return '3X'
    # handle patterns like '3rd Group A/B/C' with leading '3rd'
    if '3rd' in t:
        return '3X'
    # Winner/Runner-up Match N -> WN or  LN for Loser
    if t.startswith('Winner Match'):
        num = ''.join(ch for ch in t if ch.isdigit())
        return f'W{num}'
    if t.startswith('Loser Match'):
        num = ''.join(ch for ch in t if ch.isdigit())
        return f'L{num}'
    # Winner Match 74 style without 'Winner' handled above; also 'Winner Match 74' variations
    if t.startswith('Winner Match'):
        num = ''.join(ch for ch in t if ch.isdigit())
        return f'W{num}'
    # If already like 'Runner-up Group A' after earlier replace it's like '2A'
    if t.startswith('1') or t.startswith('2'):
        # remove spaces
        return t.replace(' ', '')
    # If already slot-like (1A, A1, etc) or group-slot like 'A1'
    # Normalize 'Mexico' -> handled earlier in schedule script; here keep literal if present
    # If token contains 'Group', fallback to 3X
    if 'Group' in t:
        return '3X'
    return t

# Knockout match definitions as (matchnum, date, home_desc, away_desc, stadium)
knockouts = [
    (73, '2026-06-28', 'Runner-up Group A', 'Runner-up Group B', 'SoFi Stadium'),
    (74, '2026-06-29', 'Winner Group E', '3rd Group A/B/C/D/F', 'Gillette Stadium'),
    (75, '2026-06-29', 'Winner Group F', 'Runner-up Group C', 'Estadio BBVA'),
    (76, '2026-06-29', 'Winner Group C', 'Runner-up Group F', 'NRG Stadium'),
    (77, '2026-06-30', 'Winner Group I', '3rd Group C/D/F/G/H', 'MetLife Stadium'),
    (78, '2026-06-30', 'Runner-up Group E', 'Runner-up Group I', 'AT&T Stadium'),
    (79, '2026-06-30', 'Winner Group A', '3rd Group C/E/F/H/I', 'Estadio Azteca'),
    (80, '2026-07-01', 'Winner Group L', '3rd Group E/H/I/J/K', 'Mercedes-Benz Stadium'),
    (81, '2026-07-01', 'Winner Group D', '3rd Group B/E/F/I/J', "Levi's Stadium"),
    (82, '2026-07-01', 'Winner Group G', '3rd Group A/E/H/I/J', 'Lumen Field'),
    (83, '2026-07-02', 'Runner-up Group K', 'Runner-up Group L', 'BMO Field'),
    (84, '2026-07-02', 'Winner Group H', 'Runner-up Group J', 'SoFi Stadium'),
    (85, '2026-07-02', 'Winner Group B', '3rd Group E/F/G/I/J', 'BC Place'),
    (86, '2026-07-03', 'Winner Group J', 'Runner-up Group H', 'Hard Rock Stadium'),
    (87, '2026-07-03', 'Winner Group K', '3rd Group D/E/I/J/L', 'Arrowhead Stadium'),
    (88, '2026-07-03', 'Runner-up Group D', 'Runner-up Group G', 'AT&T Stadium'),
    # R16
    (89, '2026-07-04', 'Winner Match 74', 'Winner Match 77', 'Lincoln Financial Field'),
    (90, '2026-07-04', 'Winner Match 73', 'Winner Match 75', 'NRG Stadium'),
    (91, '2026-07-05', 'Winner Match 76', 'Winner Match 78', 'MetLife Stadium'),
    (92, '2026-07-05', 'Winner Match 79', 'Winner Match 80', 'Estadio Azteca'),
    (93, '2026-07-06', 'Winner Match 83', 'Winner Match 84', 'AT&T Stadium'),
    (94, '2026-07-06', 'Winner Match 81', 'Winner Match 82', 'Lumen Field'),
    (95, '2026-07-07', 'Winner Match 86', 'Winner Match 88', 'Mercedes-Benz Stadium'),
    (96, '2026-07-07', 'Winner Match 85', 'Winner Match 87', 'BC Place'),
    # Quarterfinals
    (97, '2026-07-09', 'Winner Match 89', 'Winner Match 90', 'Gillette Stadium'),
    (98, '2026-07-10', 'Winner Match 93', 'Winner Match 94', 'SoFi Stadium'),
    (99, '2026-07-11', 'Winner Match 91', 'Winner Match 92', 'Hard Rock Stadium'),
    (100, '2026-07-11', 'Winner Match 95', 'Winner Match 96', 'Arrowhead Stadium'),
    # Semifinals
    (101, '2026-07-14', 'Winner Match 97', 'Winner Match 98', 'AT&T Stadium'),
    (102, '2026-07-15', 'Winner Match 99', 'Winner Match 100', 'Mercedes-Benz Stadium'),
    # Third place
    (103, '2026-07-18', 'Loser Match 101', 'Loser Match 102', 'Hard Rock Stadium'),
    # Final
    (104, '2026-07-19', 'Winner Match 101', 'Winner Match 102', 'MetLife Stadium'),
]

# stadium -> metro mapping (same as previous script)
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

# Load existing schedule
existing = {}
with open(BASE, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        existing[int(row['match'])] = row

# Add/overwrite knockout matches
for mnum, date, home_desc, away_desc, stadium in knockouts:
    home = normalize(home_desc)
    away = normalize(away_desc)
    metro = stadium_metro.get(stadium, '')
    existing[mnum] = {
        'match': str(mnum),
        'home': home,
        'away': away,
        'date': date,
        'time (est)': '',
        'stadium': stadium,
        'location': metro,
    }

# Assign times per date using rules from user
by_date = defaultdict(list)
for row in existing.values():
    by_date[row['date']].append(row)

for date, lst in by_date.items():
    lst.sort(key=lambda r: int(r['match']))
    cnt = len(lst)
    # Determine times
    if cnt == 3:
        times = ['12:00', '15:00', '18:00']
    elif cnt == 2:
        times = ['15:00', '18:00']
    else:
        # for single/other counts, place at 15:00 per instruction
        times = ['15:00'] * cnt
    for i, r in enumerate(lst):
        # Only overwrite empty times (preserve group-stage assigned times)
        if not r.get('time (est)'):
            r['time (est)'] = times[i] if i < len(times) else times[-1]

# Write updated CSV sorted by match number
fieldnames = ['match','home','away','date','time (est)','stadium','location']
with open(BASE, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for m in sorted(existing.keys()):
        w.writerow(existing[m])

print('Inserted knockout matches 73-104 into', BASE)
