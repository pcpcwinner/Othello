"""
黑白棋 GUI — Tkinter 图形界面

功能：
- 点击落子，高亮合法位置
- 设置初始棋盘布局
- 选择先手/后手
- 显示棋子数和状态
- AI 思考时显示"思考中..."
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from board import OthelloBoard, EMPTY, BLACK, WHITE, PIECE_CHAR, PIECE_NAME
from ai import OthelloAI

# 颜色方案
COLOR_BG = '#1a6b3c'        # 棋盘底色（深绿）
COLOR_GRID = '#0d4a2a'       # 网格线
COLOR_BOARD_BG = '#2a2a2a'   # 窗口背景
COLOR_BLACK = '#111111'      # 黑子
COLOR_WHITE = '#f0f0f0'      # 白子
COLOR_HINT = '#4caf50'       # 合法落子提示
COLOR_LAST_MOVE = '#ffeb3b'  # 上一步高亮
COLOR_SETUP_MODE = '#ff6600' # 设置模式下的棋盘边框色

CELL_SIZE = 64
BOARD_PADDING = 20
MARGIN = 10


class OthelloGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('黑白棋 Othello')
        self.root.configure(bg=COLOR_BOARD_BG)
        self.root.resizable(False, False)

        self.board = OthelloBoard()
        self.ai = OthelloAI()  # 自适应深度
        self.player_color = BLACK  # 玩家默认黑棋（先手）
        self.ai_color = WHITE
        self.last_move = None
        self.setup_mode = False     # 初始布局编辑模式
        self.setup_color = BLACK    # 当前放置的颜色（设置模式下）
        self.ai_thinking = False

        self._build_ui()
        self._refresh()

    # ── 界面构建 ────────────────────────────────────────────────

    def _build_ui(self):
        # 顶层框架
        self.top_frame = tk.Frame(self.root, bg=COLOR_BOARD_BG)
        self.top_frame.pack(fill=tk.X, pady=(10, 0))

        self.lbl_title = tk.Label(
            self.top_frame,
            text='黑白棋',
            font=('Arial', 20, 'bold'),
            fg='white', bg=COLOR_BOARD_BG
        )
        self.lbl_title.pack()

        # 状态栏
        self.lbl_status = tk.Label(
            self.top_frame,
            text='',
            font=('Arial', 12),
            fg='#cccccc', bg=COLOR_BOARD_BG
        )
        self.lbl_status.pack(pady=(2, 0))

        # 棋盘 Canvas
        board_px = CELL_SIZE * 8 + BOARD_PADDING * 2
        self.canvas = tk.Canvas(
            self.root,
            width=board_px,
            height=board_px,
            bg=COLOR_BOARD_BG,
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=5)
        self._draw_board_grid()
        self.canvas.bind('<Button-1>', self._on_click)

        # 信息栏
        self.info_frame = tk.Frame(self.root, bg=COLOR_BOARD_BG)
        self.info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.lbl_black = tk.Label(
            self.info_frame,
            text='● 黑棋: 2',
            font=('Arial', 12, 'bold'),
            fg='white', bg=COLOR_BOARD_BG
        )
        self.lbl_black.pack(side=tk.LEFT, padx=20)

        self.lbl_white = tk.Label(
            self.info_frame,
            text='○ 白棋: 2',
            font=('Arial', 12, 'bold'),
            fg='white', bg=COLOR_BOARD_BG
        )
        self.lbl_white.pack(side=tk.LEFT, padx=20)

        # 按钮栏
        self.btn_frame = tk.Frame(self.root, bg=COLOR_BOARD_BG)
        self.btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        self.btn_new = tk.Button(
            self.btn_frame, text='新游戏 (标准开局)',
            command=self._new_game,
            bg='#444', fg='white', relief=tk.FLAT,
            padx=12, pady=4, cursor='hand2'
        )
        self.btn_new.pack(side=tk.LEFT, padx=5)

        self.btn_setup = tk.Button(
            self.btn_frame, text='设置初始棋盘',
            command=self._toggle_setup_mode,
            bg='#5a3a1a', fg='white', relief=tk.FLAT,
            padx=12, pady=4, cursor='hand2'
        )
        self.btn_setup.pack(side=tk.LEFT, padx=5)

        self.btn_clear = tk.Button(
            self.btn_frame, text='清空棋盘',
            command=self._clear_board,
            bg='#5a1a1a', fg='white', relief=tk.FLAT,
            padx=12, pady=4, cursor='hand2'
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        self.lbl_mode = tk.Label(
            self.btn_frame,
            text='',
            font=('Arial', 10, 'bold'),
            fg=COLOR_SETUP_MODE, bg=COLOR_BOARD_BG
        )
        self.lbl_mode.pack(side=tk.LEFT, padx=15)

    def _draw_board_grid(self):
        self.canvas.delete('grid')
        x0 = BOARD_PADDING
        y0 = BOARD_PADDING
        size = CELL_SIZE * 8
        # 棋盘底色
        self.canvas.create_rectangle(
            x0, y0, x0 + size, y0 + size,
            fill=COLOR_BG, outline=COLOR_GRID, width=2, tags='grid'
        )
        # 网格线
        for i in range(9):
            pos = BOARD_PADDING + i * CELL_SIZE
            self.canvas.create_line(
                BOARD_PADDING, pos, BOARD_PADDING + size, pos,
                fill=COLOR_GRID, width=1, tags='grid'
            )
            self.canvas.create_line(
                pos, BOARD_PADDING, pos, BOARD_PADDING + size,
                fill=COLOR_GRID, width=1, tags='grid'
            )
        # 坐标标注
        for i, ch in enumerate('abcdefgh'):
            x = BOARD_PADDING + i * CELL_SIZE + CELL_SIZE // 2
            y = BOARD_PADDING - 12
            self.canvas.create_text(x, y, text=ch, fill='#888', font=('Arial', 9), tags='grid')
        for i in range(8):
            x = BOARD_PADDING - 16
            y = BOARD_PADDING + i * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_text(x, y, text=str(i + 1), fill='#888', font=('Arial', 9), tags='grid')

    # ── 坐标转换 ────────────────────────────────────────────────

    def _cell_from_click(self, event):
        col = (event.x - BOARD_PADDING) // CELL_SIZE
        row = (event.y - BOARD_PADDING) // CELL_SIZE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def _cell_to_pixel(self, row, col):
        x = BOARD_PADDING + col * CELL_SIZE
        y = BOARD_PADDING + row * CELL_SIZE
        return (x, y)

    # ── 重新绘制 ────────────────────────────────────────────────

    def _refresh(self):
        self.canvas.delete('pieces')
        self.canvas.delete('hints')
        self.canvas.delete('last')

        # 绘制设置模式边框
        if self.setup_mode:
            self.canvas.create_rectangle(
                BOARD_PADDING - 3, BOARD_PADDING - 3,
                BOARD_PADDING + CELL_SIZE * 8 + 3,
                BOARD_PADDING + CELL_SIZE * 8 + 3,
                outline=COLOR_SETUP_MODE, width=3, tags='setup_border'
            )
        else:
            self.canvas.delete('setup_border')

        # 绘制棋子
        for r in range(8):
            for c in range(8):
                p = self.board.grid[r][c]
                if p == EMPTY:
                    continue
                x, y = self._cell_to_pixel(r, c)
                cx = x + CELL_SIZE // 2
                cy = y + CELL_SIZE // 2
                radius = CELL_SIZE // 2 - 4
                color = COLOR_BLACK if p == BLACK else COLOR_WHITE
                outline = '#666' if p == BLACK else '#aaa'
                self.canvas.create_oval(
                    cx - radius, cy - radius, cx + radius, cy + radius,
                    fill=color, outline=outline, width=1, tags='pieces'
                )

        # 上一步高亮
        if self.last_move and not self.setup_mode:
            r, c = self.last_move
            x, y = self._cell_to_pixel(r, c)
            self.canvas.create_rectangle(
                x + 2, y + 2, x + CELL_SIZE - 2, y + CELL_SIZE - 2,
                outline=COLOR_LAST_MOVE, width=3, tags='last'
            )

        # 合法落子提示（不在设置模式 && 轮到玩家 && AI 不在思考）
        if not self.setup_mode and not self.ai_thinking:
            cur = self.board.current_player
            if cur == self.player_color:
                for r, c in self.board.get_valid_moves(cur):
                    x, y = self._cell_to_pixel(r, c)
                    cx = x + CELL_SIZE // 2
                    cy = y + CELL_SIZE // 2
                    self.canvas.create_oval(
                        cx - 6, cy - 6, cx + 6, cy + 6,
                        fill=COLOR_HINT, outline='', tags='hints'
                    )

        # 更新文本信息
        bc = self.board.count(BLACK)
        wc = self.board.count(WHITE)
        self.lbl_black.config(text=f'● 黑棋: {bc}')
        self.lbl_white.config(text=f'○ 白棋: {wc}')

        if self.setup_mode:
            color_name = '黑棋' if self.setup_color == BLACK else '白棋'
            self.lbl_mode.config(
                text=f'设置模式 — 点击放置 {color_name} (●/○ 切换), 右键切换颜色'
            )
            self.lbl_status.config(text='请在棋盘上摆放初始棋子，然后点击"开始游戏"')
        elif self.ai_thinking:
            self.lbl_status.config(text='AI 思考中...')
        elif self.board.is_game_over():
            winner = self.board.get_winner()
            if winner == self.player_color:
                msg = '你赢了！'
            elif winner == self.ai_color:
                msg = 'AI 赢了！'
            else:
                msg = '平局！'
            self.lbl_status.config(text=f'游戏结束 — {msg}')
        else:
            cur_name = '你' if self.board.current_player == self.player_color else 'AI'
            player_name = PIECE_NAME[self.board.current_player]
            self.lbl_status.config(
                text=f'轮到 {cur_name} ({player_name})'
                if self.board.current_player == self.player_color
                else f'轮到 AI ({player_name}) 思考...'
            )

    # ── 事件处理 ────────────────────────────────────────────────

    def _on_click(self, event):
        cell = self._cell_from_click(event)
        if cell is None:
            return

        if self.setup_mode:
            self._setup_click(cell)
            return

        if self.ai_thinking:
            return

        r, c = cell
        if self.board.current_player != self.player_color:
            return

        if not self.board.is_valid_move(r, c, self.player_color):
            return

        # 玩家落子
        self.board.make_move(r, c, self.player_color)
        self.last_move = (r, c)
        self._refresh()

        # 检查游戏结束
        if self.board.is_game_over():
            self._show_result()
            self._refresh()
            return

        # AI 回合
        self._ai_move()

    def _setup_click(self, cell):
        """设置模式下点击棋盘"""
        r, c = cell
        # 右键切换颜色（通过 event.num 无法在绑定中区分，所以在 _on_click 之前
        # 通过绑定 <Button-3> 处理。但这里直接用左键循环：空→当前色→空
        # 其实用左键也够了
        if self.board.grid[r][c] == self.setup_color:
            # 已存在当前颜色 → 移除
            self.board.grid[r][c] = EMPTY
        else:
            self.board.grid[r][c] = self.setup_color
        self._refresh()

    def _toggle_color(self, event):
        """设置模式下切换放置颜色"""
        self.setup_color = WHITE if self.setup_color == BLACK else BLACK
        self._refresh()

    # ── AI 走棋 ─────────────────────────────────────────────────

    def _ai_move(self):
        if self.board.is_game_over():
            self._show_result()
            self._refresh()
            return

        if not self.board.has_valid_move(self.ai_color):
            # AI pass
            self.board.current_player = self.player_color
            if not self.board.has_valid_move(self.player_color):
                self._show_result()
            self._refresh()
            return

        self.ai_thinking = True
        self._refresh()

        # 延时执行，让 UI 更新显示"思考中"
        self.root.after(10, self._do_ai_move)

    def _do_ai_move(self):
        move = self.ai.get_best_move(self.board, self.ai_color)
        self.ai_thinking = False

        if move is None:
            if not self.board.has_valid_move(self.player_color):
                self._show_result()
            self._refresh()
            return

        r, c = move
        self.board.make_move(r, c, self.ai_color)
        self.last_move = (r, c)
        self._refresh()

        if self.board.is_game_over():
            self._show_result()
            self._refresh()
            return

        # 玩家回合：检查是否可下
        if not self.board.has_valid_move(self.player_color):
            # 玩家被迫 pass
            self.board.current_player = self.ai_color
            if self.board.has_valid_move(self.ai_color):
                self._ai_move()
            else:
                self._show_result()
                self._refresh()
            return

        self._refresh()

    def _show_result(self):
        winner = self.board.get_winner()
        bc = self.board.count(BLACK)
        wc = self.board.count(WHITE)

        if winner == 0:
            msg = f'平局！\n黑棋 {bc} : {wc} 白棋'
            title = '平局'
        elif winner == self.player_color:
            msg = f'你赢了！\n黑棋 {bc} : {wc} 白棋\n但这是 AI 故意放水？再试一局吧。'
            title = '恭喜'
        else:
            msg = f'AI 赢了！\n黑棋 {bc} : {wc} 白棋\n再来一局？'
            title = 'AI 胜利'

        messagebox.showinfo(title, msg)

    # ── 控制按钮 ────────────────────────────────────────────────

    def _new_game(self):
        """标准开局"""
        self.setup_mode = False
        self.lbl_mode.config(text='')
        self.board.reset()
        self.last_move = None
        self.ai_thinking = False

        # 询问玩家选择先手/后手
        choice = messagebox.askquestion(
            '选择先后手',
            '你要先手（黑棋，先行）吗？\n\n选择"是" → 你先走\n选择"否" → AI 先走（你后手）'
        )
        if choice == 'yes':
            self.player_color = BLACK
            self.ai_color = WHITE
        else:
            self.player_color = WHITE
            self.ai_color = BLACK
            self.board.current_player = BLACK

        self._refresh()

        # 如果 AI 先手
        if self.board.current_player == self.ai_color:
            self._ai_move()

    def _toggle_setup_mode(self):
        """进入/退出设置模式"""
        if not self.setup_mode:
            # 进入设置模式
            self.setup_mode = True
            self.board.grid = [[EMPTY] * 8 for _ in range(8)]
            self.last_move = None
            self.ai_thinking = False

            # 绑定右键切换颜色
            self.canvas.bind('<Button-3>', self._toggle_color)
            # macOS 上右键也可能是 Button-2
            self.canvas.bind('<Button-2>', self._toggle_color)

            self.btn_setup.config(text='开始游戏', bg='#1a5a1a')
            self.btn_new.config(state=tk.DISABLED)
            self.lbl_mode.config(
                text='设置模式 — 左键放置/移除 ●, 右键切换 ●/○'
            )
            self._refresh()
        else:
            # 退出设置模式，开始游戏
            # 检查双方至少各有一子
            bc = self.board.count(BLACK)
            wc = self.board.count(WHITE)
            if bc == 0 or wc == 0:
                messagebox.showwarning('提示', '双方至少各需要一个棋子才能开始游戏！')
                return

            self.setup_mode = False
            self.canvas.unbind('<Button-3>')
            self.canvas.unbind('<Button-2>')
            self.btn_setup.config(text='设置初始棋盘', bg='#5a3a1a')
            self.btn_new.config(state=tk.NORMAL)
            self.lbl_mode.config(text='')

            # 选择先后手
            choice = messagebox.askquestion(
                '选择先后手',
                '你要先手（黑棋，先行）吗？\n\n选择"是" → 你先走\n选择"否" → AI 先走'
            )
            if choice == 'yes':
                self.player_color = BLACK
                self.ai_color = WHITE
                self.board.current_player = BLACK
            else:
                self.player_color = WHITE
                self.ai_color = BLACK
                self.board.current_player = BLACK

            self._refresh()

            # 检查当前玩家是否有合法棋步
            if self.board.current_player == self.player_color:
                if not self.board.has_valid_move(self.player_color):
                    messagebox.showinfo('提示', '玩家没有合法落子位置，AI 先行。')
                    self.board.current_player = self.ai_color
                    self._refresh()

            if self.board.current_player == self.ai_color:
                self._ai_move()

    def _clear_board(self):
        """清空棋盘（仅设置模式下）"""
        if not self.setup_mode:
            messagebox.showinfo('提示', '请先进入"设置初始棋盘"模式')
            return
        self.board.grid = [[EMPTY] * 8 for _ in range(8)]
        self._refresh()

    # ── 运行 ────────────────────────────────────────────────────

    def run(self):
        self.root.after(100, self._new_game)  # 启动后立即询问
        self.root.mainloop()
