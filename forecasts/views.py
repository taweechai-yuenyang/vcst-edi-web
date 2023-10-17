from datetime import datetime
import xlwt
from django.http import HttpResponse
from forecasts.models import PDSErrorLogs

from users.models import ManagementUser

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
