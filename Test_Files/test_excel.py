import xlsxwriter

workbook = xlsxwriter.Workbook('Duty Report.xlsx')
 
worksheet = workbook.add_worksheet("Duty Report")

header = ['Duty Import Person','Site Supervisor',	'Project Code'	,'Date'	,'Type'	,'Machine Main Type',	'Machine Sub Type'	,'Machine Capacity',	'MB Machine Type',	'Machine',	'Operator',	'Project Name',	'Owner'	,'Morning Start',	'Morning End',	'Afternoon Start',	'Afternoon End'	,'Evening Start'	,'Evening End',	'Running Hour'	,'Walk Hours',	'General Hours'	,'Total Hours'	,'Service Meter'	,'Initial Fuel(Mark)',	'Filling Fuel(Liter)'	,'Filling Fuel(Mark)'	,'Use Fuel(Mark)',	'Balance Fuel(Mark)',	'Increase Fuel(Mark)',	'Mark Per Liter',	'Total Use Fuel(Liter)'	,'1Hr Fuel Consumption',	'Rate Per Duty',	'Rate Per Hours',	'Fuel Price'	,'Duty Amount'	,'Fuel Amount',	'Total Amount'	,'Way','Completion(Feets)',	'Completion(Sud)',	'Remark'	,'Report Remark'	,'Job'	,'No:'	,'Status']
worksheet.write_row(0,0,header)
for idx,lst in enumerate(data,start=2):
    worksheet.write_row(idx,0,lst)

# for each in data:
workbook.close()
