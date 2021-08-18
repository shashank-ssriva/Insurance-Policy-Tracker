import sqlite3
con = sqlite3.connect("policies.db")
print("Database opened successfully")
#con.execute("drop table if exists lic_Policies")
con.execute("create table if not exists HDFC_Policies (Policy_No BLOB , Client_ID BLOB, Beneficiary_Name TEXT NOT NULL, Next_Due_Date BLOB, Inst_Premium BLOB, Paid_on_date BLOB, Receipt_No BLOB, Plan_Desc BLOB, PDFfilename BLOB)")  
con.execute("create table if not exists Lic_Policies (Policy_No BLOB , Beneficiary_Name TEXT NOT NULL, DOC BLOB, Inst_Premium BLOB, Sum_Assured  BLOB, Transaction_No BLOB, Paid_on_date BLOB, Receipt_No BLOB, PDFfilename BLOB)")  
print("Table created successfully")
con.close()
