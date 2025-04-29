import mwparserfromhell
import re
from .template_cleaner import clean_wiki_template

def replace_zh_template(text):
    return re.sub(r'\{zh-hans:([^;{}]+);[^{}]*\}', r'\1', text)

def remove_unparsed_templates(text):
    """
    强化版清除所有未识别模板，包括跨行{{...}}
    """
    # 连续清除嵌套模板直到收敛
    while True:
        nested = re.search(r'\{\{[^{}]*\{\{[^{}]*\}\}[^{}]*\}\}', text, flags=re.DOTALL)
        if not nested:
            break
        text = re.sub(r'\{\{[^{}]*\{\{[^{}]*\}\}[^{}]*\}\}', '', text, flags=re.DOTALL)

    # 清除普通大模板 {{...}}，支持跨行
    text = re.sub(r'\{\{[\s\S]*?\}\}', '', text)

    # 三括号 {{{...}}}
    text = re.sub(r'\{\{\{(?:[^{}]|\n|\r){1,500}?\}\}\}', '', text, flags=re.DOTALL)

    return text

def remove_other_garbage(text):
    text = re.sub(r'\[\[(Category|分类|分類):[^\]]+\]\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[(File|Image|文件):[^\]]+\]\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    if any(k in text for k in ['留言', '签名', 'signatures', '讨论', 'talk']):
        if len(text) > 500 and text.count('|') > 10:
            return ''
    return text

def normalize_text(text):
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^[\*\#\-\|]+$', line):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def clean_text_with_mwparser(title, text):
    """
    解析并清理Wiki文本，包括智能处理模板
    """
    
    wikicode = mwparserfromhell.parse(text)
    cleaned_text_parts = []
    categories = []
    templates = []

    for node in wikicode.ifilter(recursive=False):
        node_str = str(node).strip()

        # 处理模板
        if isinstance(node, mwparserfromhell.nodes.Template):
            templates.append(str(node.name).strip())
            cleaned = clean_wiki_template(node)
            if cleaned:
                cleaned_text_parts.append(cleaned)
            continue

            
        # 删除注释
        if isinstance(node, mwparserfromhell.nodes.Comment): 
            continue
        elif isinstance(node, mwparserfromhell.nodes.Tag) and node.tag.lower() in ['ref', 'gallery']:
            continue
        # 删除外部链接
        elif isinstance(node, mwparserfromhell.nodes.ExternalLink): 
            continue
        # 分类标签处理
        elif re.match(r"\[\[(Category|分类|分類):([^\]]+)\]\]", node_str, flags=re.IGNORECASE):
            match = re.match(r"\[\[(Category|分类|分類):([^\]]+)\]\]", node_str, flags=re.IGNORECASE)
            if match:
                category_name = match.group(2).strip()
                categories.append(category_name)
            continue
        # 删除图片
        elif 'thumb|' in node_str or 'File:' in node_str or 'Image:' in node_str: 
            continue
        # 删除维基百科内部链接
        elif isinstance(node, mwparserfromhell.nodes.Wikilink):
            replacement = node.text if node.text else node.title
            cleaned_text_parts.append(str(replacement))

        # 删除表格
        elif node_str.startswith('{|') and node_str.endswith('|}'):
            continue
        elif re.search(r'^{\|[\s\S]+?\|}$', node_str, re.MULTILINE):
            continue
        else:
            # 	删除<script>、<style> 
            cleaned_text_parts.append(node_str)

    clean_text = ''.join(cleaned_text_parts)
    clean_text = mwparserfromhell.parse(clean_text).strip_code()

    # 二次处理没有识别好的模板
    clean_text = replace_zh_template(clean_text)
    clean_text = remove_unparsed_templates(clean_text)
    clean_text = remove_other_garbage(clean_text)
    clean_text = normalize_text(clean_text)

    return title.strip(), clean_text.strip(), categories, templates