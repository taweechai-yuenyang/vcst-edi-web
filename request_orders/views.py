import xlwt
from django.http import HttpResponse
from django.shortcuts import render
from request_orders.models import RequestOrder, RequestOrderDetail

from users.models import ManagementUser

# Create your views here.
def export_excel(request, id):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="export_order.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Export Order')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['#', 'Order No.', 'Product', 'Qty', 'Price', ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    orderH = RequestOrder.objects.get(id=id)
    rows =  RequestOrderDetail.objects.filter(request_order_id=orderH) ### ManagementUser.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        # ws.write(row_num, columns[0], str(row_num), font_style)
            
    wb.save(response)
    return response
