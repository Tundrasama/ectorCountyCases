#Issues: originally Ector county was uploading the case statistics to an HTML table that
# could be grabbed with an importhtml in google sheets. They then changed to a link to a
# PDF file. The first page of the PDF does not appear to scrape properly, so some additional
# processing is required -- @texastom (odessacoding.com) suggested some changes for handling
# prior dates and for using pandas dataframes instead of the overly complicated regex

from tabula import read_pdf, convert_into
import re
import csv
import requests
import PyPDF2
from datetime import date, timedelta

def main():
	urlBase="http://www.co.ector.tx.us/upload/page/9908/docs/"
	pdfFile = 'ectorCases.pdf' # name for saving the file

	tStampToday=f"{date.today():%m-%d-%y}" # today's date 
	fileNameToday="Case%20Information%20" + tStampToday + ".pdf" # filename appears to change each day

	urlToday=urlBase + fileNameToday # join the url and filename
	fetchFile(urlToday,pdfFile) # fetch the file and do some processing

	txtPDF='ectorCaseFiles.txt'
	# was using tabula's convert_into function, but then took a different approach
	# convert_into(pdfFile,txtPDF,output_format="csv",pages='all',stream=True)
	readFile(txtPDF)

def main2():
	# url added images when run on 5/4/2020
    urlBase="http://www.co.ector.tx.us/upload/page/9908/images/docs/"
    pdfFile = 'ectorCaseTest.pdf'

    tStampToday=f"{date.today():%m-%d-%y}"
    fileNameToday="Case%20Information%20" + tStampToday + ".pdf"    

    urlToday=urlBase + fileNameToday
    fetchFile2(urlBase,pdfFile)

    pdf = PyPDF2.PdfFileReader(open('ectorCaseTest.pdf','rb'))
    pages = pdf.getNumPages()
    currPage = 1
    mainColumns = []
    mainDF = None
    while currPage <= pages:
        df = read_pdf('ectorCaseTest.pdf', pages=f'{currPage}', stream=True, lattice=True, pandas_options={'header': None})

        df = df[0]

        if currPage == 1:
            df.dropna(axis=1, how='all', inplace=True)
            df = df.iloc[1:]
            df.columns = df.values[0]
            mainColumns = df.values[0]
            df = df.iloc[1:]
            mainDF = df.copy()

        else:
            df.dropna(axis=1, how='all', inplace=True)
            df.columns = mainColumns
            mainDF = mainDF.append(df)

        currPage = currPage + 1
    print(mainDF)
    mainDF.to_csv('cleanedOutputPandas.csv', index=False)
    exit()

def writeFile(pdfReader,output,numPages):
	with open(output,'w') as f:
		for x in range(0,numPages):
			text=pdfReader.getPage(x).extractText()
			print(text, file=f)

def fetchFile(url,pdfFile):
	r=requests.get(url,stream=True)
	if r.status_code==200:
		with open(pdfFile,'wb') as f:
			f.write(r.content)
	elif r.status_code==404:
		print("File not found for today, fetching yesterday")
		tStampYesterday=f"{date.today()-timedelta(days=1):%m-%d-%y}"
		fileNameYesterday="Case%20Information%20" + tStampYesterday + ".pdf"
		url=url + fileNameYesterday
		fetchFile(url,pdfFile)	

def fetchFile2(baseURL,pdfFile):
    success = False
    attempts = 1
    maxAttempts = 5

    while not success:
        tStamp=f"{date.today()-timedelta(days=attempts - 1):%m-%d-%y}"
        fileName="Case%20Information%20" + tStamp + ".pdf"    
        url = baseURL + fileName
        print(f'Attempting Download: {url}')

        r=requests.get(url,stream=True)

        if r.status_code==200:
            print(f'HTTP 200: {url}')
            with open(pdfFile,'wb') as f:
                f.write(r.content)
                success = True

        attempts = attempts + 1
            
        if attempts >= maxAttempts:
            print(f"Couldn't download a file. Searched {attempts} days.")
            exit()

def readFile(txtFile):
	allLines=[]

	p2pMatch=r'(\d+),(\d{2}/\d{2}/\d{2})\s(\w+)\s(\d+)\s(\w+\s\w+\s\w+){1,3},(\w+)'
	travelMatch=r'(\d+),(\d{2}/\d{2}/\d{2})\s(\w+)\s(\d+)\s(\w+\s\w+),(\w+)'
	unknownMatch=r'(\d+),(\d{2}/\d{2}/\d{2})\s(\w+)\s(\d+)\s(\w+),(\w+)'

	with open(txtFile,'r') as f:
		lines=f.readlines()

		for i,line in enumerate(lines):
			if i <= 37:
				if re.findall(p2pMatch,line) == []:
					if re.findall(travelMatch,line)==[]:
						if re.findall(unknownMatch,line)==[]:
							pass
						else:
							newLine=re.findall(unknownMatch,line)
							newLine=','.join(re.search(unknownMatch,line).groups())
							allLines.append(''.join(newLine)+'\n')
					else:
						newLine=re.findall(travelMatch,line)
						newLine=','.join(re.search(travelMatch,line).groups())
						allLines.append(''.join(newLine)+'\n')
				else:
					newLine=re.findall(p2pMatch,line)
					newLine=','.join(re.search(p2pMatch,line).groups())
					allLines.append(''.join(newLine)+'\n')
			else:
				allLines.append(line)
	
		print(allLines)
		writeCleanedFile(allLines)

def writeCleanedFile(lines):
	with open('cleanedOutput.csv','w') as f:
		header=str("Case Number,Report Date,Sex,Age,Exposure,Testing\n")
		f.write(header)
		for line in lines:
			f.write(str(line))
		
if __name__ == "__main__":
	main2()
	# main()