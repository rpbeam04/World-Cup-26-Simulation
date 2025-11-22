import streamlit as st
import pandas as pd
import random
import time
try:
    import pycountry
except Exception:
    pycountry = None
import os

st.set_page_config(page_title="2026 World Cup Draw Simulator", layout="wide")

st.title("2026 World Cup — Draw Simulator")

st.markdown(
    """
Simple draw simulator. Click **Simulate Draw** to randomly fill groups according to pots.
"""
)

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data'))
RANKINGS_CSV = os.path.join(DATA_DIR, 'rankings.csv')
QUALIFIED_CSV = os.path.join(DATA_DIR, 'qualified.csv')

def load_qualified():
    if os.path.exists(QUALIFIED_CSV):
        dfq = pd.read_csv(QUALIFIED_CSV)
        teams = [t for t in dfq['team'].tolist()]
        conf_map = {}
        if 'confederation' in dfq.columns:
            for t, c in zip(dfq['team'].tolist(), dfq['confederation'].tolist()):
                conf_map[t] = c
        return teams, conf_map
    return [], {}

def load_rankings():
    if os.path.exists(RANKINGS_CSV):
        dfr = pd.read_csv(RANKINGS_CSV)
        return dfr
    return pd.DataFrame(columns=['team','rank'])

qualified, qualified_conf = load_qualified()
dfr = load_rankings()

groups = [chr(ord('A') + i) for i in range(12)]  # A..L (12 groups)

def make_pots(qualified, dfr):
    # produce list of qualified teams ordered by ranking
    ranked = [r for r in dfr['team'].tolist()]
    # teams present in both rankings and qualified, preserving ranking order
    rank_order = [r for r in ranked if r in qualified]
    # append any qualified teams missing from rankings at the end (to avoid losing them)
    missing_from_rankings = [q for q in qualified if q not in rank_order]
    if missing_from_rankings:
        rank_order.extend(missing_from_rankings)
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
    placeholders = [f'UEFA Path {i+1}' for i in range(4)] + [f'IC Winner {i+1}' for i in range(2)]
    for ph in placeholders:
        if len(pot4) >= 12:
            break
        pot4.append(ph)
    # if still less than 12, pad with generic placeholders
    while len(pot4) < 12:
        pot4.append(f'Pot4 Placeholder {len(pot4)+1}')

    return pot1, pot2, pot3, pot4

pot1, pot2, pot3, pot4 = make_pots(qualified, dfr)

def team_confederation(team):
    # return confederation code or None; mark intercontinental as special 'INTER'
    if team in qualified_conf:
        return qualified_conf[team]
    if isinstance(team, str):
        if team.startswith('UEFA') or 'UEFA' in team:
            return 'UEFA'
        if team.startswith('IC') or 'Intercontinental' in team:
            return 'INTER'
    return None

def conf_limit(conf):
    if conf == 'UEFA':
        return 2
    # default: one per confederation
    return 1

def can_place_team_in_group(team, grp, result):
    """Return True if `team` may be placed into group `grp` considering current `result`."""
    conf = team_confederation(team)
    if conf == 'INTER':
        return True
    # count existing teams of same conf in group
    count = 0
    for t in result.get(grp, []):
        if not t:
            continue
        tc = team_confederation(t)
        if tc == conf:
            count += 1
    limit = conf_limit(conf)
    return count < limit

def assign_pot_with_rules(result, pot, slot_index, max_attempts=500):
    """Attempt to place all teams from `pot` into `result` at `slot_index` respecting confed rules.
    Uses greedy singleton propagation and random choices; retries if conflict arises.
    Returns True on success (mutates result), False otherwise.
    """
    groups_list = list(groups)

    for attempt in range(max_attempts):
        # working copy of result for this attempt
        working = {g: list(result[g]) for g in groups_list}
        pool = pot.copy()
        random.shuffle(pool)
        success = True

        # iterative placement loop with singleton propagation
        while pool:
            progressed = False
            # compute possible groups for each team
            poss = {}
            for team in pool:
                allowed = []
                for g in groups_list:
                    # must have empty slot at slot_index
                    if working[g][slot_index] is not None:
                        continue
                    if can_place_team_in_group(team, g, working):
                        allowed.append(g)
                poss[team] = allowed

            # if any team has zero possibilities, fail this attempt
            dead = [t for t, opts in poss.items() if len(opts) == 0]
            if dead:
                success = False
                break

            # forced placements (singleton)
            forced = [t for t, opts in poss.items() if len(opts) == 1]
            if forced:
                for t in forced:
                    g = poss[t][0]
                    working[g][slot_index] = t
                    pool.remove(t)
                    progressed = True
                continue

            # otherwise pick a random team and random allowed group
            t = random.choice(pool)
            opts = poss[t]
            g = random.choice(opts)
            working[g][slot_index] = t
            pool.remove(t)
            progressed = True

            if not progressed:
                success = False
                break

        if success:
            # commit working into result
            for g in groups_list:
                result[g] = working[g]
            return True
    return False

# Show pots in an expander (dropdown) instead of sidebar
with st.expander('Show Pots'):
    st.subheader('Pots (preview)')
    # show pots as 4 columns side-by-side, teams as text lines
    cols = st.columns(4)
    pot_columns = [pot1, pot2, pot3, pot4]
    for i, pot in enumerate(pot_columns):
        with cols[i]:
            st.markdown(f"**Pot {i+1}**")
            for t in pot:
                try:
                    st.write(t)
                except Exception:
                    # protect against UI rendering issues for unexpected values
                    st.write(str(t))
    # surface any qualified teams missing from the rankings
    ranked_names = set(dfr['team'].tolist())
    missing = [q for q in qualified if q not in ranked_names]
    if missing:
        st.warning('The following qualified teams were not found in the rankings file and were appended to the pots:')
        for m in missing:
            st.write('-', m)

if 'draw_result' not in st.session_state:
    # dict group -> list of 4 slots
    st.session_state.draw_result = {g: [None, None, None, None] for g in groups}
    st.session_state.draw_done = False

def render_group_grid(result):
    """Render the groups as a 4x3 grid showing the 4 teams per group.
    This avoids storing Streamlit DeltaGenerator objects in session state.
    """
    idx = 0
    for row in range(4):
        cols = st.columns(3)
        for c in range(3):
            if idx >= len(groups):
                break
            grp = groups[idx]
            with cols[c]:
                st.markdown(f"**Group {grp}**")
                teams = result.get(grp, [None, None, None, None])
                for i, t in enumerate(teams, start=1):
                    # show flag (if available) then team name
                    row_cols = st.columns([1, 8])
                    fpath = flag_for(t) if t else None
                    if fpath:
                        try:
                            row_cols[0].image(fpath, width=24)
                        except Exception:
                            row_cols[0].write('')
                    else:
                        row_cols[0].write('')
                    row_cols[1].write(t if t else '—')
            idx += 1

flags_dir = os.path.join(DATA_DIR, 'flags')

def flag_for(team):
    # look for flag image by several strategies:
    # 1) normalized team name file (e.g. united_states.png)
    # 2) ISO2 code file using pycountry lookup (e.g. us.png)
    if not os.path.isdir(flags_dir) or not isinstance(team, str):
        return None
    name = team.lower().replace(' ', '_').replace("'", '').replace('.', '')
    for ext in ('.png', '.jpg', '.svg'):
        p = os.path.join(flags_dir, name + ext)
        if os.path.exists(p):
            return p

    # try pycountry to map to alpha2
    if pycountry:
        try:
            c = pycountry.countries.lookup(team)
            alpha2 = c.alpha_2.lower()
            for ext in ('.png', '.jpg', '.svg'):
                p = os.path.join(flags_dir, alpha2 + ext)
                if os.path.exists(p):
                    return p
        except Exception:
            try:
                res = pycountry.countries.search_fuzzy(team)
                if res:
                    alpha2 = res[0].alpha_2.lower()
                    for ext in ('.png', '.jpg', '.svg'):
                        p = os.path.join(flags_dir, alpha2 + ext)
                        if os.path.exists(p):
                            return p
            except Exception:
                pass

    # fallback: no flag found
    return None

st.write('## Groups')

col1, col2 = st.columns([1,1])

with col1:
    if st.button('Simulate Draw'):
        try:
            attempts = 300
            final_result = None
            for attempt in range(attempts):
                # start fresh
                result = {g: [None, None, None, None] for g in groups}

                # pot1: place fixed teams then place remaining with rules
                p1 = pot1.copy()
                random.shuffle(p1)
                fixed_map = {'Mexico': 'A', 'Canada': 'B', 'United States': 'D'}
                for team, grp in fixed_map.items():
                    if team in p1 and grp in groups:
                        result[grp][0] = team
                        p1.remove(team)

                ok = assign_pot_with_rules(result, p1, 0)
                if not ok:
                    continue

                # pots 2..4 with confed rules (intercontinental placeholders are exempt)
                if not assign_pot_with_rules(result, pot2, 1):
                    continue
                if not assign_pot_with_rules(result, pot3, 2):
                    continue
                if not assign_pot_with_rules(result, pot4, 3):
                    continue

                final_result = result
                break

            if final_result is None:
                st.error('Unable to produce a valid draw respecting confederation rules after several attempts.')
            else:
                st.session_state.draw_result = final_result
                st.session_state.draw_done = True
        except Exception:
            import traceback
            tb = traceback.format_exc()
            st.error('An error occurred during the draw:')
            st.text(tb)

with col2:
    if st.session_state.draw_done:
        if st.button('Continue to tournament'):
            st.info('Continue pressed — placeholder')
    else:
        st.write('Run the draw to enable the continue button')

# When draw is complete, display plain text results (simple, non-animated)
    # Allow re-running the draw every time the button is pressed
    if st.session_state.draw_done:
        pass

# render group grid after any draw action so it reflects the latest `st.session_state.draw_result`
render_group_grid(st.session_state.draw_result)
