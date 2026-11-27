# MSSV: 24110132

import time
import tkinter as tk
from tkinter import messagebox
import threading

# ==============================================================================
# 1. THUẬT TOÁN DFS & BÀI TOÁN 8-PUZZLE
# ==============================================================================

class Node:
    def __init__(self, state, parent=None, action=None, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth

def Stack():
    return []

def push(s, node):
    s.append(node)

def pop(s):
    return s.pop()

def is_empty(s):
    return len(s) == 0

def child_node(prob, node, act):
    return Node(prob.result(node.state, act), node, act, node.depth + 1)

def solution(node):
    acts, states = [], []
    curr = node
    while curr is not None:
        states.append(curr.state)
        if curr.action is not None:
            acts.append(curr.action)
        curr = curr.parent
    acts.reverse()
    states.reverse()
    return acts, states

class Problem:
    def __init__(self, initial_state, is_goal, actions, result):
        self.initial_state = initial_state
        self.is_goal = is_goal
        self.actions = actions
        self.result = result

def puzzle_is_goal(state):
    return state == (1, 2, 3, 4, 5, 6, 7, 8, 0)

def puzzle_actions(state):
    i = state.index(0)
    acts = []
    if i % 3 != 0: acts.append('Left')
    if i % 3 != 2: acts.append('Right')
    if i >= 3: acts.append('Up')
    if i <= 5: acts.append('Down')
    return acts

def puzzle_result(state, action):
    step = {'Left': -1, 'Right': 1, 'Up': -3, 'Down': 3}
    s = list(state)
    i = s.index(0)
    j = i + step[action]
    s[i], s[j] = s[j], s[i]
    return tuple(s)

def is_solvable(state):
    tiles = [x for x in state if x != 0]
    inv = sum(1 for i in range(len(tiles)) for j in range(i + 1, len(tiles)) if tiles[i] > tiles[j])
    return inv % 2 == 0

def DFS(problem):
    start_time = time.perf_counter()
    frontier = Stack()
    push(frontier, Node(problem.initial_state))
    explored = set()

    while not is_empty(frontier):
        node = pop(frontier)

        if problem.is_goal(node.state):
            elapsed = (time.perf_counter() - start_time) * 1000
            acts, states = solution(node)
            return acts, states, len(explored), len(frontier), elapsed

        explored.add(node.state)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            if child.state not in explored:
                push(frontier, child)

    elapsed = (time.perf_counter() - start_time) * 1000
    return None, None, len(explored), len(frontier), elapsed

# ==============================================================================
# 2. GIAO DIỆN NGƯỜI DÙNG TKINTER ĐƠN GIẢN & ĐẸP MẮT
# ==============================================================================

class EightPuzzleDFSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver - DFS | MSSV: 24110132")
        self.root.geometry("860x590")
        self.root.resizable(False, False)
        self.root.configure(bg="#0b1329")

        # Cấu hình dữ liệu
        self.default_init = (1, 2, 3, 4, 0, 6, 7, 5, 8)
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
        header = tk.Frame(self.root, bg="#1a1c36", padx=16, pady=10)
        header.pack(fill="x", padx=12, pady=(10, 6))

        tk.Label(header, text="🧩 BÀI TOÁN 8-PUZZLE (DFS)", font=("Segoe UI", 14, "bold"), fg="#a78bfa", bg="#1a1c36").pack(side="left")
        tk.Label(header, text="MSSV: 24110132", font=("Segoe UI", 10, "bold"), fg="#94a3b8", bg="#1a1c36").pack(side="right")

        # 2. Main content: 2 cột đơn giản
        main_box = tk.Frame(self.root, bg="#0b1329")
        main_box.pack(fill="both", expand=True, padx=12, pady=4)

        # CỘT TRÁI: Bàn cờ Canvas + Nút điều khiển bước
        left_frame = tk.Frame(main_box, bg="#161938", padx=14, pady=12, relief="ridge", bd=1)
        left_frame.pack(side="left", fill="both", padx=(0, 6))

        self.tile_size = 80
        self.tile_gap = 8
        self.margin = 12
        self.canvas_size = self.margin * 2 + 3 * self.tile_size + 2 * self.tile_gap

        self.canvas = tk.Canvas(
            left_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#0b1329",
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
            bg="#161938"
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
            bg="#161938",
            fg="#a78bfa",
            highlightthickness=0,
            troughcolor="#27274a",
            activebackground="#4f46e5"
        )
        self.step_scale.pack(fill="x", padx=6, pady=2)

        # Nút điều khiển phát lại
        ctrl_box = tk.Frame(left_frame, bg="#161938")
        ctrl_box.pack(pady=6)

        btn_opt = {"font": ("Segoe UI", 9, "bold"), "relief": "flat", "bd": 0, "cursor": "hand2", "pady": 4}
        self.btn_prev = tk.Button(ctrl_box, text="◀ Trước", bg="#27274a", fg="#ffffff", width=8, command=self.go_prev, **btn_opt)
        self.btn_prev.grid(row=0, column=0, padx=4)

        self.btn_play = tk.Button(ctrl_box, text="▶ Chạy", bg="#16a34a", fg="#ffffff", width=8, command=self.toggle_play, **btn_opt)
        self.btn_play.grid(row=0, column=1, padx=4)

        self.btn_next = tk.Button(ctrl_box, text="Sau ▶", bg="#27274a", fg="#ffffff", width=8, command=self.go_next, **btn_opt)
        self.btn_next.grid(row=0, column=2, padx=4)

        # CỘT PHẢI: Mẫu + Nút Giải + Thống kê + Log
        right_frame = tk.Frame(main_box, bg="#161938", padx=16, pady=12, relief="ridge", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # 1. Chọn Mẫu
        preset_row = tk.Frame(right_frame, bg="#161938")
        preset_row.pack(fill="x", pady=(0, 8))

        tk.Label(preset_row, text="Chọn mẫu:", font=("Segoe UI", 9, "bold"), fg="#e2e8f0", bg="#161938").pack(side="left", padx=(0, 6))
        self.btn_m1 = tk.Button(preset_row, text="Mẫu 1", bg="#4f46e5", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", padx=10, pady=4, command=self.load_preset_1)
        self.btn_m1.pack(side="left", padx=4)

        self.btn_m2 = tk.Button(preset_row, text="Mẫu 2", bg="#27274a", fg="#e2e8f0", font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", padx=10, pady=4, command=self.load_preset_2)
        self.btn_m2.pack(side="left", padx=4)

        # 2. Nút Bắt đầu tìm kiếm & Đặt lại
        action_row = tk.Frame(right_frame, bg="#161938")
        action_row.pack(fill="x", pady=4)

        self.btn_search = tk.Button(
            action_row,
            text="▶ BẮT ĐẦU TÌM KIẾM (DFS)",
            bg="#4f46e5",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=8,
            command=self.start_dfs_search
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
            fg="#a78bfa",
            bg="#161938"
        )
        self.stat_lbl.pack(anchor="w", pady=(8, 4))

        # 4. Log chi tiết ma trận
        log_label = tk.Label(right_frame, text="Lịch sử lời giải:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#161938")
        log_label.pack(anchor="w", pady=(4, 2))

        self.log_text = tk.Text(right_frame, bg="#0b1329", fg="#e2e8f0", font=("Consolas", 9), height=11, relief="sunken", bd=1)
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
        for idx, val in enumerate(state):
            r = idx // 3
            c = idx % 3
            x, y = self._get_coords(r, c)

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
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="#161938", outline="#27274a", width=2, dash=(4, 4))
        else:
            bg_col = "#818cf8" if is_sliding else "#6366f1"
            bd_col = "#facc15" if is_sliding else "#a5b4fc"
            self.canvas.create_rectangle(x, y, x + w, y + h, fill=bg_col, outline=bd_col, width=2)
            self.canvas.create_text(x + w / 2, y + h / 2, text=str(val), font=("Segoe UI", 22, "bold"), fill="#ffffff")

    def animate_step(self, s_from, s_to, on_finish):
        z_from = s_from.index(0)
        z_to = s_to.index(0)

        if z_from == z_to:
            self.draw_board(s_to)
            if on_finish: on_finish()
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

        click_idx = r * 3 + c
        zr = self.current_state.index(0) // 3
        zc = self.current_state.index(0) % 3

        if abs(r - zr) + abs(c - zc) == 1:
            s = list(self.current_state)
            zero_idx = zr * 3 + zc
            s[zero_idx], s[click_idx] = s[click_idx], s[zero_idx]
            new_state = tuple(s)

            s_from = self.current_state
            self.current_state = new_state
            self.animate_step(s_from, new_state, on_finish=None)
            self.reset_to_init(keep_state=True)
            self._reset_preset_btn_colors()

    def _reset_preset_btn_colors(self):
        self.btn_m1.configure(bg="#27274a")
        self.btn_m2.configure(bg="#27274a")

    def load_preset_1(self):
        self.current_state = (1, 2, 3, 4, 0, 6, 7, 5, 8)
        self.btn_m1.configure(bg="#4f46e5")
        self.btn_m2.configure(bg="#27274a")
        self.reset_to_init()

    def load_preset_2(self):
        self.current_state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        self.btn_m1.configure(bg="#27274a")
        self.btn_m2.configure(bg="#4f46e5")
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
        self.stat_lbl.configure(text="Trạng thái: Sẵn sàng  •  Số bước: 0  •  Thời gian: 0 ms", fg="#a78bfa")
        if not keep_state:
            self.log_text.delete("1.0", tk.END)

    def start_dfs_search(self):
        if not is_solvable(self.current_state):
            messagebox.showerror("Lỗi", "Trạng thái này không có lời giải! Hãy click di chuyển các ô để tạo thế cờ hợp lệ.")
            return

        self.btn_search.configure(state="disabled", text="⏳ Đang giải...")
        self.stat_lbl.configure(text="Trạng thái: Đang tìm kiếm...", fg="#facc15")
        self.root.update()

        prob = Problem(self.current_state, puzzle_is_goal, puzzle_actions, puzzle_result)

        def worker():
            acts, states, exp, front, el = DFS(prob)
            self.root.after(0, lambda: self.on_search_done(acts, states, exp, front, el))

        threading.Thread(target=worker, daemon=True).start()

    def on_search_done(self, acts, states, exp, front, el):
        self.btn_search.configure(state="normal", text="▶ BẮT ĐẦU TÌM KIẾM (DFS)")

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
        self.log_text.insert(tk.END, f"=== KẾT QUẢ TÌM KIẾM THEO CHIỀU SÂU (DFS) ===\nSố bước: {num_steps}  •  Đã duyệt: {exp} trạng thái  •  Thời gian: {el:.2f} ms\n\n")

        if num_steps <= 60:
            self.log_text.insert(tk.END, f"Hành động: {acts}\n\n")
            for i in range(len(states)):
                header = "Bắt đầu" if i == 0 else f"Bước {i}: {acts[i - 1]}"
                self.log_text.insert(tk.END, f"{header}\n")
                st = states[i]
                self.log_text.insert(tk.END, f"{st[0:3]}\n")
                self.log_text.insert(tk.END, f"{st[3:6]}\n")
                self.log_text.insert(tk.END, f"{st[6:9]}\n\n")
        else:
            for i in range(21):
                header = "Bắt đầu" if i == 0 else f"Bước {i}: {acts[i - 1]}"
                self.log_text.insert(tk.END, f"{header}\n")
                st = states[i]
                self.log_text.insert(tk.END, f"{st[0:3]}\n")
                self.log_text.insert(tk.END, f"{st[3:6]}\n")
                self.log_text.insert(tk.END, f"{st[6:9]}\n\n")

            self.log_text.insert(tk.END, f"... [Ẩn bớt {num_steps - 40} bước trung gian] ...\n\n")

            for i in range(num_steps - 19, num_steps + 1):
                header = f"Bước {i}: {acts[i - 1]}"
                self.log_text.insert(tk.END, f"{header}\n")
                st = states[i]
                self.log_text.insert(tk.END, f"{st[0:3]}\n")
                self.log_text.insert(tk.END, f"{st[3:6]}\n")
                self.log_text.insert(tk.END, f"{st[6:9]}\n\n")
        self.log_text.see("1.0")

        # Tự động phát hoạt ảnh nếu số bước vừa phải
        self.show_step(0, animate=False)
        if 0 < num_steps <= 40:
            self.is_playing = True
            self.btn_play.configure(text="⏸ Dừng", bg="#dc2626")
            self.root.after(400, self._auto_step)
        else:
            self.is_playing = False
            self.btn_play.configure(text="▶ Chạy", bg="#16a34a")

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

            num_steps = len(self.solution_actions)
            if num_steps <= 20:
                self.animate_step(s_from, s_to, on_finish=lambda: self.root.after(500, self._auto_step))
            elif num_steps <= 80:
                self.animate_step(s_from, s_to, on_finish=lambda: self.root.after(150, self._auto_step))
            else:
                self.draw_board(s_to)
                self.root.after(30, self._auto_step)
        else:
            self.is_playing = False
            self.btn_play.configure(text="▶ Chạy", bg="#16a34a")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = EightPuzzleDFSGUI(app_root)
    app_root.mainloop()
