import requests
import sys
from os import getenv
from dotenv import load_dotenv
from tqdm import tqdm


def get_teams(headers):
    response = requests.get('https://lksh-enter.ru/teams', headers=headers)
    if response.status_code != 200:
        return {}, {}
    
    teams_data = response.json()
    team_by_name = {}
    team_players = {}
    
    for team in teams_data:
        team_id = team['id']
        team_by_name[team['name']] = team_id
        team_players[team_id] = team['players']
    return team_by_name, team_players


def get_players(headers, player_ids):
    players_info = {}
    print(" Fetching data about players...")
    for pid in tqdm(player_ids):
        response = requests.get(f'https://lksh-enter.ru/players/{pid}', headers=headers)
        if response.status_code == 200:
            data = response.json()
            players_info[pid] = {
                'name': data.get('name', ''),
                'surname': data.get('surname', '')
            }
    print(" Successfully fetched! ")
    return players_info


def generate_player_list(players_info):
    return sorted(
        [f"{p['name']} {p['surname']}".strip() for p in players_info.values()],
        key=lambda x: x.lower()
    )


def get_matches(headers):
    response = requests.get('https://lksh-enter.ru/matches', headers=headers)
    return response.json() if response.status_code == 200 else []


def calculate_team_stats(team_id, matches):
    wins = losses = goals_scored = goals_conceded = 0
    
    for match in matches:
        t1, t2 = match['team1'], match['team2']
        s1, s2 = match['team1_score'], match['team2_score']
        
        if team_id in (t1, t2):
            is_home = team_id == t1
            team_score = s1 if is_home else s2
            opponent_score = s2 if is_home else s1
            
            goals_scored += team_score
            goals_conceded += opponent_score
            
            if team_score > opponent_score:
                wins += 1
            elif team_score < opponent_score:
                losses += 1
                
    return wins, losses, goals_scored - goals_conceded


def count_common_matches(p1, p2, matches, team_players):
    count = 0
    for match in matches:
        t1_players = team_players.get(match['team1'], [])
        t2_players = team_players.get(match['team2'], [])
        
        p1_in_t1 = p1 in t1_players
        p2_in_t2 = p2 in t2_players
        p1_in_t2 = p1 in t2_players
        p2_in_t1 = p2 in t1_players
        
        if (p1_in_t1 and p2_in_t2) or (p1_in_t2 and p2_in_t1):
            count += 1
    return count


def process_queries(matches, team_by_name, team_players, players_info):
    while True:
        line = input()
        if not line:
            continue
        
        if line.startswith('stats? "'):
            _, _, team_name = line.partition('"')
            team_name = team_name.rstrip('"')
            team_id = team_by_name.get(team_name, 0)
            
            if team_id:
                stats = calculate_team_stats(team_id, matches)
                print(f"{stats[0]} {stats[1]} {stats[2]:+}")
            else:
                print("0 0 0")
        
        elif line.startswith('versus? '):
            try:
                _, p1, p2 = line.split()
                p1 = int(p1)
                p2 = int(p2)
                valid = p1 in players_info and p2 in players_info
                print(count_common_matches(p1, p2, matches, team_players) if valid else 0)
            except (ValueError, KeyError):
                print(0)


def main():
    load_dotenv()
    token = getenv("LKSH_P_AUTH_TOKEN")
    
    if not token:
        print("Missing LKSH_P_AUTH_TOKEN", file=sys.stderr)
        sys.exit(1)
    
    headers = {'Authorization': token}
    
    team_by_name, team_players = get_teams(headers)
    all_players = {pid for players in team_players.values() for pid in players}
    players_info = get_players(headers, all_players)
    
    for name in generate_player_list(players_info):
        print(name)
    
    matches = get_matches(headers)
    process_queries(matches, team_by_name, team_players, players_info)


if __name__ == '__main__':
    main()
