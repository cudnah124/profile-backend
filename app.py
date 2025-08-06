from flask import Flask, request, jsonify, render_template, abort
from ai import State, Human, Player, RuleBased
import numpy as np
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
policy_path = os.path.join(current_dir, "policy_p1")

BOARD_ROWS = 3
BOARD_COLS = 3
wincondition = 3

app = Flask(__name__)
human = Human("Người chơi")

#AI Reinforcement Learning
ai = Player("p1", 0)
ai.loadPolicy(policy_path)

# AI Rule Based
rule_based = RuleBased("RuleBased", 0)

game = None
# Khởi tạo AI và game
@app.route('/create_game', methods=['POST'])
def create_game():
    data = request.get_json()
    global game, human, ai, rule_based, BOARD_ROWS, BOARD_COLS, wincondition
    row, col = data["row"], data["col"]
    BOARD_ROWS, BOARD_COLS = row, col
    wincondition = data["wincondition"]

    type = data["type"]
    if type == "rule_based":
        ai = RuleBased("p2", winCondition=wincondition)
    elif type == "reinforcement_learning":
        ai = Player("p1", 0.2)
        ai.loadPolicy(policy_path)
    print(f"Creating game with type: {type}, win condition: {wincondition}")
    game = State(human, ai, row, col, wincondition)
    return jsonify({'board': game.board.tolist()})

@app.route("/tictactoe")
def index():
    referer = request.headers.get("Referer")
    # Kiểm tra nếu không có referer hoặc không đến từ frontend
    if not referer or ("http://localhost:3000" not in referer and "http://localhost:5000" not in referer):
        abort(403)  # Trả về lỗi Forbidden
    return render_template('index.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/reset", methods=["POST"])
def reset():
    global human, ai, game
    game = State(human, ai, BOARD_ROWS, BOARD_COLS, wincondition)
    return jsonify({"board": game.board.tolist()})

@app.route("/human_move", methods=["POST"])
def human_move():
    global game
    data = request.get_json()
    x, y = data["x"], data["y"]

    if game.board[x][y] != 0 or game.isEnd:
        return jsonify({"error": "Invalid move"}), 400

    game.updateState((x, y))

    win = game.winner((x, y))
    if win is not None:
        return jsonify({"board": game.board.tolist(), "winner": win})
    return jsonify({
        "board": game.board.tolist(),
        "human_move": (x, y),
        "winner": win
    })
@app.route("/ai_move", methods=["GET"])
def ai_move():
    global game, ai
    ai_action = ai.chooseAction(game.availablePositions(), game.board, game.playerSymbol)
    game.updateState(ai_action)

    win = game.winner(ai_action)
    return jsonify({
        "board": game.board.tolist(),
        "ai_move": ai_action,
        "winner": win
    })

@app.route("/check_win", methods=["GET"])
def check_win():
    global game
    return jsonify({
        "winner": game.winner()
    })

if __name__ == "__main__":
    app.run(debug=True)
