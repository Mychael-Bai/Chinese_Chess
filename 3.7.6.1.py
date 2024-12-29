import tkinter as tk
from tkinter import messagebox
import os

class ChineseChess:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chinese Chess3.0")
        
        # Board dimensions and styling
        self.board_size = 9  # 9x10 board
        self.cell_size = 57
        self.piece_radius = 20  # Smaller pieces to fit on intersections
        self.board_margin = 40  # Margin around the board
        
        # Calculate board size (the actual game board area)
        self.board_width = self.cell_size * 8 + 2 * self.board_margin
        
        # Calculate total canvas size including extra width
        self.canvas_width = self.board_width + (2 * self.cell_size)  # Add two cell-sizes to total width
        self.canvas_height = self.cell_size * 9 + 2 * self.board_margin
        
        # Create a frame to hold both the canvas and button
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(pady=20)
        
        # Create canvas for the game board with increased width
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=self.canvas_width,
            height=self.canvas_height,
            bg='#f0d5b0'
        )
        self.canvas.pack(side=tk.TOP)
        
        # Create restart button
        button_size = self.piece_radius * 2  # Same size as a piece
        self.restart_button = tk.Button(
            self.main_frame,
            text="开始",
            command=self.restart_game,
            width=4,  # Adjust width to match piece size
            height=1   # Adjust height to match piece size
        )
        self.restart_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Initialize game state
        self.selected_piece = None
        self.highlighted_positions = []
        self.current_player = 'red'  # Red moves first
        self.initialize_board()
        self.draw_board()
        
        # BAND MOUSE EVENT
        self.canvas.bind('<Button-1>', self.on_click)

    # YELLOW HIGHTLIGHT(2nd modification)
    def highlight_piece(self, row, col):
        """Draw a yellow highlight around the selected piece"""
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
        
        # Calculate offset to center the board
        center_offset = self.cell_size  # One cell-size offset to center the board
        
        # Draw the outer border
        self.canvas.create_rectangle(
            self.board_margin + center_offset, self.board_margin,
            self.board_width - self.board_margin + center_offset,
            self.canvas_height - self.board_margin,
            width=2
        )

        # Draw grid lines with center offset
        for i in range(10):  # Horizontal lines
            y = self.board_margin + i * self.cell_size
            self.canvas.create_line(
                self.board_margin + center_offset, y,
                self.board_width - self.board_margin + center_offset, y
            )
            
        for i in range(9):  # Vertical lines
            x = self.board_margin + i * self.cell_size + center_offset
            # Draw vertical lines with river gap
            self.canvas.create_line(
                x, self.board_margin,
                x, self.board_margin + 4 * self.cell_size
            )
            self.canvas.create_line(
                x, self.board_margin + 5 * self.cell_size,
                x, self.canvas_height - self.board_margin
            )

        # Draw palace diagonal lines with center offset
        # Top palace
        self.canvas.create_line(
            self.board_margin + 3 * self.cell_size + center_offset, self.board_margin,
            self.board_margin + 5 * self.cell_size + center_offset, self.board_margin + 2 * self.cell_size
        )
        self.canvas.create_line(
            self.board_margin + 5 * self.cell_size + center_offset, self.board_margin,
            self.board_margin + 3 * self.cell_size + center_offset, self.board_margin + 2 * self.cell_size
        )
        
        # Bottom palace with center offset
        self.canvas.create_line(
            self.board_margin + 3 * self.cell_size + center_offset, self.canvas_height - self.board_margin - 2 * self.cell_size,
            self.board_margin + 5 * self.cell_size + center_offset, self.canvas_height - self.board_margin
        )
        self.canvas.create_line(
            self.board_margin + 5 * self.cell_size + center_offset, self.canvas_height - self.board_margin - 2 * self.cell_size,
            self.board_margin + 3 * self.cell_size + center_offset, self.canvas_height - self.board_margin
        )

        # Draw river text with center offset
        river_y = self.board_margin + 4.5 * self.cell_size
        self.canvas.create_text(
            self.canvas_width / 2, river_y,
            text="楚 河          漢 界",
            font=('Arial', 16)
        )
        
        # Draw pieces on intersections with center offset
        for row in range(10):
            for col in range(9):
                if self.board[row][col]:
                    # Calculate position on intersections with center offset
                    x = self.board_margin + col * self.cell_size + center_offset
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
                        font=('Arial', 14, 'bold')
                    )
            
        # Modify the highlight section to show all highlighted positions with center offset
        self.canvas.delete('highlight')
        for pos in self.highlighted_positions:
            row, col = pos
            x = self.board_margin + col * self.cell_size + center_offset
            y = self.board_margin + row * self.cell_size
            self.canvas.create_rectangle(
                x - self.piece_radius - 2,
                y - self.piece_radius - 2,
                x + self.piece_radius + 2,
                y + self.piece_radius + 2,
                outline='yellow',
                width=2,
                tags='highlight'
            )


    def restart_game(self):
        # Reset game state
        self.selected_piece = None
        self.highlighted_positions = []
        self.current_player = 'red'
        # Reinitialize the board
        self.initialize_board()
        # Redraw the board
        self.draw_board()            

    def on_click(self, event):

             
        # Convert click coordinates to board position, accounting for center offset
        center_offset = self.cell_size
        col = round((event.x - self.board_margin - center_offset) / self.cell_size)
        row = round((event.y - self.board_margin) / self.cell_size)
            
        # Ensure click is within board bounds
        if 0 <= row < 10 and 0 <= col < 9:
            # Get the piece at clicked position
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
                    # Keep both the original and new positions highlighted
                    self.highlighted_positions = [(start_row, start_col), (row, col)]
                    
                    # Move the piece
                    self.board[row][col] = self.board[start_row][start_col]
                    self.board[start_row][start_col] = None
                    
                    # Switch players
                    self.current_player = 'black' if self.current_player == 'red' else 'red'
                    
                    # Update selected piece to None since the move is complete
                    self.selected_piece = None
                    
                    # Redraw board with both highlights
                    self.draw_board()
            
            # If no piece is selected and clicked on own piece, select it
            elif clicked_piece and clicked_piece[0] == self.current_player[0].upper():
                self.selected_piece = (row, col)
                self.highlighted_positions = [(row, col)]  # Initialize highlights with selected piece
                self.draw_board()
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

  
    def run(self):
        self.window.mainloop()

# Create and run the game
if __name__ == "__main__":
    game = ChineseChess()
    game.run()