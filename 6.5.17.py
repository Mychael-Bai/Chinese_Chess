import tkinter as tk
from tkinter import messagebox
import os
import pygame.mixer

import numpy as np
import random



class ChineseChess:

    def __init__(self):


        pygame.mixer.init()
        try:
            # Load the sound file (you'll need to create/download a suitable sound file)
            self.move_sound = pygame.mixer.Sound('piece_sound5.wav')
        except:
            print("Warning: Could not load sound file 'piece_sound5.wav'")
            self.move_sound = None
            

        self.window = tk.Tk()
        self.window.title("Chinese Chess 6.5.15(maybe strong but consumes too much time)")
        

        self.move_history = []  # List to store moves for current game
        self.game_history = []  # List to store all games
        

        # Board dimensions and styling
        self.board_size = 9  # 9x10 board
        self.cell_size = 54
        self.piece_radius = 20  # Smaller pieces to fit on intersections
        self.board_margin = 60  # Margin around the board
        # Calculate total canvas size including margins
        self.canvas_width = self.cell_size * 8 + 2 * self.board_margin
        self.canvas_height = self.cell_size * 9 + 2 * self.board_margin
        
        # Create main horizontal frame to hold board and button side by side
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(pady=20)
        
        # Create left frame for the board
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        # Create canvas for the game board
        self.canvas = tk.Canvas(
            self.board_frame, 
            width=self.canvas_width,
            height=self.canvas_height,
            bg='#f0d5b0'
        )
        self.canvas.pack()
        
        # Create right frame for the button with padding
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.LEFT, padx=20)  # Add padding between board and button



        # Create restart button
        button_size = self.piece_radius * 2  # Same size as a piece
        self.restart_button = tk.Button(
            self.button_frame,
            text="开始",  # Keep the original Chinese text
            command=self.restart_game,
            width=6,
            height=1
        )
        self.restart_button.pack()
        
        # Initialize game state
        self.selected_piece = None
        self.highlighted_positions = []
        self.current_player = 'red'  # Red moves first
        self.initialize_board()
        self.draw_board()
                    
        # Bind mouse event
        self.canvas.bind('<Button-1>', self.on_click)

    def show_centered_warning(self, title, message):
        """Shows a warning messagebox centered on the game board"""
        # Wait for any pending events to be processed
        self.window.update_idletasks()
        
        # Create custom messagebox
        warn_window = tk.Toplevel()
        warn_window.title(title)
        warn_window.geometry('300x100')  # Set size of warning window
        
        # Configure the warning window
        warn_window.transient(self.window)
        warn_window.grab_set()
        
        # Add message and OK button
        tk.Label(warn_window, text=message, padx=20, pady=10).pack()
        tk.Button(warn_window, text="OK", command=warn_window.destroy, width=10).pack(pady=10)
        
        # Wait for the warning window to be ready
        warn_window.update_idletasks()
        
        # Get the coordinates of the main window and board
        window_x = self.window.winfo_x()
        window_y = self.window.winfo_y()
        
        # Calculate the board's center position
        board_x = window_x + self.board_frame.winfo_x() + self.canvas.winfo_x()
        board_y = window_y + self.board_frame.winfo_y() + self.canvas.winfo_y()
        board_width = self.canvas.winfo_width()
        board_height = self.canvas.winfo_height()
        
        # Get the size of the warning window
        warn_width = warn_window.winfo_width()
        warn_height = warn_window.winfo_height()
        
        # Calculate the center position
        x = board_x + (board_width - warn_width) // 2
        y = board_y + (board_height - warn_height) // 2
        
        # Position the warning window
        warn_window.geometry(f"+{x}+{y}")
        
        # Make window modal and wait for it to close
        warn_window.focus_set()
        warn_window.wait_window()        


    def evaluate_board(self):
        """Evaluate the current board position for AI"""
        piece_values = {
            '將': 6000, '帥': 6000,
            '車': 600,
            '馬': 270,
            '炮': 285,
            '象': 120, '相': 120,
            '士': 120, '仕': 120,
            '卒': 30, '兵': 30
        }
        
        score = 0
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    value = piece_values[piece[1]]
                    if piece[0] == 'B':  # Black pieces (AI)
                        score += value
                        # Bonus for advanced positions
                        if piece[1] in ['卒', '炮']:
                            score += (row * 10)  # Encourage forward movement
                    else:  # Red pieces (Human)
                        score -= value
                        if piece[1] in ['兵', '炮']:
                            score -= ((9 - row) * 10)
        
        return score

    def get_all_valid_moves(self, color):
        """Get all valid moves for a given color"""
        moves = []
        for from_row in range(10):
            for from_col in range(9):
                piece = self.board[from_row][from_col]
                if piece and piece[0] == color[0].upper():
                    for to_row in range(10):
                        for to_col in range(9):
                            if self.is_valid_move((from_row, from_col), (to_row, to_col)):
                                moves.append(((from_row, from_col), (to_row, to_col)))
        return moves



    def evaluate_center_control(self):
        """Evaluate control of the center of the board"""
        center_score = 0
        center_squares = [(4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)]
        
        for row, col in center_squares:
            piece = self.board[row][col]
            if piece:
                if piece[0] == 'B':
                    center_score += 30
                else:
                    center_score -= 30
        return center_score

    def evaluate_piece_coordination(self):
        """Evaluate how well pieces support each other"""
        coordination_score = 0
        
        # Check for protected pieces
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    if piece[0] == 'B':
                        if self.is_protected((row, col), 'black'):
                            coordination_score += 20
                    else:
                        if self.is_protected((row, col), 'red'):
                            coordination_score -= 20
        
        return coordination_score

    def is_protected(self, pos, color):
        """Check if a position is protected by friendly pieces"""
        row, col = pos
        for r in range(10):
            for c in range(9):
                piece = self.board[r][c]
                if piece and piece[0] == color[0].upper() and (r, c) != pos:
                    if self.is_valid_move((r, c), pos):
                        return True
        return False

    def get_piece_moves(self, pos):
        """Get all possible moves for a piece at given position"""
        row, col = pos
        moves = []
        for to_row in range(10):
            for to_col in range(9):
                if self.is_valid_move(pos, (to_row, to_col)):
                    moves.append((to_row, to_col))
        return moves



    def _move_sorting_score(self, move):
        """Helper function to score moves for sorting in minimax"""
        from_pos, to_pos = move
        from_piece = self.board[from_pos[0]][from_pos[1]]
        to_piece = self.board[to_pos[0]][to_pos[1]]
        
        score = 0
        # Prioritize captures based on piece values
        if to_piece:
            piece_values = {
                '將': 6000, '帥': 6000,
                '車': 600,
                '馬': 270,
                '炮': 285,
                '象': 120, '相': 120,
                '士': 120, '仕': 120,
                '卒': 30, '兵': 30
            }
            score += piece_values[to_piece[1]]
        
        # Bonus for moves that give check
        self.board[to_pos[0]][to_pos[1]] = from_piece
        self.board[from_pos[0]][from_pos[1]] = None
        if self.is_in_check('red'):
            score += 500
        self.board[from_pos[0]][from_pos[1]] = from_piece
        self.board[to_pos[0]][to_pos[1]] = to_piece
        
        return score

    def evaluate_king_safety(self, color):
        """Evaluate king safety and surrounding protection"""
        kings = self.find_kings()
        king_pos = kings[1] if color == 'black' else kings[0]
        if not king_pos:
            return -9999
        
        king_row, king_col = king_pos
        safety = 0
        
        # Check protecting pieces
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = king_row + dr, king_col + dc
                if 0 <= r < 10 and 0 <= c < 9:
                    piece = self.board[r][c]
                    if piece and piece[0] == color[0].upper():
                        safety += 30
        
        # Penalty for exposed king
        if self.is_in_check(color):
            safety -= 200
        
        return safety


    def evaluate_position_simple(self):
        """Simplified but effective position evaluation"""
        piece_values = {
            '將': 6000, '帥': 6000,
            '車': 600,
            '馬': 270,
            '炮': 285,
            '象': 120, '相': 120,
            '士': 120, '仕': 120,
            '卒': 30, '兵': 30
        }
        
        score = 0
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    base_value = piece_values[piece[1]]
                    position_bonus = 0
                    
                    # Position bonus for pawns
                    if piece[1] in ['卒', '兵']:
                        if piece[0] == 'B':  # Black pawns
                            position_bonus = row * 15  # More bonus for advanced pawns
                        else:  # Red pawns
                            position_bonus = (9 - row) * 15
                    
                    # Mobility bonus for major pieces
                    if piece[1] in ['車', '馬', '炮']:
                        moves = len([pos for pos in self.get_piece_moves((row, col))
                                   if self.is_valid_move((row, col), pos)])
                        position_bonus += moves * 5
                    
                    # Center control bonus
                    if 3 <= col <= 5 and 3 <= row <= 6:
                        position_bonus += 10
                    
                    total_value = base_value + position_bonus
                    if piece[0] == 'B':
                        score += total_value
                    else:
                        score -= total_value
        
        # Add king safety with higher weight for defense
        if self.is_in_check('black'):
            score -= 300
        if self.is_in_check('red'):
            score += 300
            
        return score


    def minimax(self, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning and move ordering"""
        if depth == 0:
            return self.evaluate_position_simple()
        
        if maximizing_player:
            max_eval = float('-inf')
            moves = self.get_all_valid_moves('black')
            moves = self._sort_moves(moves, 'black')  # Sort moves for black
            
            for from_pos, to_pos in moves:
                moving_piece = self.board[from_pos[0]][from_pos[1]]
                captured_piece = self.board[to_pos[0]][to_pos[1]]
                
                self.board[to_pos[0]][to_pos[1]] = moving_piece
                self.board[from_pos[0]][from_pos[1]] = None
                
                if not self.is_in_check('black'):
                    eval = self.minimax(depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                
                self.board[from_pos[0]][from_pos[1]] = moving_piece
                self.board[to_pos[0]][to_pos[1]] = captured_piece
                
                if beta <= alpha:
                    break
            return max_eval if max_eval != float('-inf') else self.evaluate_position_simple()
        else:
            min_eval = float('inf')
            moves = self.get_all_valid_moves('red')
            moves = self._sort_moves(moves, 'red')  # Sort moves for red
            
            for from_pos, to_pos in moves:
                moving_piece = self.board[from_pos[0]][from_pos[1]]
                captured_piece = self.board[to_pos[0]][to_pos[1]]
                
                self.board[to_pos[0]][to_pos[1]] = moving_piece
                self.board[from_pos[0]][from_pos[1]] = None
                
                if not self.is_in_check('red'):
                    eval = self.minimax(depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                
                self.board[from_pos[0]][from_pos[1]] = moving_piece
                self.board[to_pos[0]][to_pos[1]] = captured_piece
                
                if beta <= alpha:
                    break
            return min_eval if min_eval != float('inf') else self.evaluate_position_simple()


    def _sort_moves(self, moves, color):
        """Simplified but effective move sorting"""
        move_scores = []
        for from_pos, to_pos in moves:
            score = 0
            moving_piece = self.board[from_pos[0]][from_pos[1]]
            captured_piece = self.board[to_pos[0]][to_pos[1]]
            
            # Capturing moves (highest priority)
            if captured_piece:
                piece_values = {
                    '將': 6000, '帥': 6000,
                    '車': 600,
                    '馬': 270,
                    '炮': 285,
                    '象': 120, '相': 120,
                    '士': 120, '仕': 120,
                    '卒': 30, '兵': 30
                }
                score += piece_values[captured_piece[1]] * 10
            
            # Check moves (second priority)
            self.board[to_pos[0]][to_pos[1]] = moving_piece
            self.board[from_pos[0]][from_pos[1]] = None
            if self.is_in_check('red' if color == 'black' else 'black'):
                score += 500
            self.board[from_pos[0]][from_pos[1]] = moving_piece
            self.board[to_pos[0]][to_pos[1]] = captured_piece
            
            move_scores.append((score, (from_pos, to_pos)))
        
        move_scores.sort(reverse=True)
        return [move for _, move in move_scores]



    def get_piece_position_value(self, piece, row, col):
        """Evaluate piece positions based on traditional Xiangqi principles"""
        # Chariot (車) values - strong on files and ranks
        chariot_values = [
            [206, 208, 207, 213, 214, 213, 207, 208, 206],
            [206, 212, 209, 216, 233, 216, 209, 212, 206],
            [206, 208, 207, 214, 216, 214, 207, 208, 206],
            [206, 213, 213, 216, 216, 216, 213, 213, 206],
            [208, 211, 211, 214, 215, 214, 211, 211, 208],
            [208, 212, 212, 214, 215, 214, 212, 212, 208],
            [204, 209, 204, 212, 214, 212, 204, 209, 204],
            [198, 208, 204, 212, 212, 212, 204, 208, 198],
            [200, 208, 206, 212, 200, 212, 206, 208, 200],
            [194, 206, 204, 212, 200, 212, 204, 206, 194]
        ]

        # Horse (馬) values - better in center, away from edges
        horse_values = [
            [90, 90, 90, 96, 90, 96, 90, 90, 90],
            [90, 96, 103, 97, 94, 97, 103, 96, 90],
            [92, 98, 99, 103, 99, 103, 99, 98, 92],
            [93, 108, 100, 107, 100, 107, 100, 108, 93],
            [90, 100, 99, 103, 104, 103, 99, 100, 90],
            [90, 98, 101, 102, 103, 102, 101, 98, 90],
            [92, 94, 98, 95, 98, 95, 98, 94, 92],
            [93, 92, 94, 95, 92, 95, 94, 92, 93],
            [85, 90, 92, 93, 78, 93, 92, 90, 85],
            [88, 85, 90, 88, 90, 88, 90, 85, 88]
        ]

        # Cannon (炮) values - good positions for attacking
        cannon_values = [
            [100, 100, 96, 91, 90, 91, 96, 100, 100],
            [98, 98, 96, 92, 89, 92, 96, 98, 98],
            [97, 97, 96, 91, 92, 91, 96, 97, 97],
            [96, 99, 99, 98, 100, 98, 99, 99, 96],
            [96, 96, 96, 96, 100, 96, 96, 96, 96],
            [95, 96, 99, 96, 100, 96, 99, 96, 95],
            [96, 96, 96, 96, 96, 96, 96, 96, 96],
            [97, 96, 100, 99, 101, 99, 100, 96, 97],
            [96, 97, 98, 98, 98, 98, 98, 97, 96],
            [96, 96, 97, 99, 99, 99, 97, 96, 96]
        ]

        # Pawn (兵/卒) values - more valuable as they advance
        pawn_values = [
            [9, 9, 9, 11, 13, 11, 9, 9, 9],
            [19, 24, 34, 42, 44, 42, 34, 24, 19],
            [19, 24, 32, 37, 37, 37, 32, 24, 19],
            [19, 23, 27, 29, 30, 29, 27, 23, 19],
            [14, 18, 20, 27, 29, 27, 20, 18, 14],
            [7, 0, 13, 0, 16, 0, 13, 0, 7],
            [7, 0, 7, 0, 15, 0, 7, 0, 7],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

        piece_type = piece[1]
        is_black = piece[0] == 'B'
        
        if piece_type in ['車']:
            value = chariot_values[row][col]
        elif piece_type in ['馬']:
            value = horse_values[row][col]
        elif piece_type in ['炮']:
            value = cannon_values[row][col]
        elif piece_type in ['兵', '卒']:
            value = pawn_values[9-row][col] if is_black else pawn_values[row][col]
        else:
            value = 0  # Base value for other pieces
            
        return value if is_black else -value



    def evaluate_position_strategic(self):
        """Enhanced evaluation with Chinese Chess strategic principles"""
        score = 0
        
        # Basic piece values
        piece_values = {
            '將': 6000, '帥': 6000,  # Kings
            '車': 600,               # Chariot
            '馬': 270,               # Horse
            '炮': 285,               # Cannon
            '象': 120, '相': 120,    # Elephant
            '士': 120, '仕': 120,    # Advisor
            '卒': 30, '兵': 30       # Pawn
        }

        # Strategic patterns
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    # Base material value
                    base_value = piece_values[piece[1]]
                    
                    # Add position value
                    position_value = self.get_piece_position_value(piece, row, col)
                    
                    # Mobility value
                    mobility = len(self.get_piece_moves((row, col))) * 10
                    
                    # Protection value
                    protection = 15 if self.is_protected((row, col), 'black' if piece[0] == 'B' else 'red') else 0
                    
                    # Special tactical patterns
                    tactical_value = self.evaluate_tactical_patterns(row, col, piece)
                    
                    total_value = base_value + position_value + mobility + protection + tactical_value
                    
                    if piece[0] == 'B':
                        score += total_value
                    else:
                        score -= total_value
        
        # Additional strategic considerations
        score += self.evaluate_king_safety('black') - self.evaluate_king_safety('red')
        score += self.evaluate_piece_coordination() * 0.5
        score += self.evaluate_attack_potential() * 0.7
        
        return score


    def evaluate_tactical_patterns(self, row, col, piece):
        """Evaluate common tactical patterns in Chinese Chess"""
        score = 0
        piece_type = piece[1]
        is_black = piece[0] == 'B'
        
        # Double Chariots on same file
        if piece_type == '車':
            for r in range(10):
                if r != row and self.board[r][col]:
                    other_piece = self.board[r][col]
                    if other_piece[1] == '車' and other_piece[0] == piece[0]:
                        score += 30

        # Horse and Cannon cooperation
        if piece_type in ['馬', '炮']:
            for dr in [-2, -1, 1, 2]:
                for dc in [-2, -1, 1, 2]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 10 and 0 <= new_col < 9:
                        other_piece = self.board[new_row][new_col]
                        if other_piece and other_piece[0] == piece[0]:
                            if (piece_type == '馬' and other_piece[1] == '炮') or \
                               (piece_type == '炮' and other_piece[1] == '馬'):
                                score += 25

        # Advanced pawn formation
        if piece_type in ['兵', '卒']:
            if is_black and row > 4:  # Black pawns crossed river
                for dc in [-1, 1]:
                    new_col = col + dc
                    if 0 <= new_col < 9:
                        other_piece = self.board[row][new_col]
                        if other_piece and other_piece[0] == piece[0] and \
                           other_piece[1] in ['兵', '卒']:
                            score += 20
        
        return score



    def evaluate_attack_potential(self):
        """Evaluate attacking potential against enemy king"""
        score = 0
        red_king_pos, black_king_pos = self.find_kings()
        
        if not red_king_pos or not black_king_pos:
            return 0
            
        # Evaluate attack paths to enemy king
        for color, king_pos in [('black', red_king_pos), ('red', black_king_pos)]:
            king_row, king_col = king_pos
            attacking_pieces = 0
            attack_value = 0
            
            # Check attacking pieces within range of enemy king
            for row in range(10):
                for col in range(9):
                    piece = self.board[row][col]
                    if piece and piece[0] == color[0].upper():
                        if abs(row - king_row) + abs(col - king_col) <= 4:
                            attacking_pieces += 1
                            # Heavy pieces near enemy king
                            if piece[1] in ['車', '馬', '炮']:
                                attack_value += 40
                            else:
                                attack_value += 10
            
            multiplier = 1 if color == 'black' else -1
            score += (attack_value + (attacking_pieces * 15)) * multiplier
        
        return score



    def make_ai_move(self):
        import time
        
        start_time = time.time()
        max_time = 60.0  # Reduced time limit for faster response
        
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Get and sort moves
        moves = self._sort_moves(self.get_all_valid_moves('black'), 'black')
        if not moves:
            return
        
        # Fixed depth but ensure completion
        search_depth = 3  # Start with a reliable depth
        
        for from_pos, to_pos in moves:
            if time.time() - start_time > max_time:
                break
                
            moving_piece = self.board[from_pos[0]][from_pos[1]]
            captured_piece = self.board[to_pos[0]][to_pos[1]]
            
            # Make temporary move
            self.board[to_pos[0]][to_pos[1]] = moving_piece
            self.board[from_pos[0]][from_pos[1]] = None
            
            if not self.is_in_check('black'):
                score = self.minimax(search_depth, alpha, beta, False)
                
                if score > best_score:
                    best_score = score
                    best_move = (from_pos, to_pos)
                    
            # Restore position
            self.board[from_pos[0]][from_pos[1]] = moving_piece
            self.board[to_pos[0]][to_pos[1]] = captured_piece
        
        # Make the best move found
        if best_move:
            from_pos, to_pos = best_move
            self.board[to_pos[0]][to_pos[1]] = self.board[from_pos[0]][from_pos[1]]
            self.board[from_pos[0]][from_pos[1]] = None
            
            if hasattr(self, 'move_sound') and self.move_sound:
                self.move_sound.play()
            
            self.highlighted_positions = [from_pos, to_pos]
            self.current_player = 'red'
            self.draw_board()


    def is_checkmate(self, color):
        """
        Check if the given color is in checkmate.
        Returns True if the player has no legal moves to escape check.
        """
        # If not in check, can't be checkmate
        if not self.is_in_check(color):
            return False
            
        # Try every possible move for every piece of the current player
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece[0] == color[0].upper():  # If it's current player's piece
                    # Try all possible destinations
                    for to_row in range(10):
                        for to_col in range(9):
                            if self.is_valid_move((row, col), (to_row, to_col)):
                                # Try the move
                                original_piece = self.board[to_row][to_col]
                                self.board[to_row][to_col] = piece
                                self.board[row][col] = None
                                
                                # Check if still in check
                                still_in_check = self.is_in_check(color)
                                
                                # Undo the move
                                self.board[row][col] = piece
                                self.board[to_row][to_col] = original_piece
                                
                                # If any move gets out of check, not checkmate
                                if not still_in_check:
                                    return False
        
        # If no legal moves found, it's checkmate
        return True

    # YELLOW HIGHTLIGHT(2nd modification)

    def highlight_piece(self, row, col):
        """Draw a yellow highlight around the selected piece"""
        # Calculate position on intersections
        x = self.board_margin + col * self.cell_size
        y = self.board_margin + row * self.cell_size
        
        # Create a yellow square around the piece
        self.canvas.create_rectangle(
            x - self.piece_radius - 2,
            y - self.piece_radius - 2,
            x + self.piece_radius + 2,
            y + self.piece_radius + 2,
            outline='yellow',
            width=2,
            tags='highlight'
        )    

    def initialize_board(self):
        # Initialize empty board
        self.board = [[None for _ in range(9)] for _ in range(10)]
        
        # Set up initial piece positions
        self.setup_pieces()
        
    def setup_pieces(self):
        # Red pieces (bottom)
        red_pieces = {
            (9, 0): 'R車', (9, 1): 'R馬', (9, 2): 'R相',
            (9, 3): 'R仕', (9, 4): 'R帥', (9, 5): 'R仕',
            (9, 6): 'R相', (9, 7): 'R馬', (9, 8): 'R車',
            (7, 1): 'R炮', (7, 7): 'R炮',
            (6, 0): 'R兵', (6, 2): 'R兵', (6, 4): 'R兵',
            (6, 6): 'R兵', (6, 8): 'R兵'
        }
        
        # Black pieces (top)
        black_pieces = {
            (0, 0): 'B車', (0, 1): 'B馬', (0, 2): 'B象',
            (0, 3): 'B士', (0, 4): 'B將', (0, 5): 'B士',
            (0, 6): 'B象', (0, 7): 'B馬', (0, 8): 'B車',
            (2, 1): 'B炮', (2, 7): 'B炮',
            (3, 0): 'B卒', (3, 2): 'B卒', (3, 4): 'B卒',
            (3, 6): 'B卒', (3, 8): 'B卒'
        }
        
        # Place pieces on board
        for pos, piece in red_pieces.items():
            row, col = pos
            self.board[row][col] = piece
            
        for pos, piece in black_pieces.items():
            row, col = pos
            self.board[row][col] = piece

    def draw_board(self):
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw the outer border
        self.canvas.create_rectangle(
            self.board_margin, self.board_margin,
            self.canvas_width - self.board_margin,
            self.canvas_height - self.board_margin,
            width=2
        )

        # clear hightlight(3rd modification)
        self.canvas.delete('highlight')

        # add hightlight(4th modification)
        if self.selected_piece:
            row, col = self.selected_piece
            self.highlight_piece(row, col)

        # Draw grid lines
        for i in range(10):  # Horizontal lines
            y = self.board_margin + i * self.cell_size
            self.canvas.create_line(
                self.board_margin, y,
                self.canvas_width - self.board_margin, y
            )
            
        for i in range(9):  # Vertical lines
            x = self.board_margin + i * self.cell_size
            # Draw vertical lines with river gap
            self.canvas.create_line(
                x, self.board_margin,
                x, self.board_margin + 4 * self.cell_size
            )
            self.canvas.create_line(
                x, self.board_margin + 5 * self.cell_size,
                x, self.canvas_height - self.board_margin
            )

        # Draw palace diagonal lines
        # Top palace
        self.canvas.create_line(
            self.board_margin + 3 * self.cell_size, self.board_margin,
            self.board_margin + 5 * self.cell_size, self.board_margin + 2 * self.cell_size
        )
        self.canvas.create_line(
            self.board_margin + 5 * self.cell_size, self.board_margin,
            self.board_margin + 3 * self.cell_size, self.board_margin + 2 * self.cell_size
        )
        
        # Bottom palace
        self.canvas.create_line(
            self.board_margin + 3 * self.cell_size, self.canvas_height - self.board_margin - 2 * self.cell_size,
            self.board_margin + 5 * self.cell_size, self.canvas_height - self.board_margin
        )
        self.canvas.create_line(
            self.board_margin + 5 * self.cell_size, self.canvas_height - self.board_margin - 2 * self.cell_size,
            self.board_margin + 3 * self.cell_size, self.canvas_height - self.board_margin
        )

        # Draw river text
        river_y = self.board_margin + 4.5 * self.cell_size
        self.canvas.create_text(
            self.canvas_width / 2, river_y,
            text="楚 河          漢 界",
            font=('Arial', 16)
        )
        
        # Draw pieces on intersections
        for row in range(10):
            for col in range(9):
                if self.board[row][col]:
                    # Calculate position on intersections
                    x = self.board_margin + col * self.cell_size
                    y = self.board_margin + row * self.cell_size
                    
                    # Draw piece circle
                    color = 'red' if self.board[row][col][0] == 'R' else 'black'
                    self.canvas.create_oval(
                        x - self.piece_radius, y - self.piece_radius,
                        x + self.piece_radius, y + self.piece_radius,
                        fill='white',
                        outline=color,
                        width=2
                    )
                    
                    # Draw piece text
                    piece_text = self.board[row][col][1]
                    text_color = 'red' if self.board[row][col][0] == 'R' else 'black'
                    self.canvas.create_text(
                        x, y,
                        text=piece_text,
                        fill=text_color,
                        font=('KaiTi', 20, 'bold')
                    )
            
        # Modify the highlight section to show all highlighted positions
        self.canvas.delete('highlight')
        for pos in self.highlighted_positions:
            row, col = pos
            self.highlight_piece(row, col)

        # Draw column numbers at top and bottom
        # List of Chinese numbers for red side (bottom)
        red_numbers = ['九', '八', '七', '六', '五', '四', '三', '二', '一']
        # List of Arabic numbers for black side (top)
        black_numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

        # Draw top numbers (for black)
        for col, num in enumerate(black_numbers):
            x = self.board_margin + col * self.cell_size
            y = self.board_margin - 37  # Change from -15 to -25 to position numbers higher
            self.canvas.create_text(
                x, y,
                text=num,
                fill='black',
                font=('Arial', 12)
            )

        # Draw bottom numbers (for red)
        for col, num in enumerate(red_numbers):
            x = self.board_margin + col * self.cell_size
            y = self.canvas_height - self.board_margin + 37  # Change from +15 to +25 to position numbers lower
            self.canvas.create_text(
                x, y,
                text=num,
                fill='black',
                font=('Arial', 12)
            )

    def show_victory_message(self, winner):
        """Shows a victory message with special styling"""
        # Wait for any pending events to be processed
        self.window.update_idletasks()
        
        # Create victory window
        victory_window = tk.Toplevel()
        victory_window.title("胜利")
        victory_window.geometry('400x150')  # Larger size for victory message
        
        # Configure the victory window
        victory_window.transient(self.window)
        victory_window.grab_set()
        
        # Add message with larger font and decorative style
        message_frame = tk.Frame(victory_window)
        message_frame.pack(expand=True, fill='both')
        
        tk.Label(
            message_frame,
            text=f"🎊 恭喜 🎊\n{winner}获得胜利！",
            font=('Arial', 16, 'bold'),
            pady=20
        ).pack()
        
        # Add OK button with special styling
        tk.Button(
            message_frame,
            text="开始新游戏",
            command=victory_window.destroy,
            width=15,
            height=2,
            relief=tk.RAISED,
            bg='#f0f0f0'
        ).pack(pady=10)
        
        # Center the window on the board
        victory_window.update_idletasks()
        window_x = self.window.winfo_x()
        window_y = self.window.winfo_y()
        board_x = window_x + self.board_frame.winfo_x() + self.canvas.winfo_x()
        board_y = window_y + self.board_frame.winfo_y() + self.canvas.winfo_y()
        board_width = self.canvas.winfo_width()
        board_height = self.canvas.winfo_height()
        
        x = board_x + (board_width - victory_window.winfo_width()) // 2
        y = board_y + (board_height - victory_window.winfo_height()) // 2
        
        victory_window.geometry(f"+{x}+{y}")
        victory_window.focus_set()
        victory_window.wait_window()

    def restart_game(self):
        if self.move_history:  # If there was a game in progress
            self.game_history.append(self.move_history)
        self.move_history = []

        # Reset game state
        self.selected_piece = None
        self.highlighted_positions = []
        self.current_player = 'red'
        # Reinitialize the board
        self.initialize_board()
        # Redraw the board
        self.draw_board()

    def on_click(self, event):


        # Convert click coordinates to board position (remove the center_offset from here)
        col = round((event.x - self.board_margin) / self.cell_size)
        row = round((event.y - self.board_margin) / self.cell_size)
        
        # Ensure click is within board bounds
        if 0 <= row < 10 and 0 <= col < 9:
            clicked_piece = self.board[row][col]
            
            # If a piece is already selected
            if self.selected_piece:
                start_row, start_col = self.selected_piece
                
                # If clicking on another piece of the same color, select that piece instead
                if (clicked_piece and 
                    clicked_piece[0] == self.current_player[0].upper()):
                    self.selected_piece = (row, col)
                    self.highlighted_positions = [(row, col)]  # Reset highlights for new selection
                    self.draw_board()
                # If clicking on a valid move position
                elif self.is_valid_move(self.selected_piece, (row, col)):
                    # Store the current state to check for check
                    original_piece = self.board[row][col]
                    
                    # Make the move temporarily
                    self.board[row][col] = self.board[start_row][start_col]
                    self.board[start_row][start_col] = None
                    
                    # Check if the move puts own king in check
                    if self.is_in_check(self.current_player):
                        # Undo the move if it puts own king in check
                        self.board[start_row][start_col] = self.board[row][col]
                        self.board[row][col] = original_piece


                        if self.current_player == 'red':
                            self.show_centered_warning("Invalid Move", "你正在被将军")
                        else:
                            self.show_centered_warning("Invalid Move", "黑方正在被将军")

                    else:
                        # Keep both the original and new positions highlighted
                        self.highlighted_positions = [(start_row, start_col), (row, col)]
                              

                                        
                        # Play move sound
                        if hasattr(self, 'move_sound') and self.move_sound:
                            self.move_sound.play()
                            

                        # Switch players
                        self.current_player = 'black' if self.current_player == 'red' else 'red'
                        

                        # Add this code:
                        if self.current_player == 'black':
                            # Add a small delay before AI move
                            self.window.after(500, self.make_ai_move)


                    # Reset selected piece
                    self.selected_piece = None
                    
                    # Redraw board
                    self.draw_board()
            
            # If no piece is selected and clicked on own piece, select it
            elif clicked_piece and clicked_piece[0] == self.current_player[0].upper():
                self.selected_piece = (row, col)
                self.highlighted_positions = [(row, col)]  # Initialize highlights with selected piece
                self.draw_board()        

        # Check if the opponent is now in checkmate
        if self.is_checkmate(self.current_player):
            # Determine the winner
            winner = "红方" if self.current_player == 'black' else "黑方"
            self.show_centered_warning("游戏结束", f"{winner}获胜！")

    # Add piece movement validation(8 functions)

    def is_valid_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        
        # Basic validation
        if not (0 <= to_row < 10 and 0 <= to_col < 9):
            return False
            
        # Can't capture own pieces
        if self.board[to_row][to_col] and self.board[to_row][to_col][0] == piece[0]:
            return False
        
        # Get piece type (second character of the piece string)
        piece_type = piece[1]
        
        # Check specific piece movement rules
        if piece_type == '帥' or piece_type == '將':  # General/King
            return self.is_valid_general_move(from_pos, to_pos)
        elif piece_type == '仕' or piece_type == '士':  # Advisor
            return self.is_valid_advisor_move(from_pos, to_pos)
        elif piece_type == '相' or piece_type == '象':  # Elephant
            return self.is_valid_elephant_move(from_pos, to_pos)
        elif piece_type == '馬':  # Horse
            return self.is_valid_horse_move(from_pos, to_pos)
        elif piece_type == '車':  # Chariot
            return self.is_valid_chariot_move(from_pos, to_pos)
        elif piece_type == '炮':  # Cannon
            return self.is_valid_cannon_move(from_pos, to_pos)
        elif piece_type == '兵' or piece_type == '卒':  # Pawn
            return self.is_valid_pawn_move(from_pos, to_pos)
        
        return False

    def is_valid_general_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        
        # Check if move is within palace (3x3 grid)
        if piece[0] == 'R':  # Red general
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                return False
        else:  # Black general
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                return False
        
        # Can only move one step horizontally or vertically
        if abs(to_row - from_row) + abs(to_col - from_col) != 1:
            return False
            
        return True

    def is_valid_advisor_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        
        # Check if move is within palace
        if piece[0] == 'R':  # Red advisor
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                return False
        else:  # Black advisor
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                return False
        
        # Must move exactly one step diagonally
        if abs(to_row - from_row) != 1 or abs(to_col - from_col) != 1:
            return False
            
        return True

    def is_valid_elephant_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        
        # Cannot cross river
        if piece[0] == 'R':  # Red elephant
            if to_row < 5:  # Cannot cross river
                return False
        else:  # Black elephant
            if to_row > 4:  # Cannot cross river
                return False
        
        # Must move exactly two steps diagonally
        if abs(to_row - from_row) != 2 or abs(to_col - from_col) != 2:
            return False
        
        # Check if there's a piece blocking the elephant's path
        blocking_row = (from_row + to_row) // 2
        blocking_col = (from_col + to_col) // 2
        if self.board[blocking_row][blocking_col]:
            return False
            
        return True

    def is_valid_horse_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Must move in an L-shape (2 steps in one direction, 1 step in perpendicular direction)
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        if not ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)):
            return False
        
        # Check for blocking piece
        if row_diff == 2:
            blocking_row = from_row + (1 if to_row > from_row else -1)
            if self.board[blocking_row][from_col]:
                return False
        else:
            blocking_col = from_col + (1 if to_col > from_col else -1)
            if self.board[from_row][blocking_col]:
                return False
                
        return True

    def is_valid_chariot_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Must move horizontally or vertically
        if from_row != to_row and from_col != to_col:
            return False
        
        # Check if path is clear
        if from_row == to_row:  # Horizontal move
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if self.board[from_row][col]:
                    return False
        else:  # Vertical move
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if self.board[row][from_col]:
                    return False
                    
        return True

    def is_valid_cannon_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Must move horizontally or vertically
        if from_row != to_row and from_col != to_col:
            return False
        
        # Count pieces between from and to positions
        pieces_between = 0
        if from_row == to_row:  # Horizontal move
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if self.board[from_row][col]:
                    pieces_between += 1
        else:  # Vertical move
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if self.board[row][from_col]:
                    pieces_between += 1
        
        # If capturing, need exactly one piece between
        if self.board[to_row][to_col]:
            return pieces_between == 1
        # If not capturing, path must be clear
        return pieces_between == 0

    def is_valid_pawn_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        
        if piece[0] == 'R':  # Red pawn
            # Before crossing river
            if from_row > 4:
                # Can only move forward (up)
                return to_col == from_col and to_row == from_row - 1
            # After crossing river
            else:
                # Can move forward or sideways
                return (to_col == from_col and to_row == from_row - 1) or \
                       (to_row == from_row and abs(to_col - from_col) == 1)
        else:  # Black pawn
            # Before crossing river
            if from_row < 5:
                # Can only move forward (down)
                return to_col == from_col and to_row == from_row + 1
            # After crossing river
            else:
                # Can move forward or sideways
                return (to_col == from_col and to_row == from_row + 1) or \
                       (to_row == from_row and abs(to_col - from_col) == 1)

    # the following 3 functions (conbined with on_click function) is to add the CHECK feature
    def find_kings(self):
        """Find positions of both kings/generals"""
        red_king_pos = black_king_pos = None
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    if piece[1] == '帥':
                        red_king_pos = (row, col)
                    elif piece[1] == '將':
                        black_king_pos = (row, col)
        return red_king_pos, black_king_pos

    def is_position_under_attack(self, pos, attacking_color):
        """Check if a position is under attack by pieces of the given color"""
        target_row, target_col = pos
        
        # Check from all positions on the board
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece[0] == attacking_color[0].upper():
                    # Check if this piece can move to the target position
                    if self.is_valid_move((row, col), pos):
                        return True
        return False  

    def is_generals_facing(self):
        """Check if the two generals are facing each other directly"""
        red_king_pos, black_king_pos = self.find_kings()
        
        # If either king is missing, return False
        if not red_king_pos or not black_king_pos:
            return False
            
        red_row, red_col = red_king_pos
        black_row, black_col = black_king_pos
        
        # Check if generals are in the same column
        if red_col != black_col:
            return False
            
        # Check if there are any pieces between the generals
        start_row = min(red_row, black_row) + 1
        end_row = max(red_row, black_row)
        
        for row in range(start_row, end_row):
            if self.board[row][red_col]:  # If there's any piece between
                return False
                
        # If we get here, the generals are facing each other
        return True

    def is_in_check(self, color):
        """Check if the king of the given color is in check"""
        red_king_pos, black_king_pos = self.find_kings()
        
        if not red_king_pos or not black_king_pos:
            return False
        
        # First check the special case of facing generals
        if self.is_generals_facing():
            return True  # Both kings are in check in this case
        
        # Then check the normal cases of being under attack
        if color == 'red':
            return self.is_position_under_attack(red_king_pos, 'black')
        else:
            return self.is_position_under_attack(black_king_pos, 'red')

    def run(self):
        self.window.mainloop()

# Create and run the game
if __name__ == "__main__":
    game = ChineseChess()
    game.run()