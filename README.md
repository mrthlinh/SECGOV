# SECGOV Data Scrapper

## Software Installation:
1. Install Python >= 3.4:

  - https://www.python.org/getit/, double click to execute the installer
  - Select __"Add Python to PATH"__ then __Install Now__
  - Hit "Next" or "Ok" to finish installation.

2. Firefox Driver:

  - Download FireFox Browser https://www.mozilla.org/en-US/firefox/new/ then install FireFox.
  - Unzip folder of geckodriver
  - Now we need to add GeckoDriver to PATH of window
  - Press "Window" button and type __Edit the system environment variables__, hit Enter then in tab __Advanced__ choose __Environment Variables__
  - Then in __System Variables__, find __Path__ then Double-click to edit. If you are using Window XP, type ";<Path>" (don't forget the semicolon) to add new Path. For example my directory is at "E:\\SECGOV" so I need to add ";E:\\SECGOV".
  - In window of __Edit environment variable__, press __Browse..__ then choose the path of unzip GeckoDriver.
  - Hit "Enter" to finish procedure.

3. Install wkhtmltopdf:

  - Run wkhtmltox-0.12.5-1.msvc2015-win64.exe
  - Remember Path of program, usually __C:/Program Files/wkhtmltopdf/bin__
  - Add PATH of wkhtmltopdf to __System Variables__ like in second step

## Format Output
- Columns with "exact": match exactly words in "listofword.txt", lower and upper case are the same. "retirement" is different from "postretirement".
- Columns without "exact": "postretirement" and "retirement" both count as 1.

## How to Run
- __install.bat__ install needed libraries. If you see "Windows Protected your PC", choose "More info" then "Run anyway"
- __listofword.txt:__ define your search criteria
- __Compustat.csv:__ please convert excel file to csv.
- __RUN.bat__: Double-click to run this file.
- __download__: folder contains download PDF files
- __log:__ log file. If there is a bug, please send the log file and a screenshot to me.

__Note__ If something interrupts the process, hit "Ctrl + C" __many times__ to terminate the process.
