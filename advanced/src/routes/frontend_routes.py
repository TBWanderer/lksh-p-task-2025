from flask import render_template

def register_routes(app, data_manager):
    @app.route('/front/stats')
    def front_stats():
        teams = sorted([team['name'] for team in data_manager.teams])
        return render_template('stats.html', teams=teams)

    @app.route('/front/versus')
    def front_versus():
        players = sorted(
            [f"{p['name']} {p['surname']} (ID: {pid})" 
             for pid, p in data_manager.players.items()],
            key=lambda x: x.lower()
        )
        return render_template('versus.html', players=players)
