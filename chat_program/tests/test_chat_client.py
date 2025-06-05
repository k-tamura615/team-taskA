import unittest
import tkinter as tk
from unittest.mock import patch
from chat_client import ChatClientGUI

class TestChatClientGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # テスト時に画面を表示しない

        # askstring をモックしてIPと名前を仮入力
        self.dialog_patch = patch('tkinter.simpledialog.askstring', side_effect=["127.0.0.1", "test_user"])
        self.socket_patch = patch('socket.socket')
        self.dialog_patch.start()
        self.mock_socket = self.socket_patch.start()

        # モックのソケットが connect/sendall を許容
        self.mock_socket.return_value.connect.return_value = None
        self.mock_socket.return_value.sendall.return_value = None

        self.chat = ChatClientGUI(self.root)

    def tearDown(self):
        self.dialog_patch.stop()
        self.socket_patch.stop()
        self.root.destroy()

    def test_add_message_you(self):
        """自分のメッセージが右寄せ・緑背景で表示されるか"""
        msg = "こんにちは、自分です"
        self.chat.add_message(msg, sender="you")
        bubble = self.chat.message_bubbles[-1]
        self.assertEqual(bubble.cget("text"), msg)
        self.assertEqual(bubble.cget("bg"), "#dcf8c6")  # 緑背景

    def test_add_message_other(self):
        """相手のメッセージが左寄せ・白背景で表示されるか"""
        msg = "こんにちは、相手です"
        self.chat.add_message(msg, sender="other")
        bubble = self.chat.message_bubbles[-1]
        self.assertEqual(bubble.cget("text"), "こんにちは、相手です")
        self.assertEqual(bubble.cget("bg"), "#ffffff")  # 白背景

    def test_wraplength_max(self):
        """wraplength が最大横幅を超えていないか"""
        long_msg = "あ" * 200  # 長文
        self.chat.add_message(long_msg, sender="you")
        bubble = self.chat.message_bubbles[-1]
        max_width = int(self.chat.root.winfo_width() * 0.75)
        self.assertLessEqual(bubble.cget("wraplength"), max_width)

    def test_gui_components_exist(self):
        """重要なGUI部品が存在しているか"""
        self.assertIsInstance(self.chat.canvas, tk.Canvas)
        self.assertIsInstance(self.chat.entry, tk.Text)
        self.assertIsInstance(self.chat.message_frame, tk.Frame)

if __name__ == "__main__":
    unittest.main()
