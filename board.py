"""
黑白棋 (Othello/Reversi) 核心逻辑
"""
EMPTY = 0
BLACK = 1  # 黑棋先手
WHITE = 2  # 白棋后手

PIECE_CHAR = {EMPTY: '·', BLACK: '●', WHITE: '○'}
PIECE_NAME = {EMPTY: '空', BLACK: '黑棋', WHITE: '白棋'}


class OthelloBoard:
    def __init__(self):
        self.reset()

    def reset(self):
        """标准开局：中心 4 子"""
        self.grid = [[EMPTY] * 8 for _ in range(8)]
        self.grid[3][3] = WHITE
        self.grid[3][4] = BLACK
        self.grid[4][3] = BLACK
        self.grid[4][4] = WHITE
        self.current_player = BLACK

    def clone(self):
        new = OthelloBoard.__new__(OthelloBoard)
        new.grid = [row[:] for row in self.grid]
        new.current_player = self.current_player
        return new

    @staticmethod
    def opponent(player):
        return BLACK if player == WHITE else WHITE

    @staticmethod
    def on_board(r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get_flipped(self, row, col, player):
        """返回放置 (row,col) 后会被翻转的对手棋子坐标列表"""
        if not self.on_board(row, col) or self.grid[row][col] != EMPTY:
            return []
        opp = self.opponent(player)
        flipped = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if not self.on_board(r, c) or self.grid[r][c] != opp:
                    continue
                while self.on_board(r, c) and self.grid[r][c] == opp:
                    r += dr
                    c += dc
                if self.on_board(r, c) and self.grid[r][c] == player:
                    # 回溯收集翻转的棋子
                    r, c = row + dr, col + dc
                    while self.grid[r][c] == opp:
                        flipped.append((r, c))
                        r += dr
                        c += dc
        return flipped

    def is_valid_move(self, row, col, player):
        if not self.on_board(row, col) or self.grid[row][col] != EMPTY:
            return False
        return len(self.get_flipped(row, col, player)) > 0

    def get_valid_moves(self, player):
        moves = []
        for r in range(8):
            for c in range(8):
                if self.is_valid_move(r, c, player):
                    moves.append((r, c))
        return moves

    def make_move(self, row, col, player):
        """执行落子，返回是否成功"""
        if not self.is_valid_move(row, col, player):
            return False
        flipped = self.get_flipped(row, col, player)
        self.grid[row][col] = player
        for r, c in flipped:
            self.grid[r][c] = player
        self.current_player = self.opponent(player)
        return True

    def has_valid_move(self, player):
        return len(self.get_valid_moves(player)) > 0

    def can_play(self, player):
        """当前玩家能否下棋（无合法时自动 pass）"""
        return self.has_valid_move(player)

    def is_game_over(self):
        return not self.has_valid_move(BLACK) and not self.has_valid_move(WHITE)

    def get_winner(self):
        bc = sum(row.count(BLACK) for row in self.grid)
        wc = sum(row.count(WHITE) for row in self.grid)
        if bc > wc:
            return BLACK
        if wc > bc:
            return WHITE
        return 0  # 平局

    def count(self, player):
        return sum(row.count(player) for row in self.grid)

    def set_position(self, position_dict):
        """从 {(r,c): player} 设置自定义初始局面"""
        self.grid = [[EMPTY] * 8 for _ in range(8)]
        for (r, c), player in position_dict.items():
            self.grid[r][c] = player
        self.current_player = BLACK

    def draw_board(self):
        """终端文本棋盘（调试用）"""
        lines = ['  a b c d e f g h']
        for r in range(8):
            row = f"{r+1} {' '.join(PIECE_CHAR[self.grid[r][c]] for c in range(8))}"
            lines.append(row)
        return '\n'.join(lines)
