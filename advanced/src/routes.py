from flask import Flask, request, jsonify, render_template
import services, cache

app = Flask(__name__)
app.static_folder = 'static'

# JSON API
@app.route('/stats')
def stats_api():
    name = request.args.get('team_name', '')
    return jsonify(services.team_stats(name))

@app.route('/versus')
def versus_api():
    p1 = int(request.args.get('player1_id', 0))
    p2 = int(request.args.get('player2_id', 0))
    return jsonify({'matches': services.versus_ids(p1, p2)})

@app.route('/goals')
def goals_api():
    pid = int(request.args.get('player_id', 0))
    return jsonify(cache.get_goals(pid))

# HTML frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/front/stats')
def stats_html():
    teams = [t['name'] for t in cache.get_teams()]
    selected = request.args.get('team_name', '')
    result = services.team_stats(selected) if selected else None
    return render_template('stats.html', teams=teams, selected=selected, result=result)

@app.route('/front/versus')
def versus_html():
    players = services.list_players()
    p1 = request.args.get('player1', '')
    p2 = request.args.get('player2', '')
    matches = None
    if p1 and p2:
        def find_id(name):
            for t in cache.get_teams():
                for pl in cache.get_players(t['players']):
                    full = f"{pl.get('name','')} {pl.get('surname','')}".strip()
                    if full == name:
                        return pl['id']
        matches = services.versus_ids(find_id(p1), find_id(p2))
    return render_template('versus.html', players=players, p1=p1, p2=p2, matches=matches)
