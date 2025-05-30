import os
import json
import requests

API_BASE = "https://lksh-enter.ru"
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'TOKEN')
HEADERS = {'Authorization': AUTH_TOKEN}
CACHE_FILE = 'cache.json'

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
else:
    cache = {'teams': None, 'players': {}, 'matches': None, 'goals': {}}


def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)


def get_teams():
    if cache['teams'] is None:
        r = requests.get(f"{API_BASE}/teams", headers=HEADERS)
        cache['teams'] = r.json(); save_cache()
    return cache['teams']


def get_players(ids):
    result = []
    for pid in ids:
        key = str(pid)
        if key not in cache['players']:
            r = requests.get(f"{API_BASE}/players/{pid}", headers=HEADERS)
            cache['players'][key] = r.json(); save_cache()
        result.append(cache['players'][key])
    return result


def get_matches():
    if cache['matches'] is None:
        r = requests.get(f"{API_BASE}/matches", headers=HEADERS)
        cache['matches'] = r.json(); save_cache()
    return cache['matches']


def get_goals(player_id):
    key = str(player_id)
    if key not in cache['goals']:
        r = requests.get(f"{API_BASE}/goals?player_id={player_id}", headers=HEADERS)
        cache['goals'][key] = r.json(); save_cache()
    return cache['goals'][key]
