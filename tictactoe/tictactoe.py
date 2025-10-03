import pygame
import sys
import math

# Kick off Pygame so we can start drawing the window and reacting to input
pygame.init()

# Basic layout and sizing settings
WIDTH = 600
HEIGHT = 700
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Color palette (change these if you want a different vibe)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (52, 78, 91)
BUTTON_HOVER_COLOR = (84, 110, 122)

# Core game state (board contents, players, and status flags)
board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
player = 'X'  # Human player (you)
ai = 'O'      # Computer player
game_over = False
winner = None

# Create the main window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe - Minimax AI')
screen.fill(BG_COLOR)

# Fonts used for labels, messages, and buttons
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

# Draw the 3x3 grid lines
def draw_lines():
    # Horizontal separators
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)

    # Vertical separators
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, WIDTH), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, WIDTH), LINE_WIDTH)

# Render all X and O symbols currently on the board
def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'O':
                pygame.draw.circle(
                    screen,
                    CIRCLE_COLOR,
                    (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)),
                    CIRCLE_RADIUS,
                    CIRCLE_WIDTH
                )
            elif board[row][col] == 'X':
                pygame.draw.line(
                    screen,
                    CROSS_COLOR,
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE),
                    CROSS_WIDTH
                )
                pygame.draw.line(
                    screen,
                    CROSS_COLOR,
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    CROSS_WIDTH
                )

# Place a symbol for a given player on the board
def mark_square(row, col, player_symbol):
    board[row][col] = player_symbol

# True if the selected square is still empty
def available_square(row, col):
    return board[row][col] is None

# True if there are no empty squares left
def is_board_full():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                return False
    return True

# Check whether the given player just achieved a 3-in-a-row
def check_win(player_symbol):
    # Check rows
    for row in range(BOARD_ROWS):
        if board[row][0] == board[row][1] == board[row][2] == player_symbol:
            return True

    # Check columns
    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] == player_symbol:
            return True

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == player_symbol:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player_symbol:
        return True

    return False

# Return a list of all currently empty (row, col) positions
def get_empty_squares():
    empty = []
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                empty.append((row, col))
    return empty

# Core Minimax search: recursively explore moves so the AI plays perfectly.
# depth tracks how deep we are; is_maximizing tells whose turn it is.
# Returns a score from the AI's perspective (higher is better for AI).
def minimax(board_state, depth, is_maximizing):
    # Terminal state checks first: win, loss, or tie
    if check_win(ai):
        return 10 - depth
    if check_win(player):
        return depth - 10
    if is_board_full():
        return 0

    if is_maximizing:
        # AI's turn: try to maximize future outcome
        best_score = -math.inf
        for row, col in get_empty_squares():
            board_state[row][col] = ai
            score = minimax(board_state, depth + 1, False)
            board_state[row][col] = None
            best_score = max(score, best_score)
        return best_score
    else:
        # Human's turn: try to minimize AI's eventual score
        best_score = math.inf
        for row, col in get_empty_squares():
            board_state[row][col] = player
            score = minimax(board_state, depth + 1, True)
            board_state[row][col] = None
            best_score = min(score, best_score)
        return best_score

# Pick the (row, col) that gives the AI the best outcome
def best_move():
    best_score = -math.inf
    move = None

    for row, col in get_empty_squares():
        board[row][col] = ai
        score = minimax(board, 0, False)
        board[row][col] = None

        if score > best_score:
            best_score = score
            move = (row, col)

    return move

# Reset the board and status flags so a fresh game can start
def restart_game():
    global board, game_over, winner
    board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    game_over = False
    winner = None
    screen.fill(BG_COLOR)
    draw_lines()

# Draw the status area under the board: turn info, winner message, and restart button
def draw_status():
    pygame.draw.rect(screen, BG_COLOR, (0, WIDTH, WIDTH, HEIGHT - WIDTH))

    if game_over:
        if winner:
            if winner == player:
                text = font.render('You Win!', True, TEXT_COLOR)
            else:
                text = font.render('AI Wins!', True, TEXT_COLOR)
        else:
            text = font.render("It's a Tie!", True, TEXT_COLOR)

        # Restart button (clickable area)
        button_rect = pygame.Rect(WIDTH // 2 - 100, WIDTH + 50, 200, 50)
        mouse_pos = pygame.mouse.get_pos()

        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect, border_radius=10)

        button_text = small_font.render('Restart Game', True, TEXT_COLOR)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

        text_rect = text.get_rect(center=(WIDTH // 2, WIDTH + 20))
        screen.blit(text, text_rect)
    else:
        text = small_font.render('Your Turn (X)', True, TEXT_COLOR)
        text_rect = text.get_rect(center=(WIDTH // 2, WIDTH + 50))
        screen.blit(text, text_rect)

# Initial board and status draw
draw_lines()
draw_status()

# Main event loop: process input, run AI, and render updates
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouseX = event.pos[0]
            mouseY = event.pos[1]

            if mouseY < WIDTH:  # Inside the board area
                clicked_row = mouseY // SQUARE_SIZE
                clicked_col = mouseX // SQUARE_SIZE

                if available_square(clicked_row, clicked_col):
                    # Human move
                    mark_square(clicked_row, clicked_col, player)

                    if check_win(player):
                        game_over = True
                        winner = player
                    elif is_board_full():
                        game_over = True
                        winner = None
                    else:
                        # Let the AI think and move
                        ai_move = best_move()
                        if ai_move:
                            mark_square(ai_move[0], ai_move[1], ai)

                            if check_win(ai):
                                game_over = True
                                winner = ai
                            elif is_board_full():
                                game_over = True
                                winner = None

                    screen.fill(BG_COLOR)
                    draw_lines()
                    draw_figures()
                    draw_status()

        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            mouseX = event.pos[0]
            mouseY = event.pos[1]

            # Did the player click the restart button?
            button_rect = pygame.Rect(WIDTH // 2 - 100, WIDTH + 50, 200, 50)
            if button_rect.collidepoint((mouseX, mouseY)):
                restart_game()
                draw_status()

    pygame.display.update()

pygame.quit()
