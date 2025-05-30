import requests
import sys
from collections import defaultdict
import os
from tqdm import tqdm
import dotenv

class SportsData:
    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": token}
        self.base_url = "https://lksh-enter.ru"
        self.matches = []
        self.teams = []
        self.players = {}
        self.team_stats = {}
        self.player_teams = defaultdict(set)
        self.player_matches = defaultdict(set)
        self.match_teams = {}

    def fetch_data(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def load_all_data(self):
        self.matches = self.fetch_data("/matches") or []
        self.teams = self.fetch_data("/teams") or []
        
        player_ids = set()

        print("Fetching data...")

        for team in tqdm(self.teams):
            for player_id in team.get("players", []):
                player_ids.add(player_id)
        
        for player_id in tqdm(player_ids):
            player_data = self.fetch_data(f"/players/{player_id}")
            if player_data:
                self.players[player_id] = player_data
        
        for team in tqdm(self.teams):
            team_id = team["id"]
            for player_id in team.get("players", []):
                self.player_teams[player_id].add(team_id)
        
        print("Data fetched!")

        self.calculate_team_stats()
        
        for match in self.matches:
            match_id = match["id"]
            t1 = match["team1"]
            t2 = match["team2"]
            self.match_teams[match_id] = (t1, t2)
            
            
            for player_id in self.get_team_players(t1):
                self.player_matches[player_id].add(match_id)
            
            
            for player_id in self.get_team_players(t2):
                self.player_matches[player_id].add(match_id)

    def get_team_players(self, team_id):
        for team in self.teams:
            if team["id"] == team_id:
                return team.get("players", [])
        return []

    def calculate_team_stats(self):
        for team in self.teams:
            team_id = team["id"]
            self.team_stats[team_id] = {
                "wins": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0
            }
        
        for match in self.matches:
            t1 = match["team1"]
            t2 = match["team2"]
            score1 = int(match["team1_score"])
            score2 = int(match["team2_score"])
            
            
            if t1 in self.team_stats:
                self.team_stats[t1]["goals_for"] += score1
                self.team_stats[t1]["goals_against"] += score2
                if score1 > score2:
                    self.team_stats[t1]["wins"] += 1
                elif score1 < score2:
                    self.team_stats[t1]["losses"] += 1
            
            
            if t2 in self.team_stats:
                self.team_stats[t2]["goals_for"] += score2
                self.team_stats[t2]["goals_against"] += score1
                if score2 > score1:
                    self.team_stats[t2]["wins"] += 1
                elif score2 < score1:
                    self.team_stats[t2]["losses"] += 1

    def get_sorted_players(self):
        player_names = []
        for player_id, player_data in self.players.items():
            name = player_data.get("name", "")
            surname = player_data.get("surname", "")
            full_name = f"{name} {surname}".strip()
            if full_name:
                player_names.append(full_name)
        return sorted(player_names)

    def get_team_stats(self, team_name):
        for team in self.teams:
            if team["name"] == team_name:
                stats = self.team_stats.get(team["id"], {"wins": 0, "losses": 0, "goals_for": 0, "goals_against": 0})
                goal_diff = stats["goals_for"] - stats["goals_against"]
                return (stats["wins"], stats["losses"], goal_diff)
        return (0, 0, 0)

    def get_versus_count(self, player1_id, player2_id):
        
        try:
            p1 = int(player1_id)
            p2 = int(player2_id)
        except ValueError:
            return 0
        
        
        if p1 not in self.player_matches or p2 not in self.player_matches:
            return 0
        
        common_matches = self.player_matches[p1] & self.player_matches[p2]
        count = 0
        
        for match_id in common_matches:
            t1, t2 = self.match_teams[match_id]
            team1 = self.player_teams[p1] & {t1, t2}
            team2 = self.player_teams[p2] & {t1, t2}
            
            if team1 and team2 and team1 != team2:
                count += 1
        
        return count

def main():
    dotenv.load_dotenv()
    token = os.getenv("LKSH_P_AUTH_TOKEN", "TOKEN")
    if token == "TOKEN":
        print("LKSH_P_AUTH_TOKEN not set!")
        sys.exit(0)
    data = SportsData(token)
    data.load_all_data()
    
    
    for player in data.get_sorted_players():
        print(player)
    
    
    while True:
        line = input()
        if not line:
            continue
        
        if line.startswith("stats? "):
            
            parts = line[7:].split('"')
            if len(parts) >= 2:
                team_name = parts[1]
                wins, losses, diff = data.get_team_stats(team_name)
                print(f"{wins} {losses} {diff:+d}")
            else:
                print("0 0 0")
        
        elif line.startswith("versus? "):
            parts = line[8:].split()
            if len(parts) >= 2:
                count = data.get_versus_count(parts[0], parts[1])
                print(count)
            else:
                print(0)

if __name__ == "__main__":
    main()
