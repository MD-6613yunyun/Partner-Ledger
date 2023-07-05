from flask import Blueprint, render_template, jsonify, request, url_for, send_file
import psycopg2
from datetime import date,timedelta, datetime
import xlsxwriter
from reportlab.lib.pagesizes import A4,landscape,LEGAL
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle

views = Blueprint('views',__name__)

def db_connection():
    # Database connection details
    host = '192.168.0.60'
    # host = '172.30.32.183'
    port = '5432'  # Default PostgreSQL port
    database = 'mmm_uat'
    user = 'postgres'
    password = 'admin'
    
    # Establish the database connection
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return conn
    except psycopg2.Error as e:
        print('Error connecting to the database:', e)
    
@views.route('/')
def all_partners():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,code FROM analytic_project_code;")
    pj_codes = cursor.fetchall()
    cursor.execute("SELECT id,name FROM res_partner_owner;")
    owners = cursor.fetchall()
    cursor.execute("SELECT id,name FROM res_partner WHERE customer_type is not null or vendor_category is not null;")
    partners = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("all_partners.html",pj_codes = pj_codes,owners = owners, partners = partners)

@views.route('/get-data-all/<variable>')
def get_data_all(variable:str):
    data,*n = get_each_journals(variable)
    return jsonify(data)

def get_each_journals(info):
    pay,recv,post,draft,recon,pi,pc,shop,ownID,ptnID,rangeDate = info.split("@")
    pay,recv,post,draft,pi,pc,shop,ownID,ptnID = eval(pay.capitalize()),eval(recv.capitalize()),eval(post.capitalize()),eval(draft.capitalize()),eval(pi), eval(pc), eval(shop),eval(ownID),eval(ptnID)
    if pay and recv:
        where_clause = "(aa.user_type_id = 1 or aa.user_type_id = 2) and "
    else:
        if pay:
            where_clause = "aa.user_type_id = 2 and "
        else:
            where_clause = "aa.user_type_id = 1 and " 
    if draft and post:
        where_clause += "acc.parent_state != 'cancel' and "
    else:
        if draft:
            where_clause += "acc.parent_state != 'posted' and acc.parent_state != 'cancel' and "
        else:
            where_clause += "acc.parent_state = 'posted' and " 
    if recon == 'Only show unreconciled entries':
        where_clause += "acc.full_reconcile_id is null and "
    if pi:
        where_clause += f"acc.unit_id = {int(pi[0])} and "
    if pc:
        where_clause += f"acc.project_code_id = {pc} and "
    if shop:
        where_clause += f"acc.shop_id = {int(shop[0])} and "
    if ownID:
        where_clause += f"acc.owner_id = {ownID} and "
    if ptnID:
        where_clause += f"acc.partner_id = {ptnID} and "

    end_date = date.today().strftime('%Y-%m-%d')
    if rangeDate == 'Today':
        start_date = date.today().strftime('%Y-%m-%d')
    elif rangeDate == 'This week':
        start_date = (date.today() - timedelta(days=date.today().weekday())).strftime('%Y-%m-%d')
    elif rangeDate == 'This Month':
        start_date = date.today().replace(day=1).strftime('%Y-%m-%d')
    elif rangeDate == 'This Year':
        start_date = date.today().replace(day=1,month=1).strftime('%Y-%m-%d')
    else:
        dts = rangeDate.replace("~","/").split(" - ")
        start_date = (datetime.strptime(dts[0], "%m/%d/%Y")).strftime("%Y-%m-%d")
        end_date = (datetime.strptime(dts[1], "%m/%d/%Y")).strftime("%Y-%m-%d")
    
    conn = db_connection()
    cursor = conn.cursor()
    fst_where_clause = f"{where_clause}acc.date >= '{start_date}' and acc.date <= '{end_date}' "
 
    query = """
    SELECT 
        am.seq_no,aj.type, am.payment_id , ap.seq_no , acc.move_name,acc.date,aa.name,acc.date_maturity,
        acc.matching_number,acc.debit,acc.credit, acc.exchange_rate ,acc.amount_currency, acc.partner_id, 
        ptn.name, rc.name
    FROM account_move_line acc
        JOIN account_account aa ON (aa.id = acc.account_id)
        JOIN res_partner ptn ON (acc.partner_id = ptn.id)
        JOIN res_currency rc ON (acc.currency_id = rc.id )
        JOIN account_move am ON (acc.move_id = am.id)
        JOIN account_journal aj ON (am.journal_id = aj.id )
        LEFT JOIN account_payment ap ON (am.payment_id = ap.id )
    WHERE {} ORDER BY acc.partner_id, acc.date
    """
    query = query.format(fst_where_clause)
    cursor.execute(query)
    rows = cursor.fetchall()
    include_transaction_lst = [0]
    final_result, lines_result, init_bal, total_db, total_cd, bal, temp = {} , [] , 0.0 , 0 , 0 , 0.0, 0
    overallInit, overallDb, overallCd, overallBal = 0.0 , 0.0 , 0.0 , 0.0
    for row in rows:
        due_dt = "" if row[7] == None else row[7].strftime("%Y-%m-%d")
        if row[1] in ['cash','bank']:
            jrnl = row[3]
        elif row[1] in ['sale','purchase']:
            jrnl = row[0]
        else:
            jrnl = row[4]
        typ = row[1].capitalize()
        match_num = "" if not row[8] else row[8]
        if row[13] not in include_transaction_lst:
            if include_transaction_lst[-1] != row[14] and include_transaction_lst[-1] != 0:
                temp.extend([total_db,total_cd,bal])
                overallDb += total_db
                overallCd += total_cd
                overallBal += bal
                final_result[str(temp)] = lines_result
                bal, temp, total_db, total_cd = 0,0,0.0,0.0
            include_transaction_lst.append(row[13])
            init_where_clause = f"{where_clause}acc.partner_id = {row[13]} and  acc.date < '{start_date}' "
            query = """
            SELECT 
                SUM(acc.debit), SUM(acc.credit)
            FROM account_move_line acc
                JOIN account_account aa ON (acc.account_id = aa.id)
            WHERE {}
            """
            query = query.format(init_where_clause)
            cursor.execute(query)
            initRows = cursor.fetchall()
            for initRow in initRows:
                db,cd = initRow
            if not db:
                db = 0.00
            if not cd:
                cd = 0.00
            init_bal = float(db)-float(cd)
            overallInit += init_bal
            bal = (float(init_bal) + float(row[9]) ) - float(row[10])
            lines_result = [[row[5].strftime("%Y-%m-%d"),typ,row[6],jrnl,due_dt,match_num,"{0:,.2f}".format(row[11]),"{:,.2f} ".format(row[12]) + row[-1],init_bal,"{:,.2f}".format(row[9]),"{:,.2f}".format(row[10]),bal]]
            if temp == 0:
                temp = [row[13],row[14].replace("'","&lsquo;"),float(db)-float(cd)]
        else:
            init_bal = float(bal)
            bal = (init_bal + float(row[9]) ) - float(row[10])
            lines_result.append([row[5].strftime("%Y-%m-%d"),typ,row[6],jrnl,due_dt,match_num,"{0:,.2f}".format(row[11]),"{:,.2f} ".format(row[12]) + row[-1],init_bal,"{:,.2f}".format(row[9]),"{:,.2f}".format(row[10]),bal])
        total_db += float(row[9])
        total_cd += float(row[10])

    # store last result
    if rows != []:
        temp.extend([total_db,total_cd,bal])
        overallDb += total_db
        overallCd += total_cd
        overallBal += bal
        final_result[str(temp)] = lines_result
        bal, temp, total_db, total_cd = 0,0,0.0,0.0
    final_result.update(get_all_results(include_transaction_lst,f"{where_clause}acc.date < '{start_date}'"))
    cursor.close()
    conn.close()
    return final_result,start_date,end_date,shop,ownID,["{0:,.2f} K".format(overallInit),"{0:,.2f} K".format(overallDb),"{0:,.2f} K".format(overallCd),"{0:,.2f} K".format(overallBal)]

def get_all_results(explict_tuple,where_clause):
    query = """
        SELECT
            p.name AS partner_name,
            p.id as partner_id,
            COALESCE((SUM(line.debit)-SUM(line.credit)), 0) AS total_debit_amount
        FROM
            res_partner p
            LEFT JOIN account_move_line line ON line.partner_id = p.id
            LEFT JOIN account_account aa ON line.account_id = aa.id
        WHERE
            {}
        GROUP BY
            p.name,p.id;
    """
    where_clause = where_clause.replace('acc','line') if explict_tuple == [0]   else where_clause.replace('acc','line') + f" and p.id not in {tuple(explict_tuple)}"
    query = query.format(where_clause)
    print(query)
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    final_init_result = {}
    for dt in data:
        cus_name = dt[0].replace("'","&lsquo;")
        key = str([dt[1],cus_name,"{:,.2f} ".format(dt[2]),'0.00','0.00',"{:,.2f} ".format(dt[2])])
        final_init_result[key] = []
    cursor.close()
    conn.close()
    return final_init_result

def get_table_data_for_excel_pdf(variable,pdf=False):
    conn = db_connection()
    cursor = conn.cursor()
    rtn_data,start_dt,end_dt,shop,ownID,overallList = get_each_journals(variable)
    owner = "All Owners"
    if ownID:
        cursor.execute(f"SELECT id,name FROM res_partner_owner WHERE id = {ownID};")
        owners = cursor.fetchall()
        owner = owners[0][1] if len(owners) != 0 else ""
    shop_data = "All Shops" if not shop else f"{shop[1]}"

    t_data = [['Date', 'JRNL', 'Acount', 'Ref', 'Due Date', 'Matching', 'Exchange Rate', 'Amount Currency','Initial Balance', 'Debit', 'Credit',  'Balance'],
              ['Overall','','','','','','',''] + overallList
              ]
    if pdf:
        t_data = [['Date', 'JRNL', 'Acount', 'Ref', 'Matching', 'Ex.Rate', 'Amt.Currency','Initial Balance', 'Debit', 'Credit',  'Balance'],
                  ['Overall','','','','','',''] + overallList
                  ]
        ptn_range = [1]
        row_identify = 0
        for ptn , lines in rtn_data.items():
            ptnList = eval(ptn)
            t_data.append([ptnList[1],'', '', '', '', '','',ptnList[2],ptnList[3],ptnList[4],ptnList[5]])
            row_identify += 1
            ptn_range.append(row_identify+1)
            for line in lines:
                del line[4]
                line[-1] , line[-4] = "{:,.2f}".format(line[-1]) , "{:,.2f}".format(line[-4]) 
                t_data.append(line)
                row_identify += 1
        return t_data,start_dt,end_dt,shop_data,owner,ptn_range
    else:
        for ptn , lines in rtn_data.items():
            ptnList = eval(ptn)
            t_data.append([ptnList[1],'', '', '', '', '','', '',ptnList[2],ptnList[3],ptnList[4],ptnList[5]])
            for line in lines:
                line[-2] , line[-3] = line[-2].replace(",","") , line[-3].replace(",","")
                t_data.append(line)
    return t_data,start_dt,end_dt,shop_data,owner

@views.route("get-excel-partner/<variable>")
def get_excel_partner(variable):
    t_data,start_dt,end_dt,shop_data,owner = get_table_data_for_excel_pdf(variable)
    print(t_data)
    workbook = xlsxwriter.Workbook("D:\\Odoo Own Project\\Partner Ledger\\website\\PartnerLedger.xlsx")
    worksheet = workbook.add_worksheet("Partner Ledger")
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "align": "center",
            "valign": "vcenter"
        }
    )
    data_format = workbook.add_format({'bg_color': '#DDDDDD',"bold":1})

    worksheet.merge_range("A1:L1",data="MUDON MAUNG MAUNG",cell_format=merge_format)
    worksheet.merge_range("A2:L2",data="Partner Ledger",cell_format=merge_format)
    worksheet.merge_range("F3:G3",data=f"{shop_data}",cell_format=merge_format)
    worksheet.write("A3","Date -")
    worksheet.write("B3",f"From : {start_dt}")
    worksheet.write("C3",f"To : {end_dt}")
    worksheet.write("L4",f"Printed Date - {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
    worksheet.write("L3",owner)
    for idx,lst in enumerate(t_data,start=4):
        worksheet.write_row(idx,0,lst)
    worksheet.conditional_format('A6:L6', {'type': 'no_errors', 'format':data_format})
    # for each in data:
    workbook.close()
    return send_file("PartnerLedger.xlsx",as_attachment=True)

@views.route("get-pdf-partner/<variable>")
def get_pdf_partner(variable):
    t_data,start_dt,end_dt,shop_data,owner,ptn_range = get_table_data_for_excel_pdf(variable,pdf=True)

    pdf_file_path = 'D:\\Odoo Own Project\\Partner Ledger\\website\\PartnerLedger.pdf'
    doc = SimpleDocTemplate(
        pdf_file_path, 
        pagesize=landscape(LEGAL),
        leftMargin = 20,
        rightMargin = 20,
        topMargin = 20,
        bottomMargin = 20
        )
    
    table_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), '#1A78CF'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), '#F7F7F7'),
        ('SPAN', (0, 1), (3, 1)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, '#CCCCCC'),
    ]

    for i in ptn_range:
        table_styles.extend([('LINEBELOW', (0, i), (-1, i), 2, '#000000'),('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'),('SPAN', (0, i), (6, i))])

    # Create a table and set its style
    table = Table(t_data)
    table.setStyle(TableStyle(table_styles))

    styles = getSampleStyleSheet()
    header_style = styles['Heading1']
    header_style.alignment = 1  # 0=left, 1=center, 2=right
    # headers
    header = Paragraph('<b>MUDON MAUNG MAUNG</b>', header_style)    
    header1 = Paragraph(f"{shop_data}", header_style)    
    # styles  for side by side texts
    left_text_style = ParagraphStyle(name="LeftText", parent=styles["Normal"], alignment=0,leftIndent=10,fontSize=11)
    right_text_style = ParagraphStyle(name="RightText", parent=styles["Normal"], alignment=2, rightIndent=10, fontSize=10)
    center_text_style = ParagraphStyle(name="CenterText", parent=styles["Normal"], alignment=1, fontSize=10)
    # printed date 
    printed_date = Paragraph(f"Printed Date - {datetime.now().strftime('%B %d, %Y %H:%M:%S')}",right_text_style)
    # Create the data for the table
    data = [
        [Paragraph("Partner Ledger", left_text_style),Paragraph(f"{owner}", center_text_style), Paragraph(f"Date - From: {start_dt} To: {end_dt} ", right_text_style)],
        [Paragraph("", left_text_style), Paragraph("", center_text_style),Paragraph("", right_text_style)],
    ]
    # Create the table
    htable = Table(data)
    # Build the PDF document with header and table
    elements = [printed_date,header,header1,htable, table]
    doc.build(elements)
    return send_file("PartnerLedger.pdf",as_attachment=True)