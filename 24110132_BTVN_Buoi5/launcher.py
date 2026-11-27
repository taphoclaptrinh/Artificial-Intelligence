# MSSV: 24110132

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def create_modern_button(parent, text, bg, fg, command, hover_bg=None, font=("Segoe UI", 9, "bold"), padx=12, pady=6):
    if hover_bg is None:
        hover_bg = bg
    btn = tk.Button(
        parent,
        text=text,
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        font=font,
        padx=padx,
        pady=pady,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=command
    )
    def on_enter(e):
        if str(btn["state"]) != "disabled":
            btn.configure(bg=hover_bg)
    def on_leave(e):
        if str(btn["state"]) != "disabled":
            btn.configure(bg=bg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MSSV: 24110132")
        self.root.geometry("680x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1e293b", padx=20, pady=16, relief="ridge", bd=1)
        header.pack(fill="x", padx=16, pady=14)

        tk.Label(
            header,
            text="HỆ THỐNG GIAO DIỆN THUẬT TOÁN TÌM KIẾM AI",
            font=("Segoe UI", 15, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        ).pack()

        tk.Label(
            header,
            text="MSSV: 24110132",
            font=("Segoe UI", 10, "bold"),
            fg="#94a3b8",
            bg="#1e293b"
        ).pack(pady=(4, 0))

        # Khung chứa 4 bài toán
        content = tk.Frame(self.root, bg="#0f172a", padx=20, pady=6)
        content.pack(fill="both", expand=True)

        items = [
            ("🧩 1. Bài toán 8-Puzzle (BFS)", "8puzzle_bfs.py", "#0284c7", "#0369a1"),
            ("🧩 2. Bài toán 8-Puzzle (DFS)", "8puzzle_dfs.py", "#4f46e5", "#6366f1"),
            ("🤖 3. Bài toán Máy hút bụi (BFS)", "vacuum_bfs.py", "#0ea5e9", "#0284c7"),
            ("🤖 4. Bài toán Máy hút bụi (DFS)", "vacuum_dfs.py", "#7c3aed", "#6d28d9"),
        ]

        for title, script_name, color, hover_color in items:
            card = tk.Frame(content, bg="#1e293b", padx=16, pady=12, relief="ridge", bd=1)
            card.pack(fill="x", pady=5)

            left_info = tk.Frame(card, bg="#1e293b")
            left_info.pack(side="left", fill="both", expand=True)

            tk.Label(
                left_info,
                text=title,
                font=("Segoe UI", 11, "bold"),
                fg="#f1f5f9",
                bg="#1e293b"
            ).pack(anchor="w")

            tk.Label(
                left_info,
                text=f"File: {script_name}",
                font=("Segoe UI", 9),
                fg="#94a3b8",
                bg="#1e293b"
            ).pack(anchor="w", pady=(2, 0))

            btn = create_modern_button(
                card,
                "MỞ GIAO DIỆN ▶",
                color,
                "#ffffff",
                lambda s=script_name: self.launch_script(s),
                hover_bg=hover_color,
                font=("Segoe UI", 9, "bold"),
                padx=14,
                pady=8
            )
            btn.pack(side="right", padx=(10, 0))

    def launch_script(self, filename):
        file_path = os.path.join(self.base_dir, filename)
        if os.path.exists(file_path):
            subprocess.Popen([sys.executable, file_path])
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy file: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop()
