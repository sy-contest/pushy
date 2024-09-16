import os
from flask import Flask, render_template, request, jsonify
import pusher
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

pusher_client = pusher.Pusher(
    app_id=os.getenv('PUSHER_APP_ID'),
    key=os.getenv('PUSHER_APP_KEY'),
    secret=os.getenv('PUSHER_APP_SECRET'),
    cluster=os.getenv('PUSHER_APP_CLUSTER'),
    ssl=True
)

games = {}

@app.route('/')
def index():
    return render_template('index.html', pusher_key=os.getenv('PUSHER_APP_KEY'), pusher_cluster=os.getenv('PUSHER_APP_CLUSTER'))

@app.route('/game', methods=['POST'])
def game():
    data = request.json
    game_id = data['game_id']
    player = data['player']
    choice = data['choice']

    if game_id not in games:
        games[game_id] = {'players': {}}

    games[game_id]['players'][player] = choice

    if len(games[game_id]['players']) == 2:
        result = determine_winner(games[game_id]['players'])
        pusher_client.trigger(f'game-{game_id}', 'result', result)
        del games[game_id]
    else:
        pusher_client.trigger(f'game-{game_id}', 'waiting', {'message': 'Waiting for opponent'})

    return jsonify({'status': 'success'})

def determine_winner(players):
    choices = list(players.values())
    if choices[0] == choices[1]:
        return {'result': 'tie', 'choices': players}
    elif (choices[0] == 'rock' and choices[1] == 'scissors') or \
         (choices[0] == 'paper' and choices[1] == 'rock') or \
         (choices[0] == 'scissors' and choices[1] == 'paper'):
        return {'result': 'player1_wins', 'choices': players}
    else:
        return {'result': 'player2_wins', 'choices': players}

if __name__ == '__main__':
    app.run(debug=True)
