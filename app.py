# importing required modules
import PyPDF2
import re
import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
import requests
from numpy.distutils.conv_template import process_file
import glob
#import os.path

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_url_path="", static_folder="./static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 5mb
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['POST', 'GET'])
def upload_files():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            #extract_text_from_pdf(filename, 0)
            # return redirect(url_for('uploaded_file', filename=filename))
            return redirect(url_for('index', filename=filename))
    return render_template('index.html')


@app.route('/<filename>', methods=['POST', 'GET'])
def index(filename):
    # creating a pdf file object
    file_path = UPLOAD_FOLDER + filename
    pdfFileObj = open(file_path, 'rb')
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    # creating a page object
    pageObj = pdfReader.getPage(0)
    # extracting text from page
    pdf_text = pageObj.extractText()
    # closing the pdf file object
    pdfFileObj.close()
    # return pdf_text

    print("extracted text :   ", pdf_text)

    regex1 = '.+?DueCGSTSGST/UTGST([\d]+)[a-zA-Z].+'
    policy_num = re.findall(regex1, pdf_text)
    print("Policy_num: ", policy_num)

    regex2 = '.+?Receipt No :([a-zA-Z].+)HelpDesk:.+'
    benefeciary_name = re.findall(regex2, pdf_text)
    print("Benefeciary Name: ", benefeciary_name)

    regex3 = '.+?EPS1[\d]+([0-9][0-9]/[0-9][0-9]/[\d]+).+'
    paid_on_date = re.findall(regex3, pdf_text)
    print("Paid on date: ", paid_on_date)

    regex4 = '.+?EPS1([\d]+)[0-9][0-9]/.+'
    transaction_no = re.findall(regex4, pdf_text)
    print("Transaction No: ", transaction_no)

    regex5 = '.+?91-022-1251([A-z][A-z][\d]+)Policy.+'
    receipt_no = re.findall(regex5, pdf_text)
    print("receipt No: ", receipt_no)

    regex6 = '.+?([0-9][0-9]/[0-9][0-9]/[\d]+)[Y|H]LY.+'
    doc = re.findall(regex6, pdf_text)
    print("D.O.C: ", doc)

    #regex7 = '.+?[0-9][0-9]/[0-9][0-9][0-9][0-9]/[0-9][0-9]([\d]+,[\d]+\.00).+'
    regex7 = '.+?[0-9][0-9]/[0-9][0-9][0-9][0-9]/[0-9][0-9]([\d,]*\.00).+'
    inst_premium = re.findall(regex7, pdf_text)
    print("Inst. Premium: ", inst_premium)

    #regex8 = '.+?YLY([\d].+)1[0-9][0-9]/[0-9][0-9].+'
    regex8 = '.+?[Y|H]LY([\d.,]*)1[0-9][0-9]/[0-9][0-9].+'
    sum_assured = re.findall(regex8, pdf_text)
    print("Sum assured: ", sum_assured)
    """ if request.method == 'POST': 
        
        f = request.files['file']  
       # f.save(f.filename) 
    else:
        #f = None 
        return redirect(request.url)    """

    return render_template('info.html', policy_num=policy_num[0],
                           benefeciary_name=benefeciary_name[0], paid_on_date=paid_on_date[0],
                           transaction_no=transaction_no[0],
                           receipt_no=receipt_no[0],
                           doc=doc[0],
                           inst_premium=inst_premium[0], sum_assured=sum_assured[0])

    # return redirect(url_for('return_files_tut', filename=filename))


# Download API
""" @app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('info.html',value=filename) """


""" @app.route('/return-files/<filename>')
def return_files_tut(filename): """


@app.route('/download')
def download_file():
    #file = request.files['file']
    #path= file.filename

    path = os.listdir(app.config['UPLOAD_FOLDER'])

    #path= "lic.pdf"
    #ile_path = UPLOAD_FOLDER + filename

    file_type = '/*pdf'
    files = glob.glob(UPLOAD_FOLDER + file_type)
    max_file = max(files, key=os.path.getctime)
    return send_file(max_file, as_attachment=True)
    print(max_file)
    # return send_from_directory(app.config['UPLOAD_FOLDER'], path, as_attachment=True)


if __name__ == '__main__':
    app.run(port=5005, debug=True)
