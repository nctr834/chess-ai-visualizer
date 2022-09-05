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


def get_best_move(show_moves, board, move_queue):
    global best_move, count, moves, top_move_lines

    best_move = None
    count = 0
    moves = []
    top_move_lines = []
    nega_max_ab(show_moves, board, board.legal_moves, DEPTH,
                1 if board.turn == chess.WHITE else -1, move_queue)
    # print items in the queue
    # while not move_queue.empty():
    #    print(move_queue.get())
    print(count)
    move_queue.put((best_move, DEPTH))


def get_random_move(legal_moves):
    legal_moves = list(legal_moves)
    return random.choice(legal_moves)


def nega_max_ab(show_moves, board, legal_moves, depth, turn_mult, move_queue, alpha=-CHECKMATE, beta=CHECKMATE):
    global best_move, count, moves, top_move_lines
    count += 1
    if board.is_game_over() or depth == 0:
        return turn_mult * evaluate_board(board)
    max_eval = float('-inf')
    for move in legal_moves:
        board.push(move)
        if show_moves and depth >= 1:
            # moves.append(move)
            move_queue.put((move, depth))
        val = -nega_max_ab(show_moves, board, board.legal_moves,
                           depth - 1, -turn_mult, move_queue, -beta, -alpha)
        #moves = []
        board.pop()
        if val > max_eval:
            max_eval = val
            if depth == DEPTH:
                # top_move_lines.append(moves)
                #print(str(top_move_lines) + ": " + str(depth))
                best_move = move
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
            pval = piece_values[piece_map[piece].piece_type]
            if piece_map[piece].color == chess.WHITE:
                val += pval
            else:
                val -= pval

        og_turn = board.turn
        board.turn = chess.WHITE
        val += 0.1 * board.legal_moves.count()
        board.turn = chess.BLACK
        val -= 0.1 * board.legal_moves.count()
        board.turn = og_turn
        # add more evaluation factors here!!!! """

    return val
