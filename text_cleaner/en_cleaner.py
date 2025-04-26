import re

def remove_long_english_sentences(text, threshold=0.7):
    """
    删除英文字符比例超过 threshold 的整行（比如纯英文或几乎全英文的行）
    threshold：英文字母/总字符的比例，超过就删除
    """
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # 统计英文字符数量
        english_chars = len(re.findall(r'[A-Za-z]', line))
        total_chars = len(line)

        if total_chars == 0:
            continue

        ratio = english_chars / total_chars

        if ratio > threshold:
            continue  # 扔掉这行
        else:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)