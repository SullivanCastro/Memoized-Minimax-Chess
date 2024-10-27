import numpy as np
import time
import pygame
from piece import Rook, Knight, Bishop, Queen, King, Pawn, Empty
from functools import lru_cache

# Global variables
MARGIN = 10
SIZE = 90
NUM_SQUARES = 8
BOARD_LENGTH = MARGIN + NUM_SQUARES * SIZE + MARGIN

# List of initial pieces
initial_pieces = [
    Rook("black", 0, 0), Knight("black", 1, 0), Bishop("black", 2, 0), Queen("black", 3, 0),
    King("black", 4, 0), Bishop("black", 5, 0), Knight("black", 6, 0), Rook("black", 7, 0),
    Pawn("black", 0, 1), Pawn("black", 1, 1), Pawn("black", 2, 1), Pawn("black", 3, 1),
    Pawn("black", 4, 1), Pawn("black", 5, 1), Pawn("black", 6, 1), Pawn("black", 7, 1),
    Pawn("white", 0, 6), Pawn("white", 1, 6), Pawn("white", 2, 6), Pawn("white", 3, 6),
    Pawn("white", 4, 6), Pawn("white", 5, 6), Pawn("white", 6, 6), Pawn("white", 7, 6),
    Rook("white", 0, 7), Knight("white", 1, 7), Bishop("white", 2, 7), Queen("white", 3, 7),
    King("white", 4, 7), Bishop("white", 5, 7), Knight("white", 6, 7), Rook("white", 7, 7)
]

screen = pygame.display.set_mode((BOARD_LENGTH, BOARD_LENGTH))
board_surface = pygame.Surface((BOARD_LENGTH, BOARD_LENGTH))

def board_value(board):
    return np.array([[piece.value for piece in row] for row in board])

class Board:
    def __init__(self, pieces, transposition_table={}):
        self.grid = np.array([[Empty(x, y) for x in range(8)] for y in range(8)])
        for piece in pieces:
            x, y = piece.position
            self.grid[x, y] = piece
        self.turn = 0
        self.checkmate = False
        self.transposition_table = transposition_table

    def __getitem__(self, key):
        return self.grid[key]
    
    def __setitem__(self, key, value):
        self.grid[key] = value

    def reset(self, pieces):
        self.grid = np.array([[Empty(x, y) for x in range(8)] for y in range(8)])
        for piece in pieces:
            x, y = piece.position
            self.grid[x, y] = piece
        self.turn = 0
        self.checkmate = False

    def hash_state(self):
        return hash(str([piece.value for piece in self.grid.flatten()]))

    def evaluate_board(self, threat=False, defense=False):
        score = board_value(self.grid).sum()

        # Adding a threat score
        if threat:
            for x, y in zip(*np.where(board_value(self.grid) * self.turn > 10)):
                piece = self.grid[x, y]
                possible_moves = self.possible_moves(piece)
                for move in possible_moves:
                    if self[move].value < 0:
                        score += abs(self[move].value) / 10
            
        # Adding a defense score
        if defense:
            for x, y in zip(*np.where(board_value(self.grid) * self.turn < -10)):
                piece = self.grid[x, y]
                possible_moves = self.possible_moves(piece)
                for move in possible_moves:
                    if self[move].value > 0:
                        score -= abs(self[move].value) / 10

        return score

    def current_color(self):
        return "white" if self.turn % 2 == 0 else "black"
    
    def drawGame(self, screen):
        for row in self.grid:
            for piece in row:
                if piece.name != "empty":
                    x, y = piece.position
                    screen.blit(piece.image, (MARGIN + x * SIZE + SIZE / 4, MARGIN + y * SIZE + SIZE / 4))
                else:
                    pass
    
    def draw_move(self, screen, list_move):
        eps = 10 ** (-2)
        self.draw_squares(screen)
        self.drawGame(screen)
        for (x, y) in list_move:
            # pygame.draw.rect(screen, (255, 0, 0),
            #                  (MARGIN + x * SIZE + eps, MARGIN + y * SIZE + eps, SIZE - 2 * eps, SIZE - 2 * eps))
            pygame.draw.circle(screen, (255, 0, 0), center=(MARGIN + x * SIZE + eps + SIZE/2, MARGIN + y * SIZE + eps + SIZE/2), radius=SIZE/8)

    def draw_board(self, screen):
        for row in self.grid:
            for piece in row:
                if piece.name != "empty":
                    x, y = piece.position
                    screen.blit(piece.image, (MARGIN + x * SIZE + SIZE / 4, MARGIN + y * SIZE + SIZE / 4))


    def animate(self, screen, piece, new_coord):
        n = 100
        x, y = piece.position
        new_x, new_y = new_coord
        dx = (new_x - x) / n
        dy = (new_y - y) / n
        for k in range(n + 1):
            piece.position = (x + dx * k, y + dy * k)
            self.update(screen)
            pygame.display.flip()
            time.sleep(0.001)
        piece.position = (x, y)


    def draw_squares(self, screen):
        screen.fill((255, 255, 255) if self.turn % 2 == 0 else (0, 0, 0))
        for row in range(NUM_SQUARES):
            for col in range(NUM_SQUARES):
                color = (0, 168, 107) if (row + col) % 2 != 0 else (249, 228, 183)
                pygame.draw.rect(screen, color, (MARGIN + row * SIZE, MARGIN + col * SIZE, SIZE, SIZE))

    def update(self, screen):
        self.draw_squares(screen)
        self.draw_board(screen)
        

    def copy(self):
        new_board = Board([])   
        new_board.grid = self.grid.copy()
        new_board.turn = self.turn
        new_board.checkmate = self.checkmate
        new_board.transposition_table = self.transposition_table
        return new_board

    def is_check(self, color):
        board_vals = board_value(self.grid)
        king_pos = None
        for x, y in zip(*np.where(board_vals * color > 0)):
            piece = self.grid[x, y]
            if piece.value * color == 90:
                king_pos = piece.position
                break
        
        for x, y in zip(*np.where(board_vals * color < 0)):
            adv_piece = self.grid[x, y]
            if king_pos in adv_piece.possible_moves(self.grid):
                return True
        return False
    
    
    def possible_moves(self, piece):
        possible_moves_theo = piece.possible_moves(self.grid)
        possible_moves_real = []
        for new_coord in possible_moves_theo:
            board_virtual = self.copy()
            board_virtual.move(piece, new_coord)
            if not board_virtual.is_check(np.sign(piece.value)):
                possible_moves_real.append(new_coord)
        return possible_moves_real

    def score(self):
        hash_key = self.hash_state()
        
        if hash_key in self.transposition_table:
            return self.transposition_table[hash_key]
        
        if self.is_checkmate(self.turn):
            score = 1e6
        elif self.is_checkmate(-self.turn):
            score = -1e6
        else:
            score = self.evaluate_board()

        self.transposition_table[hash_key] = score
        return score
    
    def clone_board(self, board):
        return board.copy()

    def is_checkmate(self, color):
        for x, y in zip(*np.where(board_value(self.grid) * color < 0)):
            piece = self.grid[x, y]
            for move in self.possible_moves(piece):
                new_board = self.copy()
                new_board.move(piece, move)
                if not new_board.is_check(color):
                    return False
        print("[Warning] Checkmate")
        return True


    def minimax(self, depth, alpha, beta, maximizing):
        if depth == 0 or self.is_checkmate(self.turn):
            score = self.score()
            return None, None, score  # No piece or move, just the evaluation (danger)
        
        best_move = None
        best_piece = None
        if maximizing:
            max_eval = -np.inf
            for x, y in zip(*np.where(board_value(self.grid) > 0)):  # assuming positive values for maximizing player
                piece = self[x, y]
                for move in self.possible_moves(piece):
                    new_board = self.copy()  # clone the board before applying the move
                    new_piece = piece.copy()
                    new_board.move(new_piece, move)      
                    _, _, eval = new_board.minimax(depth - 1, alpha, beta, False)
                    if eval > max_eval:
                        max_eval = eval
                        best_piece = piece
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Beta cutoff
            return best_piece, best_move, max_eval  # Return the best piece, its move, and the danger score
        else:
            min_eval = np.inf
            for x, y in zip(*np.where(board_value(self.grid) < 0)):  # assuming negative values for minimizing player
                piece = self[x, y]
                for move in self.possible_moves(piece):
                    new_board = self.copy()  # clone the board before applying the move
                    new_piece = piece.copy()
                    new_board.move(new_piece, move)
                    _, _, eval = new_board.minimax(depth - 1, alpha, beta, True)
                    if eval < min_eval:
                        min_eval = eval
                        best_piece = piece
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cutoff
            return best_piece, best_move, min_eval  # Return the best piece, its move, and the danger score
            

    def move(self, piece, new_coord):
        x, y = piece.position
        new_x, new_y = new_coord

        try:
            self[new_x, new_y] = self[x, y](new_coord)
        except:
            self[new_x, new_y] = piece(new_coord)
        self[x, y] = Empty(x, y)

        if "King" in piece.name and abs(new_x - x) == 2:
            if new_x > x:
                self[new_x - 1, new_y] = self[new_x + 1, new_y]((new_x - 1, new_y))
                self[new_x + 1, new_y] = Empty(new_x + 1, new_y)
            else:
                self[new_x + 1, new_y] = self[new_x - 2, new_y]((new_x + 1, new_y))
                self[new_x - 2, new_y] = Empty(new_x - 2, new_y)

        if "Pawn" in piece.name:
            self[new_x, new_y].moved = True
            if self[new_x, new_y]._promote():
                self[new_x, new_y] = Queen(piece.color, new_x, new_y)

        if "King" in piece.name or "Rook" in piece.name:
            self[new_x, new_y].moved = True
