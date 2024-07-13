from downloadTables import get_links,downloadFiles
from pdftoxlsx import parsePDFandSave
"""TODO:Write to UMO (УМО//Учебно-методический отдел) and find out from whom i can get schedules in xlsx format
        Remake it to xlsx
        Make this shit work
"""
print('Stage 1: Downloading PDF files')
downloadedFilesList = downloadFiles(get_links())
print('Stage 2: Convering PDF files to XLSX')
for file in downloadedFilesList:
    parsePDFandSave(file)