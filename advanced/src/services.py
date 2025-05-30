from cache import get_teams, get_players, get_matches, get_goals


def list_players():
    names = []
    for team in get_teams():
        for p in get_players(team.get('players', [])):
            full = f"{p.get('name','')} {p.get('surname','')}".strip()
            if full:
                names.append(full)
    return sorted(set(names))


def team_stats(name):
    tm = next((t for t in get_teams() if t.get('name') == name), None)
    if not tm:
        return {'wins': 0, 'losses': 0, 'goal_diff': 0}
    tid = tm['id']
    wins = losses = gd = 0
    for m in get_matches():
        s1 = int(m['team1_score']); s2 = int(m['team2_score'])
        if m['team1'] == tid:
            wins += s1 > s2; losses += s1 < s2; gd += s1 - s2
        elif m['team2'] == tid:
            wins += s2 > s1; losses += s2 < s1; gd += s2 - s1
    return {'wins': wins, 'losses': losses, 'goal_diff': gd}


def versus_ids(p1, p2):
    count = 0
    for m in get_matches():
        roster = []
        for tid in (m['team1'], m['team2']):
            team = next(t for t in get_teams() if t['id'] == tid)
            roster += team.get('players', [])
        if p1 in roster and p2 in roster:
            count += 1
    return count
