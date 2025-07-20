import tkinter as tk
import pandas as pd
import psycopg2
import subprocess
import threading

DB_PARAMS = dict(dbname='waka_db', user='postgres', password='yourpass')

def initialize():
    label.config(text="初期化中…お待ちください")
    def task():
        subprocess.run(['python', 'full_auto_manyoshu.py'])
        subprocess.run(['python', 'aozora_auto_tanka.py'])
        subprocess.run(['python', 'merge_waka.py'])
        import_csv_to_db('waka.csv')
        cnt = count_waka()
        label.config(text=f"初期化完了。件数：{cnt}")
    threading.Thread(target=task).start()

def import_csv_to_db(path):
    df = pd.read_csv(path)
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS waka (
        id SERIAL PRIMARY KEY,
        text TEXT,
        kana TEXT,
        romaji TEXT,
        author VARCHAR(100),
        era VARCHAR(50),
        collection VARCHAR(100),
        season VARCHAR(20),
        theme VARCHAR(50),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    """)
    cur.execute("TRUNCATE waka")
    for _, r in df.iterrows():
        cur.execute("""
          INSERT INTO waka(text, kana, romaji, author, era, collection, season, theme, notes)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(r))
    conn.commit()
    cur.close()
    conn.close()

def count_waka():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM waka")
    cnt = cur.fetchone()[0]
    cur.close(); conn.close()
    return cnt

def search_waka():
    keyword = entry.get()
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT text, author FROM waka WHERE text ILIKE %s LIMIT 10", (f"%{keyword}%",))
    rows = cur.fetchall()
    conn.close()
    display_results(rows)

def random_show():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT text, author FROM waka ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    conn.close()
    display_results([row])

def display_results(rows):
    text_box.delete('1.0', tk.END)
    for t, a in rows:
        text_box.insert(tk.END, f"　{a}：\n　{t}\n\n")

# ── GUI構築 ────────────────────────────
root = tk.Tk()
root.title("和歌アーカイブ GUI")

frame = tk.Frame(root)
frame.pack(pady=10)

entry = tk.Entry(frame, width=40)
entry.grid(row=0, column=0, padx=5)
btn_search = tk.Button(frame, text="検索", command=search_waka)
btn_search.grid(row=0, column=1, padx=5)
btn_random = tk.Button(frame, text="ランダム", command=random_show)
btn_random.grid(row=0, column=2, padx=5)

btn_init = tk.Button(root, text="データベース初期化", command=initialize, fg="white", bg="blue")
btn_init.pack(pady=10)

label = tk.Label(root, text="未初期化", fg="green")
label.pack()

text_box = tk.Text(root, width=60, height=20, wrap="word")
text_box.pack(pady=10)

root.mainloop()