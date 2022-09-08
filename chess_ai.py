import random
import chess
DEPTH = 3
CHECKMATE = 10000
DRAW = 0
piece_values = {chess.PAWN: 1,
                chess.KNIGHT: 3,
                chess.BISHOP: 3,
                chess.ROOK: 5,
                chess.QUEEN: 9,
                chess.KING: 0}

knight_weights = [[1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 2, 2, 2, 2, 2, 2, 1],
                  [1, 2, 3, 3, 3, 3, 2, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [1, 2, 3, 3, 3, 3, 2, 1],
                  [1, 2, 2, 2, 2, 2, 2, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_weights = [[4, 3, 2, 1, 1, 2, 3, 4],
                  [3, 4, 3, 2, 2, 3, 4, 3],
                  [2, 3, 4, 3, 3, 4, 3, 2],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [2, 3, 4, 3, 3, 4, 3, 2],
                  [3, 4, 3, 2, 2, 3, 4, 3],
                  [4, 3, 2, 1, 1, 2, 3, 4]]

rook_weights = [[4, 4, 4, 4, 4, 4, 4, 4],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [2, 2, 2, 2, 2, 2, 2, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 2, 2, 2, 2, 2, 2, 2],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [4, 4, 4, 4, 4, 4, 4, 4]]

queen_weights = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]

king_weights = [[3, 4, 2, 1, 1, 2, 4, 3],
                [2, 2, 1, 1, 1, 1, 2, 2],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [2, 2, 1, 1, 1, 1, 2, 2],
                [3, 4, 2, 1, 1, 2, 4, 3]]

# Square values are flipped, so this is opposite of what you'd maybe expect
white_pawn_weights = [[0, 0, 0, 0, 0, 0, 0, 0],
                      [1, 1, 1, -1, -1, 1, 1, 1],
                      [2, 2, 2, 2, 2, 2, 2, 2],
                      [3, 3, 3, 3, 3, 3, 3, 3],
                      [4, 4, 4, 4, 4, 4, 4, 4],
                      [6, 6, 6, 6, 6, 6, 6, 6],
                      [8, 8, 8, 8, 8, 8, 8, 8],
                      [8, 8, 8, 8, 8, 8, 8, 8]]

black_pawn_weights = [[8, 8, 8, 8, 8, 8, 8, 8],
                      [8, 8, 8, 8, 8, 8, 8, 8],
                      [6, 6, 6, 6, 6, 6, 6, 6],
                      [4, 4, 4, 4, 4, 4, 4, 4],
                      [3, 3, 3, 3, 3, 3, 3, 3],
                      [2, 2, 2, 2, 2, 2, 2, 2],
                      [1, 1, 1, -1, -1, 1, 1, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0]]


def get_best_move(board, move_queue):
    global best_move, count, moves, top_move_lines

    best_move = None
    count = 0
    moves = []
    top_move_lines = []
    nega_max_ab(board, board.legal_moves, DEPTH,
                1 if board.turn == chess.WHITE else -1, move_queue)
    # print items in the queue
    # while not move_queue.empty():
    #    print(move_queue.get())
    print(str(count)+" moves evaluated")
    if move_queue:
        move_queue.put((best_move, DEPTH))
    else:
        return best_move


def get_random_move(legal_moves):
    legal_moves = list(legal_moves)
    return random.choice(legal_moves)


def nega_max_ab(board, legal_moves, depth, turn_mult, move_queue, alpha=-CHECKMATE, beta=CHECKMATE):
    global best_move, count, moves, top_move_lines
    count += 1
    if board.is_game_over() or depth == 0:
        return turn_mult * evaluate_board(board)
    max_eval = float('-inf')
    for move in legal_moves:
        board.push(move)
        if move_queue is None:
            moves.append((move, depth))

        val = -nega_max_ab(board, board.legal_moves,
                           depth - 1, -turn_mult, move_queue, -beta, -alpha)
        if val > max_eval:
            max_eval = val
            if depth == DEPTH:
                # top_move_lines.append(moves)
                # moves = []
                # print(str(top_move_lines) + ": " + str(depth))
                # moves.append(move)
                # print(str(move) + ": " + str(turn_mult*evaluate_board(board)))
                best_move = move
                top_move_lines.append(move)
                print(move)
        board.pop()
        alpha = max(alpha, max_eval)
        if alpha >= beta:
            break
    return max_eval


def evaluate_board(board):
    # maybe use machine learning to determine the value of the board
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
                val += pval*weight
            else:
                val -= pval*weight

        og_turn = board.turn
        board.turn = chess.WHITE
        val += 0.1 * board.legal_moves.count()
        board.turn = chess.BLACK
        val -= 0.1 * board.legal_moves.count()
        board.turn = og_turn
        # add more evaluation factors here!!!! """

    return val


def get_weight(piece_type, piece, color):
    if piece_type == chess.KNIGHT:
        return knight_weights[piece//8][piece % 8]
    elif piece_type == chess.BISHOP:
        return bishop_weights[piece//8][piece % 8]
    elif piece_type == chess.ROOK:
        return rook_weights[piece//8][piece % 8]
    elif piece_type == chess.QUEEN:
        return queen_weights[piece//8][piece % 8]
    elif piece_type == chess.KING:
        return king_weights[piece//8][piece % 8]
    elif piece_type == chess.PAWN and color == chess.WHITE:
        return white_pawn_weights[piece//8][piece % 8]
    elif piece_type == chess.PAWN and color == chess.BLACK:
        return black_pawn_weights[piece//8][piece % 8]
    else:
        return 1
