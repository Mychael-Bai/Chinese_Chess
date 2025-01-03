import tkinter as tk
from tkinter import messagebox
import os

class ChineseChess:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chinese Chess 5.5(add numbers)")
        

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

        # Create records button above restart button
        self.records_button = tk.Button(
            self.button_frame,
            text="记录",
            command=self.toggle_records,
            width=6,
            height=1
        )
        self.records_button.pack(pady=(0, 10))

        # Create the records frame but don't pack it yet
        self.records_frame = tk.Frame(self.main_frame)

        # Create move history display
        self.move_text = tk.Text(
            self.records_frame,
            width=20,
            height=25,
            state='disabled'
        )
        self.move_text.pack(pady=5)
        
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


    def get_piece_position_descriptor(self, from_pos, piece):
        """
        Determine 前/后 based on the players' perspective.
        Red player sits below the bottom (row 9), Black player sits above the top (row 0).
        
        For red player:
        - 前 = piece farther from red player (smaller row number)
        - 后 = piece closer to red player (larger row number)
        
        For black player:
        - 前 = piece farther from black player (larger row number)
        - 后 = piece closer to black player (smaller row number)
        """
        from_row, from_col = from_pos
        piece_color = piece[0]  # 'R' for red or 'B' for black
        piece_type = piece[1]   # '炮', '車', etc.
        
        # Get all rows where there are pieces of the same type and color in this column
        piece_rows = []
        for row in range(10):
            current_piece = self.board[row][from_col]
            if current_piece and current_piece[0] == piece_color and current_piece[1] == piece_type:
                piece_rows.append(row)
        
        # If only one piece found, no descriptor needed
        if len(piece_rows) <= 1:
            return ""
            
        if piece_color == 'R':  # Red player's perspective
            # For red pieces, larger row number means closer to red player (后)
            if from_row > min(piece_rows):  # If current piece is closer to red player
                return "后"
            else:
                return "前"
        else:  # Black player's perspective
            # For black pieces, smaller row number means closer to black player (后)
            if from_row < max(piece_rows):  # If current piece is closer to black player
                return "后"
            else:
                return "前"

    def get_move_text(self, from_pos, to_pos, piece):
        """Convert a move into Chinese chess notation"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Get the piece name
        piece_name = piece[1]
        
        # Get column numbers based on player color
        if piece[0] == 'R':  # Red player
            columns = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
            to_col_text = columns[8 - to_col]
        else:  # Black player
            columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
            to_col_text = columns[to_col]
        
        # Get position descriptor (前/后) if needed
        position_descriptor = self.get_piece_position_descriptor(from_pos, piece)
        
        # Determine direction
        if piece[0] == 'R':  # Red player
            if to_row < from_row:
                direction = '进'
            elif to_row > from_row:
                direction = '退'
            else:
                direction = '平'
        else:  # Black player
            if to_row > from_row:
                direction = '进'
            elif to_row < from_row:
                direction = '退'
            else:
                direction = '平'
        
        # Calculate steps or get destination column
        steps = abs(to_row - from_row)
        if piece[0] == 'R':  # Red player
            steps_text = columns[steps-1] if steps > 0 else to_col_text
        else:  # Black player
            steps_text = str(steps) if steps > 0 else to_col_text

        # If there's a position descriptor (前/后), use the four-character format without starting column
        if position_descriptor:
            move_text = f"{position_descriptor}{piece_name}{direction}{steps_text}"
        else:
            # For single pieces, include the starting column
            from_col_text = columns[8 - from_col] if piece[0] == 'R' else columns[from_col]
            
            # handling for 兵, 卒, 帥, 將, 車, 炮 (using steps)
            if piece_name in ['兵', '卒', '帥', '將', '車', '炮']:
                if direction == '平':
                    move_text = f"{piece_name}{from_col_text}{direction}{to_col_text}"
                else:
                    move_text = f"{piece_name}{from_col_text}{direction}{steps_text}"
            # handling for 相, 象, 馬, 仕, 士 (using destination columns)
            else:
                move_text = f"{piece_name}{from_col_text}{direction}{to_col_text}"
        
        return move_text

    def add_move_to_history(self, from_pos, to_pos, piece):
        """Add a move to the current game history"""
        move_text = self.get_move_text(from_pos, to_pos, piece)
        self.move_history.append(f"{move_text}")
        self.update_records_display()

    def update_records_display(self):
        """Update the records display if it exists"""
        if self.move_text and self.move_history:
            self.move_text.config(state='normal')
            self.move_text.delete('1.0', tk.END)
            for i, move in enumerate(self.move_history, 1):
                self.move_text.insert(tk.END, f"{i}. {move}\n")
            self.move_text.config(state='disabled')
            self.move_text.see(tk.END)  # Scroll to the bottom

    def toggle_records(self):
        """Toggle the visibility of the records frame"""
        if self.records_frame.winfo_ismapped():
            self.records_frame.pack_forget()
        else:
            # Pack the records frame at the start of main_frame
            self.records_frame.pack(side=tk.LEFT, before=self.board_frame, padx=(20, 20))

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
                        font=('Arial', 14, 'bold')
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
        if self.move_text:
            self.move_text.config(state='normal')
            self.move_text.delete('1.0', tk.END)
            self.move_text.config(state='disabled')
        
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
                                            
                        # Record the move
                        moved_piece = self.board[row][col]
                        self.add_move_to_history(
                            (start_row, start_col),
                            (row, col),
                            moved_piece)
                        # Switch players
                        self.current_player = 'black' if self.current_player == 'red' else 'red'
                        

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