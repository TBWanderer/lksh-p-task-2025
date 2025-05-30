from flask import request, jsonify, send_from_directory

def register_routes(app, data_manager):
    @app.route('/stats', methods=['GET'])
    def stats_endpoint():
        team_name = request.args.get('team_name')
        if not team_name:
            return jsonify({"error": "Missing team_name parameter"}), 400
        
        wins, losses, goal_diff = data_manager.get_team_stats(team_name)
        return jsonify({
            "wins": wins,
            "losses": losses,
            "goal_difference": goal_diff
        })

    @app.route('/versus', methods=['GET'])
    def versus_endpoint():
        player1_id = request.args.get('player1_id')
        player2_id = request.args.get('player2_id')
        
        if not player1_id or not player2_id:
            return jsonify({"error": "Missing player IDs"}), 400
        
        try:
            count = data_manager.get_versus_count(player1_id, player2_id)
            return jsonify({"match_count": count})
        except ValueError:
            return jsonify({"error": "Invalid player ID format"}), 400

    @app.route('/goals', methods=['GET'])
    def goals_endpoint():
        player_id = request.args.get('player_id')
        if not player_id:
            return jsonify({"error": "Missing player_id parameter"}), 400
        
        try:
            goals = data_manager.get_player_goals(player_id)
            return jsonify(goals)
        except ValueError:
            return jsonify({"error": "Invalid player ID format"}), 400

    @app.route('/openapi.yaml')
    def serve_openapi():
        return send_from_directory('.', 'openapi.yaml')
