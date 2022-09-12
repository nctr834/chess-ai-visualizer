import random
import chess_ai
import pygame
import chess
from multiprocessing import Process, Queue
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


BOARD_WIDTH = BOARD_HEIGHT = 700
OPTIONS_WIDTH = 200
OPTIONS_HEIGHT = 700
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
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
    # some fens to test - assign to starting_fen (in quotes)
    # "7k/p1r2b2/5q2/1p1p1pR1/5P2/P7/1P2Q2P/1K4R1 w - - 0 32"
    # "rnbqkbnr/pp4pP/8/2pppp2/8/8/PPPPPP1P/RNBQKBNR w KQkq - 0 5"
    # "rnb1k2r/pppp1ppp/5q2/4p3/1bB1P1n1/2N2N2/PPPP1PPP/R1BQ1RK1 w kq - 8 6"
    pygame.init()
    screen = pygame.display.set_mode(
        ([BOARD_WIDTH + OPTIONS_WIDTH, BOARD_HEIGHT]), pygame.DOUBLEBUF, pygame.HWSURFACE)
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    starting_fen = ""
    board = chess.Board() if len(starting_fen) == 0 else chess.Board(starting_fen)
    load_images()
    running = True
    squares_selected = []
    game_over = False
    game_over_str = ""
    human = True
    was_human = False
    popped_moves = []
    show_ai_moves = True
    move_queue = Queue()
    ai_thinking = False
    process = None
    fen_list = open("fen_list.txt", "r").read().splitlines()
    text = pygame.font.SysFont("comicsans", 15)
    while running:
        popped_moves_len = len(popped_moves)
        update_text(screen, board, text, show_ai_moves,
                    ai_thinking, game_over, game_over_str)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x = mouse_pos[0] // SQUARE_SIZE
                y = mouse_pos[1] // SQUARE_SIZE
                if x >= 8:
                    # Clicked off the board
                    squares_selected = []
                    board.turn = chess.WHITE
                    if y == 7:
                        # board = random fen from fen_list, except for first line
                        fen = fen_list[random.randint(1, len(fen_list) - 1)]
                        board = chess.Board(fen)
                        print("FEN for random position:", fen)
                        board.turn = chess.WHITE
                        human = True
                        game_over = False
                        popped_moves = []
                    # side buttons
                    if y == 6:
                        if show_ai_moves:
                            show_ai_moves = False
                        else:
                            show_ai_moves = True
                    if y == 5 and human:
                        human = False
                        if was_human:
                            was_human = False
                            board.turn = chess.BLACK
                        else:
                            board.turn = chess.WHITE
                            was_human = True
                else:
                    # Clicked on the board
                    # square ^ 56 is from the python-chess docs; because of how the board is represented in python-chess,
                    # it's necessary to flip the square referenced vertically.
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
                elif event.key == pygame.K_SPACE:
                    board = chess.Board() if len(starting_fen) == 0 else chess.Board(
                        starting_fen)  # reset board
                    board.turn = chess.WHITE
                    human = True
                    game_over = False
                    was_human = False
                    popped_moves = []
                if (popped_moves_len != 0) and ai_thinking:
                    process.terminate()
                    ai_thinking = False
        # makes move for human player when second square is selected
        if len(squares_selected) == 2 and human and popped_moves_len == 0:
            move = chess.Move(
                squares_selected[0], squares_selected[1])
            square = squares_selected[0]
            if (able_to_promote(board, move, board.piece_at(square))):
                move.promotion = chess.QUEEN
            if board.is_legal(move):
                board.push(move)
                draw_game(screen, board)
                human = False
            squares_selected = []
        draw_game(screen, board)
        # Must run after board is updated.
        if len(squares_selected) == 1:
            highlight_moves(screen, board, squares_selected[0])

        # Game finishes, and moves can't be made
        if game_over is False and board.is_game_over():
            game_over_str = get_terminate_condition(
                screen, board, text, show_ai_moves, ai_thinking)
            game_over = True

        clock.tick(MAX_FPS)
        pygame.display.flip()

        # ai move
        if not human and not game_over and popped_moves_len == 0:
            if show_ai_moves == True:
                # When AI moves are shown, the move is found, then visualized and bushed to the board
                if not ai_thinking:
                    ai_thinking = True
                    update_text(screen, board, text,
                                show_ai_moves, ai_thinking, game_over, game_over_str)
                move = chess_ai.get_best_move(board, None)
                ai_moves(screen, board, clock,
                         chess_ai.moves, was_human)
                if was_human:
                    board.turn = chess.WHITE
                else:
                    board.turn = chess.BLACK
                board.push(move)
                ai_thinking = False
                human = True
                draw_game(screen, board)
            else:
                # When AI moves are not shown, the AI will still make a move, but multithreading
                # is used to make the move in the background, allowing for the user to still click
                # around and have the game respond.
                if not ai_thinking:
                    ai_thinking = True
                    process = Process(
                        target=chess_ai.get_best_move, args=(board, move_queue))
                    process.start()
                    # so white can check legal moves while ai is computing
                    board.turn = not board.turn
                if not process.is_alive():
                    # reverting turn back
                    board.turn = not board.turn
                    print("AI has finished computing.")
                    if len(squares_selected) == 2:
                        squares_selected.pop()
                    move = move_queue.get()
                    if move is None:
                        move = chess_ai.get_random_move(board.legal_moves)
                    board.push(move[0])
                    ai_thinking = False
                    human = True


def ai_moves(screen, board, clock, moves, was_human):
    '''Driver function for the visualization of the AI's moves.'''
    moves = set(moves)
    copy_moves = moves.copy()
    for move in copy_moves:
        if (move[0], 1) in moves and (move[0], 3) in moves:
            moves.remove((move[0], 1))
    # goes through each move and visualizes the line
    while moves:
        move = moves.pop()
        depth = move[1]-1
        if depth == 1:
            board.turn = chess.WHITE
        if move[1] != 1 or (move[1] == 1 and board.is_legal(move[0])):
            visualize_line(
                screen, board, clock, move[0], depth, was_human)
        pygame.display.flip()


def visualize_line(screen, board, clock, first_move, depth, was_human):
    '''Visualizes the line of moves that the AI considered.'''
    line = []
    board.push(first_move)
    line.append(first_move)
    color = (0, 0, 0)
    # only visualizing with depth 3
    if depth == 2:
        color = (9, 121, 105)
        tick_amt = 5
    elif depth == 1:
        color = (134, 78, 118)
        tick_amt = 10
    elif depth == 0:
        color = (88, 24, 69)
        tick_amt = 15
    # finds the moves that the AI considered
    for i in range(depth, 0, -1):
        move = chess_ai.get_best_move(board, None, i)
        if move is not None:
            line.append(move)
            board.push(move)
        else:
            while line:
                board.pop()
                line.pop()
            return
    # pops moves from board, so they can be drawn smoothly
    for i in range(len(line)):
        board.pop()
    if depth == 1:
        line.reverse()
    # visualizes the moves
    if was_human:
        board.turn = chess.WHITE
    else:
        board.turn = chess.BLACK
    for move in line:
        board.push(move)
        clock.tick(tick_amt)
        draw_game(screen, board, color)
        pygame.display.flip()
    while line:
        line.pop()
        board.pop()
    clock.tick(tick_amt/2)
    draw_game(screen, board, color)
    pygame.display.flip()


def get_terminate_condition(screen, board, text, show_ai_moves, ai_thinking):
    '''Gets the reason why the game ended.'''
    game_over_str = ""
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            game_over_str = "Black wins with checkmate!"
            update_text(screen, board, text, show_ai_moves,
                        ai_thinking, True, game_over_str)
        else:
            game_over_str = "White wins with checkmate!"
            update_text(screen, board, text, show_ai_moves,
                        ai_thinking, True, game_over_str)
    elif board.is_stalemate():
        game_over_str = "Draw by stalemate."
        update_text(screen, board, text, show_ai_moves,
                    ai_thinking, True, game_over_str)
    elif board.can_claim_fifty_moves():
        game_over_str = "Draw by fifty moves."
        update_text(screen, board, text, show_ai_moves,
                    ai_thinking, True, game_over_str)
    elif board.can_claim_threefold_repetition():
        game_over_str = "Draw by threefold repetition."
        update_text(screen, board, text, show_ai_moves,
                    ai_thinking, True, game_over_str)
    elif board.is_insufficient_material():
        game_over_str = "Draw by insufficient material."
        update_text(screen, board, text, show_ai_moves,
                    ai_thinking, True, game_over_str)
    return game_over_str


def able_to_promote(board, move, piece):
    '''Checks if a pawn is able to promote.'''
    if(piece.piece_type != chess.PAWN):
        return False
    return (chess.square_rank(move.to_square) == 7 and board.turn == chess.WHITE) or (chess.square_rank(move.to_square) == 0 and board.turn == chess.BLACK)


def highlight_moves(screen, board, square):
    '''Highlights the moves that the selected piece can make.'''
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


def load_button(screen, font, button_name):
    '''Loads the fen button, show ai moves button, and the make ai move button.'''
    button = pygame.Rect(0, 0, 50, 50)
    diff = 0
    msg = ""
    if button_name == "fen_button":
        msg = "Load Random Position"
        diff = 50
    elif button_name == "show_ai_button":
        msg = "Toggle Show AI"
        diff = 145
    elif button_name == "make_ai_move_button":
        msg = "Make AI Move"
        diff = 230
    button.center = (BOARD_WIDTH+OPTIONS_WIDTH/2, BOARD_HEIGHT-diff)
    text = font.render(msg, True, (255, 255, 255))
    text_rect = text.get_rect(center=button.center)
    screen.blit(text, text_rect)


def update_text(screen, board, font, show_ai_moves, ai_thinking, game_over=False, game_over_str=""):
    '''Updates the text on the screen.'''
    # "unload" text
    screen.fill((0, 0, 0), (BOARD_WIDTH, 0, OPTIONS_WIDTH, BOARD_HEIGHT))

    text = font.render("Show AI Moves: " +
                       str(show_ai_moves), True, (255, 255, 255))
    text_rect = text.get_rect(
        center=(BOARD_WIDTH+OPTIONS_WIDTH/2, 41))
    screen.blit(text, text_rect)

    if ai_thinking:
        text = font.render("AI Thinking...", True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(BOARD_WIDTH+OPTIONS_WIDTH/2, 83))
        screen.blit(text, text_rect)

    if board.move_stack.__len__() > 1:
        piece = board.piece_at(board.move_stack[-1].to_square)
        text = font.render("Last Move: " +
                           piece.symbol().upper() + str(board.peek()), True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(BOARD_WIDTH+OPTIONS_WIDTH/2, 124))
        screen.blit(text, text_rect)

    if game_over:
        text = font.render(game_over_str, True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(BOARD_WIDTH+OPTIONS_WIDTH/2, BOARD_HEIGHT/2-43))
        screen.blit(text, text_rect)

    load_button(screen, font, "fen_button")
    load_button(screen, font, "show_ai_button")
    load_button(screen, font, "make_ai_move_button")
    pygame.display.flip()


def draw_game(screen, board, color_one=("lightblue"), color_two=("white")):
    '''Draws the board and pieces.'''
    draw_board(screen, color_one, color_two)
    draw_pieces(screen, board)


def draw_board(screen=pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT)), color_one=(187, 158, 137), color_two=("white")):
    '''Draws the board.'''
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            if (i + j) % 2 == 0:
                pygame.draw.rect(
                    screen, pygame.Color(color_one), (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(screen, pygame.Color(color_two), (i * SQUARE_SIZE,
                                 j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    '''Draws the pieces.'''
    piece_map = board.piece_map()
    for piece in piece_map:
        if piece is not None:
            square = piece ^ 56
            screen.blit(IMAGES[str(int(piece_map[piece].color)) + piece_map[piece].symbol()],
                        (square % 8 * SQUARE_SIZE,
                         square // 8 * SQUARE_SIZE))


if __name__ == '__main__':
    main()
