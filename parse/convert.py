from downloadTables import get_links,downloadFiles
from pdftoxlsx import parsePDFandSave

print('Stage 1: Downloading PDF files')
downloadedFilesList = downloadFiles(get_links())
print('Stage 2: Convering PDF files to XLSX')
for file in downloadedFilesList:
    parsePDFandSave(file)