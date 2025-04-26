import requests
from bs4 import BeautifulSoup
import os
import sys
from keras.utils import get_file
keras_home = '/Users/a16262/.keras/datasets/'

dump_url = 'https://dumps.wikimedia.org/zhwiki/20250101/'
dump_html = requests.get(dump_url).text
soup_dump = BeautifulSoup(dump_html, 'html.parser')


files = []

# Search through all files
for file in soup_dump.find_all('li', {'class': 'file'}):
    text = file.text
    # Select the relevant files
    if 'pages-articles' in text:
        files.append((text.split()[0], text.split()[1:]))

files_to_download = [file[0] for file in files if '.xml-p' in file[0] and 'multistream' not in file[0]]

data_paths = []
file_info = []

# Iterate through each file
for file in files_to_download:
    path = keras_home + file
    
    # Check to see if the path exists (if the file is already downloaded)
    if not os.path.exists(keras_home + file):
        print('Downloading')
        # If not, download the file
        data_paths.append(get_file(origin=dump_url+file))
        # Find the file size in MB
        file_size = os.stat(path).st_size / 1e6
        
        # Find the number of articles
        file_articles = int(file.split('p')[-1].split('.')[-2]) - int(file.split('p')[-2])
        file_info.append((file, file_size, file_articles))
        
    # If the file is already downloaded find some information
    else:
        data_paths.append(path)
        # Find the file size in MB
        file_size = os.stat(path).st_size / 1e6
        
        # Find the number of articles
        file_number = int(file.split('p')[-1].split('.')[-2]) - int(file.split('p')[-2])
        file_info.append((file.split('-')[-1], file_size, file_number))