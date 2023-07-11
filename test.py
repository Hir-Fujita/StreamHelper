import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x300")

# スクロールバーの設定
scrollbar = ttk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# スクロール可能なFrameの作成
canvas = tk.Canvas(root, yscrollcommand=scrollbar.set)
canvas.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=canvas.yview)

# スクロール領域のフレームを作成
scrollable_frame = ttk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# ダミーコンテンツの追加
for i in range(50):
    ttk.Label(scrollable_frame, text="Label " + str(i)).pack()

root.mainloop()
