import subprocess
import xml.sax
from data_loader.wiki_xml_handler import WikiXmlHandler
import pandas as pd
from text_cleaner.processor import process_article

handler = WikiXmlHandler()
# 修改成本地的下载路径
data_path =  '/Users/a16262/.keras/datasets/zhwiki-20250101-pages-articles3.xml-p630161p1389648.bz2'

# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

for i, line in enumerate(subprocess.Popen(['bzcat'], 
                         stdin = open(data_path), 
                         stdout = subprocess.PIPE).stdout):
    parser.feed(line)
    if len(handler._pages) > 1000: # 先 生成 1000条
        break

df = pd.DataFrame(handler._pages)
process_article(df)