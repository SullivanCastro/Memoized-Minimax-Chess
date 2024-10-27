
import numpy as np
from numpy.typing import ArrayLike
import pygame
from piece import get_image_by_value

# Global variables
MARGIN = 10
SIZE = 90
NUM_SQUARES = 8
BOARD_LENGTH = MARGIN + NUM_SQUARES * SIZE + MARGIN

class Screen:
    """
    Display the game board and pieces
    """

    def __init__(self):
        """
        Initialize the screen and board surface
        """
        self.__screen = pygame.display.set_mode((BOARD_LENGTH, BOARD_LENGTH))
    

    def _draw_game(self, board: ArrayLike) -> None:
        """
        Update locally the game board with the current state of the game

        Args:
            board (Board): The current game board

        Returns:
            None
        """
        for coord in zip(*np.where(board.grid != 0)):
            x, y = coord
            piece = board[coord]
            self.__screen.blit(pygame.image.load(get_image_by_value(piece)), 
                             (MARGIN + x * SIZE + SIZE / 4, MARGIN + y * SIZE + SIZE / 4))
    

    def draw_move(self, board: ArrayLike, list_move: list) -> None:
        """
        Display the legal moves for a selected piece

        Args:
            board (Board): The current game board
            list_move (list): List of legal moves for the selected piece

        Returns:
            None
        """
        self.draw_squares(board.turn)
        self._draw_game(board)
        for (x, y) in list_move:
            pygame.draw.circle(self.__screen, (255, 0, 0), 
                               (MARGIN + x * SIZE + SIZE / 2, MARGIN + y * SIZE + SIZE / 2), radius=SIZE / 8) 


    def draw_squares(self, turn) -> None:
        """
        Draw the chessboard squares
        """
        if turn % 2 == 0:
            self.__screen.fill((255, 255, 255, 255))
        for row in range(NUM_SQUARES):
            for col in range(NUM_SQUARES):
                color = (0, 168, 107) if (row + col) % 2 != 0 else (249, 228, 183)
                pygame.draw.rect(self.__screen, color, 
                                 (MARGIN + row * SIZE, MARGIN + col * SIZE, SIZE, SIZE))


    def draw_board(self, board: ArrayLike) -> None:
        """
        Draw the pieces on the board

        Args:
            board (Board): The current game board

        Returns:
            None
        """
        for coord in zip(*np.where(board.grid != 0)):
            x, y = coord
            if board[coord] != 0:
                image = pygame.image.load(get_image_by_value(board[coord]))
                self.__screen.blit(image, (MARGIN + x * SIZE + SIZE / 4, MARGIN + y * SIZE + SIZE / 4))


    def update(self, board: ArrayLike) -> None:
        """
        Update the screen with the current state of the game

        Args:
            board (Board): The current game board

        Returns:
            None
        """
        self.draw_squares(board.turn)
        self.draw_board(board)

