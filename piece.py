from abc import abstractmethod
from enum import Enum
from itertools import product
import numpy as np
from numpy.typing import ArrayLike 
from utils import is_within_board, is_move_valid


class ImagePieces(Enum):
    """
    Enum class for the images of the chess pieces
    """
    PAWN_BLACK = "Pieces/pawn-black.png"
    PAWN_WHITE = "Pieces/pawn-white.png"

    BISHOP_BLACK = "Pieces/bishop-black.png"
    BISHOP_WHITE = "Pieces/bishop-white.png"

    KNIGHT_BLACK = "Pieces/knight-black.png"
    KNIGHT_WHITE = "Pieces/knight-white.png"

    ROOK_BLACK = "Pieces/rook-black.png"
    ROOK_WHITE = "Pieces/rook-white.png"

    QUEEN_BLACK = "Pieces/queen-black.png"
    QUEEN_WHITE = "Pieces/queen-white.png"

    KING_BLACK = "Pieces/king-black.png"
    KING_WHITE = "Pieces/king-white.png"


class PieceValues(Enum):
    """
    Enum class for the values of the chess pieces
    """
    PAWN_BLACK = -10
    PAWN_WHITE = 10

    BISHOP_BLACK = -30
    BISHOP_WHITE = 30

    KNIGHT_BLACK = -40
    KNIGHT_WHITE = 40

    ROOK_BLACK = -50
    ROOK_WHITE = 50

    QUEEN_BLACK = -90
    QUEEN_WHITE = 90

    KING_BLACK = -900
    KING_WHITE = 900


def get_image_by_value(value: int) -> str:
    """
    Retrieve the image path for a given piece value

    Args:
        value (int): The value of the piece

    Returns:
        str: The path to the image of the piece
    """
    value_to_image = {
        PieceValues.PAWN_BLACK.value: ImagePieces.PAWN_BLACK.value,
        PieceValues.PAWN_WHITE.value: ImagePieces.PAWN_WHITE.value,
        PieceValues.BISHOP_BLACK.value: ImagePieces.BISHOP_BLACK.value,
        PieceValues.BISHOP_WHITE.value: ImagePieces.BISHOP_WHITE.value,
        PieceValues.KNIGHT_BLACK.value: ImagePieces.KNIGHT_BLACK.value,
        PieceValues.KNIGHT_WHITE.value: ImagePieces.KNIGHT_WHITE.value,
        PieceValues.ROOK_BLACK.value: ImagePieces.ROOK_BLACK.value,
        PieceValues.ROOK_WHITE.value: ImagePieces.ROOK_WHITE.value,
        PieceValues.QUEEN_BLACK.value: ImagePieces.QUEEN_BLACK.value,
        PieceValues.QUEEN_WHITE.value: ImagePieces.QUEEN_WHITE.value,
        PieceValues.KING_BLACK.value: ImagePieces.KING_BLACK.value,
        PieceValues.KING_WHITE.value: ImagePieces.KING_WHITE.value,
    }

    return value_to_image.get(value, None)


class MovePieces:
    """
    Abstract methods for the possible moves of the chess pieces
    """
    

    @abstractmethod
    def _pawn_move(board: ArrayLike, moved: ArrayLike, x: int, y: int) -> list:
        """
        Get the possible moves for a pawn

        Args:
            board (ArrayLike): The current game board
            moved (ArrayLike): The array of moved pieces
            x (int): The x-coordinate of the pawn
            y (int): The y-coordinate of the pawn
        
        Returns:
            list: List of possible moves for the pawn
        """
        value = board[x, y]
        moves = []
        dir = np.sign(value)

        # Forward move
        if is_move_valid((x, y - dir), board, value):
            moves.append((x, y - dir))

        # Double move if not moved
        if not moved[x,y] and is_move_valid((x, y - 2 * dir), board, value) and board[x, y - dir]==0:
            moves.append((x, y - 2 * dir))

        # Diagonal captures
        for dx in [-1, 1]:
            if is_within_board((x + dx, y - dir)) and board[x + dx, y - dir] * value < 0:
                moves.append((x + dx, y - dir))

        return moves
    
    
    @abstractmethod
    def _rook_move(board: ArrayLike, moved: ArrayLike, x: int, y: int) -> list:
        """
        Get the possible moves for a rook

        Args:
            board (ArrayLike): The current game board
            moved (ArrayLike): The array of moved pieces
            x (int): The x-coordinate of the rook
            y (int): The y-coordinate of the rook

        Returns:
            list: List of possible moves for the rook
        """
        value = board[x, y]
        moves = []
        for dx, dy in product([-1, 0, 1], repeat=2):
            if dx == dy == 0:
                continue
            if abs(dx) + abs(dy) == 1:  # Horizontal or vertical only
                step_x, step_y = dx, dy
                while is_move_valid((x + step_x, y + step_y), board, value):
                    moves.append((x + step_x, y + step_y))
                    step_x += np.sign(dx)
                    step_y += np.sign(dy)
                
                # Check for capture
                if is_move_valid((x + step_x, y + step_y), board, value, True):
                    moves.append((x + step_x, y + step_y))

        return moves
    

    @abstractmethod
    def _knight_move(board: ArrayLike, moved: ArrayLike, x: int, y: int) -> list:
        """
        Get the possible moves for a knight

        Args:
            board (ArrayLike): The current game board
            moved (ArrayLike): The array of moved pieces
            x (int): The x-coordinate of the knight
            y (int): The y-coordinate of the knight

        Returns:
            list: List of possible moves for the knight
        """
        value = board[x, y]
        moves = [
            (x + 2 * k, y + q)
            for k, q in product([-1, 1], [-1, 1])
            if is_move_valid((x + 2 * k, y + q), board, value, True)
        ]
        moves += [
            (x + k, y + 2 * q)
            for k, q in product([-1, 1], [-1, 1])
            if is_move_valid((x + k, y + 2 * q), board, value, True)
        ]

        return moves
    

    @abstractmethod
    def _bishop_move(board: ArrayLike, moved: ArrayLike, x: int, y: int) -> list:
        """
        Get the possible moves for a bishop

        Args:
            board (ArrayLike): The current game board
            moved (ArrayLike): The array of moved pieces
            x (int): The x-coordinate of the bishop
            y (int): The y-coordinate of the bishop

        Returns:
            list: List of possible moves for the bishop
        """
        value = board[x, y]
        moves = []
        for dx, dy in product([-1, 1], repeat=2):  # Diagonal directions
            step_x, step_y = dx, dy
            while is_move_valid((x + step_x, y + step_y), board, value):
                moves.append((x + step_x, y + step_y))
                step_x += np.sign(dx)
                step_y += np.sign(dy)

            # Check for capture
            if is_move_valid((x + step_x, y + step_y), board, value, True):
                moves.append((x + step_x, y + step_y))

        return moves
    

    @abstractmethod
    def _queen_move(board: ArrayLike, moved: ArrayLike, x: int, y: int) -> list:
        """
        Get the possible moves for a queen

        Args:
            board (ArrayLike): The current game board
            moved (ArrayLike): The array of moved pieces
            x (int): The x-coordinate of the queen
            y (int): The y-coordinate of the queen

        Returns:
            list: List of possible moves for the queen
        """
        value = board[x, y]
        moves = []
        for dx, dy in product([-1, 0, 1], repeat=2):
            if dx == dy == 0:
                continue
            step_x, step_y = dx, dy
            while is_move_valid((x + step_x, y + step_y), board, value):
                moves.append((x + step_x, y + step_y))
                step_x += np.sign(dx)
                step_y += np.sign(dy)

            # Check for capture
            if is_move_valid((x + step_x, y + step_y), board, value, True):
                moves.append((x + step_x, y + step_y))

        return moves
    

    @abstractmethod
    def _king_move(board: ArrayLike, moved: ArrayLike, x: int, y: int) -> list:
        """
        Get the possible moves for a king

        Args:
            board (ArrayLike): The current game board
            moved (ArrayLike): The array of moved pieces
            x (int): The x-coordinate of the king
            y (int): The y-coordinate of the king

        Returns:
            list: List of possible moves for the king
        """
        value = board[x, y]
        moves = []
        for dx, dy in product([-1, 0, 1], repeat=2):
            if dx == dy == 0:
                continue
            if is_move_valid((x + dx, y + dy), board, value, True):
                moves.append((x + dx, y + dy))

        # Castling left
        if not moved[x, y] and (board[x+1:x+3, y]==0).all() and not moved[x+3, y]:
            moves.append((x+2, y))
        
        # Castling right
        if not moved[x,y] and (board[x-3:x, y]==0).all() and not moved[x-4, y]:
            moves.append((x-2, y))

        return moves
    
    
    @abstractmethod
    def possible_moves(board: ArrayLike, moved: ArrayLike, coord: tuple[int, int]) -> list:
        """
        Map the piece value to the corresponding move

        Args:
            board (ArrayLike): The current game board
            moved (ArrayLike): The array of moved pieces
            coord (tuple): The coordinates of the piece

        Returns:
            list: List of possible moves for the piece
        """
        piece_value = board[coord]
        if   abs(piece_value) == 10:
            return MovePieces._pawn_move(board, moved, *coord)
        elif abs(piece_value) == 30:
            return MovePieces._bishop_move(board, moved, *coord)
        elif abs(piece_value) == 40:
            return MovePieces._knight_move(board, moved, *coord)
        elif abs(piece_value) == 50:
            return MovePieces._rook_move(board, moved, *coord)
        elif abs(piece_value) == 90:
            return MovePieces._queen_move(board, moved, *coord)
        elif abs(piece_value) == 900:
            return MovePieces._king_move(board, moved, *coord)
        
        
