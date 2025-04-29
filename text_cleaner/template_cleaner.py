import mwparserfromhell
import re

def clean_wiki_template(node):
    name = str(node.name).strip().lower()
    TEMPLATE_BLACKLIST = [
        'clear', 'reflist', 'nowrap', 'empty section', 'commonscat', 
        'authority control', 'defaultsort', 'infobox', 'sfn', 'efn',
        'cite web', 'cite news', 'cite book', 
        '#expr', '#if', '#ifeq', '#switch', '#invoke', '#lst', '#tag',
        'citation', 'book reference'
    ]
    if any(name.startswith(b) for b in TEMPLATE_BLACKLIST):
        return ''

    if name.startswith('lang-') or name == 'lang':
        if node.params:
            return f"({str(node.params[0].value).strip()})"
        return ''

    if name == 'birth date' and len(node.params) >= 3:
        y, m, d = node.params[0], node.params[1], node.params[2]
        return f"{y}年{m}月{d}日"
    
    if name == 'birth year and age' and len(node.params) >= 1:
        return f"{node.params[0]}年"
    
    if name == 'bd':
        try:
            return f"{node.get(1).value}{node.get(2).value}－{node.get(3).value}{node.get(4).value}"
        except:
            return ''.join(str(p.value).strip() for p in node.params)

    if name in ['linktext', '仮リンク']:
        return str(node.params[0].value).strip() if node.params else ''

    if name.startswith('le') or name.startswith('link-'):
        return f"《{node.params[0].value}》" if node.params else ''

    if name == 'noteTA':
        zh_titles = []
        for param in node.params:
            val = str(param.value).strip()
            if 'zh-hans:' in val or 'zh-hant:' in val or 'zh-cn:' in val:
                zh_titles.append(val.split(':', 1)[-1])
        return '，'.join(zh_titles)

    return ''
