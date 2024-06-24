import urllib
import requests as r
from bs4 import BeautifulSoup as bs
import time
#ilovepdf api key
API_KEY = 'project_public_9f999e0b88f4311fd92e23aba5a6935e_g8DnN36e43c2c1a1862efb8acf635b9a9d20d'

def download_file(url):
    local_filename = url.split('/')[-1]
    urllib.request.urlretrieve(url, local_filename)
    return local_filename
def convert_pdf_to_excel(api_key, input_pdf_path, output_excel_path):
    try:
        # Start the conversion task
        response = r.post('https://api.ilovepdf.com/v1/start/pdf2excel', data={'public_key': api_key})
        response.raise_for_status()
        task = response.json()
        
        if not task or 'task' not in task:
            print(f'Unexpected response content: {task}')
            raise KeyError('task')

        # Upload the PDF file
        with open(input_pdf_path, 'rb') as pdf_file:
            upload_response = r.post('https://api.ilovepdf.com/v1/upload', 
                                     files={'file': pdf_file}, 
                                     data={'task': task['task']})
            upload_response.raise_for_status()
            upload = upload_response.json()
        
        if not upload or 'server_filename' not in upload:
            print(f'Unexpected upload response content: {upload}')
            raise KeyError('server_filename')

        # Process the file
        process_response = r.post('https://api.ilovepdf.com/v1/process', 
                                  data={'task': task['task'], 
                                        'tool': 'pdf2excel', 
                                        'files[0][server_filename]': upload['server_filename'], 
                                        'files[0][filename]': input_pdf_path.split('/')[-1]})
        process_response.raise_for_status()

        # Polling to check task status
        while True:
            status_response = r.get(f'https://api.ilovepdf.com/v1/task/{task["task"]}')
            status_response.raise_for_status()
            status = status_response.json()
            
            if not status or 'status' not in status:
                print(f'Unexpected status response content: {status}')
                raise KeyError('status')
            
            if status['status'] == 'TaskSuccess':
                break
            if status['status'] == 'TaskError':
                raise Exception('Task failed')
            time.sleep(2)

        # Download the converted file
        download_response = r.get(f'https://api.ilovepdf.com/v1/download/{task["task"]}', stream=True)
        download_response.raise_for_status()
        
        with open(output_excel_path, 'wb') as output_file:
            for chunk in download_response.iter_content(chunk_size=8192):
                output_file.write(chunk)

        print(f'File successfully converted and saved to {output_excel_path}')
    
    except r.RequestException as e:
        print(f'An HTTP error occurred: {e}')
    except KeyError as e:
        print(f'Unexpected response structure: missing key {e}')
    except TypeError as e:
        print(f'Unexpected response type: {e}')
    except Exception as e:
        print(f'An error occurred: {e}')

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
        #print(downloadedFiles)
    print('Stage 2: Converting PDF files')    
    for file_name in downloadedFiles:
        print(f'Converting {file_name}...')
        convert_pdf_to_excel(api_key=API_KEY,input_pdf_path=file_name,output_excel_path=f'{file_name}.xlsx')
        
if __name__ == "__main__":
    main()