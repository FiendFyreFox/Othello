import random
import time

EMPTY, BLACK, WHITE, OUTER = '.', '@', 'o', '?'
PIECES = (EMPTY, BLACK, WHITE, OUTER)
PLAYERS = {BLACK: 'Black', WHITE: 'White'}

UP, DOWN, LEFT, RIGHT = -10, 10, -1, 1
UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT = -9, 11, 9, -11
DIRECTIONS = (UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT, LEFT, UP_LEFT)

SQUARE_WEIGHTS = [
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0, 120, -20,  20,   5,   5,  20, -20, 120,   0,
    0, -20, -40,  -5,  -5,  -5,  -5, -40, -20,   0,
    0,  20,  -5,  15,   3,   3,  15,  -5,  20,   0,
    0,   5,  -5,   3,   3,   3,   3,  -5,   5,   0,
    0,   5,  -5,   3,   3,   3,   3,  -5,   5,   0,
    0,  20,  -5,  15,   3,   3,  15,  -5,  20,   0,
    0, -20, -40,  -5,  -5,  -5,  -5, -40, -20,   0,
    0, 120, -20,  20,   5,   5,  20, -20, 120,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
]

def squares():

    return [i for i in range(11, 89) if 1 <= (i % 10) <= 8]

def initial_board():
    board = [OUTER] * 100
    for i in squares():
        board[i] = EMPTY

    board[44], board[45] = WHITE, BLACK
    board[54], board[55] = BLACK, WHITE
    return board

def print_board(board, show_legality=None):
    copy = list(board)
    if show_legality == BLACK:
        for move in legal_moves(BLACK, copy):
            copy[move] = '#'
    elif show_legality == WHITE:
        for move in legal_moves(WHITE, copy):
            copy[move] = '#'

    rep = ''
    rep += '  %s\n' % ' '.join(map(str, range(1, 9)))
    for row in range(1, 9):
        begin, end = 10 * row + 1, 10 * row + 9
        rep += '%d %s\n' % (row, ' '.join(copy[begin:end]))
    print(rep)
    return rep

def is_valid(move):

    return isinstance(move, int) and move in squares()

def is_onBoard(move):

    return isinstance(move, int) and move in squares()

def opponent(player):
    return BLACK if player is WHITE else WHITE

# find a square that forms a bracket with square for player
# in the given direction. Returns None if there is no such square.
def find_bracket(square, player, board, direction):

    bracket = square + direction
    if board[bracket] == player:
        return None
    opp = opponent(player)
    while board[bracket] == opp:
        bracket += direction

    return None if board[bracket] in (OUTER, EMPTY) else bracket

# determine whether a move is legal
def is_legal(move, player, board):

    hasbracket = lambda direction: find_bracket(move, player, board, direction)
    return board[move] == EMPTY and any(map(hasbracket, DIRECTIONS))

# --- MAKING MOVES ---

def make_move(move, player, board):

    board[move] = player
    for d in DIRECTIONS:
        make_flips(move, player, board, d)
    return board

def make_flips(move, player, board, direction):

    bracket = find_bracket(move, player, board, direction)

    if not bracket: return

    square = move + direction
    while square != bracket:
        # flip each square inside the bracket to the player's color
        board[square] = player
        square += direction

# --- MONITORING PLAYERS ---

class IllegalMoveError(Exception):

    def __init__(self, player, move, board):
        self.player = player
        self.move = move
        self.board = board

    def __str__(self):
        return f'{PLAYERS[self.player]} cannot move to square {self.move}'

def legal_moves(player, board):

    return [sq for sq in squares() if is_legal(sq, player, board)]

def any_legal_move(player, board):

    return any(is_legal(sq, player, board) for sq in squares())

# --- GAME MANAGEMENT ---

def play(black_strategy, white_strategy, starting_player=BLACK):

    board = initial_board()
    player = starting_player
    strategy = lambda who: black_strategy if who == BLACK else white_strategy
    move_times = {'@': [], 'o': []}

    while player is not None:
        start = time.time()
        move = get_move(strategy(player), player, board)
        end = time.time()
        print(f'that move took {end - start} seconds')
        move_times[player].append(end - start)
        make_move(move, player, board)
        print(f'{move} was played')
        player = next_player(board, player)
    winner = 'Black' if score(BLACK, board) > 0 else 'White'
    print(f'{winner} wins!')
    print(f'the mean move time for black was {sum(move_times["@"]) / len(move_times["@"])}.')
    print(f'the mean move time for white was {sum(move_times["o"]) / len(move_times["o"])}.')
    return board, score(BLACK, board)

def next_player(board, prev_player):
    opp = opponent(prev_player)
    if any_legal_move(opp, board):
        return opp
    elif any_legal_move(prev_player, board):
        return prev_player
    return None

def get_move(strategy, player, board):

    copy = list(board) # copy the board to prevent cheating
    move = strategy(player, copy)
    if not is_valid(move) or not is_legal(move, player, board):
        raise IllegalMoveError(player, move, copy)
    return move

def score(player, board):

    mine, theirs = 0, 0
    opp = opponent(player)
    for sq in squares():
        piece = board[sq]
        if piece == player: mine += 1
        elif piece == opp: theirs += 1
    return mine - theirs

# --- STRATEGIES ---

def player_strategy(player, board):

    while True:
        print_board(board, show_legality=player)
        move = int(input('Move? > '))
        if is_legal(move, player, board):
            return move


def random_strategy(player, board):

    return random.choice(legal_moves(player, board))

def score_maximizer(player, board):

    def score_move(move):
        return score(player, make_move(move, player, list(board)))
    return max(legal_moves(player, board), key=score_move)

def minimax_searcher(depth, evaluate):

    def strategy(player, board):
        return minimax(player, board, depth, evaluate)[1]
    return strategy

def alphabeta_searcher(depth, evaluate):

    def strategy(player, board):
        return alphabeta(player, board, -999, 999, depth, evaluate)[1]
    return strategy

# --- EVALUATION METHODS ---

def max_score(player, board):
    def score_move(move):
        return score(player, make_move(move, player, list(board)))

    moves = legal_moves(player, board)
    return max(moves, key=score_move)

def simple(player, board):
    return score(player, board)

def weighted_score(player, board):
    opp = opponent(player)
    total = 0
    for sq in squares():
        if board[sq] == player:
            total += SQUARE_WEIGHTS[sq]
        elif board[sq] == opp:
            total -= SQUARE_WEIGHTS[sq]

    return total




def minimax(player, board, depth, evaluate):

    if depth == 0:
        return evaluate(player, board), None

    def value(board):
        return -minimax(opponent(player), board, depth - 1, evaluate)[0]

    moves = legal_moves(player, board)

    if not moves:

        if not any_legal_move(opponent(player), board):
            return final_value(player, board), None

        return value(board), None

    return max((value(make_move(m, player, list(board))), m) for m in moves)

def alphabeta(player, board, alpha, beta, depth, evaluate):

    if depth == 0:
        return evaluate(player, board), None

    def value(board, alpha, beta):
        return -alphabeta(opponent(player), board, -beta, -alpha, depth-1, evaluate)[0]

    moves = legal_moves(player, board)
    if not moves:
        if not any_legal_move(opponent(player), board):
            return final_value(player, board), None
        return value(board, alpha, beta), None

    best_move = moves[0]
    for move in moves:

        if alpha >= beta:
            break

        val = value(make_move(move, player, list(board)), alpha, beta)

        if val > alpha:
            alpha = val
            best_move = move

    return alpha, best_move

def final_value(player, board):
    diff = score(player, board)
    if diff < 0:  # the player lost
        return -999
    elif diff > 0:  # the player won
        return 999
    return diff  # there was a tie


if __name__ == '__main__':


    board, score = play(random_strategy, alphabeta_searcher(6, weighted_score))

    print_board(board)