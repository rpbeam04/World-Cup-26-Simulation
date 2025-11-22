#!/usr/bin/env python3
"""Download country flags for teams listed in data/qualified.csv

Saves PNGs to `data/flags/` named by ISO2 code (lowercase), e.g. `us.png`.

Usage:
    python scripts/download_flags.py --source data/qualified.csv --out data/flags --size 80
"""
import os
import csv
import argparse
import requests
import pycountry
import time


OVERRIDES = {
    'United States': 'US',
    'South Korea': 'KR',
    'North Korea': 'KP',
    'Côte d\'Ivoire': 'CI',
    'Ivory Coast': 'CI',
    'DR Congo': 'CD',
    'Republic of Ireland': 'IE',
    'USA': 'US',
}


def normalize_name(name: str) -> str:
    n = name.strip()
    # remove parentheses content
    if '(' in n:
        n = n.split('(')[0].strip()
    return n


def name_to_alpha2(name: str):
    # check overrides first
    if name in OVERRIDES:
        return OVERRIDES[name].lower()
    try:
        c = pycountry.countries.lookup(name)
        return c.alpha_2.lower()
    except Exception:
        # try fuzzy search
        try:
            res = pycountry.countries.search_fuzzy(name)
            if res:
                return res[0].alpha_2.lower()
        except Exception:
            return None


def download_flag(alpha2: str, out_dir: str, size: int = 80) -> bool:
    url = f'https://flagcdn.com/w{size}/{alpha2}.png'
    out_path = os.path.join(out_dir, f'{alpha2}.png')
    if os.path.exists(out_path):
        print(f'Skipping existing {out_path}')
        return True
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            with open(out_path, 'wb') as f:
                f.write(resp.content)
            print(f'Downloaded {out_path}')
            return True
        else:
            print(f'Failed to download {alpha2}: HTTP {resp.status_code}')
            return False
    except Exception as e:
        print(f'Error downloading {alpha2}: {e}')
        return False


def read_qualified(source_path: str):
    teams = []
    if not os.path.exists(source_path):
        raise FileNotFoundError(source_path)
    with open(source_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if 'team' in reader.fieldnames:
            for r in reader:
                teams.append(r['team'].strip())
        else:
            # fallback: read first column
            f.seek(0)
            for row in reader:
                first = list(row.values())[0]
                teams.append(first.strip())
    return teams


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', default='data/qualified.csv')
    p.add_argument('--out', default='data/flags')
    p.add_argument('--size', type=int, default=80)
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    teams = read_qualified(args.source)

    for t in teams:
        name = normalize_name(t)
        # skip placeholders
        if name.startswith('UEFA PO') or name.startswith('Intercontinental') or 'Placeholder' in name:
            print(f'Skipping placeholder/team {name}')
            continue
        alpha2 = name_to_alpha2(name)
        if not alpha2:
            print(f'No ISO mapping for "{name}" — skipped')
            continue
        ok = download_flag(alpha2, args.out, size=args.size)
        # be polite
        time.sleep(0.15)


if __name__ == '__main__':
    main()
