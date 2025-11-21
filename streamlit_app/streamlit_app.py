import streamlit as st
import pandas as pd
import random
import time
import os

st.set_page_config(page_title="2026 World Cup Draw Simulator", layout="wide")

st.title("2026 World Cup — Draw Simulator")

st.markdown(
    """
Simple draw simulator. Click **Simulate Draw** to randomly fill groups according to pots.

Notes:
- Pot assignment is by world rankings and qualified teams (no geographic constraints applied yet).
- Flags: place flag images in `data/flags/` named with ISO2 lower-case codes (e.g. `us.png`, `mx.png`) or leave blank to show no flag.
"""
)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
RANKINGS_CSV = os.path.join(DATA_DIR, 'rankings.csv')
QUALIFIED_CSV = os.path.join(DATA_DIR, 'qualified.csv')

def load_qualified():
    if os.path.exists(QUALIFIED_CSV):
        dfq = pd.read_csv(QUALIFIED_CSV)
        return [t for t in dfq['team'].tolist()]
    return []

def load_rankings():
    if os.path.exists(RANKINGS_CSV):
        dfr = pd.read_csv(RANKINGS_CSV)
        return dfr
    return pd.DataFrame(columns=['team','rank'])

qualified = load_qualified()
dfr = load_rankings()

groups = [chr(ord('A') + i) for i in range(12)]  # A..L (12 groups)

st.sidebar.header('Pots info')
st.sidebar.write('Pot formation: Pot1 = Mexico, Canada, United States + top 9 qualified by ranking')

def make_pots(qualified, dfr):
    # produce list of qualified teams ordered by ranking
    rank_order = [r for r in dfr['team'].tolist() if r in qualified]
    # Ensure Mexico/Canada/United States present as A1/B1/D1
    pot1 = []
    for special in ['Mexico', 'Canada', 'United States']:
        if special in qualified:
            pot1.append(special)

    # add top-ranked qualified teams excluding specials until we have 12
    for t in rank_order:
        if t in pot1:
            continue
        if len(pot1) >= 12:
            break
        pot1.append(t)

    # Next pots: sequential in ranking order skipping pot1 teams
    remaining = [t for t in rank_order if t not in pot1]
    pot2 = remaining[:12]
    pot3 = remaining[12:24]
    pot4_real = remaining[24:]
    # Fill pot4 with placeholders to reach 12
    pot4 = pot4_real.copy()
    # placeholders: 4 UEFA PO winners, 2 intercontinental
    placeholders = [f'UEFA PO Winner {i+1}' for i in range(4)] + [f'Intercontinental PO Winner {i+1}' for i in range(2)]
    for ph in placeholders:
        if len(pot4) >= 12:
            break
        pot4.append(ph)
    # if still less than 12, pad with generic placeholders
    while len(pot4) < 12:
        pot4.append(f'Pot4 Placeholder {len(pot4)+1}')

    return pot1, pot2, pot3, pot4

pot1, pot2, pot3, pot4 = make_pots(qualified, dfr)

st.sidebar.subheader('Pots (preview)')
st.sidebar.write('Pot 1 (first 12):')
st.sidebar.write(pot1)
st.sidebar.write('Pot 2:')
st.sidebar.write(pot2)
st.sidebar.write('Pot 3:')
st.sidebar.write(pot3)
st.sidebar.write('Pot 4:')
st.sidebar.write(pot4)

if 'draw_result' not in st.session_state:
    # dict group -> list of 4 slots
    st.session_state.draw_result = {g: [None, None, None, None] for g in groups}
    st.session_state.draw_done = False

flags_dir = os.path.join(DATA_DIR, 'flags')

def flag_for(team):
    # look for simple flag image by lowercased team name or ISO code if available
    if not os.path.isdir(flags_dir):
        return None
    # try normalized name
    name = team.lower().replace(' ', '_').replace("'", '').replace('.', '')
    for ext in ('.png', '.jpg', '.svg'):
        p = os.path.join(flags_dir, name + ext)
        if os.path.exists(p):
            return p
    return None

def render_groups(placeholders=None):
    # render groups in 4 rows x 3 columns
    cols_per_row = 3
    idx = 0
    placeholders = placeholders or {}
    for row in range(4):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            if idx >= len(groups):
                break
            grp = groups[idx]
            with cols[c]:
                st.markdown(f"**Group {grp}**")
                box = st.container()
                # show 4 slots
                for slot_i in range(4):
                    key = f"{grp}_{slot_i}"
                    if placeholders and key in placeholders:
                        placeholders[key].text('')
                    val = st.session_state.draw_result[grp][slot_i]
                    if val:
                        # show flag if available
                        fpath = flag_for(val)
                        if fpath:
                            st.image(fpath, width=24)
                            st.write(val)
                        else:
                            st.write(val)
                    else:
                        st.write('—')
            idx += 1

st.write('## Groups')
render_groups()

col1, col2 = st.columns([1,1])

with col1:
    if st.button('Simulate Draw') and not st.session_state.draw_done:
        # perform draws and animate fill
        # reset
        st.session_state.draw_result = {g: [None, None, None, None] for g in groups}
        st.session_state.draw_done = False
        # prepare pots to shuffle
        p1 = pot1.copy()
        random.shuffle(p1)
        # ensure Mexico=A1, Canada=B1, USA=D1 positions fixed if present
        # we'll place the remaining pot1 teams into the other group first slots
        first_slots = [f for f in groups]
        # place fixed ones
        fixed_map = {'Mexico': 'A', 'Canada': 'B', 'United States': 'D'}
        for team, grp in fixed_map.items():
            if team in p1 and grp in first_slots:
                st.session_state.draw_result[grp][0] = team
                p1.remove(team)

        # assign remaining pot1 teams to remaining groups' first slot
        remaining_groups = [g for g in groups if st.session_state.draw_result[g][0] is None]
        for team in p1:
            tgt = remaining_groups.pop(0)
            st.session_state.draw_result[tgt][0] = team
            # animate by re-rendering partial state
            render_groups()
            time.sleep(0.25)

        # Now pots 2,3,4 fill slots 1,2,3 index positions 1..3
        for pot, slot_index in ((pot2,1), (pot3,2), (pot4,3)):
            pool = pot.copy()
            random.shuffle(pool)
            for team in pool:
                # find next group with empty slot at slot_index
                for g in groups:
                    if st.session_state.draw_result[g][slot_index] is None:
                        st.session_state.draw_result[g][slot_index] = team
                        break
                render_groups()
                time.sleep(0.25)

        st.session_state.draw_done = True

with col2:
    if st.session_state.draw_done:
        if st.button('Continue to tournament'):
            st.info('Continue pressed — placeholder')
    else:
        st.write('Run the draw to enable the continue button')

st.write('---')
st.write('Flag options:')
st.write('- Easiest: create a `data/flags/` directory and save PNGs named by normalized country (e.g. `united_states.png` or `us.png`). The app will try to find images by normalized team name.')
st.write('- Alternative: use an external flag CDN and map country names to ISO codes using `pycountry`, then fetch `https://flagcdn.com/w80/{cc}.png` dynamically.')
