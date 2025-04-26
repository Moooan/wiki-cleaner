from .wiki_text_cleaner import clean_text_with_mwparser
from .simplified_words import normalize_chinese_text
from .refine_cleaner import refine_clean_text
from .symbol_cleaner import handle_wiki_symbols
from .en_cleaner import remove_long_english_sentences
import json

def process_article(df):


    final_data = []

    for row in df.itertuples(index=False):
        title = row.title
        text = row.text

        clean_title, clean_text, category, templates = clean_text_with_mwparser(title, text)
        clean_title = normalize_chinese_text(clean_title)
        clean_text = normalize_chinese_text(clean_text)
        clean_category = []
        for x in category:
            clean_category.append(normalize_chinese_text(x))

        clean_text = refine_clean_text(clean_text)
        clean_text = handle_wiki_symbols(clean_text)
        final_text = remove_long_english_sentences(clean_text)

        final_data.append({
            "text": final_text.strip(),
            "meta": {
                "title": clean_title.strip(),
                "category": clean_category,
                "id": row.id,
                "timestamp": row.timestamp,
                "username": row.username,
                "ns": row.ns
            }
        })

    # 一次性保存或者分批保存
    with open("data/wiki_articles_final_cleaned.json", "w", encoding="utf-8") as f:
        for item in final_data:
            f.write(json.dumps(item, ensure_ascii=False) + ",\n")