import mwparserfromhell
import re
from .template_cleaner import clean_wiki_template

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

    return title.strip(), clean_text.strip(), categories, templates