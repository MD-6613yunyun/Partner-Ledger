# @views.route('/')
# def home():
#     # ptn = mmm.partners(models)
#     conn = db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id,code FROM analytic_project_code;")
#     pj_codes = cursor.fetchall()
#     cursor.execute("SELECT id,name FROM res_partner WHERE customer_type is not null or vendor_category is not null")
#     res = cursor.fetchall()
#     return render_template("test.html",res=res,pj_codes = pj_codes)

# @views.route('/get-data/<variable>')
# def get_data(variable:str):
#     result = {}
#     pay,recv,post,draft,recon,pi,pc,shop,ptnID,rangeDate = variable.split("@")
#     ptnID = ptnID.replace("~","/")
#     pay,recv,post,draft,pi,pc,shop,ptnID = eval(pay.capitalize()),eval(recv.capitalize()),eval(post.capitalize()),eval(draft.capitalize()),eval(pi), eval(pc), eval(shop), eval(ptnID)
#     mmm,models = connect_server()
#     result = mmm.filter_data(pay,recv,post,draft,recon,pi,pc,shop,rangeDate,ptnID,models)
#     initialBal = partner_info(int(ptnID[0]),variable)
#     partners_dct = {}
#     if result == []:
#         print 
#         if initialBal != 0:
#             ptnID.append(initialBal)
#             partners_dct[str(ptnID)] = []
#     else:
#         for data in result:
#             initialBal = partner_info(data['partner_id'][0],variable)
#             data['partner_id'].append(initialBal)
#             dt = str(data['partner_id'])
#             if not data['matching_number']:
#                 data['matching_number'] = ""
#             data['account_id'] = data['account_id'][1]
#             data['currency_id'] = "{:,.2f}".format(data['amount_currency'])+" " + data['currency_id'][1]
#             name,typ = get_journals(data['id'])
#             data['id'] = [name,typ]
            
#             if dt not in partners_dct:
#                 if dt != "False":
#                     partners_dct[dt] = [data]
#             else:
#                 partners_dct[dt].append(data)
#     # print(partners_dct)
#     # for key,val in partners_dct.items():
#     #     print(key,val)
#     print(partners_dct)
#     return jsonify(partners_dct)

# @views.route("get-excel-partner/<variable>")
# def get_excel_partner(variable):
#     # print(variable)
#     total_db = 0.0
#     total_cdt = 0.0
#     pay,recv,post,draft,recon,pi,pc,shop,ptnID,rangeDate = variable.split("@")
#     ptnID = ptnID.replace("~","/")
#     pay,recv,post,draft,pi,pc,shop,ptnID = eval(pay.capitalize()),eval(recv.capitalize()),eval(post.capitalize()),eval(draft.capitalize()),eval(pi), eval(pc), eval(shop), eval(ptnID)
#     mmm,models = connect_server()
#     result,start_dt,end_dt = mmm.filter_data(pay,recv,post,draft,recon,pi,pc,shop,rangeDate,ptnID,models,rtnDate=True)
#     initialBal = float(partner_info(int(ptnID[0]),variable))
#     final_result = []
#     final_result.append(['\t\t\t\t','JRNL','Acount','Ref','Due Date','Matching Number','Exchange Rate','Amount Currency','Initial Balance','Debit','Credit','Balance'])
#     if result == []:
#         if initialBal != 0:
#             final_result.append([ptnID[1],'','','','','','','',initialBal,0,0,initialBal])
#     else:
#         final_result.append([result[0]['partner_id'][1],'','','','','','','',initialBal,])
#         fstInitBal = initialBal
#         for data in result:
#             if not data['matching_number']:
#                 data['matching_number'] = ""
#             data['account_id'] = data['account_id'][1]
#             data['currency_id'] = "{:,.2f}".format(data['amount_currency'])+" " + data['currency_id'][1]
#             name,typ = get_journals(data['id'])
#             balance = ( initialBal + data['debit'] ) - data['credit']
#             final_result.append([data['date'],typ.capitalize(),data['account_id'],name,data['date_maturity'],data['matching_number'],
#                                         data['exchange_rate'],data['currency_id'],initialBal,data['debit'],data['credit'],balance])

#             initialBal = balance

#             total_db += data['debit']
#             total_cdt += data['credit']

#         total_bal = ( total_db + fstInitBal) - total_cdt
#         final_result[1].extend([total_db,total_cdt,total_bal])

#     print(final_result)
#     workbook = xlsxwriter.Workbook("D:\\Odoo Own Project\\Partner Ledger\\website\\PartnerLedger.xlsx")
 
#     worksheet = workbook.add_worksheet("Partner Ledger")

#     merge_format = workbook.add_format(
#         {
#             "bold": 1,
#             "border": 1,
#             "align": "center",
#             "valign": "vcenter"
#         }
#     )

#     worksheet.merge_range("A1:L1",data="MUDON MAUNG MAUNG",cell_format=merge_format)
#     worksheet.merge_range("A2:L2",data="Partner Ledger",cell_format=merge_format)

#     worksheet.write("A3","Date -")
#     worksheet.write("B3",f"From : {start_dt}")
#     worksheet.write("C3",f"To : {end_dt}")
#     worksheet.write("L4",f"Printed Date - {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
#     shop_data = "" if not shop else f"{shop[1]}"
#     worksheet.write("L3",shop_data)

#     print(final_result)
#     for idx,lst in enumerate(final_result,start=4):
#         if idx == 1:
#             data_format = workbook.add_format({'bg_color': '#DDDDDD'})
#             worksheet.set_row(idx, cell_format=data_format)
#         worksheet.write_row(idx,0,lst)

#     # for each in data:
#     workbook.close()
#     return send_file("PartnerLedger.xlsx",as_attachment=True)


# @views.route("get-pdf-partner/<variable>")
# def get_pdf_partner(variable):
#     # print(variable)
#     total_db = 0.0
#     total_cdt = 0.0
#     pay,recv,post,draft,recon,pi,pc,shop,ptnID,rangeDate = variable.split("@")
#     ptnID = ptnID.replace("~","/")
#     pay,recv,post,draft,pi,pc,shop,ptnID = eval(pay.capitalize()),eval(recv.capitalize()),eval(post.capitalize()),eval(draft.capitalize()),eval(pi), eval(pc), eval(shop), eval(ptnID)
#     mmm,models = connect_server()
#     result,start_dt,end_dt = mmm.filter_data(pay,recv,post,draft,recon,pi,pc,shop,rangeDate,ptnID,models,rtnDate=True)
#     initialBal = float(partner_info(int(ptnID[0]),variable))
#     final_result = []
#     final_result.append(['Date','Ref','Matching','Ex.Rate','Amt.Currency','Initial Balance','Debit','Credit','Balance'])
#     if result == []:
#         print(initialBal)
#         if initialBal != 0:
#             bal = "{:,.2f}".format(initialBal)
#             final_result.append([ptnID[1],'','','',bal,0,0,'',bal])
#     else:
#         final_result.append([result[0]['partner_id'][1],'','','','',"{:,.2f}".format(initialBal),])
#         fstInitBal = initialBal
#         for data in result:
#             if not data['matching_number']:
#                 data['matching_number'] = ""
#             data['currency_id'] = "{:,.2f}".format(data['amount_currency'])+" " + data['currency_id'][1]
#             name,typ = get_journals(data['id'])
#             balance = ( initialBal + data['debit'] ) - data['credit']
#             final_result.append([data['date'],name,data['matching_number'],data['exchange_rate'],data['currency_id'],
#                                 "{:,.2f}".format(initialBal),"{:,.2f}".format(data['debit']),
#                                 "{:,.2f}".format(data['credit']),"{:,.2f}".format(balance)])

#             initialBal = balance

#             total_db += data['debit']
#             total_cdt += data['credit']

#         total_bal = ( total_db + fstInitBal) - total_cdt
#         final_result[1].extend(["{:,.2f}".format(total_db),"{:,.2f}".format(total_cdt),"{:,.2f}".format(total_bal)])

#     print(final_result)
#     pdf_file_path = 'D:\\Odoo Own Project\\Partner Ledger\\website\\PartnerLedger.pdf'
#     doc = SimpleDocTemplate(
#         pdf_file_path, 
#         pagesize=landscape(A4),
#         leftMargin = 20,
#         rightMargin = 20,
#         topMargin = 20,
#         bottomMargin = 20
#         )
#     # Create a table and set its style
#     table = Table(final_result)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), '#1A78CF'),
#         ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 12),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#         ('BACKGROUND', (0, 1), (-1, -1), '#F7F7F7'),
#         ('SPAN', (0, 1), (3, 1)),
#         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
#         ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
#         ('GRID', (0, 0), (-1, -1), 0.5, '#CCCCCC'),
#         ('LINEBELOW', (0, 1), (-1, 1), 2, '#000000'),  # Add a bold line below the second row
#     ]))

#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     header_style.alignment = 1  # 0=left, 1=center, 2=right


#     header = Paragraph('<b>MUDON MAUNG MAUNG</b>', header_style)    
#     header1 = Paragraph(" ",header_style)
#     if shop:
#         header1 = Paragraph(f"{shop[1]}", header_style)    

#     left_text_style = ParagraphStyle(name="LeftText", parent=styles["Normal"], alignment=0,leftIndent=18,fontSize=11)
#     right_text_style = ParagraphStyle(name="RightText", parent=styles["Normal"], alignment=2, rightIndent=20, fontSize=10)

#     printed_date = Paragraph(f"Printed Date - {datetime.now().strftime('%B %d, %Y %H:%M:%S')}",right_text_style)
#     # Create the data for the table
#     data = [
#         [Paragraph("Partner Ledger", left_text_style), Paragraph(f"Date - From: {start_dt} To: {end_dt} ", right_text_style)],
#         [Paragraph("", left_text_style), Paragraph("", right_text_style)],
#     ]

#     # Create the table
#     htable = Table(data)
      
#     # Build the PDF document with header and table
#     elements = [printed_date,header,header1,htable, table]
#     doc.build(elements)
#     return send_file("PartnerLedger.pdf",as_attachment=True)

# @views.route('/partner/<idd>/<info>')
# def partner_info(idd:str,info:str):
#     pay,recv,post,draft,recon,pi,pc,shop,ptnID,rangeDate = info.split("@")
#     pay,recv,post,draft,pi,pc,shop = eval(pay.capitalize()),eval(recv.capitalize()),eval(post.capitalize()),eval(draft.capitalize()),eval(pi), eval(pc), eval(shop)
#     where_clause = f"acc.partner_id = {idd} and "
#     print(pi,pc,shop)
#     if pay and recv:
#         where_clause += "(aa.user_type_id = 1 or aa.user_type_id = 2) and "
#     else:
#         if pay:
#             where_clause += "aa.user_type_id = 2 and "
#         else:
#             where_clause += "aa.user_type_id = 1 and " 
#     if draft and post:
#         where_clause += "(acc.parent_state = 'draft' or acc.parent_state = 'posted') and "
#     else:
#         if draft:
#             where_clause += "acc.parent_state = 'draft' and "
#         else:
#             where_clause += "acc.parent_state = 'posted' and " 
#     if recon == 'Only show unreconciled entries':
#         where_clause += "acc.full_reconcile_id is null and "
#     if pi:
#         where_clause += f"acc.unit_id = {int(pi[0])} and "
#     if pc:
#         where_clause += f"acc.project_code_id = {pc} and "
#     if shop:
#         where_clause += f"acc.shop_id = {int(shop[0])} and "
#     if rangeDate == 'Today':
#         start_date = date.today().strftime('%Y-%m-%d')
#     elif rangeDate == 'This week':
#         start_date = (date.today() - timedelta(days=date.today().weekday())).strftime('%Y-%m-%d')
#     elif rangeDate == 'This Month':
#         start_date = date.today().replace(day=1).strftime('%Y-%m-%d')
#     elif rangeDate == 'This Year':
#         start_date = date.today().replace(day=1,month=1).strftime('%Y-%m-%d')
#     else:
#         start_date = (datetime.strptime(rangeDate.replace("~","/").split(" - ")[0], "%m/%d/%Y")).strftime("%Y-%m-%d")
#     where_clause += f"acc.date < '{start_date}'"

#     conn = db_connection()
#     cursor = conn.cursor()
#     query = """
#         SELECT 
#             SUM(acc.debit), SUM(acc.credit)
#         FROM account_move_line acc
#             JOIN account_account aa ON (acc.account_id = aa.id)
#         WHERE {}
#     """
#     query = query.format(where_clause)
#     print("Printing")
#     cursor.execute(query)
#     rows = cursor.fetchall()
#     for row in rows:
#         db,cd = row
#     if not db:
#         db = 0.00
#     if not cd:
#         cd = 0.00
#     return f"{float(db)-float(cd)}"


# @views.route('/journals/<line_id>')
# def get_journals(line_id):
#     conn = db_connection()
#     cursor = conn.cursor()
#     query = """
#         SELECT 
#             am.seq_no,aj.type, am.payment_id , line.move_name
#         FROM account_move_line line
#             JOIN account_move am ON ( line.move_id = am.id )
#             JOIN account_journal aj ON (am.journal_id = aj.id )
#         WHERE line.id = %s
#     """
#     cursor.execute(query,(int(line_id),))
#     # print(line_id)
#     row = cursor.fetchall()
#     # print(row)
#     # print(type(row[0][2]))

#     if row[0][1] in ['cash','bank']:
#         query = """
#         SELECT 
#             ap.seq_no
#         FROM account_move am
#             JOIN account_payment ap ON (am.payment_id = ap.id )
#         WHERE am.payment_id = %s
#         """
#         # print(row[0])
#         # print(row[0][2])
#         cursor.execute(query,(row[0][2],))
#         row_two = cursor.fetchall()
#         print(row)
#         print(row_two)
#         # print(row[0][0],row_two[0][0])
#         return (row_two[0][0],row[0][1])
#     elif row[0][1] == "general":
#         return (row[0][3],'Misc.')
#     else:
#         print(row[0])
#         return  (row[0][0],row[0][1])