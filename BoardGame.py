import random
from flask import Flask, render_template, redirect, request

app = Flask(__name__)

# Load game state from the file
def load_game():
    try:
        with open('game_state.txt', 'r') as file:
            game_data = file.read().splitlines()
        turn = game_data[0].split(":")[1].strip()
        board = {}
        for line in game_data[1:]:
            space, player = line.split(":")
            board[int(space)] = [player.strip()]
        return {'Turn': turn, 'Board': board, 'Skip': []}
    except FileNotFoundError:
        return {'Turn': 'Player 1', 'Board': {1: ['Player 1'], 2: ['Player 2']}, 'Skip': []}

# Save game state to the file
def save_game(game):
    with open('game_state.txt', 'w') as file:
        file.write(f"Turn: {game['Turn']}\n")
        for space, players in game['Board'].items():
            file.write(f"{space}: {', '.join(players)}\n")

# Load event data from the file
def load_events():
    events = {}
    try:
        with open('events.txt', 'r') as file:
            for line in file:
                space, event = line.split(":")
                events[int(space)] = event.strip()
    except FileNotFoundError:
        pass
    return events

@app.route('/')
def index():
    game = load_game()
    events = load_events()
    return render_template('index.html', game=game, events=events)

@app.route('/roll', methods=['POST'])
def roll():
    game = load_game()
    events = load_events()
    player = game['Turn']
    roll = random.randint(1, 6)

    # Find current position
    pos = next((space for space, contents in game['Board'].items() if player in contents), 0)

    # Check for skip
    if player in game['Skip']:
        game['Skip'].remove(player)
        game['Turn'] = "Player 2" if player == "Player 1" else "Player 1"
        save_game(game)
        return redirect("/")

    # Remove player from current position (ensuring only one cookie per player on the board)
    if pos and player in game['Board'][pos]:
        game['Board'][pos].remove(player)
        if not game['Board'][pos]:
            del game['Board'][pos]

    # New position
    new_pos = pos + roll
    if new_pos >= 15:
        new_pos = 15  # Player wins if they reach space 15
        game['Turn'] = f"{player} Wins!"  # Announce the winner
        save_game(game)
        return redirect("/")

    # Handle events
    event = events.get(new_pos)
    if event == "Back":
        new_pos = max(1, new_pos - 2)
    elif event == "Skip":
        game['Skip'].append(player)

    # Add player to new tile (making sure only one cookie per player)
    if new_pos in game['Board']:
        game['Board'][new_pos].append(player)
    else:
        game['Board'][new_pos] = [player]

    # Switch turn
    game['Turn'] = "Player 2" if player == "Player 1" else "Player 1"
    save_game(game)
    return redirect("/")

@app.route('/restart', methods=['POST'])
def restart_game():
    # Reset the game state
    initial_state = {
        'Turn': 'Player 1',
        'Board': {1: ['Player 1'], 2: ['Player 2']},  # Reset positions to start
        'Skip': []
    }
    
    # Reset the game state and save it to file
    save_game(initial_state)
    
    # Redirect to the main game page
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
