import sys
import chess
import pygame
import chess_ai
import multiprocessing
from multiprocessing import Process, Queue
WIDTH = HEIGHT = 700
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 10000
IMAGES = {}

""" IF AI IS ENABLED, DON'T LET PLAYER MAKE MOVES WHEN REDOING OR UNDOING MOVES """


def load_images():
    pieces = ['1B', '0b', '1N', '0n', '1R',
              '0r', '1Q', '0q', '1K', '0k', '1P', '0p']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(
            "./images/" + piece + '.png'), (SQUARE_SIZE, SQUARE_SIZE)).convert_alpha()


def main():
    # "7k/p1r2b2/5q2/1p1p1pR1/5P2/P7/1P2Q2P/1K4R1 w - - 0 32"
    # "rnbqkbnr/pp4pP/8/2pppp2/8/8/PPPPPP1P/RNBQKBNR w KQkq - 0 5"
    # "7k/p1r2b2/5q2/1p1p1p1R/5P2/P7/1P2Q2P/1K4R1 b - - 1 32"
    pygame.init()
    screen = pygame.display.set_mode(
        ([WIDTH, HEIGHT]), pygame.DOUBLEBUF, pygame.HWSURFACE)
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    #screen.fill((255, 255, 255))
    board = chess.Board()
    load_images()
    running = True
    squares_selected = []
    game_over = False
    human = True
    popped_moves = []
    show_ai_moves = False
    ai_computing = False
    process = None
    print(board)
    print(str(chess_ai.evaluate_board(board)) + "\n")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x = mouse_pos[0] // SQUARE_SIZE
                y = mouse_pos[1] // SQUARE_SIZE

                # square ^ 56 from the python-chess docs; need to mirror the square vertically. ##### APPLY TRANSFORM!!!!
                square = chess.square(x, y) ^ 56
                piece = board.piece_at(square)

                if square not in squares_selected and len(squares_selected) < 2:
                    if len(squares_selected) == 0:
                        # Will only append if the correct color is selected first.
                        if piece is not None and piece.color == board.turn:
                            squares_selected.append(square)
                    else:
                        # if piece is same color as first piece, replace
                        if piece is not None and piece.color == board.piece_at(squares_selected[0]).color:
                            squares_selected.pop()
                        squares_selected.append(square)
                        draw_game(screen, board)
                else:
                    # Only clear if the size of squares_selected isn't 1.
                    # If it is 1 in this else, it means that the user has selected the same piece twice, and there is no need to remove it from the list (improves usability).
                    if len(squares_selected) != 1:
                        squares_selected = []
            elif event.type == pygame.KEYDOWN:
                if ai_computing:
                    process.terminate()
                    ai_computing = False
                # undo last move
                if len(board.move_stack) != 0 and event.key == pygame.K_LEFT:
                    popped_moves.append(board.pop())
                # redo last move
                elif len(popped_moves) != 0 and event.key == pygame.K_RIGHT:
                    board.push(popped_moves.pop())
        if len(squares_selected) == 2 and human:
            move = chess.Move(
                squares_selected[0], squares_selected[1])

            square = squares_selected[0]
            if (able_to_promote(board, move, board.piece_at(square))):
                move.promotion = chess.QUEEN

            if board.is_legal(move) and not ai_computing:
                board.push(move)
                draw_game(screen, board)
                human = False
            squares_selected = []

        draw_game(screen, board)
        # Must run after board is updated.
        if len(squares_selected) == 1:
            highlight_moves(screen, board, squares_selected[0])

        if game_over is False and board.is_game_over():
            get_terminate_condition(board)
            game_over = True

        clock.tick(MAX_FPS)
        pygame.display.flip()

        # ai move
        if not human and not board.is_game_over():
            if not ai_computing:
                ai_computing = True
                move_queue = Queue()
                process = Process(
                    target=chess_ai.get_best_move, args=(show_ai_moves, board, move_queue))
                process.start()

                # so white can check legal moves while ai is computing
                if not show_ai_moves:
                    board.turn = not board.turn
            if not process.is_alive():
                # reverting turn back
                print("AI has finished computing.")
                if not show_ai_moves:
                    board.turn = not board.turn
                squares_selected = []
                if show_ai_moves is True:
                    ai_moves(screen, board, clock, move_queue)
                move = move_queue.get()
                if move is None:
                    move = chess_ai.get_random_move(board.legal_moves)
                board.push(move[0])
                ai_computing = False
                human = True


def ai_moves(screen, board, clock, move_queue):
    '''ai - clean up'''
    while move_queue.qsize() > 0:
        print(move_queue.qsize())
        moves = move_queue.get()
        if moves[0] is not None:
            # green if no prune - pink if prunes at depth 2
            """ visualize_line(
                screen, board, moves[1], clock, (0, 180, 160), moves[0]) if (moves[1] == 3) else visualize_line(screen, board, moves[1], clock, "pink", moves[0]) """
            if moves[1] == 3:
                visualize_line(
                    screen, board, moves[1], clock, (0, 180, 160), moves[0])
            elif moves[1] == 2:
                visualize_line(
                    screen, board, moves[1], clock, "pink", moves[0])
                # draw_game(screen, board, ("gray"), ("white"))
            pygame.display.flip()
    # board.push(ai_move)
    draw_game(screen, board)
    print(str(board))
    # else:
    #   board.push(chess_ai.get_random_move(board.legal_moves))


def visualize_line(screen, board, depth, clock, color, move):
    for i in range(depth):
        try:
            board.push(move)
        except:
            pass
        # board.turn = board.turn
        # chess_ai.moves.remove(chess_ai.moves[0])
        clock.tick(100)
        # clock.tick(10000) if depth == 3 else clock.tick(10000)
        draw_game(screen, board, color, ("white"))
        pygame.display.flip()
    for i in range(depth):
        if board.move_stack:
            board.pop()
            clock.tick(100)
        draw_game(screen, board, color, ("white"))
        pygame.display.flip()


def get_terminate_condition(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            print("Black wins with checkmate!")
        else:
            print("White wins with checkmate!")
    elif board.is_stalemate():
        print("Draw by stalemate")
    elif board.can_claim_fifty_moves():
        print("Draw by fifty moves.")
    elif board.can_claim_threefold_repetition():
        print("Draw by threefold repetition.")
    elif board.is_insufficient_material():
        print("Draw by insufficient material.")


def able_to_promote(board, move, piece):
    if(piece.piece_type != chess.PAWN):
        return False
    return chess.square_rank(move.to_square) == 7 and board.turn == chess.WHITE or chess.square_rank(move.to_square) == 0 and board.turn == chess.BLACK


""" def move_animation(screen, board, move, clock):
    return """


def highlight_moves(screen, board, square):
    # Highlight legal squares
    for move in board.legal_moves:
        if move.from_square == square:
            color = (255, 100, 100) if board.piece_at(
                move.to_square) is not None else (255, 180, 190)

            legal_square = move.to_square ^ 56
            if (legal_square % 8 + legal_square // 8) % 2 == 0:
                pygame.draw.rect(screen,
                                 color, (legal_square % 8 * SQUARE_SIZE, legal_square // 8 * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(screen,
                                 (255, 150, 150), (legal_square % 8 * SQUARE_SIZE, legal_square // 8 * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    # Also highlighting selected square
    pygame.draw.rect(screen, pygame.Color(
        (110, 50, 50)), ((square ^ 56) % 8 * SQUARE_SIZE, (square ^ 56) // 8 * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    draw_pieces(screen, board)
    pygame.display.flip()


def draw_game(screen, board, color_one=("lightblue"), color_two=("white")):
    draw_board(screen, color_one, color_two)
    draw_pieces(screen, board)


def draw_board(screen=pygame.display.set_mode((WIDTH, HEIGHT)), color_one=("lightblue"), color_two=("white")):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            if (i + j) % 2 == 0:
                pygame.draw.rect(
                    screen, pygame.Color(color_one), (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(screen, pygame.Color(color_two), (i * SQUARE_SIZE,
                                 j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    piece_map = board.piece_map()
    for piece in piece_map:
        if piece is not None:
            square = piece ^ 56
            screen.blit(IMAGES[str(int(piece_map[piece].color)) + piece_map[piece].symbol()],
                        (square % 8 * SQUARE_SIZE,
                         square // 8 * SQUARE_SIZE))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
    sys.exit()
