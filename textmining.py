# ===== セットアップ =====
# pip install PyPDF2 janome wordcloud

from pathlib import Path
import re
from collections import Counter
from typing import Optional

import PyPDF2
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud


# ---------- 1) PDFからテキスト抽出 ----------
def extract_text_from_pdf(pdf_path: Path) -> str:
    text_parts = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text() or ""
            text_parts.append(t)
    return "\n".join(text_parts)


# ---------- 2) 形態素解析（日本語＋英単語対応） ----------
def tokenize_ja_en(text: str, extra_stopwords: Optional[set[str]] = None) -> list[str]:
    t = Tokenizer()

    # 日本語の基本ストップワード
    stopwords = set("""
        する なる ある いる こと これ それ あれ ため よう もの ところ
        私 僕 です ます でした ません では から まで など また そして
        に より ので とか へ が を による における に対して として
        ー ― ～ ・ … 　 の は が を に で と も だ です ね よ にして
    """.split())

    # 英語のストップワード（よくある機能語）
    english_stopwords = set("""
        the a an and or but if then else when at to from by for of in on with 
        this that these those is are was were be been being do does did have has had
    """.split())

    stopwords |= english_stopwords

    # 外部ファイル stopwords.txt の追加
    if extra_stopwords:
        stopwords |= {w.lower() for w in extra_stopwords}

    tokens: list[str] = []

    for token in t.tokenize(text):
        base = token.base_form
        pos = token.part_of_speech.split(",")[0]
        surface = token.surface

        # 日本語 → 名詞/形容詞/動詞のみ残す
        if pos in {"名詞", "形容詞", "動詞"}:
            word = base if base != "*" else surface
        else:
            # 英単語やその他はそのまま
            word = surface

        # 記号除外
        if re.fullmatch(r"[！-／：-＠［-｀｛-～、-〜。・「」『』（）【】…―ー\s]+", word):
            continue

        if len(word) <= 1:
            continue

        # 英語は小文字化してストップワードチェック
        if word.lower() in stopwords:
            continue

        tokens.append(word)

    return tokens


# ---------- 3) ワードクラウド生成 ----------
def make_wordcloud(tokens: list[str],
                   out_path: str = "wordcloud.png",
                   font_path: Optional[str] = None):
    freqs = Counter(tokens)

    if font_path is None:
        raise ValueError("font_path を日本語フォントのパスに設定してください。")

    wc = WordCloud(
        width=1600,
        height=900,
        background_color="white",
        font_path=font_path,
        collocations=False,
        regexp=r"[^ \f\n\r\t\v]+"
    ).generate_from_frequencies(freqs)

    wc.to_file(out_path)
    print(f"Saved: {out_path}")


# ---------- 4) 実行例（pdfフォルダ内すべて対象） ----------
if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent
    PDF_DIR = BASE_DIR / "pdf"
    STOPWORDS_FILE = BASE_DIR / "stopwords.txt"
    FONT_PATH = "C:\\Windows\\Fonts\\meiryo.ttc"  # ←環境に合わせて修正

    # PDFファイルを取得
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print("pdf フォルダにPDFが見つかりませんでした。")
        exit()

    print(f"対象PDFファイル数: {len(pdf_files)}")

    # stopwords.txt を読み込み
    extra_stopwords = set()
    if STOPWORDS_FILE.exists():
        with open(STOPWORDS_FILE, "r", encoding="utf-8") as f:
            extra_stopwords = {line.strip() for line in f if line.strip()}
        print(f"除外ワード数: {len(extra_stopwords)}")
    else:
        print("stopwords.txt が見つかりません（追加ストップワードなしで実行します）")

    # テキスト結合
    all_text = ""
    for pdf_path in pdf_files:
        print(f"読み込み中: {pdf_path.name}")
        all_text += extract_text_from_pdf(pdf_path) + "\n"

    # トークン化（日本語＋英語対応）
    tokens = tokenize_ja_en(all_text, extra_stopwords=extra_stopwords)

    # ワードクラウド生成
    make_wordcloud(tokens, out_path="wordcloud.png", font_path=FONT_PATH)
