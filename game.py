import pygame
import numpy as np
from board_ia import Board
from screen import Screen, MARGIN, SIZE


pygame.init()


def game(depth: int=3, threat: bool = False, defense: bool = False) -> None:
    """
    Launch the game with the specified depth for the minimax algorithm. I personnally recommand a depth of 3.

    Args:
        depth (int): The depth of the minimax algorithm
    
    Returns:
        None
    """
    # Initialize game variables
    running = True
    turn = 1  # 1 for white, -1 for black

    main_board = Board(threat=threat, defense=defense)
    screen = Screen()

    # Game loop
    while running and main_board.turn <= 150 and abs(main_board.checkmate) <= 3:

        # Update the board display
        screen.update(main_board)
        
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if turn == 1 and event.type == pygame.MOUSEBUTTONDOWN:  # Player's turn
                x1, y1 = event.pos
                x1, y1 = (x1 - MARGIN) // SIZE, (y1 - MARGIN) // SIZE  # Convert mouse click to board coordinates

                if x1 < 0 or x1 >= 8 or y1 < 0 or y1 >= 8:
                    print("Out of bounds")
                    continue

                if main_board.grid[x1, y1] != 0 and main_board.grid[x1, y1] * turn > 0:
                    click = False
                    
                    # Get legal moves for the selected piece
                    possible_moves = main_board.possible_moves((x1, y1))
                    
                    # Draw legal moves on the board
                    screen.draw_move(main_board, possible_moves)
                    pygame.display.flip()

                    # Handle second click for destination
                    while not click:
                        for event2 in pygame.event.get():
                            if event2.type == pygame.MOUSEBUTTONDOWN:
                                x2, y2 = event2.pos
                                x2, y2 = int((x2 - MARGIN) // SIZE), int((y2 - MARGIN) // SIZE)

                                if (x2, y2) in possible_moves:

                                    # Update the board with the move
                                    main_board.move((x1, y1), (x2, y2))
                                    click = True

                                    main_board.turn += 1
                                    main_board.checkmate = 0
                                    turn *= -1  # Switch turns
                                    screen.update(main_board)

                                else:
                                    print("Invalid move")
                                    click = True

                elif main_board.grid[x1, y1] == 0:
                    print("Empty square selected")
                else:
                    print("Not your pieces")

                if main_board.is_checkmate(-turn):
                    print("Checkmate!")
                    main_board.checkmate = 5

            # AI Turn
            elif turn == -1:
                print("Calculating optimal move...")
                coord_piece_ai, new_position, danger = main_board.minimax(depth, -np.inf, np.inf, False)

                if danger == np.inf:
                    main_board.checkmate = -5
                else:
                    main_board.move(coord_piece_ai, new_position)
                    print('Calculation complete!')
                    screen.update(main_board)

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Play a game of chess against the AI")
    parser.add_argument("--depth", type=int, default=3, help="Depth of the minimax algorithm (default: 3)")
    parser.add_argument("--threat", action="store_true", help="Enable threat heuristic (default: False)")
    parser.add_argument("--defense", action="store_true", help="Enable mobility heuristic (default: False)")

    args = parser.parse_args()

    game(args.depth, args.threat, args.defense)