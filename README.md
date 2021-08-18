# Insurance Policy Tracker

A Python3 Flask web-app to track & store all LIC and HDFC insurance policy premium payments by just uploading the premium receipt. This web-app retrieves the policy details by reading the
premium receipt PDF file, stores them in a SQLite database & displays the information on the UI in a tabular format.

It also allows to download the PDF files for future reference & delete the individual records.

If the PDF file can't be read, the web-app lets us enter the details manually.

# Tech-Stack
* Backend - Python3/Flask
* Frontend - UIKit
* Database - SQLite