import csv

input_path = r"c:\Users\rpbea\Documents\World Cup\data\3rdplace.txt"
output_path = r"c:\Users\rpbea\Documents\World Cup\data\3rdplace.csv"

rows = []
with open(input_path, 'r', encoding='utf-8') as f:
    for raw in f:
        line = raw.strip()
        if not line:
            continue
        tokens = line.split()
        # skip leading number token(s)
        i = 0
        # find first token that's not a number
        while i < len(tokens) and tokens[i].isdigit():
            i += 1
        # collect single-letter group tokens until a token starting with '3' is found
        advanced = []
        while i < len(tokens) and not tokens[i].startswith('3'):
            t = tokens[i]
            if len(t) == 1 and t.isalpha():
                advanced.append(t)
            i += 1
        # now collect next 8 tokens that start with '3'
        matchups = []
        while i < len(tokens) and len(matchups) < 8:
            t = tokens[i]
            if t.startswith('3'):
                matchups.append(t)
            i += 1
        # if we didn't find 8 matchups, pad with empty strings
        while len(matchups) < 8:
            matchups.append("")

        rows.append([" ".join(advanced)] + matchups)

with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    header = ['advanced', '1A', '1B', '1D', '1E', '1G', '1I', '1K', '1L']
    writer.writerow(header)
    for r in rows:
        writer.writerow(r)

print(f"Wrote {len(rows)} rows to {output_path}")
