########################
# GUI-Author: Sultan Ahmad
# Refactored: 04-06-2025
########################

import tkinter as tk
from tkinter import messagebox, scrolledtext
import datetime

class ATM:
    """Simulates the backend logic of an ATM."""
    def __init__(self):
        self.accounts = {
            "123456789": {"pin": "1234", "balance": 1500.00, "transactions": []},
            "987654321": {"pin": "4321", "balance": 750.00, "transactions": []},
        }
        self.current_account_number = None
        self.max_pin_attempts = 3
        self.pin_attempts = 0

    def validate_pin(self, account_num, pin):
        if account_num not in self.accounts:
            return False, "Account not found."

        if self.accounts[account_num]["pin"] == pin:
            self.current_account_number = account_num
            self.pin_attempts = 0
            return True, "Login successful!"
        else:
            self.pin_attempts += 1
            remaining = self.max_pin_attempts - self.pin_attempts
            if remaining > 0:
                return False, f"Incorrect PIN. {remaining} attempts left."
            else:
                return False, "Too many incorrect PIN attempts. Card blocked."

    def get_balance(self):
        return self.accounts[self.current_account_number]["balance"]

    def record_transaction(self, type, amount):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.accounts[self.current_account_number]["transactions"].append(
            f"{timestamp} - {type}: ${amount:.2f}"
        )

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Invalid amount."
        if self.get_balance() >= amount:
            self.accounts[self.current_account_number]["balance"] -= amount
            self.record_transaction("Withdrawal", -amount)
            return True, f"Withdrawn ${amount:.2f}. New balance: ${self.get_balance():.2f}"
        return False, "Insufficient funds."

    def deposit(self, amount):
        if amount <= 0:
            return False, "Invalid amount."
        self.accounts[self.current_account_number]["balance"] += amount
        self.record_transaction("Deposit", amount)
        return True, f"Deposited ${amount:.2f}. New balance: ${self.get_balance():.2f}"

    def get_transaction_history(self):
        return self.accounts[self.current_account_number]["transactions"]

    def logout(self):
        self.current_account_number = None
        self.pin_attempts = 0

class ATM_GUI:
    def __init__(self, master):
        self.master = master
        master.title("Sultan ATM GUI")
        master.geometry("800x600")
        master.resizable(False, False)

        self.atm = ATM()
        self.input_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.state = "ACCOUNT"
        self.pin_mask = ""
        self.temp_account = ""
        self.timeout_id = None

        self.init_ui()
        self.reset_ui()

    def init_ui(self):
        # Display frame
        screen = tk.Frame(self.master, bd=5, relief="sunken", bg="lightgray")
        screen.pack(padx=20, pady=10, fill="x")

        tk.Label(screen, textvariable=self.message_var, bg="lightgray",
                 font=("Arial", 14), wraplength=700, justify="left").pack(pady=10)

        self.display = tk.Label(screen, textvariable=self.input_var, font=("Courier", 18),
                                bg="white", height=2, anchor="e", relief="sunken", bd=2)
        self.display.pack(fill="x", padx=10, pady=(0, 10))

        # Keypad
        keypad = tk.Frame(self.master)
        keypad.pack(pady=10)
        keys = ['1','2','3','4','5','6','7','8','9','CLEAR','0','ENTER']

        for idx, val in enumerate(keys):
            cmd = self.clear_input if val == 'CLEAR' else (
                  self.process_input if val == 'ENTER' else lambda v=val: self.append_input(v))
            tk.Button(keypad, text=val, width=8, height=2, font=("Arial", 14),
                      bg="orange" if val == 'CLEAR' else "green" if val == 'ENTER' else None,
                      fg="white" if val in ['CLEAR','ENTER'] else None,
                      command=cmd).grid(row=idx//3, column=idx%3, padx=5, pady=5)

        # Cancel
        tk.Button(self.master, text="CANCEL", width=26, height=2, bg="red", fg="white",
                  font=("Arial", 14), command=self.cancel).pack(pady=10)

        # Side buttons
        self.menu_frame = tk.Frame(self.master)
        self.menu_frame.pack(pady=10)
        self.buttons = {}
        for label in ["Balance", "Withdraw", "Deposit", "History"]:
            b = tk.Button(self.menu_frame, text=label, font=("Arial", 12), width=12,
                          command=lambda l=label: self.side_action(l))
            b.pack(pady=5)
            self.buttons[label] = b

    def reset_ui(self):
        self.input_var.set("")
        self.message_var.set("Welcome to Sultan Bank!\nInsert your card (Enter Account Number).")
        self.state = "ACCOUNT"
        self.temp_account = ""
        self.pin_mask = ""
        self.disable_buttons()
        self.reset_timeout()

    def append_input(self, val):
        self.reset_timeout()
        current = self.input_var.get()
        if self.state == "PIN":
            if len(self.pin_mask) < 4:
                self.pin_mask += val
                self.input_var.set("*" * len(self.pin_mask))
        elif self.state in ["WITHDRAW", "DEPOSIT"]:
            if val == '.' and '.' in current:
                return
            self.input_var.set(current + val)
        elif self.state == "ACCOUNT":
            if len(current) < 9:
                self.input_var.set(current + val)

    def clear_input(self):
        self.input_var.set("")
        if self.state == "PIN":
            self.pin_mask = ""
        self.reset_timeout()

    def process_input(self):
        self.reset_timeout()
        if self.state == "ACCOUNT":
            account = self.input_var.get()
            if account:
                self.temp_account = account
                self.input_var.set("")
                self.pin_mask = ""
                self.state = "PIN"
                self.message_var.set("Enter your 4-digit PIN:")
        elif self.state == "PIN":
            pin = self.pin_mask
            success, msg = self.atm.validate_pin(self.temp_account, pin)
            self.message_var.set(msg)
            self.input_var.set("")
            self.pin_mask = ""
            if success:
                self.state = "MENU"
                self.enable_buttons()
                self.message_var.set("Login successful! Select an option.")
            elif "blocked" in msg:
                messagebox.showerror("Blocked", msg)
                self.reset_ui()
        elif self.state == "WITHDRAW":
            try:
                amount = float(self.input_var.get())
                success, msg = self.atm.withdraw(amount)
                self.message_var.set(msg)
                if success:
                    self.state = "MENU"
                self.input_var.set("")
            except:
                self.message_var.set("Enter a valid amount.")
                self.input_var.set("")
        elif self.state == "DEPOSIT":
            try:
                amount = float(self.input_var.get())
                success, msg = self.atm.deposit(amount)
                self.message_var.set(msg)
                if success:
                    self.state = "MENU"
                self.input_var.set("")
            except:
                self.message_var.set("Enter a valid amount.")
                self.input_var.set("")

    def cancel(self):
        if messagebox.askyesno("Exit", "Cancel current operation and logout?"):
            self.reset_ui()

    def side_action(self, action):
        self.reset_timeout()
        if self.state != "MENU":
            self.message_var.set("Finish current operation or press CANCEL.")
            return

        if action == "Balance":
            balance = self.atm.get_balance()
            self.message_var.set(f"Current balance: ${balance:.2f}")
        elif action == "Withdraw":
            self.state = "WITHDRAW"
            self.message_var.set("Enter amount to withdraw:")
            self.input_var.set("")
        elif action == "Deposit":
            self.state = "DEPOSIT"
            self.message_var.set("Enter amount to deposit:")
            self.input_var.set("")
        elif action == "History":
            history = self.atm.get_transaction_history()
            text = "\n".join(history) if history else "No transactions."
            self.show_scroll_window("Transaction History", text)

    def show_scroll_window(self, title, content):
        win = tk.Toplevel(self.master)
        win.title(title)
        st = scrolledtext.ScrolledText(win, width=60, height=20)
        st.pack(padx=10, pady=10)
        st.insert(tk.END, content)
        st.config(state=tk.DISABLED)

    def enable_buttons(self):
        for btn in self.buttons.values():
            btn.config(state=tk.NORMAL)

    def disable_buttons(self):
        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED)

    def reset_timeout(self):
        if self.timeout_id:
            self.master.after_cancel(self.timeout_id)
        self.timeout_id = self.master.after(60000, self.timeout)  # 1 minute inactivity

    def timeout(self):
        messagebox.showinfo("Session Timeout", "You were logged out due to inactivity.")
        self.reset_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = ATM_GUI(root)
    root.mainloop()
