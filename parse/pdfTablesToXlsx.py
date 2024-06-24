import urllib
import requests as r
from bs4 import BeautifulSoup as bs

def download_file(url):
    local_filename = url.split('/')[-1]
    urllib.request.urlretrieve(url, local_filename)
    return local_filename

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
    print(f"File saved as {downloaded_file}")