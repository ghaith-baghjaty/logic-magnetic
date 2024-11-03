import tkinter as tk
from tkinter import messagebox


# هاد الصف فيه تصنيف للمغناطيس الجاذب لتمييزه عن باقي الكتل
class Magnet:
    def __init__(self, magnet_type, polarity):
        self.magnet_type = magnet_type
        self.polarity = polarity

    def __str__(self):
        return self.magnet_type


# هاد الصف فيه القطع البيضاء والحمراء والمعدنية
class Block:
    def __init__(self, block_type):
        self.block_type = block_type

    def __str__(self):
        return self.block_type


# هاد الصف الرئيسي يلي فيه بنشأ الرقعة وبحل مسألة من نوع ومنو بنتقل من حالة لحالةstate space search
class State:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = [[None for _ in range(cols)] for _ in range(rows)]
        self.magnet_position = None
        self.red_block_position = None
        self.selected_piece_position = None  # For the selected piece

    # هون بوصل لخلية معينة وبحدد محتواها
    def set_cell(self, row, col, value):
        self.board[row][col] = value

    # هون رح انشأ كائن من مغناطيس ورح حدد مكانو بالتابع السابق
    def add_magnet(self, row, col, magnet_type, polarity):
        magnet = Magnet(magnet_type, polarity)
        self.set_cell(row, col, magnet)
        self.magnet_position = (row, col)

    # هون رح ضيف للخلية كائن من صف كنلة
    def add_block(self, row, col, block_type):
        block = Block(block_type)
        self.set_cell(row, col, block)
        if block_type == "R":
            self.red_block_position = (row, col)

    # هون رح شوف امكانية الوصول للخلية
    def can_move(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    # في هذا التابع اقوم بتطبيق مبدأ state space search
    # حيث يقوم بنسخ الرقعة القديمة واقوم باجراء
    # التعديل عليها لتصبح رقعة جديدة وفق مبدأ رقعة بالاضافة الى عملية يقوم باعطاء رقعةجديدة
    def move_piece(self, from_row, from_col, to_row, to_col):
        """Move a piece to a new location and generate a new state."""
        if self.can_move(to_row, to_col):

            target_cell = self.board[to_row][to_col]
            if isinstance(target_cell, Block) and target_cell.block_type == "g":
                return None

            new_state = State(self.rows, self.cols)
            new_state.board = [row[:] for row in self.board]

            moving_piece = new_state.board[from_row][from_col]
            new_state.board[to_row][to_col] = moving_piece
            new_state.board[from_row][from_col] = None

            if isinstance(moving_piece, Magnet) and moving_piece.magnet_type == "N":
                self.move_neighboring_gray_blocks(new_state, to_row, to_col)

            if isinstance(moving_piece, Block) and moving_piece.block_type == "R":
                self.attract_neighboring_gray_blocks(new_state, to_row, to_col)

            return new_state

        return None

    # تابع التآثير على الجوار من القطع المعدنية
    def move_neighboring_gray_blocks(self, new_state, to_row, to_col):
        # مصفوفة الجوار فوق تحت يسار يمين
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            neighbor_row = to_row + dr
            neighbor_col = to_col + dc

            if self.can_move(neighbor_row, neighbor_col):
                neighbor_cell = new_state.board[neighbor_row][neighbor_col]
                if isinstance(neighbor_cell, Block) and neighbor_cell.block_type == "g":
                    target_row = neighbor_row + dr
                    target_col = neighbor_col + dc

                    if self.can_move(target_row, target_col):
                        if new_state.board[target_row][target_col] is None:
                            new_state.board[target_row][target_col] = Block("g")
                            new_state.board[neighbor_row][neighbor_col] = None
                        elif (
                            isinstance(new_state.board[target_row][target_col], Block)
                            and new_state.board[target_row][target_col].block_type
                            == "W"
                        ):
                            new_state.board[target_row][target_col] = Block("g")
                            new_state.board[neighbor_row][neighbor_col] = None

    # تابع الجذب لتآثير القطع الحمراء
    def attract_neighboring_gray_blocks(self, new_state, to_row, to_col):
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        for dr, dc in directions:
            neighbor_row = to_row + dr
            neighbor_col = to_col + dc

            if self.can_move(neighbor_row, neighbor_col):
                neighbor_cell = new_state.board[neighbor_row][neighbor_col]
                if isinstance(neighbor_cell, Block) and neighbor_cell.block_type == "g":
                    target_row = to_row + (dr // 2)
                    target_col = to_col + (dc // 2)

                    if self.can_move(target_row, target_col):
                        if new_state.board[target_row][target_col] is None:
                            new_state.board[target_row][target_col] = Block("g")
                            new_state.board[neighbor_row][neighbor_col] = None
                        elif (
                            isinstance(new_state.board[target_row][target_col], Block)
                            and new_state.board[target_row][target_col].block_type
                            == "W"
                        ):
                            new_state.board[target_row][target_col] = Block("g")
                            new_state.board[neighbor_row][neighbor_col] = None

    # تابع للتشييك على الوصول الى حالة نهائية
    def check_solution(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if (
                    isinstance(self.board[row][col], Block)
                    and self.board[row][col].block_type == "W"
                ):
                    return False
        return True

    def redraw(self):
        return self.board


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Logic Magnets Game")
        self.state = State(5, 5)
        self.selected_piece_position = None

        # هون رح عين الرقعة
        self.buttons = [[None for _ in range(5)] for _ in range(5)]
        for row in range(5):
            for col in range(5):
                btn = tk.Button(
                    self.master,
                    text=" ",
                    width=5,
                    height=2,
                    command=lambda r=row, c=col: self.select_piece(r, c),
                )
                btn.grid(row=row, column=col)
                self.buttons[row][col] = btn

            self.state.add_block(0, 0, "W")
            self.state.add_block(0, 2, "W")
            self.state.add_block(2, 2, "W")
            self.state.add_block(1, 1, "g")
            self.state.add_block(1, 2, "g")
            self.state.add_magnet(2, 0, "N", "North")
        self.update_board()

    def update_board(self):
        for row in range(5):
            for col in range(5):
                item = self.state.redraw()[row][col]
                if isinstance(item, Magnet):
                    self.buttons[row][col].config(text=str(item), bg="lightblue")
                elif isinstance(item, Block):
                    if item.block_type == "g":
                        self.buttons[row][col].config(
                            text="g", bg="gray"
                        )  # قطعة معدنية رمادية
                    elif item.block_type == "W":
                        self.buttons[row][col].config(
                            text="W", bg="lightgreen"
                        )  # قطعة بيضاء
                    elif item.block_type == "R":
                        self.buttons[row][col].config(text="R", bg="red")  # قطعة حمراء
                else:
                    self.buttons[row][col].config(text=" ", bg="SystemButtonFace")

    def select_piece(self, new_row, new_col):
        if self.state.selected_piece_position is None:

            piece = self.state.redraw()[new_row][new_col]
            if piece and (
                isinstance(piece, Block)
                and (piece.block_type == "R" or piece.block_type == "g")
                or (isinstance(piece, Magnet) and piece.magnet_type == "N")
            ):
                self.state.selected_piece_position = (new_row, new_col)
                self.highlight_selected_piece(new_row, new_col)
        else:
            selected_row, selected_col = self.state.selected_piece_position
            new_state = self.state.move_piece(
                selected_row, selected_col, new_row, new_col
            )
            if new_state:
                self.state = new_state
                self.state.selected_piece_position = None
                self.update_board()
                if self.state.check_solution():
                    messagebox.showinfo(
                        "Information", "You have reached the final state!"
                    )
            self.clear_highlight(selected_row, selected_col)

    def highlight_selected_piece(self, row, col):
        self.buttons[row][col].config(bg="lightyellow")

    def clear_highlight(self, row, col):
        piece = self.state.redraw()[row][col]
        if isinstance(piece, Magnet):
            self.buttons[row][col].config(bg="lightblue")
        elif isinstance(piece, Block):
            if piece.block_type == "g":
                self.buttons[row][col].config(bg="gray")
            elif piece.block_type == "W":
                self.buttons[row][col].config(bg="lightgreen")
            elif piece.block_type == "R":
                self.buttons[row][col].config(bg="red")
        else:
            self.buttons[row][col].config(bg="SystemButtonFace")


if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
