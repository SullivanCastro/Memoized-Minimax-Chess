import numpy as np
from numpy.typing import ArrayLike
from piece import MovePieces, PieceValues

# List of initial pieces
INITIAL_PIECES = np.array([
    [PieceValues.ROOK_BLACK.value, PieceValues.KNIGHT_BLACK.value, PieceValues.BISHOP_BLACK.value, PieceValues.QUEEN_BLACK.value,
     PieceValues.KING_BLACK.value, PieceValues.BISHOP_BLACK.value, PieceValues.KNIGHT_BLACK.value, PieceValues.ROOK_BLACK.value],
    [PieceValues.PAWN_BLACK.value] * 8,
    [0] * 8,
    [0] * 8,
    [0] * 8,
    [0] * 8,
    [PieceValues.PAWN_WHITE.value] * 8,
    [PieceValues.ROOK_WHITE.value, PieceValues.KNIGHT_WHITE.value, PieceValues.BISHOP_WHITE.value, PieceValues.QUEEN_WHITE.value,
     PieceValues.KING_WHITE.value, PieceValues.BISHOP_WHITE.value, PieceValues.KNIGHT_WHITE.value, PieceValues.ROOK_WHITE.value]
]).T

class Board:
    """
    Class to represent and manage the chessboard state, including piece positions,
    move tracking, and board evaluations for minimax calculations.
    """
    def __init__(self, initial_pieces: ArrayLike = INITIAL_PIECES, moved: ArrayLike=[], transposition_table: dict={}, threat: bool = False, defense: bool = False) -> None:
        """
        Initialize the Board with pieces in starting positions, moved status for special moves,
        and an optional transposition table for memoization.

        Args:
            initial_pieces (np.array): Initial 2D array representing the piece layout.
            transposition_table (dict): Optional dictionary for caching board states to optimize calculations.
        """
        # Board grid layout and tracking moved pieces for castling and pawn promotions
        self.grid = initial_pieces.copy()
        if len(moved) != 0:
            self.__moved = moved
        else:
            self.__moved = ~np.isin(abs(self.grid), 
                            [PieceValues.KING_WHITE.value, 
                            PieceValues.ROOK_WHITE.value, 
                            PieceValues.PAWN_WHITE.value])
        self.turn = 0  # Tracks the current turn (0: White, 1: Black)
        self.checkmate = False # Checkmate status flag
        self.__transposition_table = transposition_table # Cache of board states and scores
        self.__threat = threat
        self.__defense = defense


    def __getitem__(self, key: tuple) -> None:
        """
        Allow grid access through board[key].

        Args:
            key (tuple): Position on the grid as (x, y) coordinates.

        Returns:
            int: Piece value at the given position.
        """
        return self.grid[key]
    

    def __setitem__(self, key: tuple, value: float) -> None:
        """
        Allow grid modification by setting board[key] = value.

        Args:
            key (tuple): Position on the grid as (x, y) coordinates.
            value (int): Piece value to be placed at the position.
        """
        self.grid[key] = value


    def _hash_state(self) -> int:
        """
        Generate a unique hash for the current board state to use in the transposition table.

        Returns:
            int: Hash value representing the current board layout.
        """
        return hash(str(self.grid.flatten()))


    def _evaluate_board(self, threat: bool = False, defense: bool = False) -> float:
        """
        Calculate a score based on current board positions, optionally considering threat and defense.

        Args:
            threat (bool): If True, adds points for threatening opposing pieces.
            defense (bool): If True, reduces points for defending pieces.

        Returns:
            float: Calculated board score.
        """
        score = self.grid.sum()

         # If threat assessment is enabled, adds a small score boost for threatening opponent pieces
        if threat:
            for coord in zip(*np.where(self.grid * self.turn > 10)):
                possible_moves = self.possible_moves(coord)
                for move in possible_moves:
                    if self[move] < 0:
                        score += abs(self[move]) / 10
            
        # If defense assessment is enabled, when a piece is threatened
        if defense:
            for coord in zip(*np.where(self.grid * self.turn < -10)):
                possible_moves = self.possible_moves(coord)
                for move in possible_moves:
                    if self[move] > 0:
                        score -= abs(self[move]) / 10

        return score


    def _copy(self) -> None:
        """
        Create a deep copy of the current board instance, including all necessary attributes.

        Returns:
            Board: New Board instance with the same layout and state.
        """
        new_board                     = Board(self.grid, self.__moved.copy(), self.__transposition_table, self.__threat, self.__defense) 
        new_board.turn                = self.turn
        new_board.checkmate           = self.checkmate
        return new_board


    def _is_check(self, color: int) -> bool:
        """
        Determine if the specified color is in check.

        Args:
            color (int): Color indicator, positive for White, negative for Black.

        Returns:
            bool: True if color's king is in check, False otherwise.
        """
        king_pos = np.where(self.grid * color == 900)
        
        for coord in zip(*np.where(self.grid * color < 0)):
            if king_pos in MovePieces.possible_moves(self.grid, self.__moved, coord):
                return True
        return False
    

    def is_checkmate(self, color: int) -> bool:
        """
        Determine if the specified color is in checkmate.

        Args:
            color (int): Color indicator, positive for White, negative for Black.

        Returns:
            bool: True if color's king is in checkmate, False otherwise.
        """
        for coord in zip(*np.where(self.grid * color < 0)):
            for move in self.possible_moves(coord):
                new_board = self._copy()
                new_board.move(coord, move)
                if not new_board._is_check(color):
                    return False
        return True
    
    
    def possible_moves(self, piece_coord: tuple) -> list:
        """
        Generate legal moves for a piece at the given coordinates.

        Args:
            piece_coord (tuple): Coordinates of the piece to move.

        Returns:
            list: List of legal move coordinates.
        """
        possible_moves_theo = MovePieces.possible_moves(self.grid, self.__moved, piece_coord)
        possible_moves_real = []
        for new_coord in possible_moves_theo:
            board_virtual = self._copy()
            board_virtual.move(piece_coord, new_coord)
            if not board_virtual._is_check(np.sign(self[piece_coord])):
                possible_moves_real.append(new_coord)
        return possible_moves_real


    def score(self) -> float:
        """
        Return the board evaluation score, using the transposition table for memoization.

        Returns:
            float: Board evaluation score.
        """
        hash_key = self._hash_state()
        
        if hash_key in self.__transposition_table:
            return self.__transposition_table[hash_key]
        
        if self.is_checkmate(self.turn):
            score = 1e6
        elif self.is_checkmate(-self.turn):
            score = -1e6
        else:
            score = self._evaluate_board(threat=self.__threat, defense=self.__defense)

        self.__transposition_table[hash_key] = score
        return score
    

    def move(self, coord: tuple, new_coord: tuple) -> None:
        """
        Move a piece from the given coordinates to the new coordinates, updating the board state.

        Args:
            coord (tuple): Current piece coordinates.
            new_coord (tuple): New piece coordinates.
        
        Returns:
            None
        """
        piece        = self[coord]
        x, y         = coord
        new_x, new_y = new_coord

        self[new_x, new_y] = self[x, y]
        self[x, y] = 0
        self.__moved[(x, y)] = True

        if abs(piece) == 900 and abs(new_x - x) == 2:
            if new_x > x:
                self[new_x - 1, new_y] = self[new_x + 1, new_y]
                self[new_x + 1, new_y] = 0
                self.__moved[(new_x+1, new_y)] = True
            else:
                self[new_x + 1, new_y] = self[new_x - 2, new_y]
                self[new_x - 2, new_y] = 0
                self.__moved[(new_x-2, new_y)] = True

        if abs(piece) == 10:
            if y==0 and piece>0:
                self[new_x, new_y] = 9
            elif y==7 and piece<0:
                self[new_x, new_y] = -9
    

    def minimax(self, depth: int, alpha: float, beta: float, maximizing: bool) -> tuple:
        """
        Minimax algorithm with alpha-beta pruning to find the best move for the current player.

        Args:
            depth (int): Maximum depth to search in the game tree.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
            maximizing (bool): True if maximizing player, False if minimizing.

        Returns:
            tuple: Best piece coordinates, best move coordinates, and the evaluation score.
        """
        if depth == 0 or self.is_checkmate(self.turn):
            score = self.score()
            return None, None, score  # No piece or move, just the evaluation (danger)
        
        best_move = None
        best_piece_coord = None
        if maximizing:
            max_eval = -np.inf
            for coord in zip(*np.where(self.grid > 0)):  # assuming positive values for maximizing player
                for move in self.possible_moves(coord):
                    new_board = self._copy()  # clone the board before applying the move
                    new_board.move(coord, move)  
                    _, _, eval = new_board.minimax(depth - 1, alpha, beta, False)
                    if eval > max_eval:
                        max_eval = eval
                        best_piece_coord = coord
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Beta cutoff
            return best_piece_coord, best_move, max_eval  # Return the best piece, its move, and the danger score
        else:
            min_eval = np.inf
            for coord in zip(*np.where(self.grid < 0)):  # assuming negative values for minimizing player
                for move in self.possible_moves(coord):
                    new_board = self._copy()  # clone the board before applying the move
                    new_board.move(coord, move)
                    _, _, eval = new_board.minimax(depth - 1, alpha, beta, True)
                    if eval < min_eval:
                        min_eval = eval
                        best_piece_coord = coord
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cutoff
            return best_piece_coord, best_move, min_eval  # Return the best piece, its move, and the danger score


