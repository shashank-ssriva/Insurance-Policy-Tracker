# importing required modules
import PyPDF2
import re
import os
from flask import Flask, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
import sqlite3
import glob
import subprocess


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_url_path="", static_folder="./static",
            template_folder="./templates")
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
            print("Filename", filename)
            return redirect(url_for('index_LICdefault', filename=filename))
    return render_template('index.html')


@app.route('/duplicate_upload<msg>', methods=['POST', 'GET'])
def reattempt_upload_files(msg):
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
            print("Filename", filename)
            return redirect(url_for('index_LICdefault', filename=filename))
    return render_template('index.html', msg=msg)


@app.route('/LIClist', methods=['POST', 'GET'])
def LIC_list_history():
    with sqlite3.connect("policies.db") as con:
        cur = con.cursor()
        con.row_factory = sqlite3.Row
        cur.execute("select * from Lic_Policies")
        rows = cur.fetchall()
        limit = len(rows)
    return render_template('LIC_list.html',  rows=rows, limit=limit)


@app.route('/HDFClist', methods=['POST', 'GET'])
def HDFC_list_history():
    with sqlite3.connect("policies.db") as con:
        cur = con.cursor()
        con.row_factory = sqlite3.Row
        cur.execute("select * from HDFC_Policies")
        rows = cur.fetchall()
        limit = len(rows) 
        #print(limit)
    return render_template('HDFC_list.html',  rows=rows, limit=limit)


""" @app.route('/menu', methods=['POST', 'GET'])
def test_css():
    return render_template('menu.html') """


@app.route('/duplicate_upload<msg>', methods=['POST', 'GET'])
def duplicate_upload(msg):
    # return render_template('duplicate_upload_failed.html',  msg= msg)
    return redirect('http://localhost:5005', code=301)


@app.route('/<filename>', methods=['POST', 'GET'])
def index_LICdefault(filename):
    is_hdfc_file = False
    #match = re.search("HDFC", filename)
    if (filename.find("HDFC") != -1):
        is_hdfc_file = True
    print("hahaha")
    if (is_hdfc_file == True):
        return redirect(url_for('HDFC_index', filename=filename))
    else:
        # creating a pdf file object
        file_path = UPLOAD_FOLDER + filename
        pdfFileObj = open(file_path, 'rb')
        # creating a pdf reader object
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

        # Decrypting the pdf file
        if pdfReader.isEncrypted:
            try:
                pdfReader.decrypt('')
                print('File Decrypted (PyPDF2)')
            except:
                command = ("cp " + filename +
                           " temp.pdf; qpdf --password='' --decrypt temp.pdf " + filename
                           + "; rm temp.pdf")
                os.system(command)
                print('File Decrypted (qpdf)')
                pdfFileObj = open(filename)
                pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            msg = "Encrypted File( " + filename + \
                " ) uploaded successfully but couldn't read incompatible data even after decryption. Sorry for inconvenience!! Enter data manually"
            return render_template('manualEntryForm.html', msg=msg, filename=filename)
        else:
            # creating a page object
            pageObj = pdfReader.getPage(0)
            # extracting text from page
            pdf_text = pageObj.extractText()
            # closing the pdf file object
            pdfFileObj.close()
            # return pdf_text

            #print("extracted text :   ", pdf_text)
            if pdf_text:
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

                regex7 = '.+?[0-9][0-9]/[0-9][0-9][0-9][0-9]/[0-9][0-9]([\d,]*\.00).+'
                inst_premium = re.findall(regex7, pdf_text)
                print("Inst. Premium: ", inst_premium)

                regex8 = '.+?[Y|H]LY([\d.,]*)1[0-9][0-9]/[0-9][0-9].+'
                sum_assured = re.findall(regex8, pdf_text)
                print("Sum assured: ", sum_assured)

                # Adding details to database
                with sqlite3.connect("policies.db") as con:
                    cur = con.cursor()
                    con.row_factory = sqlite3.Row
                    cur.execute("select * from Lic_Policies")
                    rows = cur.fetchall()
                    limit = len(rows)
                # limit = limit-1
                    if(len(rows) == 0):
                        cur.execute("INSERT into Lic_Policies  values (?,?,?,?,?,?,?,?,?)", (policy_num[0],
                                    benefeciary_name[0], doc[0], inst_premium[0], sum_assured[0], transaction_no[0], paid_on_date[0], receipt_no[0], filename))
                        con.commit()
                        msg = "Records successfully Added"
                        print(msg)
                    else:
                        for row in rows:
                            status = " "
                            if(transaction_no[0] == row[5]):
                                msg = "The LIC Insurance Policy data you are trying to upload already exists"
                                return redirect(url_for('duplicate_upload', msg=msg))
                            else:
                                status = "Not a duplicate data"
                        if(status == "Not a duplicate data"):
                            cur.execute("INSERT into Lic_Policies  values (?,?,?,?,?,?,?,?,?)", (policy_num[0],
                                                                                                 benefeciary_name[0], doc[0], inst_premium[0], sum_assured[0], transaction_no[0], paid_on_date[0], receipt_no[0], filename))
                            con.commit()
                            msg = "Records successfully Added"
                            print(msg)
                            # print("limit", len(rows))
                    """ for row in rows[:limit]:
                        print("row", row)   """
                    # Closing the connection
                    # con.close()
                return render_template('info.html', policy_num=policy_num[0],
                                       benefeciary_name=benefeciary_name[0], paid_on_date=paid_on_date[0],
                                       transaction_no=transaction_no[0],
                                       receipt_no=receipt_no[0],
                                       doc=doc[0],
                                       inst_premium=inst_premium[0], sum_assured=sum_assured[0], rows=rows, limit=limit, filename=filename)

                # return redirect(url_for('return_files_tut', filename=filename))

            else:
                msg = "File( " + filename + " ) uploaded successfully but couldn't read incompatible data. Sorry for inconvenience!! Enter data manually"
                return render_template('manualEntryForm.html', msg=msg, filename=filename)


@app.route('/HDFC_index<filename>', methods=['POST', 'GET'])
def HDFC_index(filename):
    filepath = UPLOAD_FOLDER + filename
    print('Getting text content for {}...'.format(filepath))
    process = subprocess.Popen(
        ['pdf2txt.py', filepath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    if process.returncode != 0 or stderr:
        raise OSError('Executing the command for {} caused an error:\nCode: {}\nOutput: {}\nError: {}'.format(
            filepath, process.returncode, stdout, stderr))
    # print(stdout)
    pdf_text = stdout.decode('utf-8')
    #print(pdf_text)

    regex1 = r'\bProposal/Policy No\b\.:\s([\S]*)\n'
    policy_num = re.findall(regex1, pdf_text)
    print("Policy_num: ", policy_num)

    regex2 = r'Life\sAssured\s:\s(.*)\n'
    benefeciary_name = re.findall(regex2, pdf_text)
    print("Benefeciary Name: ", benefeciary_name)

    regex3 = r'Date\s:\s(.*)\n'
    paid_on_date = re.findall(regex3, pdf_text)
    print("Paid on date: ", paid_on_date)

    regex4 = r'Next\sPremium\sDue:\s(.*)\n'
    next_due_date = re.findall(regex4, pdf_text)
    print("Next Premium Due Date: ", next_due_date)

    regex5 = r'Receipt\sNo\s:\s(.*)\n'
    receipt_no = re.findall(regex5, pdf_text)
    print("receipt No: ", receipt_no)

    regex6 = r'Plan\sDescription\s:\s(.*)\n'
    plan_desc = re.findall(regex6, pdf_text)
    print("Plan Description: ", plan_desc)

    regex7 = r'Total\sAmount\sPaid:\s\**(.*)\n'
    inst_premium = re.findall(regex7, pdf_text)
    print("Inst. Premium: ", inst_premium)

    regex8 = r'Client\sID\s:\s(.*)\n'
    client_id = re.findall(regex8, pdf_text)
    print("Client ID: ", client_id)
    # return stdout.decode('utf-8')

    # Adding details to database
    with sqlite3.connect("policies.db") as con:
        cur = con.cursor()
        con.row_factory = sqlite3.Row
        cur.execute("select * from HDFC_Policies")
        rows = cur.fetchall()
        limit = len(rows)
    # limit = limit-1
        if(len(rows) == 0):
            cur.execute("INSERT into HDFC_Policies  values (?,?,?,?,?,?,?,?,?)", (policy_num[0],
                                                                                  client_id[0], benefeciary_name[0], next_due_date[0], inst_premium[0], paid_on_date[0], receipt_no[0], plan_desc[0], filename))
            con.commit()
            msg = "Records successfully Added"
            print(msg)
        else:
            for row in rows:
                status = " "
                if(receipt_no[0] == row[6]):
                    msg = "The HDFC Life Insurance Policy data you are trying to upload already exists"
                    return redirect(url_for('duplicate_upload', msg=msg))
                else:
                    status = "Not a duplicate data"
            if(status == "Not a duplicate data"):
                cur.execute("INSERT into HDFC_Policies  values (?,?,?,?,?,?,?,?,?)", (policy_num[0],
                                                                                      client_id[0], benefeciary_name[0], next_due_date[0], inst_premium[0], paid_on_date[0], receipt_no[0], plan_desc[0], filename))
                con.commit()
                msg = "Records successfully Added"
                print(msg)

    return render_template('HDFCinfo.html', policy_num=policy_num[0],
                           benefeciary_name=benefeciary_name[0], paid_on_date=paid_on_date[0],
                           client_id=client_id[0],
                           receipt_no=receipt_no[0],
                           next_due_date=next_due_date[0],
                           inst_premium=inst_premium[0], plan_desc=plan_desc[0], rows=rows, limit=limit, filename=filename)
    # return "ok"


# Manual data entry
@app.route('/manualDtaEntry<filename>', methods=['POST', 'GET'])
def manual_data_entry(filename):
    default_name = '0'
    policy_num = request.form.get('policy_num', default_name)
    first_name = request.form.get('first_name', default_name)
    middle_name = request.form['middle_name']
    last_name = request.form.get('last_name', default_name)
    paid_on_date = request.form['paid_on_date']
    transaction_no = request.form['transaction_no']
    receipt_no = request.form['receipt_no']
    doc = request.form['doc']
    inst_premium = request.form['inst_premium']
    sum_assured = request.form['sum_assured']
    benefeciary_name = first_name + " " + middle_name + " " + last_name
    # print(benefeciary_name)
    with sqlite3.connect("policies.db") as con:
        cur = con.cursor()
        con.row_factory = sqlite3.Row
        cur.execute("select * from Lic_Policies")
        rows = cur.fetchall()
        limit = len(rows)
        #limit = limit-1
        if(len(rows) == 0):
            cur.execute("INSERT into Lic_Policies  values (?,?,?,?,?,?,?,?,?)", (policy_num,
                                                                                 benefeciary_name, doc, inst_premium, sum_assured, transaction_no, paid_on_date, receipt_no, filename))
            con.commit()
            msg = "Records successfully Added"
            print(msg)
        else:
            for row in rows:
                status = " "
                if(transaction_no == row[5]):
                    msg = "The data you are trying to upload already exists"
                    return render_template('index.html', msg=msg)
                else:
                    status = "Not a duplicate data"
            if(status == "Not a duplicate data"):
                cur.execute("INSERT into Lic_Policies  values (?,?,?,?,?,?,?,?,?)", (policy_num,
                                                                                     benefeciary_name, doc, inst_premium, sum_assured, transaction_no, paid_on_date, receipt_no, filename))
                con.commit()
                msg = "Records successfully Added"
                print(msg)
                # print("limit", len(rows))
    return render_template('info.html', policy_num=policy_num,
                           benefeciary_name=benefeciary_name, paid_on_date=paid_on_date,
                           transaction_no=transaction_no,
                           receipt_no=receipt_no,
                           doc=doc,
                           inst_premium=inst_premium, sum_assured=sum_assured, rows=rows, limit=limit)


# Download API
@app.route('/download')
def download_file():
    file_type = '/*pdf'
    files = glob.glob(UPLOAD_FOLDER + file_type)
    max_file = max(files, key=os.path.getctime)
    return send_file(max_file, as_attachment=True)
    print(max_file)
    # return send_from_directory(app.config['UPLOAD_FOLDER'], path, as_attachment=True)


@app.route('/download_history<filename>')
def download_history_file(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True)


@app.route('/deleteHDFC_history/<filename>/<Receipt_No>', methods=['POST', 'GET'])
def deleteHDFC_history_file(filename, Receipt_No):
    file_path = UPLOAD_FOLDER + filename
    with sqlite3.connect("policies.db") as con:
        cur = con.cursor()
        sql = "Delete from HDFC_Policies where Receipt_No=? and PDFfilename =?"
        param = (Receipt_No, filename)
        cur.execute(sql, param)
        con.commit()
        print("Record Deleted successfully ")
    os.remove(file_path)
    print("PDF file deleted successfully")
    return redirect(url_for('HDFC_list_history'))


@app.route('/deleteLIC_history/<filename>/<Transaction_No>', methods=['POST', 'GET'])
def deleteLIC_history_file(filename, Transaction_No):
    file_path = UPLOAD_FOLDER + filename
    with sqlite3.connect("policies.db") as con:
        cur = con.cursor()
        sql = "Delete from LIC_Policies where Transaction_No=? and PDFfilename =?"
        param = (Transaction_No, filename)
        cur.execute(sql, param)
        con.commit()
        print("Record Deleted successfully ")
    os.remove(file_path)
    print("PDF file deleted successfully")
    return redirect(url_for('LIC_list_history'))


if __name__ == '__main__':
    app.run(port=5005, debug=True)
