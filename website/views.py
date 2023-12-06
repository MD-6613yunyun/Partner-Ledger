from flask import Blueprint, render_template, jsonify, request, url_for, send_file,redirect, session
from website import db_connection
from datetime import date,timedelta, datetime
import xlsxwriter
from reportlab.lib.pagesizes import A4,portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle
import os

# Get the base directory of your project
base_directory = os.path.dirname(os.path.abspath(__file__))

# Combine the base directory and relative path to get the full file path
excel_path = os.path.join(base_directory, "static/downloadable_files/PartnerLedger.xlsx")
pdf_path = os.path.join(base_directory, "static/downloadable_files/PartnerLedger.pdf")

views = Blueprint('views',__name__)

def get_financial_year_dates():
    date = datetime.now().date()
    if date.month >= 4:  # April or later
        start_date = datetime(date.year, 4, 1).strftime('%Y-%m-%d')
        end_date = datetime(date.year + 1, 3, 31).strftime('%Y-%m-%d')
    else:  # Before April
        start_date = datetime(date.year - 1, 4, 1).strftime('%Y-%m-%d')
        end_date = datetime(date.year, 3, 31).strftime('%Y-%m-%d')

    return start_date, end_date

@views.route('/')
def nani_home():
    return redirect(url_for('auth.authenticate',typ='log'))

@views.route('/ledger-report')
def all_partners():
    conn = db_connection()
    cursor = conn.cursor()
    if 'ledger_id' not in session or 'ledger_admin' not in session:
        return redirect(url_for('auth.authenticate',typ='log'))
    code = session['ledger_id']
    admin = session['ledger_admin']
    if not code:
        return redirect(url_for('auth.authenticate'))
    cursor.execute("SELECT unit_code,shop_code,admin FROM user_auth WHERE code = %s;",(code,))
    datas = cursor.fetchone()
    if not datas:
        return redirect(url_for('auth.authenticate'))
    session['ledger_admin'] = datas[2]
    admins = [code,datas[2]]
    units_ids = [dt for dt in datas[0].split(",") if dt != '']
    shops_ids = [dt for dt in datas[1].split(",") if dt != '']
    units,shops = [] , []
    if units_ids != []:
        cursor.execute("SELECT id,name FROM res_company WHERE id in %s",(tuple(units_ids),))
        units = cursor.fetchall()
    if '0' in units_ids:
        units.append((0,'All Business Units'))
    if shops_ids != []:
        cursor.execute("SELECT id,name FROM analytic_shop WHERE id in %s",(tuple(shops_ids),))
        shops = cursor.fetchall()
    if '0' in shops_ids:
        shops.append((0,'All Shops'))
    cursor.execute("SELECT id,code FROM analytic_project_code;")
    pj_codes = cursor.fetchall()
    cursor.execute("SELECT id,name FROM res_partner_owner;")
    owners = cursor.fetchall()
    cursor.execute("SELECT id,name FROM res_partner WHERE customer_type is not null or vendor_category is not null;")
    partners = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("all_partners.html",pj_codes = pj_codes,owners = owners, partners = partners,units = units, shops = shops,admins=admins)

@views.route('/get-data-all/<variable>')
def get_data_all(variable:str):
    data,*n = get_each_journals(variable)
    return jsonify(data)

def get_each_journals(info,export=False):
    # pay@all@posted@39@@22@@@2023-12-01@2023-12-01
    pay,recon,status,unit,pj_code,shop,owner,partner,start_date,end_date = info.split("@")
    pi,pc,shop,ownID,ptnID = eval(unit), eval(pj_code), eval(shop),eval(owner),eval(partner)
    # pay,recv,post,draft,recon,pi,pc,shop,ownID,ptnID,rangeDate = info.split("@")
    # pay,recv,post,draft,pi,pc,shop,ownID,ptnID = eval(pay.capitalize()),eval(recv.capitalize()),eval(post.capitalize()),eval(draft.capitalize()),eval(pi), eval(pc), eval(shop),eval(ownID),eval(ptnID)
    if pay == 'both':
        where_clause = "(aa.user_type_id = 1 or aa.user_type_id = 2) and "
    else:
        if pay == 'pay':
            where_clause = "aa.user_type_id = 2 and "
        else:
            where_clause = "aa.user_type_id = 1 and " 
    if status == 'both':
        where_clause += "acc.parent_state != 'cancel' and "
    else:
        if status == 'draft':
            where_clause += "acc.parent_state != 'posted' and acc.parent_state != 'cancel' and "
        else:
            where_clause += "acc.parent_state = 'posted' and " 
    if recon == 'unreconciled':
        where_clause += "acc.full_reconcile_id is null and "
    if pi and pi[0] != '0':
        where_clause += f"acc.unit_id = {int(pi[0])} and "
    if pc:
        where_clause += f"acc.project_code_id = {pc} and "
    if shop and shop[0] != '0':
        where_clause += f"acc.shop_id = {int(shop[0])} and "
    if ownID:
        where_clause += f"acc.owner_id = {ownID} and "
    if ptnID:
        where_clause += f"acc.partner_id = {ptnID} and "

    # end_date = date.today().strftime('%Y-%m-%d')
    # if rangeDate == 'Today':
    #     start_date = date.today().strftime('%Y-%m-%d')
    # elif rangeDate == 'This week':
    #     start_date = (date.today() - timedelta(days=date.today().weekday())).strftime('%Y-%m-%d')
    # elif rangeDate == 'This Month':
    #     start_date = date.today().replace(day=1).strftime('%Y-%m-%d')
    # elif rangeDate == 'This Year':
    #     start_date,end_date = get_financial_year_dates()
    # else:
    # start_date = (datetime.strptime(start_dt, "%Y/%m/%d")).strftime("%Y-%m-%d")
    # end_date = (datetime.strptime(end_dt, "%Y/%m/%d")).strftime("%Y-%m-%d")
    
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
                temp[1] = "  " + temp[1]
                if lines_result != []:
                    temp[1] = "⏬ " + temp[1]
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
            curr = row[-1] if row[-1] != 'MMK' else 'K'
            lines_result = [[row[5].strftime("%Y-%m-%d"),typ,row[6],jrnl,due_dt,match_num,"{0:,.2f}".format(row[11]),"{:,.2f} ".format(row[12]) + curr,init_bal,"{:,.2f}".format(row[9]),"{:,.2f}".format(row[10]),bal]]
            if temp == 0:
                if not export:
                    temp = [row[13],row[14].replace("'","&lsquo;"),float(db)-float(cd)]
                else:
                    temp = [row[13],row[14],float(db)-float(cd)]
        else:
            init_bal = float(bal)
            bal = (init_bal + float(row[9]) ) - float(row[10])
            lines_result.append([row[5].strftime("%Y-%m-%d"),typ,row[6],jrnl,due_dt,match_num,"{0:,.2f}".format(row[11]),"{:,.2f} ".format(row[12]) + curr ,init_bal,"{:,.2f}".format(row[9]),"{:,.2f}".format(row[10]),bal])
        total_db += float(row[9])
        total_cd += float(row[10])

    # store last result
    if rows != []:
        temp.extend([total_db,total_cd,bal])
        overallDb += total_db
        overallCd += total_cd
        overallBal += bal
        if lines_result != []:
            temp[1] = "⏬ " + temp[1]
        else:
            temp[1] = "  " + temp[1]
        final_result[str(temp)] = lines_result
        bal, temp, total_db, total_cd = 0,0,0.0,0.0
    dct , var = get_all_results(include_transaction_lst,f"{where_clause}acc.date < '{start_date}'")
    final_result.update(dct)
    cursor.close()
    conn.close()
    return final_result,start_date,end_date,shop,ownID,pi,["{0:,.2f} K".format(overallInit+var),"{0:,.2f} K".format(overallDb),"{0:,.2f} K".format(overallCd),"{0:,.2f} K".format(overallBal+var)]

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
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    final_init_result = {}
    initBal = 0.0
    for dt in data:
        cus_name = dt[0].replace("'","&lsquo;")
        initBal += float(dt[2])
        if dt[2] != 0.0:
            key = str([dt[1],"  " + cus_name,"{:,.2f}".format(dt[2]),'0.00','0.00',"{:,.2f}".format(dt[2])])
            final_init_result[key] = []
    cursor.close()
    conn.close()
    return final_init_result, initBal

def get_table_data_for_excel_pdf(variable,pdf=False):
    conn = db_connection()
    cursor = conn.cursor()
    rtn_data,start_dt,end_dt,shop,ownID,pi,overallList = get_each_journals(variable,export=True)
    owner = ""
    if pi:
        pi = pi[1]
        if "Auto Part" in pi:
            pi = "AUTO PARTS SALES CENTER"
    if ownID:
        cursor.execute(f"SELECT id,name FROM res_partner_owner WHERE id = {ownID};")
        owners = cursor.fetchall()
        owner = owners[0][1] if len(owners) != 0 else ""
    shop_data = "All Shops" if not shop else f"{shop[1]}"

    t_data = [['Date', 'JRNL', 'Acount', 'Ref', 'Due Date', 'Matching', 'Exchange Rate', 'Amount Currency','Initial Balance', 'Debit', 'Credit',  'Balance'],
              ['Overall','','','','','','',''] + overallList
              ]
    if pdf:
        t_data = [['Date', 'JRNL',  'Ref',  'Rate', 'Amt.Currency','Init.Balance', 'Debit', 'Credit',  'Balance'],
                  ['Overall','','','',''] + overallList
                  ]
        ptn_range = [1]
        row_identify = 0
        for ptn , lines in rtn_data.items():
            ptnList = eval(ptn)
            t_data.append([ptnList[1][2:],'', '', '', '', "{:,.2f}".format(ptnList[2]) if isinstance(ptnList[2],float) else ptnList[2],"{:,.2f}".format(ptnList[3]) if isinstance(ptnList[3],float) else ptnList[3],"{:,.2f}".format(ptnList[4]) if isinstance(ptnList[4],float) else ptnList[4],"{:,.2f}".format(ptnList[5]) if isinstance(ptnList[5],float) else ptnList[5]])
            row_identify += 1
            ptn_range.append(row_identify+1)
            for line in lines:
                del line[4] , line[2] , line[3]
                line[-1] , line[-4] = "{:,.2f}".format(line[-1]) , "{:,.2f}".format(line[-4]) 
                t_data.append(line)
                row_identify += 1
        return t_data,start_dt,end_dt,shop_data,owner,ptn_range,pi
    else:
        for ptn , lines in rtn_data.items():
            ptnList = eval(ptn)
            t_data.append([ptnList[1][2:],'', '', '', '', '','', '',ptnList[2],ptnList[3],ptnList[4],ptnList[5]])
            for line in lines:
                line[-2] , line[-3] = line[-2].replace(",","") , line[-3].replace(",","")
                t_data.append(line)
    return t_data,start_dt,end_dt,shop_data,owner,pi

@views.route("get-excel-partner/<variable>")
def get_excel_partner(variable):
    t_data,start_dt,end_dt,shop_data,owner,BI = get_table_data_for_excel_pdf(variable)
    workbook = xlsxwriter.Workbook(excel_path)
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
    return send_file(excel_path,as_attachment=True)

@views.route("get-pdf-partner/<variable>")
def get_pdf_partner(variable):
    t_data,start_dt,end_dt,shop_data,owner,ptn_range,BI = get_table_data_for_excel_pdf(variable,pdf=True)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=portrait(A4),
        leftMargin = 20,
        rightMargin = 20,
        topMargin = 20,
        bottomMargin = 20
        )
    table_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), '#1A78CF'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), '#F7F7F7'),
        ('SPAN', (0, 1), (3, 1)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Align cells in column 3 (index starts from 0) to center
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, '#CCCCCC'),
    ]
    for i in t_data:
        if i[1] != "":
            table_styles[4] = ('FONTSIZE', (0, 0), (-1, -1), 7)
            break

    for i in ptn_range:
        table_styles.extend([('LINEBELOW', (0, i), (-1, i), 2, '#000000'),('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'),('SPAN', (0, i), (4, i))])

    # Create a table and set its style
    table = Table(t_data)
    table.setStyle(TableStyle(table_styles))

    styles = getSampleStyleSheet()
    header_style = styles['Heading2']
    header_style.alignment = 1  # 0=left, 1=center, 2=right
    # headers
    header = Paragraph('MUDON MAUNG MAUNG', header_style)    
    header1 = Paragraph(f"{shop_data}", header_style) 
    if BI:
        header2 = Paragraph(f"{BI}", header_style)          
    # styles  for side by side texts
    left_text_style = ParagraphStyle(name="LeftText", parent=styles["Normal"], alignment=0,leftIndent=5,fontSize=8)
    right_text_style = ParagraphStyle(name="RightText", parent=styles["Normal"], alignment=2, rightIndent=5, fontSize=8)
    center_text_style = ParagraphStyle(name="CenterText", parent=styles["Normal"], alignment=1, fontSize=8)
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
    if BI:
        elements = [printed_date,header,header2,header1,htable, table]
    else:
        elements = [printed_date,header,header1,htable, table]
    doc.build(elements)
    return send_file(pdf_path,as_attachment=True)