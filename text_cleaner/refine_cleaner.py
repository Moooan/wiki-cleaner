import re

def normalize_double_paren(text):
    """
    双括号问题
    """
    text = re.sub(r'\(\((.*?)\)\)', r'（\1）', text)
    text = re.sub(r'（（(.*?)））', r'（\1）', text)
    return text

def refine_clean_text(text):
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # 检查是否有内嵌标题（行内标题）
        while True:
            match = re.search(r"(.*?)\s*(={2,})\s*([^=]+?)\s*\2\s*(.*)", line)
            if match:
                before = match.group(1).strip()
                title = match.group(3).strip()
                after = match.group(4).strip()

                if before:
                    lines.append(before)

                lines.append(f"<<TITLE>>{title}")  # 用特殊标记，等下再处理！
                line = after
            else:
                break
        
        if line:
            lines.append(line)

    # 合并行，分成块处理
    final_lines = []
    temp_block = []
    for line in lines:
        if line.startswith("<<TITLE>>"):
            # 遇到标题，先处理之前的块
            if temp_block:
                final_lines.extend(temp_block)
                temp_block = []
            final_lines.append(line)
        else:
            temp_block.append(line)

    if temp_block:
        final_lines.extend(temp_block)

    # 第二轮：删除空标题（标题后面没有正文块）
    cleaned_lines = []
    skip_next_title = False
    for i, line in enumerate(final_lines):
        if line.startswith("<<TITLE>>"):
            # 看下一个是否是正文
            if i == len(final_lines) - 1 or final_lines[i+1].startswith("<<TITLE>>"):
                continue  # 当前标题后没有正文，跳过（删除）
            cleaned_lines.append(line.replace("<<TITLE>>", ""))  # 恢复标题，去掉标记
        else:
            cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    
    # 删除所有 <ref>...</ref> 标签及内容（支持格式错误的）
    text = re.sub(r"<\s*ref[^>]*?>[\s\S]*?<\s*/\s*ref\s*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*ref\b[^>/]*?/\s*>", "", text, flags=re.IGNORECASE)
    
    text = re.sub(r"'{2,}", "", text)
    
    text = re.sub(r"<[^>]+>", "", text)
    
    text = re.sub(r"\[\[Category:[^\]]+\]\]", "", text)
    text = re.sub(r"\[\[分类:[^\]]+\]\]", "", text)
    text = re.sub(r"\[\[分類:[^\]]+\]\]", "", text)
    
    text = re.sub(r"^\s+|\s+$", "", text)
    

    #  删除 markdown / wiki 列表标记
    text = re.sub(r"^[*#]+", "", text, flags=re.MULTILINE)

    #  删除多余空行，合并多个空行为1行
    text = re.sub(r"\n{2,}", "\n", text)


    # 删除媒体文件行（.jpg|说明文字）
    text = re.sub(r"^[^\n]*\.(jpg|jpeg|png|svg|gif|ogg|ogv|webm)\|.*$", "", text, flags=re.MULTILINE | re.IGNORECASE)

    #  删除空或无效括号
    text = re.sub(r"[\(\（][\s　]*[\)\）]", "", text)  # 纯空括号
    text = re.sub(r"[\(\（][^\u4e00-\u9fa5]{0,2}[\)\）]", "", text)  # 短无意义括号
    
    #  去除行首尾空格
    text = "\n".join(line.strip() for line in text.splitlines())
    
    text = normalize_double_paren(text)

    # 清除 MediaWiki 表格语法残渣，例如 !colspan=...|xxxx
    text = re.sub(r'!+\s*colspan\s*=\s*".+?"\s*\|', '', text, flags=re.IGNORECASE)


    return text.strip()