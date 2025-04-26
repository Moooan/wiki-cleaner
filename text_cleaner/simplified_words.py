from opencc import OpenCC
import re

def normalize_chinese_text(text):
    """标准的中文文本预处理：
    - 繁转简
    - 全角转半角
    - 保留中文标点
    - 中英文之间加空格
    - 清理多余空格
    """

    # 1. 繁转简
    cc = OpenCC('t2s')
    text = cc.convert(text)

    # 2. 全角转半角
    def fullwidth_to_halfwidth(s):
        result = []
        for char in s:
            code = ord(char)
            if 0xFF01 <= code <= 0xFF5E:
                code -= 0xFEE0
            elif code == 0x3000:
                code = 0x0020
            result.append(chr(code))
        return ''.join(result)

    text = fullwidth_to_halfwidth(text)

    # 3. 中英文之间加空格（中文字符和英文、数字之间加空格）
    def add_space(text):
        # 中文与英文/数字之间加空格
        text = re.sub(r"([\u4e00-\u9fa5])([a-zA-Z0-9])", r"\1 \2", text)
        text = re.sub(r"([a-zA-Z0-9])([\u4e00-\u9fa5])", r"\1 \2", text)
        return text

    text = add_space(text)

    # 4. 去除多余的连续空格
    text = re.sub(r"\s+", " ", text).strip()

    return text