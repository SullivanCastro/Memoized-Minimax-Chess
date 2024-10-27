import pygame
from abc import abstractmethod
from itertools import product
from numpy import sign


# Utility Functions
def is_within_board(coord):
    x, y = coord
    return 0 <= x <= 7 and 0 <= y <= 7


def is_move_valid(coord, board, piece, capture=False):
    x, y = coord
    if capture:
        return is_within_board(coord) and board[x, y].value * piece.value <= 0
    else:
        return is_within_board(coord) and board[x, y].value == 0


def different_colors(piece1, piece2):
    return piece1.value * piece2.value < 0


# Abstract Base Class for Pieces
class Piece:
    def __init__(self, color, x, y):
        self.color = str(color)
        self.position = (x, y)
        self.value = (color == "white") - (color == "black")

    @abstractmethod
    def possible_moves(self, board):
        pass

    def __call__(self, new_coord):
        self.position = new_coord

    def copy(self):
        return self.__class__(self.color, *self.position)
    
    def _is_empty(self):
        return self.value == 0


# Pawn Class
class Pawn(Piece):
    def __init__(self, color, x, y, moved=False):
        super().__init__(color, x, y)
        path = f"Pieces/pawn-{color}.png"
        self.name = f"Pawn {color}"
        self.image = pygame.image.load(path)
        self.moved = moved
        self.value *= 1

    def _promote(self):
        height = self.position[1]
        return height==0 if self.color=="white" else height==7

    def possible_moves(self, board):
        x, y = self.position
        moves = []

        # Forward move
        if is_move_valid((x, y - self.value), board, self):
            moves.append((x, y - self.value))

        # Double move if not moved
        if not self.moved and is_move_valid((x, y - 2 * self.value), board, self) and board[x, y - self.value]._is_empty():
            moves.append((x, y - 2 * self.value))

        # Diagonal captures
        for dx in [-1, 1]:
            if is_within_board((x + dx, y - self.value)) and board[x + dx, y - self.value].value * self.value < 0:
                moves.append((x + dx, y - self.value))

        return moves

    def __call__(self, new_coord, moved=False):
        new_x, new_y = new_coord
        return Pawn(self.color, new_x, new_y, moved)


# Rook Class
class Rook(Piece):
    def __init__(self, color, x, y, moved=False):
        super().__init__(color, x, y)
        path = f"Pieces/rook-{color}.png"
        self.name = f"Rook {color}"
        self.image = pygame.image.load(path)
        self.value *= 5
        self.moved = moved

    def possible_moves(self, board):
        x, y = self.position
        moves = []
        for dx, dy in product([-1, 0, 1], repeat=2):
            if abs(dx) + abs(dy) == 1:  # Horizontal or vertical only
                step_x, step_y = dx, dy
                while is_move_valid((x + step_x, y + step_y), board, self):
                    moves.append((x + step_x, y + step_y))
                    step_x += sign(dx)
                    step_y += sign(dy)
                
                # Check for capture
                if is_move_valid((x + step_x, y + step_y), board, self, True):
                    moves.append((x + step_x, y + step_y))

        return moves

    def __call__(self, new_coord, moved=False):
        new_x, new_y = new_coord
        return Rook(self.color, new_x, new_y, moved)


# Knight Class
class Knight(Piece):
    def __init__(self, color, x, y, moved=False):
        super().__init__(color, x, y)
        path = f"Pieces/knight-{color}.png"
        self.name = f"Knight {color}"
        self.image = pygame.image.load(path)
        self.value *= 3
        self.moved = False

    def possible_moves(self, board):
        x, y = self.position
        moves = [
            (x + 2 * k, y + q)
            for k, q in product([-1, 1], [-1, 1])
            if is_move_valid((x + 2 * k, y + q), board, self, True)
        ]
        moves += [
            (x + k, y + 2 * q)
            for k, q in product([-1, 1], [-1, 1])
            if is_move_valid((x + k, y + 2 * q), board, self, True)
        ]

        return moves

    def __call__(self, new_coord):
        new_x, new_y = new_coord
        return Knight(self.color, new_x, new_y)


# Bishop Class
class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        path = f"Pieces/bishop-{color}.png"
        self.name = f"Bishop {color}"
        self.image = pygame.image.load(path)
        self.value *= 3

    def possible_moves(self, board):
        x, y = self.position
        moves = []
        for dx, dy in product([-1, 1], repeat=2):  # Diagonal directions
            step_x, step_y = dx, dy
            while is_move_valid((x + step_x, y + step_y), board, self):
                moves.append((x + step_x, y + step_y))
                step_x += sign(dx)
                step_y += sign(dy)

            # Check for capture
            if is_move_valid((x + step_x, y + step_y), board, self, True):
                moves.append((x + step_x, y + step_y))

        return moves

    def __call__(self, new_coord):
        new_x, new_y = new_coord
        return Bishop(self.color, new_x, new_y)


# Queen Class
class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        path = f"Pieces/queen-{color}.png"
        self.name = f"Queen {color}"
        self.image = pygame.image.load(path)
        self.value *= 9

    def possible_moves(self, board):
        x, y = self.position
        moves = []
        for dx, dy in product([-1, 0, 1], repeat=2):
            step_x, step_y = dx, dy
            while is_move_valid((x + step_x, y + step_y), board, self):
                moves.append((x + step_x, y + step_y))
                step_x += sign(dx)
                step_y += sign(dy)

            # Check for capture
            if is_move_valid((x + step_x, y + step_y), board, self, True):
                moves.append((x + step_x, y + step_y))

        return moves

    def __call__(self, new_coord):
        new_x, new_y = new_coord
        return Queen(self.color, new_x, new_y)


# King Class
class King(Piece):
    def __init__(self, color, x, y, moved=False):
        super().__init__(color, x, y)
        path = f"Pieces/king-{color}.png"
        self.name = f"King {color}"
        self.image = pygame.image.load(path)
        self.value *= 90
        self.moved = moved

    def possible_moves(self, board):
        x, y = self.position
        moves = []
        for dx, dy in product([-1, 0, 1], repeat=2):
            if is_move_valid((x + dx, y + dy), board, self, True):
                moves.append((x + dx, y + dy))

        if not self.moved and board[x+1, y]._is_empty() and board[x+2, y]._is_empty():
            piece_roque = board[x+3, y]
            if "Rook" in piece_roque.name and not piece_roque.moved:
                moves.append((x+2, y))
        
        if not self.moved and board[x-1, y]._is_empty() and board[x-2, y]._is_empty() and board[x-3, y]._is_empty():
            piece_roque = board[x-4, y]
            if "Rook" in piece_roque.name and not piece_roque.moved:
                moves.append((x-2, y))

        return moves

    def __call__(self, new_coord, moved=False):
        new_x, new_y = new_coord
        return King(self.color, new_x, new_y, moved)


# Empty Space Class (for empty squares on the board)
class Empty(Piece):
    def __init__(self, x, y):
        super().__init__("white", x, y)
        self.name = "empty"
        self.value = 0

    def possible_moves(self, board):
        return []

    def __call__(self, new_coord):
        new_x, new_y = new_coord
        return Empty(new_x, new_y)
