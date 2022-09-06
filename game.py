import chess_ai
import pygame
import chess
from multiprocessing import Process, Queue
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


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
    # screen.fill((255, 255, 255))
    board = chess.Board(
        "7k/p1r2b2/5q2/1p1p1pR1/5P2/P7/1P2Q2P/1K4R1 w - - 0 32")
    load_images()
    running = True
    squares_selected = []
    game_over = False
    human = True
    popped_moves = []
    show_ai_moves = True
    ai_computing = False
    process = None
    while running:
        popped_moves_len = len(popped_moves)
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
                        if piece is not None:
                            if piece.color == board.piece_at(squares_selected[0]).color:
                                squares_selected.pop()
                        squares_selected.append(square)
                        draw_game(screen, board)
                else:
                    # Only clear if the size of squares_selected isn't 1.
                    # If it is 1 in this else, it means that the user has selected the same piece twice, and there is no need to remove it from the list (improves usability).
                    if len(squares_selected) != 1:
                        squares_selected = []
            elif event.type == pygame.KEYDOWN:
                # undo last move
                if len(board.move_stack) != 0 and event.key == pygame.K_LEFT:
                    popped_moves.append(board.pop())
                # redo last move
                elif popped_moves_len != 0 and event.key == pygame.K_RIGHT:
                    board.push(popped_moves.pop())
                if (popped_moves_len != 0) and ai_computing:
                    process.terminate()
                    ai_computing = False
        if len(squares_selected) == 2 and human and popped_moves_len == 0:
            move = chess.Move(
                squares_selected[0], squares_selected[1])
            square = squares_selected[0]
            if board.is_legal(move):
                if (able_to_promote(board, move, board.piece_at(square))):
                    move.promotion = chess.QUEEN
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
        if not human and not game_over and popped_moves_len == 0:
            print("AI is thinking...")
            if show_ai_moves == True:
                move = chess_ai.get_best_move(board, None)
                ai_moves(screen, board, clock, chess_ai.moves)
                board.push(move)
                human = True
                draw_game(screen, board)
            else:
                if not ai_computing:
                    ai_computing = True
                    move_queue = Queue()
                    process = Process(
                        target=chess_ai.get_best_move, args=(board, move_queue))
                    process.start()
                    # so white can check legal moves while ai is computing
                    board.turn = not board.turn
                if not process.is_alive():
                    # reverting turn back
                    board.turn = not board.turn
                    print("AI has finished computing.")
                    squares_selected = []
                    move = move_queue.get()
                    if move is None:
                        move = chess_ai.get_random_move(board.legal_moves)
                    board.push(move[0])
                    ai_computing = False
                    human = True
            print("\n"+str(chess_ai.evaluate_board(board)) + "\n")


def ai_moves(screen, board, clock, moves):
    '''ai - clean up'''
    while moves:
        board.turn = chess.BLACK
        current_line = []
        move = moves.pop(0)
        current_line.append(move)
        while moves and move[1] != 1:
            current_line.append(move)
            move = moves.pop(0)
            # print(current_line)
            # board.turn = chess.BLACK
        visualize_line(
            screen, board, clock, current_line)
        pygame.display.flip()


def visualize_line(screen, board, clock, current_line):
    size_current_line = len(current_line)
    while current_line:
        move = current_line.pop()[0]
        if not board.is_legal(move):
            move = chess_ai.get_random_move(board.legal_moves)
        if size_current_line != 1:
            board.push(move)
        else:
            size_current_line -= 1
            break
        clock.tick(5) if size_current_line == 3 else clock.tick(60)
        color = (size_current_line*50, 180 -
                 size_current_line*10, 160+size_current_line*20)
        draw_game(screen, board, color)
        pygame.display.flip()
    for i in range(size_current_line):
        if board.move_stack:
            board.pop()
            pygame.display.flip()
    clock.tick(5) if size_current_line == 3 else clock.tick(60)
    # draw_game(screen, board, (180, 180, 180), ("white"))
    # clock.tick(250)
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


""" def highlight_square(screen, board, square):
    square ^= 56
    x = square % 8
    y = square // 8
    pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(
        x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    piece = board.piece_at(square ^ 56)
    if piece:
        screen.blit(IMAGES[str(int(piece.color)) + piece.symbol()],
                    (x * SQUARE_SIZE,
                    y * SQUARE_SIZE))

 """


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
    main()
