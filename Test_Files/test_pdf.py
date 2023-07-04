from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle

def create_pdf_with_table():
    # Create a new PDF file
    pdf_file_path = 'example.pdf'
    doc = SimpleDocTemplate(
        pdf_file_path, 
        pagesize=landscape(A4),
        leftMargin = 20,
        rightMargin = 20,
        topMargin = 20,
        bottomMargin = 20
        )

    # Define table data

    data = [['', 'Ref', 'Due Date', 'Matching', 'Initial Balance', 'Debit', 'Credit', 'Ex.Rate', 'Amt.Currency', 'Balance'], 
            ['MMM_TEST_004', '', '', '', '0.00 K', '100,000.00 K', '110,000.00 K', '', '', '-10,000.00 K'], 
            ['2023-06-01', 'SPT/PV/000051', '2023-06-01', 'A48447', '0.00 K', '0.00 K', '100,000.00 K', 1.0, '-100,000.00 K MMK', '-100,000.00 K'], 
            ['2023-06-01', 'SPT/PV/000051', '2023-06-01', 'A48448', '-100,000.00 K', '100,000.00 K', '0.00 K', 1.0, '100,000.00 K MMK', '0.00 K'], 
            ['2023-06-15', 'SPT/BILL/000149', '2023-06-27', '', '0.00 K', '0.00 K', '10,000.00 K', 1.0, '-10,000.00 K MMK', '-10,000.00 K']]
    # Create a table and set its style
    table = Table(data)
    table.setStyle(TableStyle([
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
    ]))
    # headerTable = [
    #     []
    # ]
    # table = Table(headerTable)
    # Create a header paragraph
    styles = getSampleStyleSheet()
    header_style = styles['Heading1']
    header_style.alignment = 1  # 0=left, 1=center, 2=right


    header = Paragraph('<b>MUDON MAUNG MAUNG</b>', header_style)


    left_text_style = ParagraphStyle(name="LeftText", parent=styles["Normal"], alignment=0,leftIndent=18,fontSize=12)
    right_text_style = ParagraphStyle(name="RightText", parent=styles["Normal"], alignment=2, rightIndent=20, fontSize=12)

    # Create the data for the table
    data = [
        [Paragraph("Partner Ledger", left_text_style), Paragraph("Date - To:   From:  ", right_text_style)],
        [Paragraph("", left_text_style), Paragraph("", right_text_style)],
    ]

    # Create the table
    htable = Table(data)

    # Build the PDF document with header and table
    elements = [header,htable, table]
    doc.build(elements)

create_pdf_with_table()
