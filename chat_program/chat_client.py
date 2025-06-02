import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

PORT = 12345

class ChatClientGUI:
    def __init__(self, master):
        self.root = master
        self.root.withdraw()
        self.message_bubbles = []

        self.server_ip = simpledialog.askstring("接続先", "サーバーのIPアドレスを入力してください:", parent=self.root)
        if not self.server_ip:
            messagebox.showerror("エラー", "IPアドレスが入力されていません。")
            self.root.destroy()
            return

        self.name = simpledialog.askstring("ニックネーム", "あなたの名前を入力してください:", parent=self.root)
        if not self.name:
            self.root.destroy()
            return

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.server_ip, PORT))
            self.client.sendall(self.name.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("接続失敗", f"サーバーに接続できませんでした。\nエラー: {e}")
            self.root.destroy()
            return

        self.setup_chat_window()
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()
        self.root.mainloop()

    def setup_chat_window(self):
        self.root.deiconify()
        self.root.title(f"LINE風チャット - {self.name}")
        self.root.geometry("600x600")
        self.root.configure(bg="#e5ddd5")
        self.root.resizable(True, True)
        self.root.bind("<Configure>", lambda e: self.update_wraplengths())

        top_frame = tk.Frame(self.root, bg="#e5ddd5")
        top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.75)

        self.canvas = tk.Canvas(top_frame, bg="#e5ddd5", highlightthickness=0)
        self.frame = tk.Frame(self.canvas, bg="#e5ddd5")
        self.scrollbar = tk.Scrollbar(top_frame, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.place(relx=0, rely=0.75, relwidth=1, relheight=0.25)

        self.entry = tk.Text(bottom_frame, font=("Meiryo", 12), height=4, wrap=tk.WORD)
        self.entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        self.entry.bind("<Return>", self.send_message)
        self.entry.bind("<Shift-Return>", self.allow_newline)

    def update_wraplengths(self):
        for bubble in self.message_bubbles:
            pass  # 必要ならここでwraplengthを調整できます

    def send_message(self, event=None):
        msg = self.entry.get("1.0", tk.END).strip()
        if msg:
            try:
                full_msg = f"{self.name}: {msg}"
                self.client.sendall(full_msg.encode('utf-8'))
                self.add_message(full_msg, sender="you")
                self.entry.delete("1.0", tk.END)
            except:
                self.add_message("送信エラー", sender="system")
        return 'break'

    def allow_newline(self, event=None):
        self.entry.insert(tk.INSERT, '\n')
        return 'break'

    def add_message(self, msg, sender="other"):
        bubble_color = "#dcf8c6" if sender == "you" else "#ffffff"
        right_margin = 5  # ここを5pxに変更しました
        max_bubble_width = int(self.root.winfo_width() * 0.75)

        char_width_px = 7
        text_length = len(msg)
        desired_width = min(max_bubble_width, char_width_px * text_length + 20)
        wrap_length = desired_width - 20

        msg_frame = tk.Frame(self.frame, bg="#e5ddd5")

        bubble = tk.Label(
            msg_frame,
            text=msg,
            bg=bubble_color,
            font=("Meiryo", 11),
            padx=10,
            pady=6,
            justify="left",
            anchor="w",
            wraplength=wrap_length
        )

        self.message_bubbles.append(bubble)

        bubble.pack()

        if sender == "you":
            msg_frame.pack(anchor="e", padx=(0, right_margin), pady=4)
        elif sender == "other":
            msg_frame.pack(anchor="w", padx=(right_margin, 0), pady=4)
        else:
            msg_frame.pack(anchor="center", pady=4)

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode('utf-8')
                if msg:
                    self.add_message(msg, sender="other")
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
