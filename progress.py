import tkinter as tk
from tkinter import ttk
import pandas as pd
import psycopg2
import subprocess
import threading
from import_and_gui import import_csv_to_db, count_waka, search_waka, random_show

DB_PARAMS = dict(dbname='waka_db', user='postgres', password='yourpass')

def initialize():
    btn_init.config(state='disabled')
    prog.start()
    label.config(text="初期化中…お待ちください")
    threading.Thread(target=run_initialization).start()

def run_initialization():
    subprocess.run(['python', 'full_auto_manyoshu.py'])
    subprocess.run(['python', 'aozora_auto_tanka.py'])
    subprocess.run(['python', 'merge_waka.py'])
    import_csv_to_db('waka.csv')
    cnt = count_waka()
    prog.stop()
    label.config(text=f"初期化完了。件数：{cnt}")
    btn_init.config(state='normal')

# ... import_csv_to_db, count_waka, search/random/display は前と同じ ...

# ── GUI 構成 ──────────────────────────────────
root = tk.Tk()
root.title("和歌アーカイブ GUI（進捗付き）")

frame = tk.Frame(root); frame.pack(pady=10)
entry = tk.Entry(frame, width=40)
entry.grid(row=0, column=0, padx=5)
tk.Button(frame, text="検索", command=search_waka).grid(row=0, column=1, padx=5)
tk.Button(frame, text="ランダム", command=random_show).grid(row=0, column=2, padx=5)

btn_init = tk.Button(root, text="DB 初期化", command=initialize, fg="white", bg="blue")
btn_init.pack(pady=8)

prog = ttk.Progressbar(root, mode='indeterminate', length=300)
prog.pack(pady=4)

label = tk.Label(root, text="未初期化", fg="green"); label.pack()
text_box = tk.Text(root, width=60, height=20, wrap="word"); text_box.pack(pady=10)

root.mainloop()
#UI 改良サンプル