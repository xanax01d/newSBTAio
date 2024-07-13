import urllib
import requests as r
from bs4 import BeautifulSoup as bs
import time
from spire.pdf.common import *
from spire.pdf import *


def download_file(url):
    local_filename = url.split('/')[-1]
    urllib.request.urlretrieve(url, local_filename)
    return local_filename

def parsePDF(file):
    pdf = PdfDocument()
    pdf.LoadFromFile(file)
    convertOptions = XlsxLineLayoutOptions(True, True, False, True, False)
    pdf.ConvertOptions.SetPdfToXlsxOptions(convertOptions)
    pdf.SaveToFile(f"{file}.xlsx", FileFormat.XLSX)
    pdf.Close()
    return(True)

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