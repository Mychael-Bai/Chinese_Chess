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
        
        # Calculate total canvas size including margins
        self.canvas_width = self.cell_size * 8 + 2 * self.board_margin
        self.canvas_height = self.cell_size * 9 + 2 * self.board_margin
        
        # Create canvas for the game board
        self.canvas = tk.Canvas(
            self.window, 
            width=self.canvas_width,
            height=self.canvas_height,
            bg='#f0d5b0'
        )
        self.canvas.pack(pady=20)
        
        # Initialize game state
        self.selected_piece = None
        self.current_player = 'red'  # Red moves first
        self.initialize_board()
        self.draw_board()
        
        # BAND MOUSE EVENT(1st modification)
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
                        font=('Arial', 14, 'bold')
                    )

        # Add position markers for cannon positions and soldier crossing points
        marker_positions = [
            # Cannon positions
            (2, 1), (2, 7), (7, 1), (7, 7),
            # Soldier crossing points
            (3, 0), (3, 2), (3, 4), (3, 6), (3, 8),
            (6, 0), (6, 2), (6, 4), (6, 6), (6, 8)
        ]
        
        for row, col in marker_positions:
            x = self.board_margin + col * self.cell_size
            y = self.board_margin + row * self.cell_size
            marker_size = 5
            # Draw small crosses at these positions
            self.canvas.create_line(x - marker_size, y, x + marker_size, y)
            self.canvas.create_line(x, y - marker_size, x, y + marker_size)

    def on_click(self, event):
        # Convert click coordinates to board position
        col = round((event.x - self.board_margin) / self.cell_size)
        row = round((event.y - self.board_margin) / self.cell_size)
        
        # Ensure click is within board bounds
        if 0 <= row < 10 and 0 <= col < 9:
            # Handle piece selection and movement
            if self.selected_piece is None:
                if self.board[row][col] and self.board[row][col][0] == self.current_player[0].upper():
                    self.selected_piece = (row, col)
                    # Redraw board with highlight
                    self.draw_board()
            else:
                # Handle piece movement
                if self.is_valid_move(self.selected_piece, (row, col)):
                    start_row, start_col = self.selected_piece
                    # Move the piece
                    self.board[row][col] = self.board[start_row][start_col]
                    self.board[start_row][start_col] = None
                    # Switch players
                    self.current_player = 'black' if self.current_player == 'red' else 'red'
                
                # Clear selection
                self.selected_piece = None
                # Redraw board without highlight
                self.draw_board()
    
    # Add piece movement validation
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
            
        # Add specific piece movement rules here
        return True

    def run(self):
        self.window.mainloop()

# Create and run the game
if __name__ == "__main__":
    game = ChineseChess()
    game.run()