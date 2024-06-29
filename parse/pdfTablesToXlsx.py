import urllib
import requests as r
from bs4 import BeautifulSoup as bs
import time
import fitz  # PyMuPDF
import openpyxl
from openpyxl.utils import get_column_letter

def download_file(url):
    local_filename = url.split('/')[-1]
    urllib.request.urlretrieve(url, local_filename)
    return local_filename
def parsePDF(pdf):
    doc = fitz.open(pdf) # open a document
    out = open(f"{pdf}.txt", "wb") # create a text output
    for page in doc: # iterate the document pages
        text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
        out.write(text) # write text of page
        out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
    out.close()

def main():
    print('Stage 1: Downloading PDF files')
    downloadedFiles = []
    sitePage = 'http://bsac.by/'
    tablesPage = 'http://bsac.by/tasks/vo/do'
    page = r.get(tablesPage )
    soup = bs(page.content,'html.parser')
    links = soup.find_all('a',href = True)
    pdfs = [link['href'] for link in links if link['href'].endswith('.pdf') and 'Curs' in link['href']]

    for pdf_link in pdfs:
        if not pdf_link.startswith('http'):
            pdf_link = sitePage.rsplit('/', 1)[0] + '/' + pdf_link 
        print(f"Downloading {pdf_link}...")
        downloaded_file = download_file(pdf_link)
        downloadedFiles.append(downloaded_file)
        print(f"File saved as {downloaded_file}")
    print('Stage 2: Converting PDF files')    
    for file_name in downloadedFiles:
        print(f'Converting {file_name}...')
        parsePDF(file_name)
        
if __name__ == "__main__":
    main()