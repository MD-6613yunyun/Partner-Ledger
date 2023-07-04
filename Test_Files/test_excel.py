import xlsxwriter

rtn_data = {
    "[13849, 'AR/ATP/TWN-Desire Workshop (South Oakkalar)', 3415600.0, 8578900.0, 7634700.0, 4833000.0]": [
            ['2023-01-03', 'Sale', 'Account Receivable', 'TWN/INV/000032', '2023-01-17', '', 3415600.0, '184800.00', '0.00', 1.0, '184800.00 MMK', 3600400.0], 
            ['2023-01-03', 'Sale', 'Account Receivable', 'TWN/INV/000025', '2023-01-17', '', 3600400.0, '178000.00', '0.00', 1.0, '178000.00 MMK', 3778400.0]
        ],
    "[138499, 'AR/ATP/TWN-Desire Workshop (South Oakkalar)', 3415600.0, 8578900.0, 7634700.0, 4833000.0]": [
        ['2023-01-03', 'Sale', 'Account Receivable', 'TWN/INV/000032', '2023-01-17', '', 3415600.0, '184800.00', '0.00', 1.0, '184800.00 MMK', 3600400.0], 
        ['2023-01-03', 'Sale', 'Account Receivable', 'TWN/INV/000025', '2023-01-17', '', 3600400.0, '178000.00', '0.00', 1.0, '178000.00 MMK', 3778400.0]
    ]
    }

workbook = xlsxwriter.Workbook('Example3.xlsx')
 
worksheet = workbook.add_worksheet("Partner Ledger")
date = [['\t\t\t\t', 'JRNL', 'Acount', 'Ref', 'Due Date', 'Matching', 'Initial Balance', 'Debit', 'Credit', 'Exchange Rate', 'Amount Currency', 'Balance'], 
        ['MMM_TEST_004', '', '', '', '', '', '0.00', '100,000.00', '110,000.00', '', '', '-10,000.00'], 
        ['2023-06-01', 'Cash', 'Advance Payable', 'SPT/PV/000051', '2023-06-01', 'A48447', '0.00', '0.00', '100,000.00', 1.0, '-100,000.00 MMK', '-100,000.00'], 
        ['2023-06-01', 'Cash', 'AP - Local', 'SPT/PV/000051', '2023-06-01', 'A48448', '-100,000.00', '100,000.00', '0.00', 1.0, '100,000.00 MMK', '0.00'], 
        ['2023-06-15', 'Purchase', 'AP - Local', 'SPT/BILL/000149', '2023-06-27', '', '0.00', '0.00', '10,000.00', 1.0, '-10,000.00 MMK', '-10,000.00']]

t_data = [['\t\t\t\t', 'JRNL', 'Acount', 'Ref', 'Due Date', 'Matching', 'Initial Balance', 'Debit', 'Credit', 'Exchange Rate', 'Amount Currency', 'Balance']]
for ptn , lines in rtn_data.items():
    ptnList = list(ptn)
    t_data.append([ptnList[1],'', '', '', '', '',ptnList[2],ptnList[3],ptnList[4],ptnList[5]])
    for line in lines:
        t_data.append(line)

merge_format = workbook.add_format(
    {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter"
    }
)

worksheet.merge_range("A1:L1",data="MUDON MAUNG MAUNG",cell_format=merge_format)
worksheet.merge_range("A2:L2",data="Partner Ledger",cell_format=merge_format)

worksheet.write("A3","Date -")
worksheet.write("B3",f"From : Sth")
worksheet.write("C3",f"To : Sth")

for idx,lst in enumerate(date,start=4):
    if idx == 1:
        data_format = workbook.add_format({'bg_color': '#DDDDDD'})
        worksheet.set_row(idx, cell_format=data_format)
    worksheet.write_row(idx,0,date[idx-4])

# for each in data:
workbook.close()
