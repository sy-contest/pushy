let gameId;
let player;
const pusher = new Pusher(PUSHER_KEY, {
    cluster: PUSHER_CLUSTER
});

function joinGame() {
    gameId = document.getElementById('game-id').value;
    if (!gameId) {
        alert('Please enter a game ID');
        return;
    }

    player = Math.random() < 0.5 ? 'player1' : 'player2';
    document.getElementById('current-game-id').textContent = gameId;
    document.getElementById('game-setup').style.display = 'none';
    document.getElementById('game-area').style.display = 'block';

    const channel = pusher.subscribe(`game-${gameId}`);
    channel.bind('result', handleResult);
    channel.bind('waiting', handleWaiting);
}

function makeChoice(choice) {
    fetch('/game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            game_id: gameId,
            player: player,
            choice: choice
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('result').textContent = 'Waiting for opponent...';
        }
    });
}

function handleResult(data) {
    let resultText;
    if (data.result === 'tie') {
        resultText = "It's a tie!";
    } else if (data.result === `${player}_wins`) {
        resultText = "You win!";
    } else {
        resultText = "You lose!";
    }
    document.getElementById('result').textContent = `${resultText} (You: ${data.choices[player]}, Opponent: ${data.choices[player === 'player1' ? 'player2' : 'player1']})`;
}

function handleWaiting(data) {
    document.getElementById('result').textContent = data.message;
}
