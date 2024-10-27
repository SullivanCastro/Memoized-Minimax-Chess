from numpy.typing import ArrayLike

def is_within_board(coord: tuple[int, int]) -> bool:
    """
    Check that the coordinates are within the board

    Args:
        coord (tuple): The coordinates to check

    Returns:
        bool: True if the coordinates are within the board, False otherwise
    """
    x, y = coord
    return 0 <= x <= 7 and 0 <= y <= 7

#
def is_move_valid(coord, board: ArrayLike, piece_value: float, capture: bool = False) -> bool:
    """
    Check if a move is valid

    Args:
        coord (tuple): The coordinates of the move
        board (ArrayLike): The current game board
        piece_value (int): The piece value
        capture (bool): Whether the move is a capture

    Returns:
        bool: True if the move is valid, False otherwise
    """
    x, y = coord
    if capture:
        return is_within_board(coord) and board[x, y] * piece_value <= 0
    else:
        return is_within_board(coord) and board[x, y] == 0