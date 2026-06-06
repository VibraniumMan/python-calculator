import tkinter as tk

# ── Colour palette ──────────────────────────────────────────────────────────
BG        = "#1e1e2e"   # dark background
DISP_BG   = "#181825"   # display area
BTN_NUM   = "#313244"   # number buttons
BTN_OP    = "#89b4fa"   # operator buttons (blue)
BTN_EQ    = "#a6e3a1"   # equals button  (green)
BTN_CLR   = "#f38ba8"   # clear button   (red/pink)
TXT_LIGHT = "#cdd6f4"   # light text
TXT_DARK  = "#1e1e2e"   # dark text (used on coloured buttons)
FONT_MAIN = ("Courier New", 28, "bold")
FONT_SMALL= ("Courier New", 13)
FONT_BTN  = ("Courier New", 18, "bold")

class Calculator:
    def __init__(self, root):
        root.title("Calculator")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.expression = ""   # full expression string
        self.just_evaluated = False

        # ── Display ──────────────────────────────────────────────────────
        disp_frame = tk.Frame(root, bg=DISP_BG, padx=16, pady=12)
        disp_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=12, pady=(12, 4))

        # small label shows the running expression
        self.expr_label = tk.Label(
            disp_frame, text="", anchor="e",
            bg=DISP_BG, fg="#6c7086",
            font=FONT_SMALL, width=18
        )
        self.expr_label.pack(fill="x")

        # big label shows current number / result
        self.result_label = tk.Label(
            disp_frame, text="0", anchor="e",
            bg=DISP_BG, fg=TXT_LIGHT,
            font=FONT_MAIN, width=18
        )
        self.result_label.pack(fill="x")

        # ── Button grid ──────────────────────────────────────────────────
        buttons = [
            # (label,  row, col, colspan, style)
            ("AC",  1, 0, 1, "clr"),
            ("+/-", 1, 1, 1, "op"),
            ("%",   1, 2, 1, "op"),
            ("÷",   1, 3, 1, "op"),

            ("7",   2, 0, 1, "num"),
            ("8",   2, 1, 1, "num"),
            ("9",   2, 2, 1, "num"),
            ("×",   2, 3, 1, "op"),

            ("4",   3, 0, 1, "num"),
            ("5",   3, 1, 1, "num"),
            ("6",   3, 2, 1, "num"),
            ("−",   3, 3, 1, "op"),

            ("1",   4, 0, 1, "num"),
            ("2",   4, 1, 1, "num"),
            ("3",   4, 2, 1, "num"),
            ("+",   4, 3, 1, "op"),

            ("0",   5, 0, 2, "num"),   # wide zero
            (".",   5, 2, 1, "num"),
            ("=",   5, 3, 1, "eq"),
        ]

        colors = {"num": BTN_NUM, "op": BTN_OP, "clr": BTN_CLR, "eq": BTN_EQ}
        fgmap  = {"num": TXT_LIGHT, "op": TXT_DARK, "clr": TXT_DARK, "eq": TXT_DARK}

        for (label, row, col, colspan, style) in buttons:
            btn = tk.Button(
                root,
                text=label,
                bg=colors[style],
                fg=fgmap[style],
                activebackground=colors[style],
                activeforeground=fgmap[style],
                font=FONT_BTN,
                bd=0,
                relief="flat",
                cursor="hand2",
                command=lambda l=label: self.on_press(l),
            )
            btn.grid(
                row=row, column=col, columnspan=colspan,
                padx=5, pady=5, sticky="nsew", ipady=14
            )

        # make columns & rows resize evenly
        for c in range(4):
            root.columnconfigure(c, weight=1)
        for r in range(1, 6):
            root.rowconfigure(r, weight=1)

        # keyboard support
        root.bind("<Key>", self.on_key)

    # ── Display helpers ──────────────────────────────────────────────────
    def set_display(self, top="", bottom="0"):
        self.expr_label.config(text=top)
        self.result_label.config(text=bottom)

    # ── Button logic ─────────────────────────────────────────────────────
    def on_press(self, label):
        expr = self.expression

        if label == "AC":
            self.expression = ""
            self.just_evaluated = False
            self.set_display()
            return

        if label == "=":
            if not expr:
                return
            try:
                result = eval(expr)           # safe here: user input only
                # show result as int if it's a whole number
                display = int(result) if isinstance(result, float) and result.is_integer() else result
                self.set_display(top=expr + " =", bottom=str(display))
                self.expression = str(result)
                self.just_evaluated = True
            except ZeroDivisionError:
                self.set_display(bottom="Can't ÷ 0")
                self.expression = ""
            except Exception:
                self.set_display(bottom="Error")
                self.expression = ""
            return

        if label == "+/-":
            if expr:
                if expr.startswith("-"):
                    self.expression = expr[1:]
                else:
                    self.expression = "-" + expr
                self.set_display(bottom=self.expression)
            return

        if label == "%":
            if expr:
                try:
                    self.expression = str(eval(expr) / 100)
                    self.set_display(bottom=self.expression)
                except Exception:
                    pass
            return

        # map display symbols → Python operators
        op_map = {"÷": "/", "×": "*", "−": "-"}
        char = op_map.get(label, label)

        # if we just evaluated, start fresh on digit, continue on operator
        if self.just_evaluated:
            if char in "+-*/":
                pass   # chain: keep result, add operator
            else:
                self.expression = ""   # new number
            self.just_evaluated = False

        self.expression += char
        self.set_display(bottom=self.expression)

    # ── Keyboard support ─────────────────────────────────────────────────
    def on_key(self, event):
        key = event.char
        mapping = {
            "/": "÷", "*": "×", "-": "−",
            "\r": "=", "\x08": "AC",   # Enter & Backspace
        }
        if key in mapping:
            self.on_press(mapping[key])
        elif key in "0123456789.+":
            self.on_press(key)
        elif event.keysym == "BackSpace":
            self.expression = self.expression[:-1]
            self.set_display(bottom=self.expression or "0")
        elif event.keysym == "Escape":
            self.on_press("AC")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
