import requests
import zipfile, io, re
import os, pandas as pd
from aozora_corpus_generator.aozora import read_aozora_bunko_list, read_aozora_bunko_xml

# 万葉集 book_id
BOOK_ID = '200015542'
# 青空文庫パス
AOZORA_REPO = 'path/to/aozorabunko'
CSV_LIST = os.path.join(AOZORA_REPO, 'list_person_all_extended_utf8.zip')

def fetch_manyoshu():
    url = f'https://codh.rois.ac.jp/pmjt/book/{BOOK_ID}/download.zip'
    print("Downloading 万葉集 ZIP from:", url)
    r = requests.get(url); r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    poems=[]
    for name in z.namelist():
        if name.endswith('.txt'):
            txt = z.read(name).decode('utf-8')
            parts = re.split(r'\n(?=\d+)', txt)
            for part in parts:
                lines = part.strip().splitlines()
                if len(lines)>=2 and re.match(r'^\d+', lines[0]):
                    poems.append(''.join(lines[1:]).strip())
    print(f"万葉集取得：{len(poems)} 首")
    return pd.DataFrame({
        'text': poems,'kana':'','romaji':'','author':'不明',
        'era':'奈良','collection':'万葉集','season':'','theme':'','notes':''})

def fetch_aozora():
    aozora_db = read_aozora_bunko_list(CSV_LIST, ndc_map=None)
    rows=[]
    for author, works in aozora_db.items():
        for title, meta in works.items():
            if '短歌' in title or '和歌集' in title:
                path = os.path.join(AOZORA_REPO, meta['file_path'])
                proc = read_aozora_bunko_xml(path, features=['orth'], no_punc=True)
                for line in proc['text'].split('\n'):
                    line = line.strip()
                    if len(line)>10:
                        rows.append({
                            'text': line,'kana':'','romaji':'','author':author,
                            'era':'','collection':title,'season':'','theme':'','notes':''
                        })
    print(f"青空文庫取得：{len(rows)} 首")
    return pd.DataFrame(rows)

def main():
    df1 = fetch_manyoshu()
    df2 = fetch_aozora()
    df = pd.concat([df1, df2], ignore_index=True).drop_duplicates(subset=['text'])
    df.to_csv('waka.csv', index=False, encoding='utf-8')
    print(f"統合 waka.csv 完成：{len(df)} 件")

if __name__ == '__main__':
    main()