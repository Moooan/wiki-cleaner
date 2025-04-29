from .wiki_text_cleaner import clean_text_with_mwparser
from .simplified_words import normalize_chinese_text
from .refine_cleaner import refine_clean_text
from .symbol_cleaner import handle_wiki_symbols
from .en_cleaner import remove_long_english_sentences
import json

def should_drop_article(text, title, ns) -> bool:
    """
    判断一篇文章是否应当丢弃（如MediaWiki系统页、签名、垃圾配置）
    meta: 字典，包含 'ns', 'title' 字段
    text: 原始文本内容
    返回 True 表示应丢弃
    """


    # 1. 命名空间过滤：MediaWiki系统空间等
    if ns == "8":  # MediaWiki 系统空间
        return True
    if ns == "10":  # Template: 模板空间
        # 有些模板页面也不是正文内容（如果你想保留一部分模板可例外处理）
        if any(kw in title for kw in ['documentation', 'sandbox', 'testcases']):
            return True

    # 2. 标题关键词过滤
    drop_keywords = [
        'newusermessage', 'signatures', 'gadget', 'common.css', 'common.js',
        'vector.js', 'vector.css', 'sitenotice', 'watchlist', 'talk', 'admin',
        'javascript', 'testcases', 'abusefilter', 'sitestatistics'
    ]
    if any(kw in title for kw in drop_keywords):
        return True

    # 3. 内容特征过滤（过多签名、讨论、留言、inactive标签等）
    bad_content_keywords = ['inactive|', 'blocked|', '留言', '签名', 'signatures', 'talk', '欢迎']
    bad_line_count = sum(1 for kw in bad_content_keywords if kw in text.lower())
    if bad_line_count >= 3 and text.count('|') > 10 and len(text) > 300:
        return True

    return False

def process_article(df):


    final_data = []

    for row in df.itertuples(index=False):
        title = row.title
        text = row.text
        ns = row.ns

        clean_title, clean_text, category, templates = clean_text_with_mwparser(title, text)
        clean_title = normalize_chinese_text(clean_title)
        clean_text = normalize_chinese_text(clean_text)
        if should_drop_article(clean_text, clean_title, ns):
            continue
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