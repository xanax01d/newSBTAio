from spire.pdf import *
from spire.pdf.common import *

def parsePDFandSave(file):
    pdf = PdfDocument()
    pdf.LoadFromFile(file)
    convertOptions = XlsxLineLayoutOptions(True, True, False, True, False)
    pdf.ConvertOptions.SetPdfToXlsxOptions(convertOptions)
    pdf.SaveToFile(f"{file}.xlsx", FileFormat.XLSX)
    pdf.Close()
    print(f'File {file} was converted')
