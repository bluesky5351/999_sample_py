import re
from typing import Optional
from fugashi import Tokenizer

def tokenize_ja_en(text: str, extra_stopwords: Optional[set[str]] = None) -> list[str]:
    t = Tokenizer()
    # 日本語基本ストップワード
    stopwords = set("""
        する なる ある いる こと これ それ あれ ため よう もの ところ
        私 僕 です ます でした ません では から まで など また そして
        に により ので とか へ が を による における に対して として
        ー ― ～ ・ … 　 の は が を に で と も だ です ね よ
    """.split())
    # 英語の簡易ストップワード（必要なら拡張可）
    english_stopwords = set("""
        the a an and or but if then else when at to from by for of in on with 
        this that these those is are was were be been being do does did have has had
    """.split())
    stopwords |= english_stopwords
    # 外部ファイルの追加
    if extra_stopwords:
        stopwords |= extra_stopwords
    tokens: list[str] = []
    for token in t.tokenize(text):
        base = token.base_form
        pos = token.part_of_speech.split(",")[0]
        surface = token.surface
        # 日本語の名詞/形容詞/動詞はそのまま
        if pos in {"名詞", "形容詞", "動詞"}:
            word = base if base != "*" else surface
        else:
            # 日本語以外（英単語など）は原形そのまま使う
            word = surface
        # 記号は除外
        if re.fullmatch(r"[！-／：-＠［-｀｛-～、-〜。・「」『』（）【】…―ー\s]+", word):
            continue
        if len(word) <= 1:
            continue
        if word.lower() in stopwords:  # 英語小文字化して比較
            continue
        tokens.append(word)
    return tokens

if __name__ == "__main__":
    print("=== テキストマイニング ツール ===")
    print()
    
    while True:
        print("1. テキストを入力してトークナイズ")
        print("2. ファイルからテキストを読み込んでトークナイズ")
        print("3. 終了")
        print()
        
        choice = input("選択してください (1-3): ").strip()
        
        if choice == "1":
            print("\n--- テキスト入力モード ---")
            text = input("解析したいテキストを入力してください: ")
            if text.strip():
                print("\n解析中...")
                tokens = tokenize_ja_en(text)
                print(f"\nトークン数: {len(tokens)}")
                print("トークン一覧:")
                for i, token in enumerate(tokens, 1):
                    print(f"{i:3d}: {token}")
            else:
                print("テキストが入力されていません。")
        
        elif choice == "2":
            print("\n--- ファイル読み込みモード ---")
            file_path = input("ファイルパスを入力してください: ").strip()
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                print(f"\nファイルを読み込みました: {file_path}")
                print("解析中...")
                tokens = tokenize_ja_en(text)
                print(f"\nトークン数: {len(tokens)}")
                print("トークン一覧:")
                for i, token in enumerate(tokens, 1):
                    print(f"{i:3d}: {token}")
                    
                # 結果をファイルに保存するか確認
                save = input("\n結果をファイルに保存しますか？ (y/n): ").strip().lower()
                if save in ['y', 'yes']:
                    output_path = file_path.replace('.txt', '_tokens.txt')
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for token in tokens:
                            f.write(token + '\n')
                    print(f"結果を保存しました: {output_path}")
                    
            except FileNotFoundError:
                print(f"ファイルが見つかりません: {file_path}")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
        
        elif choice == "3":
            print("プログラムを終了します。")
            break
        
        else:
            print("無効な選択です。1-3の数字を入力してください。")
        
        print("\n" + "="*50 + "\n")
    
    input("Enterキーを押して終了してください...")