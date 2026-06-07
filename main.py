import tkinter as tk
from tkinter import ttk
import time
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class KPSTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyboard CPS Tester")
        self.root.geometry("500x440")  # Increased width to prevent layout clipping
        self.root.resizable(False, False)
        
        # Muted Nord/Slate Theme
        self.bg_main = "#22252a"       # Deep soft dark grey background
        self.bg_card = "#2b303c"       # Soft graphite for cards
        self.fg_light = "#eef1f6"      # Eye-friendly white
        self.fg_dim = "#8a95a5"        # Muted grey for labels
        self.accent_blue = "#5eacb6"   # Soft pastel cyan (CPS)
        self.accent_green = "#76a065"  # Muted green (START)
        self.accent_red = "#c16666"    # Pastel red (STOP)
        
        self.root.configure(bg=self.bg_main)

        # Test logic variables
        self.is_running = False
        self.click_count = 0
        self.start_time = 0
        self.test_duration = 10
        self.pressed_keys = set()

        # History data for the graph
        self.cps_history = []
        self.time_history = []
        self.last_tracked_second = -1

        # Default key settings
        self.key1 = "h"
        self.key2 = "j"
        self.canvas = None

        self.setup_ui()
        
        # Keyboard event listeners
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TCombobox", 
            fieldbackground=self.bg_card, 
            background=self.bg_card, 
            foreground=self.fg_light, 
            arrowcolor=self.fg_light,
            borderwidth=0
        )
        self.root.option_add("*TCombobox*Listbox.background", self.bg_card)
        self.root.option_add("*TCombobox*Listbox.foreground", self.fg_light)
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.accent_blue)

        # 1. HEADER
        lbl_title = tk.Label(
            self.root, text="KEYBOARD CPS TESTER", 
            font=("Segoe UI", 15, "bold"), bg=self.bg_main, fg=self.accent_blue
        )
        lbl_title.pack(pady=(18, 5))

        # 2. SETTINGS PANEL
        settings_frame = tk.Frame(
            self.root, bg=self.bg_card, 
            highlightbackground="#373e4d", highlightthickness=1
        )
        settings_frame.pack(fill="x", padx=24, pady=10)
        
        inner_settings = tk.Frame(settings_frame, bg=self.bg_card)
        inner_settings.pack(padx=16, pady=12, fill="x")

        tk.Label(
            inner_settings, text="Keys:", font=("Segoe UI", 10), 
            bg=self.bg_card, fg=self.fg_dim
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.entry_key1 = tk.Entry(
            inner_settings, width=4, font=("Segoe UI", 11, "bold"), 
            justify="center", bg=self.bg_main, fg=self.fg_light, 
            bd=0, insertbackground=self.fg_light, 
            highlightthickness=1, highlightbackground="#373e4d"
        )
        self.entry_key1.insert(0, self.key1)
        self.entry_key1.grid(row=0, column=1, padx=6, pady=5)

        self.entry_key2 = tk.Entry(
            inner_settings, width=4, font=("Segoe UI", 11, "bold"), 
            justify="center", bg=self.bg_main, fg=self.fg_light, 
            bd=0, insertbackground=self.fg_light, 
            highlightthickness=1, highlightbackground="#373e4d"
        )
        self.entry_key2.insert(0, self.key2)
        self.entry_key2.grid(row=0, column=2, padx=6, pady=5)

        tk.Label(
            inner_settings, text="Time:", font=("Segoe UI", 10), 
            bg=self.bg_card, fg=self.fg_dim
        ).grid(row=0, column=3, sticky="w", padx=(15, 6), pady=5)
        
        self.time_combo = ttk.Combobox(
            inner_settings, values=["5", "10", "15", "30", "60"], 
            width=4, font=("Segoe UI", 10, "bold"), state="readonly"
        )
        self.time_combo.set("10")
        self.time_combo.grid(row=0, column=4, padx=6, pady=5)

        # Action Button (START / STOP) with explicit padding configuration
        self.btn_action = tk.Button(
            inner_settings, text="START", font=("Segoe UI", 10, "bold"),
            bg=self.accent_green, fg=self.fg_light,
            activebackground="#84ae72", activeforeground=self.fg_light,
            bd=0, cursor="hand2", width=11, command=self.handle_action
        )
        self.btn_action.grid(row=0, column=5, padx=(20, 0), pady=5, sticky="e")

        # 3. STATS CARDS
        stats_frame = tk.Frame(self.root, bg=self.bg_main)
        stats_frame.pack(fill="x", padx=24, pady=5)

        card_time = tk.Frame(stats_frame, bg=self.bg_card, width=140, height=68, highlightbackground="#373e4d", highlightthickness=1)
        card_time.pack_propagate(False)
        card_time.pack(side="left", padx=(0, 12))
        tk.Label(card_time, text="TIME", font=("Segoe UI", 8, "bold"), bg=self.bg_card, fg=self.fg_dim).pack(pady=(8, 2))
        self.lbl_timer = tk.Label(card_time, text="10.0s", font=("Segoe UI", 14, "bold"), bg=self.bg_card, fg=self.fg_light)
        self.lbl_timer.pack()

        card_clicks = tk.Frame(stats_frame, bg=self.bg_card, width=140, height=68, highlightbackground="#373e4d", highlightthickness=1)
        card_clicks.pack_propagate(False)
        card_clicks.pack(side="left", padx=0)
        tk.Label(card_clicks, text="CLICKS", font=("Segoe UI", 8, "bold"), bg=self.bg_card, fg=self.fg_dim).pack(pady=(8, 2))
        self.lbl_clicks = tk.Label(card_clicks, text="0", font=("Segoe UI", 14, "bold"), bg=self.bg_card, fg=self.fg_light)
        self.lbl_clicks.pack()

        card_cps = tk.Frame(stats_frame, bg=self.bg_card, width=150, height=68, highlightbackground=self.accent_blue, highlightthickness=1)
        card_cps.pack_propagate(False)
        card_cps.pack(side="right", padx=0)
        tk.Label(card_cps, text="CURRENT CPS", font=("Segoe UI", 8, "bold"), bg=self.bg_card, fg=self.fg_dim).pack(pady=(8, 2))
        self.lbl_kps = tk.Label(card_cps, text="0.00", font=("Segoe UI", 15, "bold"), bg=self.bg_card, fg=self.accent_blue)
        self.lbl_kps.pack()

        # 4. STATUS LABEL
        self.lbl_status = tk.Label(
            self.root, text="Ready to start the test", 
            font=("Segoe UI", 9, "italic"), bg=self.bg_main, fg=self.fg_dim
        )
        self.lbl_status.pack(pady=(16, 6))

        # 5. GRAPH TOGGLE BUTTON
        self.btn_graph = tk.Button(
            self.root, text="Show CPS Dynamics", font=("Segoe UI", 9, "bold"), 
            bg="#2b303c", fg=self.fg_dim, activebackground="#373e4d", activeforeground=self.fg_light,
            bd=0, cursor="hand2", padx=16, pady=6, state="disabled", command=self.toggle_graph
        )
        self.btn_graph.pack(pady=5)

        self.graph_frame = tk.Frame(self.root, bg=self.bg_main)
        self.graph_frame.pack(fill="both", expand=True, padx=24, pady=(10, 15))

    def handle_action(self):
        if not self.is_running:
            self.start_test()
        else:
            self.stop_test(finished_fully=False)

    def start_test(self):
        k1 = self.entry_key1.get().strip().lower()
        k2 = self.entry_key2.get().strip().lower()
        
        if not k1 or not k2:
            self.lbl_status.config(text="Error: Enter both keys!", fg=self.accent_red)
            return

        self.key1 = k1
        self.key2 = k2
        self.test_duration = int(self.time_combo.get())

        self.hide_graph_panel()
        self.cps_history = []
        self.time_history = []
        self.last_tracked_second = -1
        self.pressed_keys.clear()

        self.click_count = 0
        self.lbl_clicks.config(text="0")
        self.lbl_kps.config(text="0.00", fg=self.accent_blue)
        self.lbl_timer.config(text=f"{self.test_duration:.1f}s")
        
        self.is_running = True
        self.lbl_status.config(text="TEST IN PROGRESS! Press the designated keys", fg="#d6996d")
        
        self.btn_action.config(text="STOP", bg=self.accent_red, activebackground="#cc7777")
        self.btn_graph.config(state="disabled", bg="#252932", fg=self.fg_dim)
        
        self.entry_key1.config(state="disabled", disabledbackground=self.bg_main)
        self.entry_key2.config(state="disabled", disabledbackground=self.bg_main)
        self.time_combo.config(state="disabled")
        
        self.root.focus_set()
        self.start_time = time.time()
        self.update_timer()

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key not in self.pressed_keys:
            self.pressed_keys.add(key)
            if self.is_running and (key == self.key1 or key == self.key2):
                self.click_count += 1
                self.lbl_clicks.config(text=str(self.click_count))

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def update_timer(self):
        if not self.is_running:
            return

        elapsed = time.time() - self.start_time
        remaining = max(0.0, self.test_duration - elapsed)
        
        self.lbl_timer.config(text=f"{remaining:.1f}s")
        
        current_cps = 0.0
        if elapsed > 0:
            current_cps = self.click_count / elapsed
            self.lbl_kps.config(text=f"{current_cps:.2f}")

        current_second = int(elapsed)
        if current_second > self.last_tracked_second and current_second <= self.test_duration:
            self.time_history.append(current_second)
            self.cps_history.append(round(current_cps, 2))
            self.last_tracked_second = current_second

        if remaining <= 0:
            self.stop_test(finished_fully=True)
        else:
            self.root.after(50, self.update_timer)

    def stop_test(self, finished_fully=True):
        if not self.is_running:
            return
        self.is_running = False
        elapsed = time.time() - self.start_time
        actual_time = self.test_duration if finished_fully else max(0.1, elapsed)
        final_cps = self.click_count / actual_time

        if not finished_fully:
            self.time_history.append(round(elapsed, 1))
            self.cps_history.append(round(final_cps, 2))

        self.btn_action.config(text="START", bg=self.accent_green, activebackground="#84ae72")
        self.entry_key1.config(state="normal")
        self.entry_key2.config(state="normal")
        self.time_combo.config(state="readonly")

        self.btn_graph.config(state="normal", bg=self.bg_card, fg=self.accent_blue)

        if finished_fully:
            self.lbl_timer.config(text="0.0s")
            self.lbl_kps.config(text=f"{final_cps:.2f}", fg=self.accent_green)
            self.lbl_status.config(text="Test completed! Result saved.", fg=self.accent_green)
        else:
            self.click_count = 0
            self.lbl_clicks.config(text="0")
            self.lbl_kps.config(text="0.00", fg=self.accent_blue)
            self.lbl_timer.config(text=f"{self.test_duration:.1f}s")
            self.lbl_status.config(text=f"Test aborted at {elapsed:.1f}s. Data reset.", fg=self.accent_red)

    def toggle_graph(self):
        if self.canvas:
            self.hide_graph_panel()
        else:
            self.show_graph_panel()

    def show_graph_panel(self):
        if not self.time_history:
            return
        self.root.geometry("500x720")  # Extended height to fit the plot panel

        fig = Figure(figsize=(4, 2.5), dpi=100, facecolor=self.bg_main)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.bg_card)
        
        # Smooth anti-aliased layout graph line
        ax.plot(self.time_history, self.cps_history, marker='o', color=self.accent_blue, linewidth=2, markersize=5, antialiased=True)
        
        ax.set_title("CPS Dynamics", fontsize=10, color=self.fg_light, weight="bold", pad=10)
        ax.set_xlabel("Seconds", fontsize=8, color=self.fg_dim)
        ax.set_ylabel("CPS", fontsize=8, color=self.fg_dim)
        
        # Frame axis styling
        for spine in ax.spines.values():
            spine.set_color("#373e4d")
            
        ax.tick_params(axis='both', colors=self.fg_dim, labelsize=8)
        ax.grid(True, linestyle='--', color="#373e4d", alpha=0.5)
        ax.set_xticks(self.time_history)

        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.btn_graph.config(text="Hide CPS Dynamics")

    def hide_graph_panel(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.root.geometry("500x440")
        self.btn_graph.config(text="Show CPS Dynamics")

if __name__ == "__main__":
    root = tk.Tk()
    app = KPSTester(root)
    root.mainloop()