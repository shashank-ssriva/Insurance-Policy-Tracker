# Insurance Policy Tracker

A Python3 Flask web-app to track & store all LIC and HDFC insurance policy premium payments by just uploading the premium receipt. This web-app retrieves the policy details by reading the
premium receipt PDF file, stores them in a SQLite database & displays the information on the UI in a tabular format.

It also allows to download the PDF files for future reference & delete the individual records.

If the PDF file can't be read, the web-app lets us enter the details manually.

# Tech-Stack

* Backend - Python3/Flask
* Frontend - UIKit
* Database - SQLite

# Directory structure

```
shashank@XE-GGN-IT-03362 ~/D/Insurance-Policy-Tracker (main)> tree
.
├── PoliciesDB.py
├── README.md
├── app.py
├── policies.db
├── static
│   └── images
│       ├── New.jpg
│       ├── icons
│       │   ├── favicon.ico
│       │   ├── insurance.png
│       │   └── life.png
│       ├── nothing-found-80.png
│       ├── nothing-found.png
│       ├── sad.png
│       ├── sad1.png
│       └── sad2.png
├── templates
│   ├── HDFC_list.html
│   ├── HDFCinfo.html
│   ├── LIC_list.html
│   ├── duplicate_upload_failed.html
│   ├── index.html
│   ├── info.html
│   ├── manualEntryForm.html
│   ├── menu.html
│   └── new-icon-gif-4.jpg
└── uploads
    └── dummyfile.txt
```