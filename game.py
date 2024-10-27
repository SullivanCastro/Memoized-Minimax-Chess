from board_ia import *
import pygame
import numpy as np
import time

pygame.init()

# Initialize game variables
running = True
turn = 1  # 1 for white, -1 for black

main_board = Board(initial_pieces)

# Game loop
while running and main_board.turn <= 150 and abs(main_board.checkmate) <= 3:

    # Update the board display
    main_board.update(screen)
    
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if turn == 1 and event.type == pygame.MOUSEBUTTONDOWN:  # Player's turn
            x1, y1 = event.pos
            x1, y1 = (x1 - MARGIN) // SIZE, (y1 - MARGIN) // SIZE  # Convert mouse click to board coordinates

            if main_board.grid[x1, y1].name != "Empty" and main_board.grid[x1, y1].value * turn > 0:
                click = False
                piece = main_board.grid[x1, y1]
                
                # Get legal moves for the selected piece
                possible_moves = main_board.possible_moves(piece)
                
                # Draw legal moves on the board
                main_board.draw_move(screen, possible_moves)
                pygame.display.flip()

                # Handle second click for destination
                while not click:
                    for event2 in pygame.event.get():
                        if event2.type == pygame.MOUSEBUTTONDOWN:
                            x2, y2 = event2.pos
                            x2, y2 = int((x2 - MARGIN) // SIZE), int((y2 - MARGIN) // SIZE)

                            if (x2, y2) in possible_moves:

                                # Animate the move
                                main_board.animate(screen, piece, (x2, y2))

                                # Update the board with the move
                                main_board.move(piece, (x2, y2))
                                click = True

                                main_board.turn += 1
                                main_board.checkmate = 0
                                turn *= -1  # Switch turns
                                main_board.update(screen)

                            else:
                                print("Invalid move")
                                click = True

            elif main_board.grid[x1, y1].name == "Empty":
                print("Empty square selected")
            else:
                print("Not your pieces")

            if main_board.is_checkmate(-turn):
                print("Checkmate!")
                main_board.checkmate = 5

        # AI Turn
        elif turn == -1:
            print("Calculating optimal move...")
            piece_ai, new_position, danger = main_board.minimax(3, -np.inf, np.inf, False)

            if danger == np.inf:
                main_board.checkmate = -5
            else:
                main_board.animate(screen, piece_ai, new_position)
                main_board.move(piece_ai, new_position)
                print('Calculation complete!')
                main_board.update(screen)

            main_board.turn += 1
            main_board.checkmate = 0
            turn *= -1  # Switch turns

            if main_board.is_checkmate(-turn):
                print("Checkmate!")
                main_board.checkmate = -5

    pygame.display.flip()

# End of game: Determine winner
total_score = main_board.score()

if main_board.checkmate <= -3 or total_score > 0:
    print(f"White wins on turn {main_board.turn}")
elif main_board.checkmate >= 3 or total_score < 0:
    print(f"Black wins on turn {main_board.turn}")
else:
    print("Draw")

pygame.quit()
