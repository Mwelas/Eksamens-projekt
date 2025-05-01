import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "users_data.json"

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatApp")
        self.root.geometry("750x550")
        self.root.configure(bg="#202225")
        self.root.resizable(False, False)
        self.current_user = None
        self.current_chat = None
        self.refresh_interval = 1000
        self.login_screen()

    def login_screen(self):
        self.clear()
        tk.Label(self.root, text="Velkommen til ChatApp", font=("Helvetica Neue", 20, "bold"), fg="#FFFFFF", bg="#202225").pack(pady=30)
        self.username_entry = tk.Entry(self.root, font=("Helvetica Neue", 14), width=30, bg="#2f3136", fg="#FFFFFF", insertbackground="white", relief="flat")
        self.username_entry.pack(pady=10)
        tk.Button(self.root, text="Log ind / Opret", command=self.login, font=("Helvetica Neue", 12), bg="#7289DA", fg="white", relief="flat").pack(pady=15)

    def login(self):
        name = self.username_entry.get().strip()
        if not name:
            messagebox.showerror("Fejl", "Indtast et brugernavn")
            return
        users = load_users()
        if name not in users:
            users[name] = {"friends": [], "messages": {}}
            save_users(users)
        self.current_user = name
        self.main_screen()

    def main_screen(self):
        self.clear()
        self.left_frame = tk.Frame(self.root, width=220, bg="#2f3136")
        self.left_frame.pack(side="left", fill="y")
        self.right_frame = tk.Frame(self.root, bg="#36393F")
        self.right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(self.left_frame, text=f"Bruger: {self.current_user}", bg="#2f3136", fg="white", font=("Helvetica Neue", 12)).pack(pady=15)
        self.friend_listbox = tk.Listbox(self.left_frame, bg="#23272A", fg="white", font=("Helvetica Neue", 11), selectbackground="#7289DA", relief="flat", activestyle="none")
        self.friend_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.friend_listbox.bind("<<ListboxSelect>>", self.select_chat)

        tk.Button(self.left_frame, text="Tilføj ven", command=self.add_friend, font=("Helvetica Neue", 11), bg="#43B581", fg="white", relief="flat").pack(pady=10)

        self.chat_display = tk.Text(self.right_frame, bg="#2C2F33", fg="white", font=("Helvetica Neue", 11), state="disabled", wrap="word", relief="flat", padx=10, pady=10)
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.chat_entry = tk.Entry(self.right_frame, font=("Helvetica Neue", 11), bg="#40444B", fg="white", insertbackground="white", relief="flat")
        self.chat_entry.pack(fill="x", padx=10, pady=10)
        self.chat_entry.bind("<Return>", self.send_message)

        self.update_friend_list()
        self.auto_refresh()

    def add_friend(self):
        users = load_users()
        friend = simpledialog.askstring("Tilføj ven", "Brugernavn på ven:")
        if not friend:
            return
        if friend == self.current_user:
            messagebox.showwarning("Fejl", "Du kan ikke tilføje dig selv")
            return
        if friend not in users:
            messagebox.showerror("Fejl", "Brugeren findes ikke")
            return
        if friend in users[self.current_user]["friends"]:
            messagebox.showinfo("Info", "I er allerede venner")
            return
        users[self.current_user]["friends"].append(friend)
        users[friend]["friends"].append(self.current_user)
        users[self.current_user]["messages"].setdefault(friend, [])
        users[friend]["messages"].setdefault(self.current_user, [])
        save_users(users)
        self.update_friend_list()
        messagebox.showinfo("Tilføjet", f"Du er nu venner med {friend}")

    def update_friend_list(self):
        users = load_users()
        self.friend_listbox.delete(0, tk.END)
        for f in users[self.current_user]["friends"]:
            self.friend_listbox.insert(tk.END, f)

    def select_chat(self, event):
        sel = self.friend_listbox.curselection()
        if not sel:
            return
        self.current_chat = self.friend_listbox.get(sel)
        self.refresh_chat()

    def refresh_chat(self):
        users = load_users()
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        if self.current_chat:
            for msg_data in users[self.current_user]["messages"].get(self.current_chat, []):
                try:
                    sender, content, timestamp = msg_data.split("||")
                except:
                    continue
                tag = "me" if sender == self.current_user else "other"
                formatted = f"{sender} [{timestamp}]:\n{content}\n\n"
                self.chat_display.insert(tk.END, formatted, tag)
            self.chat_display.tag_config("me", foreground="#43B581")
            self.chat_display.tag_config("other", foreground="#7289DA")
        self.chat_display.config(state="disabled")

    def send_message(self, event=None):
        users = load_users()
        if not self.current_chat:
            return
        msg = self.chat_entry.get().strip()
        if msg:
            timestamp = datetime.now().strftime("%H:%M")
            formatted_msg = f"{self.current_user}||{msg}||{timestamp}"
            users[self.current_user]["messages"][self.current_chat].append(formatted_msg)
            users[self.current_chat]["messages"][self.current_user].append(formatted_msg)
            save_users(users)
            self.chat_entry.delete(0, tk.END)
            self.refresh_chat()

    def auto_refresh(self):
        if self.current_chat:
            self.refresh_chat()
        self.root.after(self.refresh_interval, self.auto_refresh)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
