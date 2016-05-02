# NEED TO WRITE SOMETHING IN YOUR CODE THAT CONTINUES EVEN IF THE FILE DNE

# Objective: Create a searchable databse of all daily stock price movements in indian stocks
# Practice with databases using SQLLite

import urllib2, cookielib
import zipfile, os, csv
import time
import sqlite3
from datetime import datetime

# Step 1: Create a blank table with the schema that we care about

conn = sqlite3.connect('example.db')
c = conn.cursor()

# Create table
c.execute('DROP TABLE prices')
c.execute('CREATE TABLE prices (SYMBOL text, SERIES text, OPEN real, LOW real, CLOSE real, LAST real, PREVCLOSE real, TOTTRDQTY real, TOTTRDVAL real, TIMESTAMP date, TOTALTRADES real, ISIN text, PRIMARY KEY(SYMBOL, SERIES, TIMESTAMP))')
conn.commit()

# Step 2: Download and unzip daily stock movement files from the national stock exchange of India for this year and last

def download(localZipFilePath, urlOfFile):
	# Download zip file from website
	# Need to mimic a human downloading the zip
	# User-agent propery set in the HTTP headers
	hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
		   'Accept': 'text/html, application/xhtml+xml,application/xml;q=0.9,*/*q=0.8',
	       'Accept-Charset':'ISO-8859-1;utf-8,q=0.7,*;q=0.3',
	       'Accept-Encoding':'none',
	       'Accept-Language':'en-US,en;q=0.8',
	       'Connection':'keep-alive'
	}

	# This makes a web request
	webRequest = urllib2.Request(urlOfFile, headers=hdr)

	# Using try/except as safety net
	try:
		page = urllib2.urlopen(webRequest)
		# Save the contents (zip file) of this page
		content = page.read()
		# Save contents of zip file to local copy
		output = open(localZipFilePath, "wb")
		output.write(bytearray(content))
		output.close()

	except urllib2.HTTPError as e:
		print e.fp.read()
		print "Looks like the file download did not go through"


def unzip(localZipFilePath, localExtractFilePath):
	# Unzip file and extract

	# localExtractFilePath = "/Users/conne/Desktop/Python Courses/Machine Learning/"
	# ^^^ This needed to be deleted, because it was resetting the variable

	if os.path.exists(localZipFilePath):
		print "localZipFilePath exists"

		listOfFiles = []

		fh = open(localZipFilePath, 'rb')

		zipFileHandler = zipfile.ZipFile(fh)

		for filename in zipFileHandler.namelist():
			zipFileHandler.extract(filename,localExtractFilePath)
			listOfFiles.append(localExtractFilePath + filename)
			print "Extracted" + filename + " from the zip file"
		print "In total, we extracted", str(len(listOfFiles)), " files"
		fh.close()

def downloadAndUnzipForPeriod(listofMonths, listofYears):
	# Builds list of dates to iterate through download and unzip functions
	for year in listofYears:
		for month in listofMonths:
			for dayOfMonth in range(31):
				date = dayOfMonth + 1
				dateStr = str(date)
				if date < 10:
					dateStr = "0"+dateStr
				print dateStr, "-", month, "-", year
				fileName = "cm" +str(dateStr) + str(month) + str(year) + "bhav.csv.zip"
				urlOfFile = "http://www.nseindia.com/content/historical/EQUITIES/"+ year +"/"+ month +"/"+ fileName
				localZipFilePath = "/Users/conne/Desktop/Python Courses/Machine Learning/Building A Database Example/" + fileName
				download(localZipFilePath, urlOfFile)
				unzip(localZipFilePath, localExtractFilePath)
				# This might overload the NSE website- next line is to pause
				time.sleep(10) # Pauses for 10 seconds before it executes next bit of code
	print 'OK, all done with downloading and extracting!'

localExtractFilePath = "/Users/conne/Desktop/Python Courses/Machine Learning/Building A Database Example/"

listofMonths = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
listofYears = ['2016']

#downloadAndUnzipForPeriod(listofMonths,listofYears)

# Step 3: Parse each file and insert row of each file into the database

def insertRows(fileName, conn):
	# conn is connection to database
	# given a connection we need a session with the database

	c = conn.cursor()
	lineNum = 0
	with open(fileName, 'rb') as csvFile:
		lineReader = csv.reader(csvFile, delimiter = ',', quotechar = "\"")
		for row in lineReader:
			lineNum += 1
			if lineNum == 1:
				continue # Line 1 contains the header
			date_object = datetime.strptime(row[10], '%d-%b-%Y') # This writes to the database

			oneTuple = [row[0],row[1],float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]),date_object,float(row[11]), row[12]]
			# This statement will actually insert a single row into the table called prices
			c.execute("INSERT INTO prices VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", oneTuple)
		conn.commit()
		#print "Done iterating over file contents"


for file in os.listdir(localExtractFilePath):
	if file.endswith(".csv"):
		insertRows(localExtractFilePath+"/"+file, conn)

# Step 4: Run a test query against the database to make sure it is set up right

tl = 'ICICIBANK'
series = 'EQ'
c = conn.cursor()
cursor = c.execute('SELECT symbol, max(close), min(close), max(timestamp), count(timestamp) FROM prices WHERE symbol = ? and series = ? GROUP BY symbol ORDER BY timestamp', (tl, series))
for row in cursor:
	print row

# Step 5: Accept a ticker from the user, run a query, and create a spreadsheet with a line chart of price movements

import xlsxwriter

def createExcelChart(ticker, conn):
	c = conn.cursor()
	cursor = c.execute('SELECT symbol, timestamp, close FROM prices WHERE symbol = ? and series = ? ORDER BY timestamp', (ticker,series))
	# ?'s are placeholders and the variables allow for customizable queries

	excelFileName = '/Users/conne/Desktop/Python Courses/Machine Learning/Building A Database Example/'+ticker+'.xlsx'
	workbook = xlsxwriter.Workbook(excelFileName)
	worksheet = workbook.add_worksheet("Summary")
	worksheet.write_row("A1", ["Top Traded Stocks"])
	worksheet.write_row("A2", ["Stock", "Date", "Closing"])
	lineNum = 3 # Start after the headers

	for row in cursor:
		worksheet.write_row("A"+str(lineNum), list(row))
		print "A"+str(lineNum), list(row)
		lineNum += 1

	chart1 = workbook.add_chart({'type':'line'})
	chart1.add_series({
		'categories': '=Summary!$B$3:$B$' + str(lineNum),
		'values' : '=Summary!$C$3:$C$' + str(lineNum)
		})
	chart1.set_title({'name': ticker})
	chart1.set_x_axis({'name': 'Date'})
	chart1.set_y_axis({'name': 'Closing Price'})

	worksheet.insert_chart('F2', chart1, {'x_offset': 25, 'y_offset': 10})
	workbook.close()

conn = sqlite3.connect('example.db')
#ticker = input('Which stock would you like to see?')
createExcelChart('AIL',conn)

# Step 6: Drop Table to clear up

conn=sqlite3.connect('example.db') # Establishes connection
c = conn.cursor() # Connects to table
c.execute('DROP TABLE prices') # Erases the entire table
conn.commit() # Commits changes