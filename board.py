import pygame
import numpy as np
from piece import *

# Global variables
margin = 10
square_size = 90
num_squares = 8
board_size = margin + num_squares * square_size + margin
pieces_list = [
    Rook("black", 0, 0), Knight("black", 1, 0), Bishop("black", 2, 0), Queen("black", 3, 0),
    King("black", 4, 0), Bishop("black", 5, 0), Knight("black", 6, 0), Rook("black", 7, 0),
    Pawn("black", 0, 1), Pawn("black", 1, 1), Pawn("black", 2, 1), Pawn("black", 3, 1),
    Pawn("black", 4, 1), Pawn("black", 5, 1), Pawn("black", 6, 1), Pawn("black", 7, 1),
    Pawn("white", 0, 6), Pawn("white", 1, 6), Pawn("white", 2, 6), Pawn("white", 3, 6),
    Pawn("white", 4, 6), Pawn("white", 5, 6), Pawn("white", 6, 6), Pawn("white", 7, 6),
    Rook("white", 0, 7), Knight("white", 1, 7), Bishop("white", 2, 7), Queen("white", 3, 7),
    King("white", 4, 7), Bishop("white", 5, 7), Knight("white", 6, 7), Rook("white", 7, 7)
]

# Initialize screen
screen = pygame.display.set_mode((board_size + 3 * margin, board_size))
square = pygame.Rect((margin + num_squares * square_size + 5, margin + num_squares * square_size + 5, margin + num_squares * square_size, margin + num_squares * square_size))
board_surface = pygame.Surface((board_size, board_size))


class ChessBoard:
    def __init__(self, pieces_list):
        self.board = np.array([[Empty(x, y) for x in range(8)] for y in range(8)])
        for piece in pieces_list:
            x, y = piece.position
            self.board[x, y] = piece
        self.machine_learning = np.array([[self.board[x, y].value for x in range(8)] for y in range(8)])
        self.turn = 0
        self.checkmate = False

    def current_turn_color(self):
        return "white" if self.turn % 2 == 0 else "black"

    def draw_pieces(self):
        for row in self.board:
            for piece in row:
                if piece.name != "empty":
                    x, y = piece.position
                    screen.blit(piece.image, (margin + x * square_size + square_size / 4, margin + y * square_size + square_size / 4))

    def draw_squares(self, screen):
        if self.turn % 2 == 0:
            screen.fill((255, 255, 255, 255))
        else:
            screen.fill((0, 0, 0, 0))

        for row in range(num_squares):
            for col in range(num_squares):
                color = (0, 168, 107) if (row + col) % 2 == 0 else (249, 228, 183)
                pygame.draw.rect(screen, color, (margin + row * square_size, margin + col * square_size, square_size, square_size))

        pygame.draw.line(screen, (0, 168, 107), (margin, margin), (margin + num_squares * square_size, margin))
        pygame.draw.line(screen, (0, 168, 107), (margin, margin), (margin, margin + num_squares * square_size))
        pygame.draw.line(screen, (0, 168, 107), (margin + num_squares * square_size, margin), (margin + num_squares * square_size, margin + num_squares * square_size))
        pygame.draw.line(screen, (0, 168, 107), (margin, margin + num_squares * square_size), (margin + num_squares * square_size, margin + num_squares * square_size))

    def update(self, screen):
        self.draw_squares(screen)
        self.draw_pieces()

    def valid_moves(self, piece):
        moves = []

        if piece.name.startswith("pawn"):
            x, y = piece.position
            direction = piece.value
            if y == 6 and direction > 0 or y == 1 and direction < 0:
                moves.append((x, y + direction))
                moves.append((x, y + 2 * direction))
            elif inside((x, y + direction)) and self.board[x, y + direction].value == 0:
                moves.append((x, y + direction))
            for dx in [-1, 1]:
                if inside((x + dx, y + direction)) and self.board[x + dx, y + direction].value * piece.value < 0:
                    moves.append((x + dx, y + direction))

        if piece.name.startswith("rook"):
            x, y = piece.position
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                while inside((nx, ny)) and self.board[nx, ny].value == 0:
                    moves.append((nx, ny))
                    nx, ny = nx + dx, ny + dy
                if inside((nx, ny)) and self.board[nx, ny].value * piece.value < 0:
                    moves.append((nx, ny))

        if piece.name.startswith("bishop"):
            x, y = piece.position
            for dx, dy in product([-1, 1], [-1, 1]):
                nx, ny = x + dx, y + dy
                while inside((nx, ny)) and self.board[nx, ny].value == 0:
                    moves.append((nx, ny))
                    nx, ny = nx + dx, ny + dy
                if inside((nx, ny)) and self.board[nx, ny].value * piece.value < 0:
                    moves.append((nx, ny))

        if piece.name.startswith("queen"):
            moves.extend(self.valid_moves(self.board[x, y]))  # Rook moves + bishop moves
            moves.extend(self.valid_moves(self.board[x, y]))  # Reuse bishop method for queen moves

        if piece.name.startswith("knight"):
            x, y = piece.position
            for dx, dy in product([-2, 2], [-1, 1]):
                if inside((x + dx, y + dy)) and self.board[x + dx, y + dy].value * piece.value <= 0:
                    moves.append((x + dx, y + dy))

        if piece.name.startswith("king"):
            x, y = piece.position
            for dx, dy in product([-1, 0, 1], [-1, 0, 1]):
                if inside((x + dx, y + dy)) and self.board[x + dx, y + dy].value * piece.value <= 0:
                    moves.append((x + dx, y + dy))

        return moves

    def is_check(self, piece):
        x_king, y_king = next((x, y) for x in range(8) for y in range(8) if self.board[x, y].name == "king " + piece.color)
        for row in range(8):
            for col in range(8):
                moves = self.valid_moves(self.board[row, col])
                if self.board[row, col].value * self.board[x_king, y_king].value < 0 and (x_king, y_king) in moves:
                    return True
        return False

# Initialize the board
main_board = ChessBoard(pieces_list)
