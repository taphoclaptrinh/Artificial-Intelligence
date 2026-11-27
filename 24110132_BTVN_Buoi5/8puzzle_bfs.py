# MSSV: 24110132

import time
import tkinter as tk
from tkinter import messagebox
import threading

# ==============================================================================
# 1. THUẬT TOÁN BFS & BÀI TOÁN 8-PUZZLE (THEO ĐÚNG BÀI HỌC VÀ SLIDE)
# ==============================================================================

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action

def Queue():
    return []

def enqueue(q, node):
    q.append(node)

def dequeue(q):
    return q.pop(0) if q else None

def is_empty(q):
    return len(q) == 0

def child_node(prob, parent, act):
    return Node(prob.result(parent.state, act), parent, act)

def solution(node):
    states, actions = [], []
    curr = node
    while curr is not None:
        states.append(curr.state)
        if curr.action is not None:
            actions.append(curr.action)
        curr = curr.parent
    states.reverse()
    actions.reverse()
    return actions, states

class Problem:
    def __init__(self, initial_state, goal_state, actions, result):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.actions = actions
        self.result = result

def is_goal(prob, state):
    return state == prob.goal_state

def actions_8puzzle(state):
    r, c = 0, 0
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                r, c = i, j
                break
    moves = []
    if r > 0: moves.append("Lên")
    if r < 2: moves.append("Xuống")
    if c > 0: moves.append("Trái")
    if c < 2: moves.append("Phải")
    return moves

def result_8puzzle(state, act):
    r, c = 0, 0
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                r, c = i, j
                break
    board = [list(row) for row in state]
    if act == "Lên":
        board[r][c], board[r - 1][c] = board[r - 1][c], board[r][c]
    elif act == "Xuống":
        board[r][c], board[r + 1][c] = board[r + 1][c], board[r][c]
    elif act == "Trái":
        board[r][c], board[r][c - 1] = board[r][c - 1], board[r][c]
    elif act == "Phải":
        board[r][c], board[r][c + 1] = board[r][c + 1], board[r][c]
    return tuple(tuple(row) for row in board)

def is_solvable(state, goal=((1, 2, 3), (4, 5, 6), (7, 8, 0))):
    flat = [val for row in state for val in row if val != 0]
    inv = sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) if flat[i] > flat[j])
    return inv % 2 == 0

def BFS(problem):
    start_time = time.perf_counter()
    start_node = Node(problem.initial_state)

    if is_goal(problem, start_node.state):
        elapsed = (time.perf_counter() - start_time) * 1000
        acts, sts = solution(start_node)
        return acts, sts, 1, 1, elapsed

    frontier = Queue()
    enqueue(frontier, start_node)
    frontier_set = {start_node.state}
    explored = set()

    while not is_empty(frontier):
        node = dequeue(frontier)
        frontier_set.discard(node.state)
        explored.add(node.state)

        for act in problem.actions(node.state):
            child = child_node(problem, node, act)
            if child.state not in explored and child.state not in frontier_set:
                if is_goal(problem, child.state):
                    elapsed = (time.perf_counter() - start_time) * 1000
                    acts, sts = solution(child)
                    return acts, sts, len(explored), len(frontier) + 1, elapsed
                enqueue(frontier, child)
                frontier_set.add(child.state)

    elapsed = (time.perf_counter() - start_time) * 1000
    return None, None, len(explored), len(frontier), elapsed

# ==============================================================================
# 2. GIAO DIỆN NGƯỜI DÙNG TKINTER ĐƠN GIẢN & ĐẸP MẮT
# ==============================================================================

class EightPuzzleBFSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver - BFS | MSSV: 24110132")
        self.root.geometry("860x590")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        # Cấu hình dữ liệu
        self.default_init = ((1, 2, 3), (4, 0, 6), (7, 5, 8))
        self.default_goal = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
        self.current_state = self.default_init

        # Kết quả tìm kiếm
        self.solution_actions = []
        self.solution_states = [self.default_init]
        self.current_step = 0
        self.is_playing = False

        self._build_ui()
        self.draw_board(self.current_state)

    def _build_ui(self):
        # 1. Header gọn gàng
        header = tk.Frame(self.root, bg="#1e293b", padx=16, pady=10)
        header.pack(fill="x", padx=12, pady=(10, 6))

        tk.Label(header, text="🧩 BÀI TOÁN 8-PUZZLE (BFS)", font=("Segoe UI", 14, "bold"), fg="#38bdf8", bg="#1e293b").pack(side="left")
        tk.Label(header, text="MSSV: 24110132", font=("Segoe UI", 10, "bold"), fg="#94a3b8", bg="#1e293b").pack(side="right")

        # 2. Main content: 2 cột đơn giản
        main_box = tk.Frame(self.root, bg="#0f172a")
        main_box.pack(fill="both", expand=True, padx=12, pady=4)

        # CỘT TRÁI: Bàn cờ Canvas + Nút điều khiển bước
        left_frame = tk.Frame(main_box, bg="#1e293b", padx=14, pady=12, relief="ridge", bd=1)
        left_frame.pack(side="left", fill="both", padx=(0, 6))

        # Canvas vẽ bàn cờ
        self.tile_size = 80
        self.tile_gap = 8
        self.margin = 12
        self.canvas_size = self.margin * 2 + 3 * self.tile_size + 2 * self.tile_gap

        self.canvas = tk.Canvas(
            left_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#0f172a",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(pady=4)
        self.canvas.bind("<Button-1>", self.on_tile_clicked)

        self.step_info_lbl = tk.Label(
            left_frame,
            text="Bước: 0 / 0 | Bắt đầu",
            font=("Segoe UI", 10, "bold"),
            fg="#facc15",
            bg="#1e293b"
        )
        self.step_info_lbl.pack(pady=4)

        # Thanh trượt bước
        self.step_scale = tk.Scale(
            left_frame,
            from_=0,
            to=0,
            orient="horizontal",
            showvalue=True,
            command=self.on_slider_change,
            bg="#1e293b",
            fg="#38bdf8",
            highlightthickness=0,
            troughcolor="#334155",
            activebackground="#0284c7"
        )
        self.step_scale.pack(fill="x", padx=6, pady=2)

        # Nút điều khiển phát lại
        ctrl_box = tk.Frame(left_frame, bg="#1e293b")
        ctrl_box.pack(pady=6)

        btn_opt = {"font": ("Segoe UI", 9, "bold"), "relief": "flat", "bd": 0, "cursor": "hand2", "pady": 4}
        self.btn_prev = tk.Button(ctrl_box, text="◀ Trước", bg="#334155", fg="#ffffff", width=8, command=self.go_prev, **btn_opt)
        self.btn_prev.grid(row=0, column=0, padx=4)

        self.btn_play = tk.Button(ctrl_box, text="▶ Chạy", bg="#16a34a", fg="#ffffff", width=8, command=self.toggle_play, **btn_opt)
        self.btn_play.grid(row=0, column=1, padx=4)

        self.btn_next = tk.Button(ctrl_box, text="Sau ▶", bg="#334155", fg="#ffffff", width=8, command=self.go_next, **btn_opt)
        self.btn_next.grid(row=0, column=2, padx=4)

        # CỘT PHẢI: Mẫu + Nút Giải + Thống kê + Log
        right_frame = tk.Frame(main_box, bg="#1e293b", padx=16, pady=12, relief="ridge", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # 1. Chọn Mẫu
        preset_row = tk.Frame(right_frame, bg="#1e293b")
        preset_row.pack(fill="x", pady=(0, 8))

        tk.Label(preset_row, text="Chọn mẫu:", font=("Segoe UI", 9, "bold"), fg="#e2e8f0", bg="#1e293b").pack(side="left", padx=(0, 6))
        self.btn_m1 = tk.Button(preset_row, text="Mẫu 1", bg="#0284c7", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", padx=10, pady=4, command=self.load_preset_1)
        self.btn_m1.pack(side="left", padx=4)

        self.btn_m2 = tk.Button(preset_row, text="Mẫu 2", bg="#334155", fg="#e2e8f0", font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", padx=10, pady=4, command=self.load_preset_2)
        self.btn_m2.pack(side="left", padx=4)

        # 2. Nút Bắt đầu tìm kiếm & Đặt lại
        action_row = tk.Frame(right_frame, bg="#1e293b")
        action_row.pack(fill="x", pady=4)

        self.btn_search = tk.Button(
            action_row,
            text="▶ BẮT ĐẦU TÌM KIẾM (BFS)",
            bg="#0284c7",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=8,
            command=self.start_bfs_search
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
            command=self.reset_to_init
        )
        self.btn_reset.pack(side="right")

        # 3. Thống kê kết quả 1 dòng gọn
        self.stat_lbl = tk.Label(
            right_frame,
            text="Trạng thái: Sẵn sàng  •  Số bước: 0  •  Thời gian: 0 ms",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        self.stat_lbl.pack(anchor="w", pady=(8, 4))

        # 4. Log chi tiết ma trận
        log_label = tk.Label(right_frame, text="Lịch sử lời giải:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b")
        log_label.pack(anchor="w", pady=(4, 2))

        self.log_text = tk.Text(right_frame, bg="#0f172a", fg="#e2e8f0", font=("Consolas", 9), height=11, relief="sunken", bd=1)
        log_scroll = tk.Scrollbar(right_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

    # ==========================================================================
    # VẼ BÀN CỜ & HOẠT ẢNH TRƯỢT
    # ==========================================================================

    def _get_coords(self, r, c):
        x = self.margin + c * (self.tile_size + self.tile_gap)
        y = self.margin + r * (self.tile_size + self.tile_gap)
        return x, y

    def draw_board(self, state, moving_tile=None, moving_x=None, moving_y=None):
        self.canvas.delete("all")
        for r in range(3):
            for c in range(3):
                x, y = self._get_coords(r, c)
                val = state[r][c]

                if moving_tile is not None and val == moving_tile:
                    self._draw_tile(x, y, 0)
                    continue
                self._draw_tile(x, y, val)

        if moving_tile is not None and moving_x is not None and moving_y is not None:
            self._draw_tile(moving_x, moving_y, moving_tile, is_sliding=True)

    def _draw_tile(self, x, y, val, is_sliding=False):
        w = self.tile_size
        h = self.tile_size
        if val == 0:
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="#1e293b", outline="#334155", width=2, dash=(4, 4))
        else:
            bg_col = "#38bdf8" if is_sliding else "#2563eb"
            bd_col = "#facc15" if is_sliding else "#60a5fa"
            self.canvas.create_rectangle(x, y, x + w, y + h, fill=bg_col, outline=bd_col, width=2)
            self.canvas.create_text(x + w / 2, y + h / 2, text=str(val), font=("Segoe UI", 22, "bold"), fill="#ffffff")

    def animate_step(self, s_from, s_to, on_finish):
        z_from, z_to = None, None
        for r in range(3):
            for c in range(3):
                if s_from[r][c] == 0: z_from = (r, c)
                if s_to[r][c] == 0: z_to = (r, c)

        if not z_from or not z_to or z_from == z_to:
            self.draw_board(s_to)
            if on_finish: on_finish()
            return

        r_src, c_src = z_to
        r_dst, c_dst = z_from
        moving_val = s_from[r_src][c_src]

        x_start, y_start = self._get_coords(r_src, c_src)
        x_end, y_end = self._get_coords(r_dst, c_dst)

        frames = 8
        cur = 0

        def step():
            nonlocal cur
            cur += 1
            t = cur / frames
            self.draw_board(s_from, moving_tile=moving_val, moving_x=x_start + (x_end - x_start) * t, moving_y=y_start + (y_end - y_start) * t)
            if cur < frames:
                self.root.after(16, step)
            else:
                self.draw_board(s_to)
                if on_finish: on_finish()

        step()

    # ==========================================================================
    # TƯƠNG TÁC CLICK TRỰC TIẾP ĐỂ SẮP XẾP BÀN CỜ
    # ==========================================================================

    def on_tile_clicked(self, event):
        if self.is_playing:
            return

        c = (event.x - self.margin) // (self.tile_size + self.tile_gap)
        r = (event.y - self.margin) // (self.tile_size + self.tile_gap)

        if not (0 <= r < 3 and 0 <= c < 3):
            return

        # Tìm ô trống
        zr, zc = 0, 0
        for i in range(3):
            for j in range(3):
                if self.current_state[i][j] == 0:
                    zr, zc = i, j
                    break

        # Nếu ô click liền kề ô trống -> trượt ô
        if abs(r - zr) + abs(c - zc) == 1:
            board = [list(row) for row in self.current_state]
            board[zr][zc], board[r][c] = board[r][c], board[zr][zc]
            new_state = tuple(tuple(row) for row in board)

            s_from = self.current_state
            self.current_state = new_state
            self.animate_step(s_from, new_state, on_finish=None)
            self.reset_to_init(keep_state=True)
            self._reset_preset_btn_colors()

    def _reset_preset_btn_colors(self):
        self.btn_m1.configure(bg="#334155")
        self.btn_m2.configure(bg="#334155")

    def load_preset_1(self):
        self.current_state = ((1, 2, 3), (4, 0, 6), (7, 5, 8))
        self.btn_m1.configure(bg="#0284c7")
        self.btn_m2.configure(bg="#334155")
        self.reset_to_init()

    def load_preset_2(self):
        self.current_state = ((1, 2, 3), (4, 5, 0), (7, 8, 6))
        self.btn_m1.configure(bg="#334155")
        self.btn_m2.configure(bg="#0284c7")
        self.reset_to_init()

    def reset_to_init(self, keep_state=False):
        self.is_playing = False
        self.btn_play.configure(text="▶ Chạy", bg="#16a34a")
        self.solution_actions = []
        self.solution_states = [self.current_state]
        self.current_step = 0
        self.step_scale.configure(to=0)
        self.step_scale.set(0)
        self.draw_board(self.current_state)
        self.step_info_lbl.configure(text="Bước: 0 / 0 | Bắt đầu")
        self.stat_lbl.configure(text="Trạng thái: Sẵn sàng  •  Số bước: 0  •  Thời gian: 0 ms", fg="#38bdf8")
        if not keep_state:
            self.log_text.delete("1.0", tk.END)

    def start_bfs_search(self):
        if not is_solvable(self.current_state, self.default_goal):
            messagebox.showerror("Lỗi", "Trạng thái này không có lời giải! Hãy click di chuyển các ô để tạo thế cờ hợp lệ.")
            return

        self.btn_search.configure(state="disabled", text="⏳ Đang giải...")
        self.stat_lbl.configure(text="Trạng thái: Đang tìm kiếm...", fg="#facc15")
        self.root.update()

        prob = Problem(self.current_state, self.default_goal, actions_8puzzle, result_8puzzle)

        def worker():
            acts, states, exp, front, el = BFS(prob)
            self.root.after(0, lambda: self.on_search_done(acts, states, exp, front, el))

        threading.Thread(target=worker, daemon=True).start()

    def on_search_done(self, acts, states, exp, front, el):
        self.btn_search.configure(state="normal", text="▶ BẮT ĐẦU TÌM KIẾM (BFS)")

        if states is None:
            self.stat_lbl.configure(text="Trạng thái: Không tìm thấy lời giải!", fg="#ef4444")
            return

        self.solution_actions = acts
        self.solution_states = states
        self.current_step = 0

        num_steps = len(acts)
        self.step_scale.configure(to=num_steps)
        self.step_scale.set(0)

        self.stat_lbl.configure(text=f"Trạng thái: Thành công!  •  Số bước: {num_steps}  •  Đã duyệt: {exp}  •  Thời gian: {el:.2f} ms", fg="#22c55e")

        # In log
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, f"Tìm thấy lời giải sau {num_steps} bước di chuyển:\n\n")
        for step, st in enumerate(states):
            act_str = f" ({acts[step - 1]})" if step > 0 else " (Bắt đầu)"
            self.log_text.insert(tk.END, f"Bước {step}:{act_str}\n")
            for row in st:
                self.log_text.insert(tk.END, f"[{row[0]} {row[1]} {row[2]}]\n")
            self.log_text.insert(tk.END, "\n")
        self.log_text.see("1.0")

        # Tự động phát hoạt ảnh
        self.show_step(0, animate=False)
        if num_steps > 0:
            self.is_playing = True
            self.btn_play.configure(text="⏸ Dừng", bg="#dc2626")
            self.root.after(400, self._auto_step)

    def show_step(self, idx, animate=True):
        if not self.solution_states or idx < 0 or idx >= len(self.solution_states):
            return

        prev = self.current_step
        self.current_step = idx
        self.step_scale.set(idx)

        act = "Bắt đầu" if idx == 0 else self.solution_actions[idx - 1]
        self.step_info_lbl.configure(text=f"Bước: {idx} / {len(self.solution_states)-1} | {act}")

        if animate and (idx == prev + 1):
            self.animate_step(self.solution_states[prev], self.solution_states[idx], on_finish=None)
        else:
            self.draw_board(self.solution_states[idx])

    def on_slider_change(self, val):
        if not self.is_playing:
            self.show_step(int(val), animate=False)

    def go_prev(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1, animate=False)

    def go_next(self):
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
            self.btn_play.configure(text="▶ Chạy", bg="#16a34a")

    def _auto_step(self):
        if not self.is_playing:
            return
        if self.current_step < len(self.solution_states) - 1:
            next_idx = self.current_step + 1
            s_from = self.solution_states[self.current_step]
            s_to = self.solution_states[next_idx]

            self.current_step = next_idx
            self.step_scale.set(next_idx)
            act = self.solution_actions[next_idx - 1]
            self.step_info_lbl.configure(text=f"Bước: {next_idx} / {len(self.solution_states)-1} | {act}")

            self.animate_step(s_from, s_to, on_finish=lambda: self.root.after(700, self._auto_step))
        else:
            self.is_playing = False
            self.btn_play.configure(text="▶ Chạy", bg="#16a34a")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = EightPuzzleBFSGUI(app_root)
    app_root.mainloop()
