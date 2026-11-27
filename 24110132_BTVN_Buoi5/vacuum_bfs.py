# MSSV: 24110132

import time
import tkinter as tk
from tkinter import messagebox
import threading

# ==============================================================================
# 1. THUẬT TOÁN BFS & BÀI TOÁN MÁY HÚT BỤI
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
    acts, states = [], []
    curr = node
    while curr is not None:
        states.insert(0, curr.state)
        if curr.action is not None:
            acts.insert(0, curr.action)
        curr = curr.parent
    return acts, states

class Problem:
    def __init__(self, initial_state, is_goal, actions, result):
        self.initial_state = initial_state
        self.is_goal = is_goal
        self.actions = actions
        self.result = result

def vacuum_is_goal(state):
    return state[1] == 'C' and state[2] == 'C'

def vacuum_actions(state):
    pos, a, b = state
    acts = []
    if pos == 'A': acts.append('Right')
    else: acts.append('Left')
    if (pos == 'A' and a == 'D') or (pos == 'B' and b == 'D'):
        acts.append('Suck')
    return acts

def vacuum_result(state, action):
    pos, a, b = state
    if action == 'Left': return ('A', a, b)
    if action == 'Right': return ('B', a, b)
    if pos == 'A': return ('A', 'C', b)
    return ('B', a, 'C')

def BFS(problem):
    start_time = time.perf_counter()
    start_node = Node(problem.initial_state)

    if problem.is_goal(start_node.state):
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
                if problem.is_goal(child.state):
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

class VacuumBFSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vacuum Cleaner Solver - BFS | MSSV: 24110132")
        self.root.geometry("860x590")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        # Cấu hình trạng thái mặc định: ('A', 'D', 'D')
        self.current_state = ('A', 'D', 'D')

        # Dữ liệu truy vết
        self.solution_actions = []
        self.solution_states = [self.current_state]
        self.current_step = 0
        self.is_playing = False

        self._build_ui()
        self.draw_environment(self.current_state)

    def _build_ui(self):
        # 1. Header gọn gàng
        header = tk.Frame(self.root, bg="#1e293b", padx=16, pady=10)
        header.pack(fill="x", padx=12, pady=(10, 6))

        tk.Label(header, text="🤖 MÁY HÚT BỤI 2 PHÒNG (BFS)", font=("Segoe UI", 14, "bold"), fg="#38bdf8", bg="#1e293b").pack(side="left")
        tk.Label(header, text="MSSV: 24110132", font=("Segoe UI", 10, "bold"), fg="#94a3b8", bg="#1e293b").pack(side="right")

        # 2. Main content: 2 cột
        main_box = tk.Frame(self.root, bg="#0f172a")
        main_box.pack(fill="both", expand=True, padx=12, pady=4)

        # CỘT TRÁI: Canvas 2 phòng + Nút điều khiển bước
        left_frame = tk.Frame(main_box, bg="#1e293b", padx=14, pady=12, relief="ridge", bd=1)
        left_frame.pack(side="left", fill="both", padx=(0, 6))

        self.canvas_w = 380
        self.canvas_h = 240
        self.canvas = tk.Canvas(
            left_frame,
            width=self.canvas_w,
            height=self.canvas_h,
            bg="#0b1329",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(pady=4)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.step_info_lbl = tk.Label(
            left_frame,
            text="Bước: 0 / 0 | Bắt đầu | ('A', 'D', 'D')",
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

        # 4. Log chi tiết
        log_label = tk.Label(right_frame, text="Lịch sử lời giải:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b")
        log_label.pack(anchor="w", pady=(4, 2))

        self.log_text = tk.Text(right_frame, bg="#0f172a", fg="#e2e8f0", font=("Consolas", 9), height=11, relief="sunken", bd=1)
        log_scroll = tk.Scrollbar(right_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

    # ==========================================================================
    # VẼ MÔ PHỎNG & HOẠT ẢNH DI CHUYỂN
    # ==========================================================================

    def draw_environment(self, state, robot_x=None, is_sucking=False):
        self.canvas.delete("all")
        pos, ra, rb = state

        # Phòng A [20, 30, 185, 215]
        # Phòng B [195, 30, 360, 215]
        self.canvas.create_rectangle(20, 30, 185, 215, fill="#1e293b", outline="#334155", width=2)
        self.canvas.create_rectangle(195, 30, 360, 215, fill="#1e293b", outline="#334155", width=2)

        self.canvas.create_text(102, 50, text="PHÒNG A", fill="#38bdf8", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(277, 50, text="PHÒNG B", fill="#38bdf8", font=("Segoe UI", 11, "bold"))

        # Trạng thái phòng A
        if ra == 'D':
            self.canvas.create_text(102, 75, text="[ DƠ ]", fill="#ef4444", font=("Segoe UI", 9, "bold"))
            self._draw_dirt(102, 165)
        else:
            self.canvas.create_text(102, 75, text="[ SẠCH ]", fill="#22c55e", font=("Segoe UI", 9, "bold"))
            self.canvas.create_text(102, 165, text="✨ SẠCH", fill="#22c55e", font=("Segoe UI", 9, "italic"))

        # Trạng thái phòng B
        if rb == 'D':
            self.canvas.create_text(277, 75, text="[ DƠ ]", fill="#ef4444", font=("Segoe UI", 9, "bold"))
            self._draw_dirt(277, 165)
        else:
            self.canvas.create_text(277, 75, text="[ SẠCH ]", fill="#22c55e", font=("Segoe UI", 9, "bold"))
            self.canvas.create_text(277, 165, text="✨ SẠCH", fill="#22c55e", font=("Segoe UI", 9, "italic"))

        if robot_x is None:
            robot_x = 102 if pos == 'A' else 277
        self._draw_robot(robot_x, 145, is_sucking=is_sucking)

    def _draw_dirt(self, cx, cy):
        for dx, dy in [(-15, 0), (12, -8), (6, 10), (-8, -10), (0, 12), (16, 8)]:
            self.canvas.create_oval(cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4, fill="#78350f", outline="#b45309")
        self.canvas.create_text(cx, cy + 26, text="🌪 Bụi bẩn", fill="#f87171", font=("Segoe UI", 8))

    def _draw_robot(self, cx, cy, is_sucking=False):
        r = 28
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#0284c7", outline="#38bdf8", width=2)
        led = "#ef4444" if is_sucking else "#22c55e"
        self.canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill=led, outline="#ffffff")
        self.canvas.create_text(cx, cy - 36, text="🤖 ROBOT", fill="#38bdf8", font=("Segoe UI", 9, "bold"))
        if is_sucking:
            self.canvas.create_oval(cx - 38, cy - 38, cx + 38, cy + 38, outline="#facc15", width=2, dash=(2, 2))
            self.canvas.create_text(cx, cy + 40, text="⚡ HÚT BỤI... ⚡", fill="#facc15", font=("Segoe UI", 8, "bold"))

    def animate_step(self, s_from, s_to, act, on_finish):
        pos_from, _, _ = s_from
        pos_to, _, _ = s_to
        x_start = 102 if pos_from == 'A' else 277
        x_end = 102 if pos_to == 'A' else 277

        if act in ['Right', 'Left']:
            frames = 12
            cur = 0
            def step():
                nonlocal cur
                cur += 1
                t = cur / frames
                self.draw_environment(s_from, robot_x=x_start + (x_end - x_start) * t)
                if cur < frames: self.root.after(16, step)
                else:
                    self.draw_environment(s_to)
                    if on_finish: on_finish()
            step()
        elif act == 'Suck':
            frames = 10
            cur = 0
            def step_suck():
                nonlocal cur
                cur += 1
                mid = s_to if cur >= frames // 2 else s_from
                self.draw_environment(mid, robot_x=x_start, is_sucking=True)
                if cur < frames: self.root.after(30, step_suck)
                else:
                    self.draw_environment(s_to, robot_x=x_start, is_sucking=False)
                    if on_finish: on_finish()
            step_suck()
        else:
            self.draw_environment(s_to)
            if on_finish: on_finish()

    # ==========================================================================
    # TƯƠNG TÁC CLICK TRỰC TIẾP TRÊN PHÒNG & ROBOT
    # ==========================================================================

    def on_canvas_click(self, event):
        if self.is_playing:
            return

        pos, ra, rb = self.current_state
        rx = 102 if pos == 'A' else 277

        # Click vào robot -> đổi phòng
        if (event.x - rx) ** 2 + (event.y - 145) ** 2 <= 30 ** 2:
            new_pos = 'B' if pos == 'A' else 'A'
            self.current_state = (new_pos, ra, rb)
        # Click vào phòng A -> đổi Dơ/Sạch
        elif 20 <= event.x <= 185 and 30 <= event.y <= 215:
            new_ra = 'C' if ra == 'D' else 'D'
            self.current_state = (pos, new_ra, rb)
        # Click vào phòng B -> đổi Dơ/Sạch
        elif 195 <= event.x <= 360 and 30 <= event.y <= 215:
            new_rb = 'C' if rb == 'D' else 'D'
            self.current_state = (pos, ra, new_rb)

        self._reset_preset_btn_colors()
        self.reset_to_init()

    def _reset_preset_btn_colors(self):
        self.btn_m1.configure(bg="#334155")
        self.btn_m2.configure(bg="#334155")

    def load_preset_1(self):
        self.current_state = ('A', 'D', 'D')
        self.btn_m1.configure(bg="#0284c7")
        self.btn_m2.configure(bg="#334155")
        self.reset_to_init()

    def load_preset_2(self):
        self.current_state = ('B', 'D', 'D')
        self.btn_m1.configure(bg="#334155")
        self.btn_m2.configure(bg="#0284c7")
        self.reset_to_init()

    def reset_to_init(self):
        self.is_playing = False
        self.btn_play.configure(text="▶ Chạy", bg="#16a34a")
        self.solution_actions = []
        self.solution_states = [self.current_state]
        self.current_step = 0
        self.step_scale.configure(to=0)
        self.step_scale.set(0)
        self.draw_environment(self.current_state)
        self.step_info_lbl.configure(text=f"Bước: 0 / 0 | Bắt đầu | {self.current_state}")
        self.stat_lbl.configure(text="Trạng thái: Sẵn sàng  •  Số bước: 0  •  Thời gian: 0 ms", fg="#38bdf8")
        self.log_text.delete("1.0", tk.END)

    def start_bfs_search(self):
        self.btn_search.configure(state="disabled", text="⏳ Đang giải...")
        self.stat_lbl.configure(text="Trạng thái: Đang tìm kiếm...", fg="#facc15")
        self.root.update()

        prob = Problem(self.current_state, vacuum_is_goal, vacuum_actions, vacuum_result)

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
        self.log_text.insert(tk.END, f"Số bước: {num_steps}\n")
        self.log_text.insert(tk.END, f"Hành động: {acts}\n\n")
        for i in range(len(states)):
            pos, a, b = states[i]
            buoc = "Bắt đầu" if i == 0 else acts[i - 1]
            self.log_text.insert(tk.END, f"{i}. {buoc:8} -> robot ở {pos}, A = {a}, B = {b}\n")
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
        st = self.solution_states[idx]
        self.step_info_lbl.configure(text=f"Bước: {idx} / {len(self.solution_states)-1} | {act} | {st}")

        if animate and (idx == prev + 1):
            self.animate_step(self.solution_states[prev], self.solution_states[idx], act, on_finish=None)
        else:
            self.draw_environment(st)

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
            act = self.solution_actions[next_idx - 1]

            self.current_step = next_idx
            self.step_scale.set(next_idx)
            self.step_info_lbl.configure(text=f"Bước: {next_idx} / {len(self.solution_states)-1} | {act} | {s_to}")

            self.animate_step(s_from, s_to, act, on_finish=lambda: self.root.after(700, self._auto_step))
        else:
            self.is_playing = False
            self.btn_play.configure(text="▶ Chạy", bg="#16a34a")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = VacuumBFSGUI(app_root)
    app_root.mainloop()
