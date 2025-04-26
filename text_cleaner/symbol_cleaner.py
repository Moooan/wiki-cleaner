import re

def handle_wiki_symbols(text):
    """
    统一处理 Wikipedia 原始文本中：
    - 表格
    - #, #*, #**, #*** 多层级有序/无序列表
    - * 无序列表
    - 一行多个 *条目 分裂处理
    - 正文中 *强调* 样式
    - 行首 ;:、::、: 这种标记清除
    """
    # 先整体删除表格
    text = re.sub(r"(?s)\{\|.*?\|\}", "", text)    # 删除 {| ... |} 区块
    text = re.sub(r"(?m)^(\|\-|\|.*)$", "", text)   # 删除 |- 开头、|内容行

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue  # 跳过空行

        # 先去掉行首的 ;:、::、: 标记
        line = re.sub(r"^(;:|::|:|;)\s*", "", line)

        # 处理 #* 多层级列表（#*、#**、#***）
        if re.match(r"^#+\*+", line):
            depth = line.count("*")
            content = re.sub(r"^#+\*+\s*", '', line)
            lines.append("    " * depth + "- " + content)
            continue

        # 处理 # 有序列表（纯 #，无 *）
        if re.match(r"^#+\s*", line):
            content = re.sub(r"^#+\s*", '', line)
            lines.append(content)
            continue

        # 处理一行多个 *条目
        if re.match(r"^\*(.+\*\s*)+", line):
            items = re.findall(r"\*\s*([^*]+)", line)
            for item in items:
                item = item.strip()
                if len(item) < 15 and not re.search(r"[。！？；：.!?;:]$", item):
                    continue
                lines.append("- " + item)
            continue

        # 处理单个 * 无序列表行
        if re.match(r"^\*", line):
            content = line.lstrip("*").strip()
            if len(content) < 15 and not re.search(r"[。！？；：.!?;:]$", content):
                continue
            lines.append("- " + content)
            continue

        # 正文里处理 *强调*，去掉两边的 *
        line = re.sub(r"\*(\S+?)\*", r"\1", line)
        lines.append(line)

    return "\n".join(lines)