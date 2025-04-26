import xml.sax

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        super().__init__()
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []

    def characters(self, content):
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        if name in ('title', 'text', 'timestamp', 'id', 'username', 'ns'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            title = self._values.get('title', '').strip()
            text = self._values.get('text', '').strip()
            timestamp = self._values.get('timestamp', '').strip()
            page_id = self._values.get('id', '').strip()
            username = self._values.get('username', '').strip()
            ns = self._values.get('ns', '').strip()

            # 过滤无效页面
            if (
                '#redirect' in text.lower() or
                '#重定向' in text.lower() or
                title.startswith(('Category:', 'Template:', 'Wikipedia:', 'File:', 'Help:', 'Portal:')) or
                len(text) < 100 or
                any(tag in text.lower() for tag in ['{{delete', '{{copyvio', '{{db-', '{{afd', '{{vfd', '{{prod'])
            ):
                self._values.clear()
                return

            self._pages.append({
                'title': title,
                'text': text,
                'timestamp': timestamp,
                'id': page_id,
                'username': username,
                'ns': ns
            })

            self._values.clear()