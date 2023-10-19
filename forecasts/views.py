from datetime import datetime
import os
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
import xlwt
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
import pdfkit
from forecasts.models import FileForecast, OpenPDS, OpenPDSDetail, PDSErrorLogs
from forecasts.serializers import FileForecastSerializer

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
    dte = datetime.now()
    fname = f"export_forecast_{dte.strftime('%Y%m%d%H%M')}.pdf"
    try:
        template = get_template("reports/forecast.html")
        pds = OpenPDS.objects.get(id=id)
        pds_detail = OpenPDSDetail.objects.filter(pds_id=id)
        context = {
            'pds': pds,
            'pds_list': pds_detail
        }
        
        # return HttpResponse(template.render(context, request))
        template = render_to_string("reports/forecast.html", context)
        css = os.path.join(settings.BASE_DIR, 'static/css', 'bulma.min.css')
        fname = f"export_forecast_{dte.strftime('%Y%m%d%H%M')}.pdf"
        file_name = os.path.join(settings.BASE_DIR, 'static/exports', fname)
        pdfkit.from_string(template, file_name, css=css)
    except Exception as ex:
        print(ex)
        pass
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return redirect(f"/static/exports/{fname}")

class FileForecastListApiView(APIView):
    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        # Supplier = Supplier.objects.filter(user = request.user.id)
        id = self.request.query_params.get('id')
        if id:
            obj = FileForecast.objects.get(id=id)
            serializer = FileForecastSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = FileForecast.objects.all()
        serializer = FileForecastSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)