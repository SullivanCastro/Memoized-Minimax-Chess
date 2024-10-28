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

# INITIAL_PIECES = np.array([
#     [0] * 8,
#     [0] * 8,
#     [0] * 8,
#     [0] * 8,
#     [0] * 8,
#     [0] * 8,
#     [0] * 8,
#     [0] * 8,
#     [0] * 8,
# ]).T

# INITIAL_PIECES[5, 5] = PieceValues.KING_WHITE.value
# INITIAL_PIECES[6, 2] = PieceValues.KING_BLACK.value
# INITIAL_PIECES[1, 1] = PieceValues.PAWN_WHITE.value

class Board:
    """
    Class to represent and manage the chessboard state, including piece positions,
    move tracking, and board evaluations for minimax calculations.
    """
    def __init__(self, initial_pieces: ArrayLike = INITIAL_PIECES, moved: ArrayLike=[], max_best_piece_coord_table: dict={}, max_best_move_table: dict = {}, max_eval_table: dict={}, min_best_piece_coord_table: dict={}, min_best_move_table: dict = {}, min_eval_table: dict={}, threat: bool = False, defense: bool = False) -> None:
        """
        Initialize the Board with pieces in starting positions, moved status for special moves,
        and an optional transposition table for memoization.

        Args:
            initial_pieces (np.array): Initial 2D array representing the piece layout.
            moved (np.array): 2D array tracking moved pieces for castling and pawn promotions.
            __best_piece_coord_table (dict): Optional dictionary for caching best piece coordinates.
            __best_move_table (dict): Optional dictionary for caching best move coordinates.
            eval_table (dict): Optional dictionary for caching board states to optimize calculations.
            threat (bool): If True, adds points for threatening opposing pieces.
            defense (bool): If True, reduces points for defending pieces.
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

        # Max evaluation table for memoization
        self.__max_best_piece_coord_table = max_best_piece_coord_table # Cache of best piece coordinates
        self.__max_best_move_table        = max_best_move_table # Cache of best move coordinates
        self.__max_eval_table             = max_eval_table # Cache of board states and scores

        # Min evaluation table for memoization
        self.__min_best_piece_coord_table = min_best_piece_coord_table # Cache of best piece coordinates
        self.__min_best_move_table        = min_best_move_table # Cache of best move coordinates
        self.__min_eval_table             = min_eval_table # Cache of board states and scores

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
    

    def _memoized(self, maximizing: bool, hash_key: str) -> dict:
        """
        Return the appropriate transposition table based on the current player.

        Args:
            maximizing (bool): True if maximizing player, False if minimizing.

        Returns:
            dict: Transposition table for the current player.
        """
        if maximizing:
            return hash_key in self.__max_eval_table
        else:
            return hash_key in self.__min_eval_table
        

    def _get_memoized(self, maximizing: bool, hash_key: str) -> tuple:
        """
        Retrieve the best piece and move coordinates and the evaluation score from the transposition table.

        Args:
            maximizing (bool): True if maximizing player, False if minimizing.
            hash_key (str): Hash value representing the current board layout.

        Returns:
            tuple: Best piece coordinates, best move coordinates, and the evaluation score.
        """
        if maximizing:
            return self.__max_best_piece_coord_table[hash_key], self.__max_best_move_table[hash_key], self.__max_eval_table[hash_key]
        else:
            return self.__min_best_piece_coord_table[hash_key], self.__min_best_move_table[hash_key], self.__min_eval_table[hash_key]
    
    
    def _fill_tables(self, maximizing:bool, hash_key: int, best_piece_coord: tuple, best_move: tuple, eval: float) -> None:
        """
        Fill the transposition tables with the best piece and move coordinates and the evaluation score.

        Args:
            hash_key (int): Hash value representing the current board layout.
            best_piece_coord (tuple): Best piece coordinates for the current player.
            best_move (tuple): Best move coordinates for the current player.
            eval (float): Evaluation score for the current board state.
        """
        if maximizing:
            self.__max_best_piece_coord_table[hash_key] = best_piece_coord
            self.__max_best_move_table[hash_key]        = best_move
            self.__max_eval_table[hash_key]             = eval
        else:
            self.__min_best_piece_coord_table[hash_key] = best_piece_coord
            self.__min_best_move_table[hash_key]        = best_move
            self.__min_eval_table[hash_key]             = eval


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
        new_board                     = Board(self.grid.copy(), self.__moved.copy(), self.__max_best_piece_coord_table, self.__max_best_move_table, self.__max_eval_table, self.__min_best_piece_coord_table, self.__min_best_move_table, self.__min_eval_table, self.__threat, self.__defense) 
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
        
        if self.is_checkmate(self.turn):
            score = 1e6
        elif self.is_checkmate(-self.turn):
            score = -1e6
        else:
            score = self._evaluate_board(threat=self.__threat, defense=self.__defense)

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
        self.__moved[x, y] = True
        self.__moved[new_x, new_y] = True

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
            if new_y == 0 and piece>0:
                self[new_x, new_y] = 90
            elif new_y == 7 and piece < 0:
                self[new_x, new_y] = -90
    

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
        
        hash_key = self._hash_state()
        if self._memoized(maximizing, hash_key):
            return self._get_memoized(maximizing, hash_key)
        
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
                        best_piece_coord = coord
                        best_move        = move
                        max_eval         = eval
                        self._fill_tables(False, hash_key, coord, move, eval)
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
                        best_piece_coord = coord
                        best_move        = move
                        min_eval         = eval
                        self._fill_tables(True, hash_key, coord, move, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cutoff
            return best_piece_coord, best_move, min_eval  # Return the best piece, its move, and the danger score


