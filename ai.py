"""
黑白棋 AI — Minimax + Alpha-Beta 剪枝 + 局面评估

搜素深度 8 层，配合强势评估函数：
- 位置价值表（角落极高、C位极低）
- 机动性（合法步数差）
- 角落控制
- 棋子数差异（残局权重增高）
- 边缘稳定性
"""
from board import OthelloBoard, EMPTY, BLACK, WHITE

# ── 经典位置价值表 ────────────────────────────────────────────
# 角落 100，C位 -50，边缘中等，X位低
POS_WEIGHT = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   1,   1,   1,   1,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   1,   1,   1,   1,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]

CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]
# C位：角落的邻格（危险位置）
C_SQUARES = [(0, 1), (1, 0), (1, 1),
             (0, 6), (1, 6), (1, 7),
             (6, 0), (6, 1), (7, 1),
             (6, 6), (6, 7), (7, 6)]
# X位：C位对角
X_SQUARES = [(1, 1), (1, 6), (6, 1), (6, 6)]


class OthelloAI:
    def __init__(self, max_depth=8, time_limit=8.0):
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.nodes_searched = 0

    def _select_depth(self, board):
        """自适应搜索深度：棋子越多搜索越深，保证响应速度
        开局-中盘用 depth=6（~2s），后期加深。
        """
        total = board.count(BLACK) + board.count(WHITE)
        if total < 30:
            return 6   # 开局-中盘，分支因子最高，depth=6 足够强
        elif total < 44:
            return 7   # 中盘后期，分支减少
        else:
            return 9   # 残局，分支少，可深搜

    def get_best_move(self, board, player):
        depth = self._select_depth(board)
        return self._search(board, player, depth)

    def _search(self, board, player, depth):
        moves = board.get_valid_moves(player)
        if not moves:
            return None
        if len(moves) == 1:
            return moves[0]

        self.nodes_searched = 0
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        moves = self._order_moves(moves, board, player)
        for move in moves:
            nb = board.clone()
            nb.make_move(move[0], move[1], player)
            score = self._minimax(nb, depth - 1, alpha, beta, False, player)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)

        return best_move

    def _order_moves(self, moves, board, player):
        """启发式排序：角落 > 边缘 > 翻转多 > C/X位靠后"""
        def key(m):
            r, c = m
            if (r, c) in CORNERS:
                return -100
            if (r, c) in C_SQUARES or (r, c) in X_SQUARES:
                return 100
            # 落子后翻转数（越多越好，但这里取负因为 sorted 默认升序）
            return -len(board.get_flipped(r, c, player))
        return sorted(moves, key=key)

    def _minimax(self, board, depth, alpha, beta, maximizing, ai_player):
        self.nodes_searched += 1

        if depth == 0 or board.is_game_over():
            return self._evaluate(board, ai_player)

        if maximizing:
            player = ai_player
        else:
            player = OthelloBoard.opponent(ai_player)

        moves = board.get_valid_moves(player)
        if not moves:
            # 无棋可下 → pass
            opp = OthelloBoard.opponent(player)
            if not board.has_valid_move(opp):
                return self._evaluate(board, ai_player)
            nb = board.clone()
            nb.current_player = opp
            return self._minimax(nb, depth - 1, alpha, beta, not maximizing, ai_player)

        moves = self._order_moves(moves, board, player)

        if maximizing:
            value = float('-inf')
            for m in moves:
                nb = board.clone()
                nb.make_move(m[0], m[1], player)
                value = max(value, self._minimax(nb, depth - 1, alpha, beta, False, ai_player))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for m in moves:
                nb = board.clone()
                nb.make_move(m[0], m[1], player)
                value = min(value, self._minimax(nb, depth - 1, alpha, beta, True, ai_player))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    # ── 局面评估 ───────────────────────────────────────────────

    def _evaluate(self, board, ai_player):
        opp = OthelloBoard.opponent(ai_player)
        total_pieces = board.count(BLACK) + board.count(WHITE)

        # 终局：直接返回胜/负
        if board.is_game_over():
            winner = board.get_winner()
            if winner == ai_player:
                return 100000 + (64 - total_pieces)  # 越快赢越好
            elif winner == opp:
                return -100000 - (64 - total_pieces)
            return 0

        score = 0.0

        # 1) 位置价值
        pos = 0
        for r in range(8):
            for c in range(8):
                p = board.grid[r][c]
                if p == ai_player:
                    pos += POS_WEIGHT[r][c]
                elif p == opp:
                    pos -= POS_WEIGHT[r][c]
        score += pos

        # 2) 角落控制（高权重）
        my_corners = sum(1 for c in CORNERS if board.grid[c[0]][c[1]] == ai_player)
        opp_corners = sum(1 for c in CORNERS if board.grid[c[0]][c[1]] == opp)
        score += 200 * (my_corners - opp_corners)

        # 3) 机动性（合法步数差 — 极重要）
        my_moves = len(board.get_valid_moves(ai_player))
        opp_moves = len(board.get_valid_moves(opp))
        if my_moves + opp_moves > 0:
            score += 30 * (my_moves - opp_moves)

        # 4) 棋子数 — 残局权重逐渐加大
        my_count = board.count(ai_player)
        opp_count = board.count(opp)
        parity_weight = 0.5 + 1.5 * (total_pieces / 64.0)  # 从0.5线性增长到2.0
        if my_count + opp_count > 0:
            score += parity_weight * 10 * (my_count - opp_count)

        # 5) 边缘稳定性（边线上的稳定子）
        stable = self._edge_stability(board, ai_player, opp)
        score += stable * 8

        # 6) 残局惩罚：如果己方在最后几步仍损失角落，大幅扣分
        if total_pieces > 50 and my_corners < opp_corners:
            score -= 100

        return score

    def _edge_stability(self, board, player, opponent):
        """简化边缘稳定性评估"""
        score = 0
        # 上边
        for c in range(8):
            if board.grid[0][c] == player:
                score += 1
            elif board.grid[0][c] == opponent:
                score -= 1
        # 下边 (去重首尾)
        for c in range(8):
            if board.grid[7][c] == player:
                score += 1
            elif board.grid[7][c] == opponent:
                score -= 1
        # 左边 (去重首尾)
        for r in range(1, 7):
            if board.grid[r][0] == player:
                score += 1
            elif board.grid[r][0] == opponent:
                score -= 1
        # 右边
        for r in range(1, 7):
            if board.grid[r][7] == player:
                score += 1
            elif board.grid[r][7] == opponent:
                score -= 1
        return score
