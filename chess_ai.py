import random
import chess
import numpy as np
DEPTH = 3
CHECKMATE = 10000
DRAW = 0
piece_values = {chess.PAWN: 1,
                chess.KNIGHT: 3,
                chess.BISHOP: 3,
                chess.ROOK: 5,
                chess.QUEEN: 9,
                chess.KING: 1}

# weights for pieces to improve evaluation
knight_weights = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                           [1, 2, 2, 2, 2, 2, 2, 1],
                           [1, 2, 2, 2, 2, 2, 2, 1],
                           [1, 2, 2, 3, 3, 2, 2, 1],
                           [1, 2, 2, 3, 3, 2, 2, 1],
                           [1, 2, 2, 2, 2, 2, 2, 1],
                           [1, 2, 2, 2, 2, 2, 2, 1],
                           [1, 1, 1, 1, 1, 1, 1, 1]])

bishop_weights = np.array([[4, 3, 2, 1, 1, 2, 3, 4],
                           [3, 4, 3, 2, 2, 3, 4, 3],
                           [2, 2, 4, 3, 3, 4, 2, 2],
                           [1, 3, 3, 3, 3, 3, 3, 1],
                           [1, 3, 3, 3, 3, 3, 3, 1],
                           [2, 2, 4, 3, 3, 4, 2, 2],
                           [3, 4, 3, 2, 2, 3, 4, 3],
                           [4, 3, 2, 1, 1, 2, 3, 4]])

rook_weights = np.array([[4, 4, 4, 4, 4, 4, 4, 4],
                         [3, 3, 3, 3, 3, 3, 3, 3],
                         [2, 2, 2, 2, 2, 2, 2, 2],
                         [1, 2, 3, 3, 3, 3, 2, 1],
                         [1, 2, 3, 3, 3, 3, 2, 1],
                         [2, 2, 2, 2, 2, 2, 2, 2],
                         [3, 3, 3, 3, 3, 3, 3, 3],
                         [4, 4, 4, 4, 4, 4, 4, 4]])

queen_weights = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                          [1, 2, 2, 2, 2, 2, 2, 1],
                          [1, 2, 3, 3, 3, 3, 2, 1],
                          [1, 2, 3, 3, 3, 3, 2, 1],
                          [1, 2, 3, 3, 3, 3, 2, 1],
                          [1, 2, 3, 3, 3, 3, 2, 1],
                          [1, 2, 2, 2, 2, 2, 2, 1],
                          [1, 1, 1, 1, 1, 1, 1, 1]])

king_weights = np.array([[3, 4, 0, 0, 0, 0, 4, 3],
                         [2, 2, 0, 0, 0, 0, 2, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 1, 0, 0, 0, 0, 1, 1],
                         [3, 4, 0, 0, 0, 0, 4, 3]])

# Square values are flipped, so this is opposite of what you'd maybe expect
white_pawn_weights = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                               [1, 1, 1, -1, -1, 1, 1, 1],
                               [2, 2, 2, 2, 2, 2, 2, 2],
                               [2, 2, 3, 4, 4, 3, 2, 2],
                               [4, 4, 4, 4, 4, 4, 4, 4],
                               [6, 6, 6, 6, 6, 6, 6, 6],
                               [8, 8, 8, 8, 8, 8, 8, 8],
                               [8, 8, 8, 8, 8, 8, 8, 8]])


black_pawn_weights = np.array([[8, 8, 8, 8, 8, 8, 8, 8],
                              [8, 8, 8, 8, 8, 8, 8, 8],
                               [6, 6, 6, 6, 6, 6, 6, 6],
                               [4, 4, 4, 4, 4, 4, 4, 4],
                               [2, 2, 3, 4, 4, 3, 2, 2],
                               [2, 2, 2, 2, 2, 2, 2, 2],
                               [1, 1, 1, -1, -1, 1, 1, 1],
                               [0, 0, 0, 0, 0, 0, 0, 0]])


def get_best_move(board, move_queue, depth=DEPTH):
    '''Returns the best move from the list of legal moves'''
    global best_move, count, moves, DEPTH
    legal_moves = list(board.legal_moves)
    random.shuffle(legal_moves)

    if DEPTH != depth:
        DEPTH = depth
    best_move = None
    count = 0
    moves = []
    nega_max_ab(board, legal_moves, depth, move_queue,
                1 if board.turn == chess.WHITE else -1)

    if depth >= 3:
        print(str(count)+" moves evaluated")
    if move_queue:
        move_queue.put((best_move, DEPTH))
    else:
        return best_move


def get_random_move(legal_moves):
    '''Returns a random move from the list of legal moves'''
    legal_moves = list(legal_moves)
    return random.choice(legal_moves)


def nega_max_ab(board, legal_moves, depth, move_queue, turn_mult, alpha=-CHECKMATE, beta=CHECKMATE):
    ''' Negamax with alpha-beta pruning - explained on Github'''
    global best_move, count, moves
    count += 1
    if board.is_game_over() or depth == 0:
        if move_queue is not None:
            quiescence_search(board, alpha, beta, DEPTH)
        return turn_mult * evaluate_board(board)
    max_eval = float('-inf')
    for move in legal_moves:
        board.push(move)
        val = -nega_max_ab(board, board.legal_moves,
                           depth - 1, move_queue, -turn_mult, -beta, -alpha)

        if val > max_eval:
            max_eval = val
            # Move this if statement to line 127 to animate every move, and not just the best candiates
            if move_queue is None:
                moves.append((move, depth))
            if depth == DEPTH:
                if depth >= 3:
                    # remove if you don't want to see evaluation (entire if statement)
                    print(str(move) + ": " + str(evaluate_board(board)))
                best_move = move
        board.pop()
        alpha = max(alpha, max_eval)
        if alpha >= beta:
            break
    return max_eval


# quiescence search
def quiescence_search(board, alpha, beta, depth):
    ''' Quiescence search algorithm - explained on Github'''
    global count
    count += 1
    current_eval = evaluate_board(board)

    if current_eval >= beta:
        return beta

    if current_eval > alpha:
        alpha = current_eval

    if board.is_game_over() or depth == 0:
        return alpha

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            val = -quiescence_search(board, -beta, -alpha, depth - 1)
            board.pop()
            if val >= beta:
                return beta
            if val > alpha:
                alpha = val
    return alpha


def evaluate_board(board):
    '''Returns the evaluation of the board'''
    # improvement - maybe use machine learning to determine the value of the board
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif board.is_stalemate():
        return DRAW
    elif board.can_claim_draw():
        return DRAW
    elif board.is_insufficient_material():
        return DRAW
    else:
        val = 0
        # piece values
        piece_map = board.piece_map()
        for piece in piece_map:
            color = piece_map[piece].color
            weight = get_weight(
                piece_map[piece].piece_type, piece, color)
            pval = piece_values[piece_map[piece].piece_type]
            if color == chess.WHITE:
                val += (pval+weight*0.1)
            else:
                val -= (pval+weight*0.1)

        # This causes the AI to play more aggressively with the Queen, which is typically bad
        #og_turn = board.turn
        #board.turn = chess.WHITE
        #val += 0.1 * board.legal_moves.count()
        #board.turn = chess.BLACK
        #val -= 0.1 * board.legal_moves.count()
        # board.turn = og_turn """
        # add more evaluation factors here
    return val


def get_weight(piece_type, piece, color):
    '''Returns the weight of a piece based on the piece's position'''
    r = piece // 8
    c = piece % 8
    if piece_type == chess.KNIGHT:
        return knight_weights[r][c]
    elif piece_type == chess.BISHOP:
        return bishop_weights[r][c]
    elif piece_type == chess.ROOK:
        return rook_weights[r][c]
    elif piece_type == chess.QUEEN:
        return queen_weights[r][c]
    elif piece_type == chess.KING:
        return king_weights[r][c]
    elif piece_type == chess.PAWN and color == chess.WHITE:
        return white_pawn_weights[r][c]
    elif piece_type == chess.PAWN and color == chess.BLACK:
        return black_pawn_weights[r][c]
    else:
        return 1
