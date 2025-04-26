
def clean_wiki_template(node):
    """
    更完善地清理和展开单个模板节点
    """
    name = str(node.name).strip().lower()

    # 明确要直接删除的模板
    TEMPLATE_BLACKLIST = [
        'clear', 'reflist', 'nowrap', 'empty section', 'commonscat', 
        'authority control', 'defaultsort', 'infobox', 'sfn', 'efn',
        'cite web', 'cite news', 'cite book', 
        '#expr', '#if', '#ifeq', '#switch', '#invoke', '#lst', '#tag',
    ]
    if any(name.startswith(b) for b in TEMPLATE_BLACKLIST):
        return ''

    # 特别处理
    if name.startswith('lang-') or name == 'lang':
        if node.params:
            return f"({str(node.params[0].value).strip()})"
        else:
            return ''

    if name == 'birth date' and len(node.params) >= 3:
        y, m, d = node.params[0], node.params[1], node.params[2]
        return f"{y}年{m}月{d}日"
    
    if name == 'birth year and age' and len(node.params) >= 1:
        y = node.params[0]
        return f"{y}年"
    
    if name == 'bd':
        try:
            birth_year = str(node.get(1).value).strip()
            birth_month_day = str(node.get(2).value).strip()
            death_year = str(node.get(3).value).strip()
            death_month_day = str(node.get(4).value).strip()
            return f"{birth_year}{birth_month_day}－{death_year}{death_month_day}"
        except (ValueError, IndexError):
            params = [str(p.value).strip() for p in node.params]
            return ''.join(params)

    if name in ['linktext', '仮リンク']:
        if len(node.params) >= 1:
            return str(node.params[0].value).strip()
        else:
            return ''

    if name.startswith('le') or name.startswith('link-'):
        if node.params and len(node.params) >= 1:
            content = str(node.params[0].value).strip()
            return f"《{content}》"

    if name == 'noteTA':
        # 取所有中文标题，通常参数是 zh-hans、zh-hant、zh-cn 等
        zh_titles = []
        for param in node.params:
            pval = str(param.value).strip()
            if 'zh-hans:' in pval or 'zh-hant:' in pval or 'zh-cn:' in pval:
                title = pval.split(':', 1)[-1]
                zh_titles.append(title)
        return '，'.join(zh_titles)

    # 如果遇到其他不认识的模板，直接丢弃
    return ''