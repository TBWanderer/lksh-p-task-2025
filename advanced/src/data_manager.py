import json
import requests
import logging
from collections import defaultdict
from datetime import datetime

class DataCache:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_cache()

    def load_cache(self):
        logging.debug("Loading cache")
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error while loading cache: {e}")
            return None

    def save_cache(self, data):
        logging.debug("Saving cache")
        with open(self.filename, 'w') as f:
            json.dump(data, f)
        self.data = data
        logging.debug("Cache saved")

class SportsData:
    def __init__(self, token: str, base_url: str, cache_file: str):
        
        if not token:
            import sys
            logging.error(f"LKSH_P_AUTH_TOKEN not set!")
            sys.exit(1)

        self.token = token
        self.base_url = base_url
        self.headers = {"Authorization": token}
        self.cache = DataCache(cache_file)
        self.matches = []
        self.teams = []
        self.players = {}
        self.goals = []
        self.team_stats = {}
        self.player_matches = defaultdict(set)
        self.player_team_in_match = {}  

        print("Loading data (1-2m)")
        self.load_data()
        print("Loaded data")

    def fetch_data(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        logging.debug(f"Fetching data from '{url}'")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return None

    def load_data(self):
        if self.cache.data:
            self.load_from_cache()
            return

        logging.debug("Fetching matches")
        self.matches = self.fetch_data("/matches") or []
        logging.debug("Fetching teams")
        self.teams = self.fetch_data("/teams") or []
        self.goals = []

        player_ids = set()
        for team in self.teams:
            player_ids.update(team.get("players", []))
        
        self.players = {}
        logging.debug("Fetching players")
        for player_id in player_ids:
            player_data = self.fetch_data(f"/players/{player_id}")
            if player_data:
                self.players[player_id] = player_data

        logging.debug("Fetching goals by match")
        for match in self.matches:
            goals_data = self.fetch_data(f"/goals?match_id={match['id']}")
            if goals_data:
                self.goals.extend(goals_data)

        self.process_data()
        self.cache.save_cache(self.get_cache_data())

    def load_from_cache(self):
        cache_data = self.cache.data
        self.matches = cache_data.get("matches", [])
        self.teams = cache_data.get("teams", [])
        self.players = cache_data.get("players", {})
        self.goals = cache_data.get("goals", [])
        self.process_data()

    def get_cache_data(self):
        return {
            "matches": self.matches,
            "teams": self.teams,
            "players": self.players,
            "goals": self.goals,
            "timestamp": datetime.now().isoformat()
        }

    def process_data(self):
        self.team_stats = {}
        self.player_matches = defaultdict(set)
        self.player_team_in_match = {}  
        
        
        team_players = {}
        for team in self.teams:
            team_players[team['id']] = set(team.get('players', []))
        
        
        logging.debug("Processing matches")
        for match in self.matches:
            match_id = match["id"]
            team1 = match["team1"]
            team2 = match["team2"]
            score1 = int(match["team1_score"])
            score2 = int(match["team2_score"])
            
            
            if team1 not in self.team_stats:
                self.team_stats[team1] = {"wins": 0, "losses": 0, "goals_for": 0, "goals_against": 0}
            self.team_stats[team1]["goals_for"] += score1
            self.team_stats[team1]["goals_against"] += score2
            
            if score1 > score2:
                self.team_stats[team1]["wins"] += 1
            elif score1 < score2:
                self.team_stats[team1]["losses"] += 1
            
            if team2 not in self.team_stats:
                self.team_stats[team2] = {"wins": 0, "losses": 0, "goals_for": 0, "goals_against": 0}
            self.team_stats[team2]["goals_for"] += score2
            self.team_stats[team2]["goals_against"] += score1
            
            if score2 > score1:
                self.team_stats[team2]["wins"] += 1
            elif score2 < score1:
                self.team_stats[team2]["losses"] += 1
            
            
            self.player_team_in_match[match_id] = {}
            
            for player_id in team_players.get(team1, set()):
                self.player_team_in_match[match_id][player_id] = team1
            
            for player_id in team_players.get(team2, set()):
                self.player_team_in_match[match_id][player_id] = team2
        
        logging.debug("Processing teams for player matches")
        for team in self.teams:
            team_id = team["id"]
            players = team.get("players", [])
            for player_id in players:
                for match in self.matches:
                    if match["team1"] == team_id or match["team2"] == team_id:
                        self.player_matches[player_id].add(match["id"])
        
        logging.debug("Processing goals for player matches")
        for goal in self.goals:
            player_id = goal["player"]
            match_id = goal["match"]
            self.player_matches[player_id].add(match_id)

    def get_team_stats(self, team_name):
        logging.info(f"Getting '{team_name}' team's stats")
        for team in self.teams:
            if team["name"] == team_name:
                stats = self.team_stats.get(team["id"], {"wins": 0, "losses": 0, "goals_for": 0, "goals_against": 0})
                goal_diff = stats["goals_for"] - stats["goals_against"]
                return (stats["wins"], stats["losses"], goal_diff)
        return (0, 0, 0)

    def get_versus_count(self, player1_id, player2_id):
        logging.info(f"Getting versus count of players (ID1: {player1_id}, ID2: {player2_id})")
        try:
            pid1 = int(player1_id)
            pid2 = int(player2_id)
        except ValueError:
            return 0  
        
        
        matches1 = self.player_matches.get(pid1, set())
        matches2 = self.player_matches.get(pid2, set())
        common_matches = matches1 & matches2
        
        count = 0
        for match_id in common_matches:
            
            match_teams = self.player_team_in_match.get(match_id, {})
            team1 = match_teams.get(pid1)
            team2 = match_teams.get(pid2)
            
            
            if team1 is not None and team2 is not None and team1 != team2:
                count += 1
                
        return count

    def get_player_goals(self, player_id):
        logging.info(f"Getting player's (ID:{player_id}) goals")
        player_goals = []
        for goal in self.goals:
            if goal["player"] == int(player_id):
                player_goals.append({
                    "match": goal["match"],
                    "time": goal["minute"]
                })
        return player_goals
