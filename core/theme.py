"""core/theme.py — Colour palette, fonts, reusable widget builders"""
import tkinter as tk

BG     = "#080c20"
PANEL  = "#0d1535"
PANEL2 = "#111840"
TEXT   = "#d0d8ff"
DIM    = "#6a7aaa"
BLUE   = "#4fc3f7"
GREEN  = "#69f0ae"
ORANGE = "#ffb74d"
PURPLE = "#ce93d8"
RED    = "#ef5350"
YELLOW = "#fff176"
GOLD   = "#ffd700"
WHITE  = "#ffffff"

ROLE_COLORS = {"admin": RED, "moderator": PURPLE, "player": BLUE}

F_HUGE  = ("Courier New", 30, "bold")
F_TITLE = ("Courier New", 16, "bold")
F_SUB   = ("Courier New", 13, "bold")
F_BODY  = ("Courier New", 11)
F_SMALL = ("Courier New", 9)

def card(parent, color, **kw):
    outer = tk.Frame(parent, bg=color, padx=2, pady=2)
    inner = tk.Frame(outer, bg=PANEL, **kw)
    inner.pack(fill="both", expand=True)
    return outer, inner

def button(parent, text, fg=TEXT, bg=PANEL2, cmd=None, font=F_BODY, **kw):
    return tk.Button(parent, text=text, fg=fg, bg=bg, font=font,
                     relief="flat", cursor="hand2", command=cmd, **kw)

def scrollable(parent, bg=BG):
    canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
    sb     = tk.Scrollbar(parent, orient="vertical", command=canvas.yview,
                          bg=PANEL, troughcolor=PANEL2)
    frame  = tk.Frame(canvas, bg=bg)
    frame.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    return canvas, frame

def stat_card(parent, value, label_text, color):
    outer, inner = card(parent, color, padx=14, pady=8)
    outer.pack(side="left", padx=5, expand=True)
    tk.Label(inner, text=str(value), font=("Courier New", 22, "bold"),
             fg=color, bg=PANEL).pack()
    tk.Label(inner, text=label_text, font=F_SMALL, fg=TEXT, bg=PANEL).pack()
    return outer

def col_header(parent, cols_widths, bg=PANEL2):
    hdr = tk.Frame(parent, bg=bg, pady=4)
    hdr.pack(fill="x")
    for col, w in cols_widths:
        tk.Label(hdr, text=col, font=F_BODY, fg=YELLOW,
                 bg=bg, width=w, anchor="w").pack(side="left", padx=4)
    return hdr