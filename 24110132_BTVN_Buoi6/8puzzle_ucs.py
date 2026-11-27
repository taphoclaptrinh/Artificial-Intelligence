# MSSV: 24110132

import heapq
import random
import time
import threading
import tkinter as tk
from tkinter import messagebox

# ==============================================================================
# 1. THUẬT TOÁN UCS (UNIFORM-COST SEARCH) & BÀI TOÁN 8-PUZZLE
# ==============================================================================

GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MAX_EXPANSIONS = 50000
MAX_TRACE_STEPS = 150


class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = depth


class Problem:
    def __init__(self, initial_state, is_goal, actions, result, step_cost):
        self.initial_state = initial_state
        self.is_goal = is_goal
        self.actions = actions
        self.result = result
        self.step_cost = step_cost


def puzzle_is_goal(state):
    return state == GOAL_STATE


def puzzle_actions(state):
    i = state.index(0)
    acts = []
    if i % 3 != 0:
        acts.append("Left")
    if i % 3 != 2:
        acts.append("Right")
    if i >= 3:
        acts.append("Up")
    if i <= 5:
        acts.append("Down")
    return acts


def puzzle_result(state, action):
    step = {"Left": -1, "Right": 1, "Up": -3, "Down": 3}
    s = list(state)
    i = s.index(0)
    j = i + step[action]
    s[i], s[j] = s[j], s[i]
    return tuple(s)


def step_cost_uniform(state, action, next_state):
    return 1


def step_cost_tile(state, action, next_state):
    # Chi phí bước đi bằng chính giá trị của ô số vừa trượt vào ô trống
    zero_idx = state.index(0)
    return next_state[zero_idx]


def is_solvable(state):
    tiles = [x for x in state if x != 0]
    inv = sum(
        1
        for i in range(len(tiles))
        for j in range(i + 1, len(tiles))
        if tiles[i] > tiles[j]
    )
    return inv % 2 == 0


def generate_random_state(num_moves=8):
    state = GOAL_STATE
    last_state = None
    visited = {GOAL_STATE}

    for _ in range(num_moves):
        candidates = [puzzle_result(state, act) for act in puzzle_actions(state)]
        fresh = [s for s in candidates if s not in visited]
        if fresh:
            chosen = random.choice(fresh)
        else:
            non_backtrack = [s for s in candidates if s != last_state]
            chosen = random.choice(non_backtrack if non_backtrack else candidates)

        last_state = state
        state = chosen
        visited.add(state)

    if num_moves > 0 and state == GOAL_STATE:
        acts = puzzle_actions(state)
        state = puzzle_result(state, random.choice(acts))
    return state


def solution(node):
    acts, states, step_costs, cum_costs = [], [], [], []
    curr = node
    while curr is not None:
        states.append(curr.state)
        cum_costs.append(curr.path_cost)
        if curr.action is not None:
            acts.append(curr.action)
            step_costs.append(curr.path_cost - curr.parent.path_cost)
        curr = curr.parent
    acts.reverse()
    states.reverse()
    step_costs.reverse()
    cum_costs.reverse()
    return acts, states, step_costs, cum_costs


def format_state_inline(state):
    return f"({state[0]},{state[1]},{state[2]} | {state[3]},{state[4]},{state[5]} | {state[6]},{state[7]},{state[8]})"


def UCS(problem):
    start_time = time.perf_counter()

    if not is_solvable(problem.initial_state):
        elapsed = (time.perf_counter() - start_time) * 1000
        return {
            "solved": False,
            "reason": "Trạng thái không thể giải được (số nghịch thế lẻ).",
            "acts": [],
            "states": [problem.initial_state],
            "step_costs": [],
            "cum_costs": [0],
            "total_cost": 0,
            "expanded_count": 0,
            "explored_count": 0,
            "max_frontier": 0,
            "elapsed_ms": elapsed,
            "trace": [],
            "trace_truncated": False,
        }

    counter = 0
    root = Node(problem.initial_state, parent=None, action=None, path_cost=0, depth=0)
    frontier = [(0, counter, root)]
    frontier_best = {problem.initial_state: (0, None, counter)}
    explored = set()
    trace = []
    trace_truncated = False
    expanded_count = 0
    max_frontier = 1

    while frontier:
        g, _, node = heapq.heappop(frontier)

        # Bỏ qua bản sao cũ đã duyệt hoặc đã có chi phí tốt hơn trong frontier
        if node.state in explored:
            continue
        best_entry = frontier_best.get(node.state)
        if best_entry is not None and g > best_entry[0]:
            continue

        frontier_best.pop(node.state, None)

        if expanded_count >= MAX_EXPANSIONS:
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "solved": False,
                "reason": f"Vượt giới hạn an toàn ({MAX_EXPANSIONS:,} lần mở rộng).",
                "acts": [],
                "states": [problem.initial_state],
                "step_costs": [],
                "cum_costs": [0],
                "total_cost": 0,
                "expanded_count": expanded_count,
                "explored_count": len(explored),
                "max_frontier": max_frontier,
                "elapsed_ms": elapsed,
                "trace": trace,
                "trace_truncated": trace_truncated,
            }

        expanded_count += 1

        # Kiểm tra đích KHI LẤY RA (Pop) khỏi hàng đợi ưu tiên
        if problem.is_goal(node.state):
            if len(trace) < MAX_TRACE_STEPS:
                frontier_top = [
                    (fg, fst, fact)
                    for fst, (fg, fact, _) in sorted(
                        frontier_best.items(), key=lambda kv: (kv[1][0], kv[1][2])
                    )[:6]
                ]
                trace.append(
                    {
                        "step_num": expanded_count,
                        "popped_state": node.state,
                        "popped_g": node.path_cost,
                        "popped_action": node.action,
                        "is_goal": True,
                        "children": [],
                        "frontier_top": frontier_top,
                        "frontier_size": len(frontier_best),
                        "explored_count": len(explored),
                    }
                )
            else:
                trace_truncated = True

            elapsed = (time.perf_counter() - start_time) * 1000
            acts, states, step_costs, cum_costs = solution(node)
            return {
                "solved": True,
                "reason": "Thành công!",
                "acts": acts,
                "states": states,
                "step_costs": step_costs,
                "cum_costs": cum_costs,
                "total_cost": node.path_cost,
                "expanded_count": expanded_count,
                "explored_count": len(explored),
                "max_frontier": max_frontier,
                "elapsed_ms": elapsed,
                "trace": trace,
                "trace_truncated": trace_truncated,
            }

        explored.add(node.state)
        children_log = []

        for action in problem.actions(node.state):
            next_state = problem.result(node.state, action)
            sc = problem.step_cost(node.state, action, next_state)
            new_g = node.path_cost + sc

            if next_state in explored:
                children_log.append(
                    {
                        "action": action,
                        "state": next_state,
                        "step_cost": sc,
                        "g": new_g,
                        "status": "ignored_explored",
                    }
                )
            elif next_state not in frontier_best:
                counter += 1
                child = Node(next_state, node, action, new_g, node.depth + 1)
                heapq.heappush(frontier, (new_g, counter, child))
                frontier_best[next_state] = (new_g, action, counter)
                children_log.append(
                    {
                        "action": action,
                        "state": next_state,
                        "step_cost": sc,
                        "g": new_g,
                        "status": "added",
                    }
                )
            else:
                old_g, _, _ = frontier_best[next_state]
                if new_g < old_g:
                    counter += 1
                    child = Node(next_state, node, action, new_g, node.depth + 1)
                    heapq.heappush(frontier, (new_g, counter, child))
                    frontier_best[next_state] = (new_g, action, counter)
                    children_log.append(
                        {
                            "action": action,
                            "state": next_state,
                            "step_cost": sc,
                            "g": new_g,
                            "status": "updated",
                        }
                    )
                else:
                    children_log.append(
                        {
                            "action": action,
                            "state": next_state,
                            "step_cost": sc,
                            "g": new_g,
                            "status": "ignored_higher",
                        }
                    )

        max_frontier = max(max_frontier, len(frontier_best))

        if len(trace) < MAX_TRACE_STEPS:
            frontier_top = [
                (fg, fst, fact)
                for fst, (fg, fact, _) in sorted(
                    frontier_best.items(), key=lambda kv: (kv[1][0], kv[1][2])
                )[:6]
            ]
            trace.append(
                {
                    "step_num": expanded_count,
                    "popped_state": node.state,
                    "popped_g": node.path_cost,
                    "popped_action": node.action,
                    "is_goal": False,
                    "children": children_log,
                    "frontier_top": frontier_top,
                    "frontier_size": len(frontier_best),
                    "explored_count": len(explored),
                }
            )
        else:
            trace_truncated = True

    elapsed = (time.perf_counter() - start_time) * 1000
    return {
        "solved": False,
        "reason": "Không tìm thấy lời giải!",
        "acts": [],
        "states": [problem.initial_state],
        "step_costs": [],
        "cum_costs": [0],
        "total_cost": 0,
        "expanded_count": expanded_count,
        "explored_count": len(explored),
        "max_frontier": max_frontier,
        "elapsed_ms": elapsed,
        "trace": trace,
        "trace_truncated": trace_truncated,
    }


# ==============================================================================
# 2. GIAO DIỆN NGƯỜI DÙNG TKINTER (KHÔNG CẦN CÀI THÊM THƯ VIỆN)
# ==============================================================================

class EightPuzzleUCSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver - UCS | MSSV: 24110132")
        self.root.geometry("960x640")
        self.root.resizable(False, False)
        self.root.configure(bg="#0b1329")

        # Cấu hình dữ liệu
        self.preset_1 = (1, 2, 3, 4, 0, 6, 7, 5, 8)
        self.preset_2 = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        self.preset_3 = (1, 2, 3, 5, 0, 6, 4, 7, 8)
        self.current_state = self.preset_1
        self.cost_mode = "uniform"  # "uniform" | "tile"
        self.log_tab = "solution"   # "solution" | "trace"

        # Kết quả tìm kiếm & trạng thái chạy
        self.last_result = None
        self.solution_actions = []
        self.solution_states = [self.current_state]
        self.solution_step_costs = []
        self.solution_cum_costs = [0]
        self.current_step = 0
        self.is_playing = False
        self.is_searching = False

        # Quản lý timer & thanh trượt an toàn
        self._play_after_id = None
        self._anim_after_id = None
        self._updating_slider = False

        self._build_ui()
        self.draw_board(self.current_state)

    def _build_ui(self):
        # 1. Header
        header = tk.Frame(self.root, bg="#1a1c36", padx=16, pady=10)
        header.pack(fill="x", padx=12, pady=(10, 6))

        tk.Label(
            header,
            text="🧩 BÀI TOÁN 8-PUZZLE (UCS - UNIFORM-COST SEARCH)",
            font=("Segoe UI", 14, "bold"),
            fg="#a78bfa",
            bg="#1a1c36",
        ).pack(side="left")
        tk.Label(
            header,
            text="MSSV: 24110132",
            font=("Segoe UI", 10, "bold"),
            fg="#94a3b8",
            bg="#1a1c36",
        ).pack(side="right")

        # 2. Main content: 2 cột
        main_box = tk.Frame(self.root, bg="#0b1329")
        main_box.pack(fill="both", expand=True, padx=12, pady=4)

        # CỘT TRÁI: Bàn cờ Canvas + Thanh trượt + Nút phát lại
        left_frame = tk.Frame(main_box, bg="#161938", padx=14, pady=12, relief="ridge", bd=1)
        left_frame.pack(side="left", fill="both", padx=(0, 6))

        self.tile_size = 88
        self.tile_gap = 8
        self.margin = 12
        self.canvas_size = self.margin * 2 + 3 * self.tile_size + 2 * self.tile_gap

        self.canvas = tk.Canvas(
            left_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#0b1329",
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(pady=4)
        self.canvas.bind("<Button-1>", self.on_tile_clicked)

        self.step_info_lbl = tk.Label(
            left_frame,
            text="Bước: 0 / 0 | Bắt đầu | g(n) = 0",
            font=("Segoe UI", 10, "bold"),
            fg="#facc15",
            bg="#161938",
        )
        self.step_info_lbl.pack(pady=4)

        self.step_scale = tk.Scale(
            left_frame,
            from_=0,
            to=0,
            orient="horizontal",
            showvalue=True,
            command=self.on_slider_change,
            bg="#161938",
            fg="#a78bfa",
            highlightthickness=0,
            troughcolor="#27274a",
            activebackground="#4f46e5",
        )
        self.step_scale.pack(fill="x", padx=6, pady=2)

        ctrl_box = tk.Frame(left_frame, bg="#161938")
        ctrl_box.pack(pady=8)

        btn_opt = {"font": ("Segoe UI", 9, "bold"), "relief": "flat", "bd": 0, "cursor": "hand2", "pady": 5}
        self.btn_prev = tk.Button(ctrl_box, text="◀ Trước", bg="#27274a", fg="#ffffff", width=9, command=self.go_prev, **btn_opt)
        self.btn_prev.grid(row=0, column=0, padx=4)

        self.btn_play = tk.Button(ctrl_box, text="▶ Chạy", bg="#16a34a", fg="#ffffff", width=9, command=self.toggle_play, **btn_opt)
        self.btn_play.grid(row=0, column=1, padx=4)

        self.btn_next = tk.Button(ctrl_box, text="Sau ▶", bg="#27274a", fg="#ffffff", width=9, command=self.go_next, **btn_opt)
        self.btn_next.grid(row=0, column=2, padx=4)

        tk.Label(
            left_frame,
            text="Mẹo: Click ô cạnh ô trống để tự chỉnh thế cờ\nÔ xanh lá là ô đang nằm đúng vị trí đích",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#161938",
            justify="center",
        ).pack(pady=(6, 0))

        # CỘT PHẢI: Mẫu + Chi phí + Tìm kiếm + Thống kê + Log / Trace
        right_frame = tk.Frame(main_box, bg="#161938", padx=16, pady=12, relief="ridge", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # Row 1: Chọn mẫu
        preset_row = tk.Frame(right_frame, bg="#161938")
        preset_row.pack(fill="x", pady=(0, 6))

        tk.Label(preset_row, text="Chọn mẫu:", font=("Segoe UI", 9, "bold"), fg="#e2e8f0", bg="#161938").pack(side="left", padx=(0, 6))
        p_opt = {"font": ("Segoe UI", 9, "bold"), "relief": "flat", "bd": 0, "cursor": "hand2", "padx": 10, "pady": 4}
        self.btn_m1 = tk.Button(preset_row, text="Mẫu 1", bg="#4f46e5", fg="#ffffff", command=self.load_preset_1, **p_opt)
        self.btn_m1.pack(side="left", padx=3)

        self.btn_m2 = tk.Button(preset_row, text="Mẫu 2", bg="#27274a", fg="#e2e8f0", command=self.load_preset_2, **p_opt)
        self.btn_m2.pack(side="left", padx=3)

        self.btn_m3 = tk.Button(preset_row, text="Mẫu 3", bg="#27274a", fg="#e2e8f0", command=self.load_preset_3, **p_opt)
        self.btn_m3.pack(side="left", padx=3)

        self.btn_shuffle = tk.Button(preset_row, text="🎲 Trộn (8 bước)", bg="#0284c7", fg="#ffffff", command=self.load_random_preset, **p_opt)
        self.btn_shuffle.pack(side="right")

        # Row 2: Chế độ chi phí
        cost_row = tk.Frame(right_frame, bg="#161938")
        cost_row.pack(fill="x", pady=(0, 8))

        tk.Label(cost_row, text="Chi phí g(n):", font=("Segoe UI", 9, "bold"), fg="#e2e8f0", bg="#161938").pack(side="left", padx=(0, 6))
        self.btn_cost_uni = tk.Button(
            cost_row,
            text="Chi phí = 1 (Đều)",
            bg="#4f46e5",
            fg="#ffffff",
            command=lambda: self.set_cost_mode("uniform"),
            **p_opt,
        )
        self.btn_cost_uni.pack(side="left", padx=3)

        self.btn_cost_tile = tk.Button(
            cost_row,
            text="Chi phí = Giá trị ô",
            bg="#27274a",
            fg="#e2e8f0",
            command=lambda: self.set_cost_mode("tile"),
            **p_opt,
        )
        self.btn_cost_tile.pack(side="left", padx=3)

        # Row 3: Nút Bắt đầu tìm kiếm & Đặt lại
        action_row = tk.Frame(right_frame, bg="#161938")
        action_row.pack(fill="x", pady=4)

        self.btn_search = tk.Button(
            action_row,
            text="▶ BẮT ĐẦU TÌM KIẾM (UCS)",
            bg="#4f46e5",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=8,
            command=self.start_ucs_search,
        )
        self.btn_search.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_reset = tk.Button(
            action_row,
            text="🔄 Đặt lại",
            bg="#475569",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=8,
            command=self.reset_to_init,
        )
        self.btn_reset.pack(side="right")

        # Row 4: Thống kê
        self.stat_lbl = tk.Label(
            right_frame,
            text="Trạng thái: Sẵn sàng  •  Tổng g(n): 0  •  Số bước: 0  •  Thời gian: 0 ms",
            font=("Segoe UI", 9, "bold"),
            fg="#a78bfa",
            bg="#161938",
        )
        self.stat_lbl.pack(anchor="w", pady=(6, 4))

        # Row 5: Tab chuyển đổi Lời giải / Trace UCS
        tab_row = tk.Frame(right_frame, bg="#161938")
        tab_row.pack(fill="x", pady=(2, 4))

        t_opt = {"font": ("Segoe UI", 9, "bold"), "relief": "flat", "bd": 0, "cursor": "hand2", "padx": 10, "pady": 4}
        self.btn_tab_sol = tk.Button(
            tab_row,
            text="📄 Lịch sử lời giải",
            bg="#059669",
            fg="#ffffff",
            command=lambda: self.set_log_tab("solution"),
            **t_opt,
        )
        self.btn_tab_sol.pack(side="left", padx=(0, 4))

        self.btn_tab_trace = tk.Button(
            tab_row,
            text="🔍 Trace UCS (Priority Queue)",
            bg="#27274a",
            fg="#e2e8f0",
            command=lambda: self.set_log_tab("trace"),
            **t_opt,
        )
        self.btn_tab_trace.pack(side="left")

        # Khung log + thanh cuộn
        log_box = tk.Frame(right_frame, bg="#161938")
        log_box.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            log_box,
            bg="#0b1329",
            fg="#e2e8f0",
            font=("Consolas", 9),
            relief="sunken",
            bd=1,
            wrap="none",
        )
        log_scroll_y = tk.Scrollbar(log_box, orient="vertical", command=self.log_text.yview)
        log_scroll_x = tk.Scrollbar(log_box, orient="horizontal", command=self.log_text.xview)
        self.log_text.configure(yscrollcommand=log_scroll_y.set, xscrollcommand=log_scroll_x.set)

        log_scroll_y.pack(side="right", fill="y")
        log_scroll_x.pack(side="bottom", fill="x")
        self.log_text.pack(side="left", fill="both", expand=True)

    # ==========================================================================
    # QUẢN LÝ TIMER & VẼ BÀN CỜ
    # ==========================================================================

    def _cancel_timers(self):
        if self._play_after_id is not None:
            try:
                self.root.after_cancel(self._play_after_id)
            except Exception:
                pass
            self._play_after_id = None

        if self._anim_after_id is not None:
            try:
                self.root.after_cancel(self._anim_after_id)
            except Exception:
                pass
            self._anim_after_id = None

    def _get_coords(self, r, c):
        x = self.margin + c * (self.tile_size + self.tile_gap)
        y = self.margin + r * (self.tile_size + self.tile_gap)
        return x, y

    def draw_board(self, state, moving_tile=None, moving_x=None, moving_y=None):
        self.canvas.delete("all")
        for idx, val in enumerate(state):
            r = idx // 3
            c = idx % 3
            x, y = self._get_coords(r, c)

            if moving_tile is not None and val == moving_tile:
                self._draw_tile(x, y, 0, idx)
                continue
            self._draw_tile(x, y, val, idx)

        if moving_tile is not None and moving_x is not None and moving_y is not None:
            self._draw_tile(moving_x, moving_y, moving_tile, None, is_sliding=True)

    def _draw_tile(self, x, y, val, idx, is_sliding=False):
        w = self.tile_size
        h = self.tile_size
        if val == 0:
            self.canvas.create_rectangle(
                x, y, x + w, y + h, fill="#161938", outline="#27274a", width=2, dash=(4, 4)
            )
            return

        in_goal_pos = (idx is not None) and (val == idx + 1)
        if is_sliding:
            bg_col = "#818cf8"
            bd_col = "#facc15"
        elif in_goal_pos:
            bg_col = "#059669"
            bd_col = "#6ee7b7"
        else:
            bg_col = "#6366f1"
            bd_col = "#a5b4fc"

        self.canvas.create_rectangle(x, y, x + w, y + h, fill=bg_col, outline=bd_col, width=2)
        self.canvas.create_text(
            x + w / 2, y + h / 2, text=str(val), font=("Segoe UI", 22, "bold"), fill="#ffffff"
        )
        if self.cost_mode == "tile":
            self.canvas.create_text(
                x + w - 7,
                y + h - 6,
                text=f"c={val}",
                font=("Segoe UI", 8, "bold"),
                fill="#e2e8f0",
                anchor="se",
            )

    def animate_step(self, s_from, s_to, on_finish):
        if self._anim_after_id is not None:
            try:
                self.root.after_cancel(self._anim_after_id)
            except Exception:
                pass
            self._anim_after_id = None

        z_from = s_from.index(0)
        z_to = s_to.index(0)

        if z_from == z_to:
            self.draw_board(s_to)
            if on_finish:
                on_finish()
            return

        moving_val = s_from[z_to]
        r_src, c_src = z_to // 3, z_to % 3
        r_dst, c_dst = z_from // 3, z_from % 3

        x_start, y_start = self._get_coords(r_src, c_src)
        x_end, y_end = self._get_coords(r_dst, c_dst)

        frames = 8
        cur = 0

        def step():
            nonlocal cur
            self._anim_after_id = None
            cur += 1
            t = cur / frames
            self.draw_board(
                s_from,
                moving_tile=moving_val,
                moving_x=x_start + (x_end - x_start) * t,
                moving_y=y_start + (y_end - y_start) * t,
            )
            if cur < frames:
                self._anim_after_id = self.root.after(16, step)
            else:
                self.draw_board(s_to)
                if on_finish:
                    on_finish()

        step()

    # ==========================================================================
    # TƯƠNG TÁC MẪU, CHẾ ĐỘ CHI PHÍ & CLICK Ô
    # ==========================================================================

    def on_tile_clicked(self, event):
        if self.is_playing or self.is_searching:
            return

        c = (event.x - self.margin) // (self.tile_size + self.tile_gap)
        r = (event.y - self.margin) // (self.tile_size + self.tile_gap)

        if not (0 <= r < 3 and 0 <= c < 3):
            return

        click_idx = r * 3 + c
        zero_idx = self.current_state.index(0)
        zr, zc = zero_idx // 3, zero_idx % 3

        if abs(r - zr) + abs(c - zc) == 1:
            s = list(self.current_state)
            s[zero_idx], s[click_idx] = s[click_idx], s[zero_idx]
            new_state = tuple(s)

            s_from = self.current_state
            self.current_state = new_state
            self.reset_to_init(keep_state=True)
            self._reset_preset_btn_colors()
            self.animate_step(s_from, new_state, on_finish=None)

    def _reset_preset_btn_colors(self):
        self.btn_m1.configure(bg="#27274a", fg="#e2e8f0")
        self.btn_m2.configure(bg="#27274a", fg="#e2e8f0")
        self.btn_m3.configure(bg="#27274a", fg="#e2e8f0")

    def load_preset_1(self):
        if self.is_searching:
            return
        self.current_state = self.preset_1
        self._reset_preset_btn_colors()
        self.btn_m1.configure(bg="#4f46e5", fg="#ffffff")
        self.reset_to_init()

    def load_preset_2(self):
        if self.is_searching:
            return
        self.current_state = self.preset_2
        self._reset_preset_btn_colors()
        self.btn_m2.configure(bg="#4f46e5", fg="#ffffff")
        self.reset_to_init()

    def load_preset_3(self):
        if self.is_searching:
            return
        self.current_state = self.preset_3
        self._reset_preset_btn_colors()
        self.btn_m3.configure(bg="#4f46e5", fg="#ffffff")
        self.reset_to_init()

    def load_random_preset(self):
        if self.is_searching:
            return
        self.current_state = generate_random_state(8)
        self._reset_preset_btn_colors()
        self.reset_to_init()

    def set_cost_mode(self, mode):
        if self.is_searching or self.cost_mode == mode:
            return
        self.cost_mode = mode
        if mode == "uniform":
            self.btn_cost_uni.configure(bg="#4f46e5", fg="#ffffff")
            self.btn_cost_tile.configure(bg="#27274a", fg="#e2e8f0")
        else:
            self.btn_cost_uni.configure(bg="#27274a", fg="#e2e8f0")
            self.btn_cost_tile.configure(bg="#4f46e5", fg="#ffffff")
        self.reset_to_init()

    def set_log_tab(self, tab):
        if self.log_tab == tab:
            return
        self.log_tab = tab
        if tab == "solution":
            self.btn_tab_sol.configure(bg="#059669", fg="#ffffff")
            self.btn_tab_trace.configure(bg="#27274a", fg="#e2e8f0")
        else:
            self.btn_tab_sol.configure(bg="#27274a", fg="#e2e8f0")
            self.btn_tab_trace.configure(bg="#059669", fg="#ffffff")
        self._render_log()

    def reset_to_init(self, keep_state=False):
        self._cancel_timers()
        self.is_playing = False
        self.btn_play.configure(text="▶ Chạy", bg="#16a34a")

        self.last_result = None
        self.solution_actions = []
        self.solution_states = [self.current_state]
        self.solution_step_costs = []
        self.solution_cum_costs = [0]
        self.current_step = 0

        self._updating_slider = True
        self.step_scale.configure(to=0)
        self.step_scale.set(0)
        self._updating_slider = False

        self.draw_board(self.current_state)
        self.step_info_lbl.configure(text="Bước: 0 / 0 | Bắt đầu | g(n) = 0", fg="#facc15")
        self.stat_lbl.configure(
            text="Trạng thái: Sẵn sàng  •  Tổng g(n): 0  •  Số bước: 0  •  Thời gian: 0 ms",
            fg="#a78bfa",
        )
        if not keep_state:
            self.log_text.delete("1.0", tk.END)

    # ==========================================================================
    # CHẠY TÌM KIẾM UCS & HIỂN THỊ KẾT QUẢ / TRACE
    # ==========================================================================

    def start_ucs_search(self):
        if self.is_searching:
            return
        if not is_solvable(self.current_state):
            messagebox.showerror(
                "Lỗi",
                "Trạng thái này không có lời giải! Hãy click di chuyển các ô để tạo thế cờ hợp lệ.",
            )
            return

        self._cancel_timers()
        self.is_playing = False
        self.is_searching = True
        self.btn_play.configure(text="▶ Chạy", bg="#16a34a")
        self.btn_search.configure(state="disabled", text="⏳ Đang giải UCS...")
        self.stat_lbl.configure(text="Trạng thái: Đang tìm kiếm bằng UCS...", fg="#facc15")
        self.root.update_idletasks()

        cost_fn = step_cost_uniform if self.cost_mode == "uniform" else step_cost_tile
        prob = Problem(self.current_state, puzzle_is_goal, puzzle_actions, puzzle_result, cost_fn)

        def worker():
            res = UCS(prob)
            self.root.after(0, lambda: self.on_search_done(res))

        threading.Thread(target=worker, daemon=True).start()

    def on_search_done(self, res):
        self.is_searching = False
        self.btn_search.configure(state="normal", text="▶ BẮT ĐẦU TÌM KIẾM (UCS)")
        self.last_result = res

        if not res["solved"]:
            self.stat_lbl.configure(text=f"Trạng thái: {res['reason']}", fg="#ef4444")
            self._render_log()
            return

        self.solution_actions = res["acts"]
        self.solution_states = res["states"]
        self.solution_step_costs = res["step_costs"]
        self.solution_cum_costs = res["cum_costs"]
        self.current_step = 0

        num_steps = len(self.solution_actions)
        self._updating_slider = True
        self.step_scale.configure(to=num_steps)
        self.step_scale.set(0)
        self._updating_slider = False

        self.stat_lbl.configure(
            text=(
                f"Thành công!  •  Tổng g(n): {res['total_cost']}  •  Bước: {num_steps}  •  "
                f"Pop: {res['expanded_count']}  •  Max PQ: {res['max_frontier']}  •  {res['elapsed_ms']:.2f} ms"
            ),
            fg="#22c55e",
        )

        self._render_log()
        self.show_step(0, animate=False)

        if 0 < num_steps <= 40:
            self.is_playing = True
            self.btn_play.configure(text="⏸ Dừng", bg="#dc2626")
            self._play_after_id = self.root.after(400, self._auto_step)

    def _render_log(self):
        self.log_text.delete("1.0", tk.END)
        res = self.last_result
        if res is None:
            return

        cost_desc = "Chi phí mỗi bước = 1" if self.cost_mode == "uniform" else "Chi phí = giá trị ô trượt"

        if self.log_tab == "solution":
            self.log_text.insert(
                tk.END,
                f"=== KẾT QUẢ TÌM KIẾM CHI PHÍ ĐỒNG NHẤT (UCS) ===\n"
                f"Chế độ: {cost_desc}\n"
                f"Tổng chi phí g(n): {res['total_cost']}  •  Số bước: {len(res['acts'])}  •  "
                f"Số lần Pop: {res['expanded_count']}  •  Thời gian: {res['elapsed_ms']:.2f} ms\n\n",
            )
            if not res["solved"]:
                self.log_text.insert(tk.END, f"Lỗi: {res['reason']}\n")
                return

            acts = res["acts"]
            states = res["states"]
            sc = res["step_costs"]
            cg = res["cum_costs"]
            num_steps = len(acts)

            def write_step_block(idx):
                if idx == 0:
                    header = "0. Bắt đầu (g = 0)"
                else:
                    header = f"Bước {idx}: {acts[idx - 1]} (+{sc[idx - 1]} -> g = {cg[idx]})"
                st = states[idx]
                self.log_text.insert(tk.END, f"{header}\n{st[0:3]}\n{st[3:6]}\n{st[6:9]}\n\n")

            if num_steps <= 60:
                self.log_text.insert(tk.END, f"Hành động: {acts}\n\n")
                for i in range(len(states)):
                    write_step_block(i)
            else:
                for i in range(21):
                    write_step_block(i)
                self.log_text.insert(tk.END, f"... [Ẩn bớt {num_steps - 40} bước trung gian] ...\n\n")
                for i in range(num_steps - 19, num_steps + 1):
                    write_step_block(i)
        else:
            trace = res["trace"]
            self.log_text.insert(
                tk.END,
                f"=== TRACE VÒNG LẶP UCS (PRIORITY QUEUE THEO g(n)) ===\n"
                f"Chế độ: {cost_desc}  •  Tổng số lần Pop: {res['expanded_count']}\n\n",
            )
            status_txt = {
                "added": "+ Thêm vào PQ",
                "updated": "~ Cập nhật g thấp hơn",
                "ignored_explored": "x Đã ở Explored",
                "ignored_higher": "- Đã có g <= hơn",
            }
            for t in trace:
                act_lbl = t["popped_action"] if t["popped_action"] else "Gốc"
                goal_lbl = "ĐÍCH! (DỪNG)" if t["is_goal"] else "Chưa phải đích -> Mở rộng"
                self.log_text.insert(
                    tk.END,
                    f"[Vòng #{t['step_num']}] POP ({act_lbl}) | g={t['popped_g']} | {format_state_inline(t['popped_state'])}\n"
                    f"  Kiểm tra đích: {goal_lbl}\n",
                )
                if not t["is_goal"]:
                    for ch in t["children"]:
                        self.log_text.insert(
                            tk.END,
                            f"    -> {ch['action']:5} (+{ch['step_cost']} -> g={ch['g']:<2}) "
                            f"{format_state_inline(ch['state'])}  [{status_txt[ch['status']]}]\n",
                        )
                    pq_preview = ", ".join(
                        f"(g={fg}: {format_state_inline(fst)})" for fg, fst, _ in t["frontier_top"][:3]
                    )
                    extra = f" ... (+{t['frontier_size'] - 3} nút)" if t["frontier_size"] > 3 else ""
                    self.log_text.insert(
                        tk.END,
                        f"  PQ (size={t['frontier_size']}): {pq_preview}{extra} | Explored={t['explored_count']}\n\n",
                    )
                else:
                    self.log_text.insert(tk.END, "\n")

            if res.get("trace_truncated"):
                self.log_text.insert(
                    tk.END,
                    f"... [Chỉ hiển thị {MAX_TRACE_STEPS} vòng lặp đầu tiên để giữ giao diện mượt] ...\n",
                )

        self.log_text.see("1.0")

    # ==========================================================================
    # PHÁT LẠI CÁC BƯỚC GIẢI
    # ==========================================================================

    def show_step(self, idx, animate=True):
        if not self.solution_states or idx < 0 or idx >= len(self.solution_states):
            return

        prev = self.current_step
        self.current_step = idx

        self._updating_slider = True
        self.step_scale.set(idx)
        self._updating_slider = False

        total = len(self.solution_states) - 1
        cur_g = self.solution_cum_costs[idx] if idx < len(self.solution_cum_costs) else 0
        if idx == 0:
            self.step_info_lbl.configure(text=f"Bước: 0 / {total} | Bắt đầu | g(n) = 0", fg="#facc15")
        else:
            act = self.solution_actions[idx - 1]
            sc = self.solution_step_costs[idx - 1]
            is_goal_now = self.solution_states[idx] == GOAL_STATE
            lbl_color = "#22c55e" if is_goal_now else "#facc15"
            self.step_info_lbl.configure(
                text=f"Bước: {idx} / {total} | {act} (+{sc}) | g(n) = {cur_g}",
                fg=lbl_color,
            )

        if animate and (idx == prev + 1):
            self.animate_step(self.solution_states[prev], self.solution_states[idx], on_finish=None)
        else:
            self.draw_board(self.solution_states[idx])

    def on_slider_change(self, val):
        if self._updating_slider or self.is_playing:
            return
        idx = int(val)
        if idx != self.current_step:
            self.show_step(idx, animate=False)

    def go_prev(self):
        if self.is_playing:
            self.toggle_play()
        if self.current_step > 0:
            self.show_step(self.current_step - 1, animate=False)

    def go_next(self):
        if self.is_playing:
            self.toggle_play()
        if self.current_step < len(self.solution_states) - 1:
            self.show_step(self.current_step + 1, animate=True)

    def toggle_play(self):
        if len(self.solution_states) <= 1:
            return
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.configure(text="⏸ Dừng", bg="#dc2626")
            if self.current_step >= len(self.solution_states) - 1:
                self.show_step(0, animate=False)
            self._auto_step()
        else:
            self._cancel_timers()
            self.btn_play.configure(text="▶ Chạy", bg="#16a34a")

    def _auto_step(self):
        self._play_after_id = None
        if not self.is_playing:
            return
        if self.current_step < len(self.solution_states) - 1:
            next_idx = self.current_step + 1
            s_from = self.solution_states[self.current_step]
            s_to = self.solution_states[next_idx]

            self.current_step = next_idx
            self._updating_slider = True
            self.step_scale.set(next_idx)
            self._updating_slider = False

            total = len(self.solution_states) - 1
            act = self.solution_actions[next_idx - 1]
            sc = self.solution_step_costs[next_idx - 1]
            cur_g = self.solution_cum_costs[next_idx]
            lbl_color = "#22c55e" if s_to == GOAL_STATE else "#facc15"
            self.step_info_lbl.configure(
                text=f"Bước: {next_idx} / {total} | {act} (+{sc}) | g(n) = {cur_g}",
                fg=lbl_color,
            )

            num_steps = len(self.solution_actions)
            if num_steps <= 20:
                self.animate_step(
                    s_from, s_to, on_finish=lambda: setattr(self, "_play_after_id", self.root.after(480, self._auto_step))
                )
            elif num_steps <= 80:
                self.animate_step(
                    s_from, s_to, on_finish=lambda: setattr(self, "_play_after_id", self.root.after(150, self._auto_step))
                )
            else:
                self.draw_board(s_to)
                self._play_after_id = self.root.after(30, self._auto_step)
        else:
            self.is_playing = False
            self.btn_play.configure(text="▶ Chạy", bg="#16a34a")


if __name__ == "__main__":
    app_root = tk.Tk()
    app = EightPuzzleUCSGUI(app_root)
    app_root.mainloop()
