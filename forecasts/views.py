from datetime import datetime
import xlwt
from django.http import HttpResponse
from django.template import loader
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa  
from forecasts.models import OpenPDS, OpenPDSDetail, PDSErrorLogs

from users.models import ManagementUser

# defining the function to convert an HTML file to a PDF file
def __html_to_pdf(template_src, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None

# Create your views here.
def export_excel(request, id):
    dte = datetime.now()
    file_name = f"export_error_{dte.strftime('%Y%m%d%H%M')}"
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Export Error Log')
    # Sheet header, first row
    row_num = 0
    # Create a style for the table cells with borders
    table_style = xlwt.XFStyle()

    # Set borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    table_style.borders = borders
    
    # Set text alignment
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT  # Right alignment
    alignment.vert = xlwt.Alignment.VERT_CENTER  # Center alignment vertically
    table_style.alignment = alignment

    col_widths = [9000, 5000, 9000, 4000, 4000,2500, 2500, 2500,2500, 15000]
    columns = ["Part Code","Part No.","Part Name","Supplier","Model","Rev.0","Rev.1","Rev.2","Rev.3", "Remark",]
    for col_index, (header_value, width) in enumerate(zip(columns, col_widths)):
        ws.write(0, col_index, header_value, style=table_style)
        ws.col(col_index).width = width
    
    # Freeze the top row
    ws.set_panes_frozen(True)
    ws.set_remove_splits(True)
    ws.set_horz_split_pos(1)   
    # # Sheet body, remaining rows
    rows =  PDSErrorLogs.objects.filter(file_name=id, is_success=False).values_list("part_code","part_no","part_name","supplier","model","rev_0","rev_1","rev_2","rev_3","remark",)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], table_style)
        
    wb.save(response)
    return response

def download_forecast(request, id):
    # # return HttpResponse(f"Hello world!: {id}")
    # pds = OpenPDS.objects.filter(id=id)
    # template = loader.get_template("reports/forecast.html")
    # context = {
    #     "pds_list": pds,
    # }
    # return HttpResponse(template.render(context, request))
    dte = datetime.now()
    file_name = f"export_forecast_{dte.strftime('%Y%m%d%H%M')}"
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Export Error Log')
    # Sheet header, first row
    row_num = 0
    # Create a style for the table cells with borders
    table_style = xlwt.XFStyle()

    # Set borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    table_style.borders = borders
    
    # Set text alignment
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT  # Right alignment
    alignment.vert = xlwt.Alignment.VERT_CENTER  # Center alignment vertically
    table_style.alignment = alignment
    
    # Merge cells for the header
    header_alignment = xlwt.Alignment()
    header_alignment.horz = xlwt.Alignment.HORZ_CENTER  # Right alignment
    header_alignment.vert = xlwt.Alignment.VERT_CENTER  # Center alignment vertically
    
    # Create a style for the header
    header_style = xlwt.XFStyle()
    header_style.font.bold = True  # Bold font
    header_style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    # header_style.pattern.pattern_fore_colour = xlwt.Style.colour_map['light_blue']  # Background color
    header_style.alignment = header_alignment
    
    # Fetch Data
    head = OpenPDS.objects.get(id=id)
    # Merge cells for the header
    ws.write_merge(0, 0, 0, 4, head.supplier_id.name, style=header_style)  # Merging cells (0,0) to (0,2)
    ws.col(0).height = 5000

    col_widths = [3000, 4000, 9000, 11000, 4000]
    columns = ["Item","Model","Part No","Part Name","Qty",]
    for col_index, (header_value, width) in enumerate(zip(columns, col_widths)):
        ws.write(1, col_index, header_value, style=table_style)
        ws.col(col_index).width = width
    
    # Freeze the top row
    ws.set_panes_frozen(True)
    ws.set_remove_splits(True)
    ws.set_horz_split_pos(1)   
    # # Sheet body, remaining rows
    # rows =  PDSErrorLogs.objects.filter(file_name=id).values_list("part_code","part_no","part_name","supplier","model","rev_0","rev_1","rev_2","rev_3","remark",)
    rows = OpenPDSDetail.objects.filter(pds_id=id)
    i = 0
    row_num = 2
    for r in rows:
        ws.write(row_num, 0, str(i + 1), table_style)
        ws.write(row_num, 1, r.import_model_by_user, table_style)
        ws.write(row_num, 2, r.product_id.code, table_style)
        ws.write(row_num, 3, r.product_id.name, table_style)
        ws.write(row_num, 4, r.request_qty, table_style)
        i += 1
        row_num += 1
        
    # for row in rows:
    #     row_num += 1
    #     for col_num in range(len(row)):
    #         ws.write(row_num, col_num, row[col_num], table_style)
        
    wb.save(response)
    return response

def test_reporting(request, id):
    # # # return HttpResponse(f"Hello world!: {id}")
    # pds = OpenPDS.objects.get(id=id)
    # template = loader.get_template("reports/forecast.html")
    # context = {
    #     "obj": pds,
    # }
    # return HttpResponse(template.render(context, request))
    pdf = __html_to_pdf("reports/forecast.html")
    return HttpResponse(pdf, content_type='application/pdf')