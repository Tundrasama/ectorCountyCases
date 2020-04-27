# http://www.co.ector.tx.us/upload/page/9908/docs/Case%20Information%2004-26-20.pdf
# the pdf has the date in the name, would have to check for the new date, or default to date - 1

from tabula import read_pdf, convert_into
import re
import csv
import requests
import PyPDF2
from datetime import date, timedelta

def main():
	urlBase="http://www.co.ector.tx.us/upload/page/9908/docs/"
	pdfFile = 'ectorCaseTest.pdf'

	tStampToday=f"{date.today():%m-%d-%y}"
	fileNameToday="Case%20Information%20" + tStampToday + ".pdf"	

	urlToday=urlBase + fileNameToday
	fetchFile(urlToday,pdfFile)

	txtPDF='ectorCaseFiles.txt'
	# convert_into(pdfFile,txtPDF,output_format="csv",pages='all',stream=True)

	readFile(txtPDF)

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
	main()