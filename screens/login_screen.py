"""screens/login_screen.py — Login & Register with animated city background"""
import tkinter as tk
import random
from core.theme import *
import core.database as DB
import core.sounds as SND


class LoginScreen(tk.Frame):
    def __init__(self, master, nav):
        super().__init__(master, bg=BG)
        self.nav   = nav
        self._mode = "login"
        self.pack(fill="both", expand=True)
        self._build_bg()
        self._build_form()
        self._animate()

    def _build_bg(self):
        self._canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._clouds = []
        self._draw_city()
        self._init_clouds()

    def _draw_city(self):
        c = self._canvas
        W, H = 1140, 720
        sky_colors = ["#04060f","#060915","#08101e","#0a1428","#0c1830"]
        band = H * 0.65 / len(sky_colors)
        for i, col in enumerate(sky_colors):
            c.create_rectangle(0, i*band, W, (i+1)*band+1, fill=col, outline="")
        for _ in range(80):
            x, y = random.randint(0, W), random.randint(0, int(H*0.5))
            r    = random.choice([1,1,1,2])
            c.create_oval(x-r, y-r, x+r, y+r, fill="white", outline="")
        c.create_oval(60, 35, 115, 90,  fill="#b8c4d8", outline="")
        c.create_oval(78, 28, 133, 83,  fill="#060915", outline="")
        gy = int(H*0.73)
        c.create_rectangle(0, gy, W, H, fill="#0a150a", outline="")
        ry = int(H*0.83)
        c.create_rectangle(0, ry, W, H, fill="#14142a", outline="")
        for x in range(0, W, 80):
            c.create_rectangle(x, ry+18, x+44, ry+26, fill="#888800", outline="")
        buildings = [
            (10,.42,80,"#16203a"),(110,.33,70,"#101c34"),(200,.50,90,"#1a2650"),
            (310,.28,65,"#141e38"),(395,.46,85,"#18244a"),(500,.36,75,"#1c2a54"),
            (595,.30,68,"#16203a"),(683,.48,88,"#101c34"),(790,.32,70,"#1a2650"),
            (880,.44,80,"#141e38"),(980,.26,60,"#18244a"),(1060,.38,70,"#1c2a54"),
        ]
        for bx, hf, bw, col in buildings:
            by = int(gy - H*hf)
            c.create_rectangle(bx, by, bx+bw, gy, fill=col, outline="#0a1030", width=1)
            mx = bx + bw//2
            c.create_line(mx, by, mx, by-18, fill="#223355", width=2)
            c.create_oval(mx-3, by-22, mx+3, by-16, fill=RED, outline="")
            for wy in range(by+8, gy-8, 20):
                for wx in range(bx+6, bx+bw-6, 16):
                    wc = "#ffcc44" if random.random() > .25 else "#1a2255"
                    c.create_rectangle(wx, wy, wx+9, wy+12, fill=wc, outline="")
        for tx in [48,148,295,450,570,660,770,880,990,1090]:
            ty = gy - 8
            c.create_rectangle(tx-3, ty-28, tx+3, ty, fill="#2d1a0a", outline="")
            c.create_oval(tx-20, ty-60, tx+20, ty-28, fill="#1e4a1a", outline="")
            c.create_oval(tx-14, ty-72, tx+14, ty-42, fill="#265e22", outline="")
        for lx in [82,232,388,538,686,840,996]:
            ly = gy - 4
            c.create_line(lx, ly, lx, ly-52, fill="#9999bb", width=3)
            c.create_line(lx, ly-52, lx+16, ly-52, fill="#9999bb", width=2)
            c.create_oval(lx+10, ly-58, lx+26, ly-46, fill="#ffe88a", outline="")

    def _init_clouds(self):
        for _ in range(6):
            self._spawn_cloud(random.randint(0, 1140),
                              random.randint(30, 140),
                              random.uniform(.7, 1.4))

    def _spawn_cloud(self, x, y, s):
        c = self._canvas; parts = []
        for ox, oy, r in [(-32,0,26),(0,-16,31),(32,0,26),(0,12,21)]:
            p = c.create_oval(x+ox*s-r*s, y+oy*s-r*s,
                              x+ox*s+r*s, y+oy*s+r*s,
                              fill="#2a2d3e", outline="")
            parts.append(p)
        self._clouds.append(parts)

    def _animate(self):
        if not self.winfo_exists(): return
        c = self._canvas
        for parts in self._clouds:
            for p in parts: c.move(p, -0.7, 0)
            coords = c.coords(parts[0])
            if coords and coords[2] < 0:
                for p in parts: c.move(p, 1360, 0)
        self.after(40, self._animate)

    def _build_form(self):
        panel = tk.Frame(self, bg=PANEL, padx=42, pady=36)
        panel.place(relx=.5, rely=.5, anchor="center")
        tk.Label(panel, text="EcoCity Mayor", font=("Courier New",28,"bold"),
                 fg=GREEN, bg=PANEL).pack()
        self._subtitle = tk.Label(panel, text="Sign in to manage your city",
                                  font=F_BODY, fg=DIM, bg=PANEL)
        self._subtitle.pack(pady=(2, 18))
        tk.Label(panel, text="Username", font=F_BODY, fg=TEXT,
                 bg=PANEL, anchor="w").pack(fill="x")
        self._uvar = tk.StringVar()
        tk.Entry(panel, textvariable=self._uvar, font=F_BODY,
                 bg=PANEL2, fg=YELLOW, insertbackground=YELLOW,
                 relief="flat", width=28).pack(fill="x", pady=(2, 8))
        tk.Label(panel, text="Password", font=F_BODY, fg=TEXT,
                 bg=PANEL, anchor="w").pack(fill="x")
        self._pvar = tk.StringVar()
        self._pentry = tk.Entry(panel, textvariable=self._pvar, show="●",
                                font=F_BODY, bg=PANEL2, fg=YELLOW,
                                insertbackground=YELLOW, relief="flat", width=28)
        self._pentry.pack(fill="x", pady=(2, 6))
        self._conf_label = tk.Label(panel, text="Confirm Password",
                                    font=F_BODY, fg=TEXT, bg=PANEL, anchor="w")
        self._cvar = tk.StringVar()
        self._centry = tk.Entry(panel, textvariable=self._cvar, show="●",
                                font=F_BODY, bg=PANEL2, fg=YELLOW,
                                insertbackground=YELLOW, relief="flat", width=28)
        self._err = tk.Label(panel, text="", font=F_SMALL, fg=RED, bg=PANEL)
        self._err.pack(pady=(0, 4))
        btn_row = tk.Frame(panel, bg=PANEL); btn_row.pack(fill="x", pady=4)
        self._btn_login = tk.Button(btn_row, text="Login", font=F_BODY,
                                    bg="#0a2a50", fg=BLUE, relief="flat",
                                    cursor="hand2", padx=18, pady=8,
                                    command=self._do_login)
        self._btn_login.pack(side="left", padx=4)
        self._btn_reg = tk.Button(btn_row, text="Register", font=F_BODY,
                                  bg="#0a3020", fg=GREEN, relief="flat",
                                  cursor="hand2", padx=18, pady=8,
                                  command=self._toggle_mode)
        self._btn_reg.pack(side="left", padx=4)
        tk.Label(panel, text="Demo: player1 / mod1 / admin1  |  password: 1234",
                 font=F_SMALL, fg=DIM, bg=PANEL).pack(pady=(10, 0))
        self.bind_all("<Return>", lambda e: self._do_login()
                      if self._mode == "login" else self._do_register())

    def _toggle_mode(self):
        if self._mode == "login":
            self._mode = "register"
            self._subtitle.configure(text="Create a new account")
            self._conf_label.pack(fill="x", before=self._err)
            self._centry.pack(fill="x", pady=(2, 6), before=self._err)
            self._btn_login.configure(text="← Back to Login",
                                      bg="#1a0a30", fg=PURPLE,
                                      command=self._toggle_mode)
            self._btn_reg.configure(text="Create Account",
                                    bg="#0a3020", fg=GREEN,
                                    command=self._do_register)
        else:
            self._mode = "login"
            self._subtitle.configure(text="Sign in to manage your city")
            self._conf_label.pack_forget()
            self._centry.pack_forget()
            self._btn_login.configure(text="Login", bg="#0a2a50",
                                      fg=BLUE, command=self._do_login)
            self._btn_reg.configure(text="Register", command=self._toggle_mode)
        self._err.configure(text="")

    def _do_login(self):
        u, p = self._uvar.get().strip(), self._pvar.get()
        if not u or not p:
            self._err.configure(text="Enter username and password."); return
        user = DB.login(u, p)
        if not user:
            self._err.configure(text="Invalid username or password."); return
        if user.get("status") == "banned":
            self._err.configure(text="This account has been banned."); return
        DB.log(u, "LOGIN", f"Role: {user['role']}")
        SND.play("click")
        self.nav.after_login(user)

    def _do_register(self):
        u = self._uvar.get().strip()
        p = self._pvar.get()
        c = self._cvar.get()
        if not u or not p:
            self._err.configure(text="All fields required."); return
        if p != c:
            self._err.configure(text="Passwords do not match."); return
        ok, msg = DB.register(u, p)
        if not ok:
            self._err.configure(text=msg); return
        DB.log(u, "REGISTER")
        self._err.configure(text=msg, fg=GREEN)
        self._toggle_mode()