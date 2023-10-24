from datetime import datetime
from django.contrib import messages
import os

import nanoid
import requests

from forecasts.models import Forecast, ForecastDetail, PDSDetail, PDSHeader
from formula_vcst.models import BOOK, COOR, DEPT, EMPLOYEE, PROD, SECT, UM, NoteCut, OrderH, OrderI

def create_purchase_order(request, id, prefixRef="PR", bookGroup="0002"):
    dte = datetime.now()
    ordH = None
    try:
        ## Line Notification
        token = request.user.line_notification_id.token
        if bool(os.environ.get('DEBUG_MODE')):
            token = os.environ.get("LINE_TOKEN")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {token}'
        }
        
        ### Get Formula Master Data
        emp = EMPLOYEE.objects.filter(FCCODE=request.user.formula_user_id.code).values()
        dept = DEPT.objects.filter(FCCODE=request.user.department_id.code).values()
        sect = SECT.objects.filter(FCCODE=request.user.section_id.code).values()
        ordBook = BOOK.objects.filter(FCREFTYPE=prefixRef, FCCODE=bookGroup).values()
        
        if prefixRef == "PO":
            obj = PDSHeader.objects.get(id=id)
            fccode = obj.pds_date.strftime("%Y%m%d")[3:6]
            ordRnd = OrderH.objects.filter(FCCODE__gte=fccode).count() + 1
            fccodeNo = f"{fccode}{ordRnd:05d}"
            prNo = f"{str(ordBook[0]['FCPREFIX']).strip()}{fccodeNo}"### PR TEST REFNO
            msg = f"message=เรียนแผนก PU\nขณะนี้ทางแผนก Planning ได้ทำการเปิดเอกสาร{str(ordBook[0]['FCNAME']).strip()} เลขที่ {prNo} เรียบร้อยแล้วคะ"
            ### Get Supplier Information
            supplier = COOR.objects.filter(FCCODE=obj.forecast_id.supplier_id.code).values()
            ordH = None
            if obj.ref_formula_id is None:
                ordH = OrderH(
                    FCSKID=nanoid.generate(size=8),
                    FCREFTYPE=prefixRef,
                    FCDEPT=dept[0]['FCSKID'],
                    FCSECT=sect[0]['FCSKID'],
                    FCBOOK=ordBook[0]['FCSKID'],
                    FCCREATEBY=emp[0]['FCSKID'],
                    FCAPPROVEB=emp[0]['FCSKID'],
                    FCCODE=fccodeNo,
                    FCREFNO=prNo,
                    FCCOOR=supplier[0]['FCSKID'],
                    FDDATE=obj.pds_date,
                    FDDUEDATE=obj.pds_date,
                    FNAMT=obj.qty,
                )
                obj.ref_formula_id = ordH.FCSKID
                
            else:
                ordH = OrderH.objects.get(FCSKID=obj.ref_formula_id)
                ordH.FCREFTYPE=prefixRef
                ordH.FCDEPT=dept[0]['FCSKID']
                ordH.FCSECT=sect[0]['FCSKID']
                ordH.FCBOOK=ordBook[0]['FCSKID']
                ordH.FCCREATEBY=emp[0]['FCSKID']
                ordH.FCAPPROVEB=emp[0]['FCSKID']
                ordH.FCCOOR=supplier[0]['FCSKID']
                ordH.FDDATE=obj.pds_date
                ordH.FDDUEDATE=obj.pds_date
                ordH.FNAMT=obj.qty
                pass
            
            ordH.save()
            
            ordDetail = PDSDetail.objects.filter(pds_header_id=obj).all()
            seq = 1
            qty = 0
            summary_price = 0
            for i in ordDetail:
                ordI = None
                ordProd = PROD.objects.filter(FCCODE=i.forecast_detail_id.product_id.code,FCTYPE=i.forecast_detail_id.product_id.prod_type_id.code).values()
                unitObj = UM.objects.filter(FCCODE=i.forecast_detail_id.product_id.unit_id.code).values()
                try:
                    ordI = OrderI.objects.get(FCSKID=i.ref_formula_id)
                    ordI.FCCOOR=supplier[0]['FCSKID']
                    ordI.FCDEPT=dept[0]['FCSKID']
                    ordI.FCORDERH=ordH.FCSKID
                    ordI.FCPROD=ordProd[0]["FCSKID"]
                    ordI.FCPRODTYPE=ordProd[0]["FCTYPE"]
                    ordI.FCREFTYPE=prefixRef
                    ordI.FCSECT=sect[0]['FCSKID']
                    ordI.FCSEQ=f"{seq:03d}"
                    ordI.FCSTUM=unitObj[0]["FCSKID"]
                    ordI.FCUM=unitObj[0]["FCSKID"]
                    ordI.FCUMSTD=unitObj[0]["FCSKID"]
                    ordI.FDDATE=obj.pds_date
                    ordI.FNQTY=i.qty
                    ordI.FMREMARK=i.remark
                    #### Update Nagative to Positive
                    olderQty = int(ordI.FNBACKQTY)
                    ordI.FNBACKQTY=abs(int(i.qty)-olderQty)
                    ######
                    ordI.FNPRICE=ordProd[0]['FNPRICE']
                    ordI.FNPRICEKE=ordProd[0]['FNPRICE']
                    ordI.FCSHOWCOMP=""
                        
                except OrderI.DoesNotExist as e:
                    ordI = OrderI(
                        FCSKID=nanoid.generate(size=8),
                        FCCOOR=supplier[0]['FCSKID'],
                        FCDEPT=dept[0]['FCSKID'],
                        FCORDERH=ordH.FCSKID,
                        FCPROD=ordProd[0]["FCSKID"],
                        FCPRODTYPE=ordProd[0]["FCTYPE"],
                        FCREFTYPE=prefixRef,
                        FCSECT=sect[0]['FCSKID'],
                        FCSEQ=f"{seq:03d}",
                        FCSTUM=unitObj[0]["FCSKID"],
                        FCUM=unitObj[0]["FCSKID"],
                        FCUMSTD=unitObj[0]["FCSKID"],
                        FDDATE=obj.pds_date,
                        FNQTY=i.qty,
                        FMREMARK=i.remark,
                        FNBACKQTY=i.qty,
                        FNPRICE=ordProd[0]['FNPRICE'],
                        FNPRICEKE=ordProd[0]['FNPRICE'],
                        FCSHOWCOMP="",
                    )
                    pass
                
                ordI.save()
                
                ### Create Notecut
                orderPRID = obj.forecast_id.ref_formula_id
                orderPRDetailID = i.forecast_detail_id.ref_formula_id
                
                
                orderPOID = ordH.FCSKID
                orderPODetailID = ordI.FCSKID
                
                ### Create Notecut
                noteCut = NoteCut(
                        FCAPPNAME="",
                        FCSKID=nanoid.generate(size=8),
                        FCCHILDH=orderPRID,
                        FCCHILDI=orderPRDetailID,
                        FCMASTERH=orderPOID,
                        FCMASTERI=orderPODetailID,
                        FNQTY=i.qty,
                        FNUMQTY=i.qty,
                        FCCORRECTB=emp[0]["FCSKID"],
                        FCCREATEBY=emp[0]["FCSKID"],
                        FCCREATETY="",
                        FCCUACC="",
                        FCDATAIMP="",
                        FCORGCODE="",
                        FCSELTAG="",
                        FCSRCUPD="",
                        FCU1ACC="",
                        FCUDATE="",
                        FCUTIME="",
                    )
                noteCut.save()
                # Update Status Order Details
                i.ref_formula_id = ordI.FCSKID
                i.request_status = "1"
                i.save()
            
            obj.ref_formula_id = ordH.FCSKID
            obj.pds_status = "1"
            obj.save()
            requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
        else:
            obj = Forecast.objects.get(id=id)
            ### Create PDSHeader
            pdsHead = None
            pdsCount = PDSHeader.objects.filter(pds_date=dte).count() + 1
            pds_no = f"PDS{str(dte.strftime('%Y%m'))[3:]}{pdsCount:04d}"
            try:
                pdsHead = PDSHeader.objects.get(forecast_id=obj)
                pdsHead.pds_date = datetime.now()
                pdsHead.pds_no = pds_no
                pdsHead.item = 0
                pdsHead.qty = 0
                pdsHead.summary_price = 0
                pdsHead.is_active = True
            except PDSHeader.DoesNotExist:
                pdsHead = PDSHeader(
                    forecast_id = obj,
                    pds_date = datetime.now(),
                    pds_no = pds_no,
                    item = 0,
                    qty = 0,
                    summary_price = 0,
                    remark = "-",
                    is_active = True,
                )
                pass
            
            pdsHead.save()
            ### End PDSHeader
            
            supplier = COOR.objects.filter(FCCODE=obj.supplier_id.code).values()
            if obj.ref_formula_id is None:
                ### Create PR to Formula
                # #### Create Formula OrderH
                fccode = obj.forecast_date.strftime("%Y%m%d")[3:6]
                ordRnd = OrderH.objects.filter(FCCODE__gte=fccode).count() + 1
                fccodeNo = f"{fccode}{ordRnd:05d}"
                prNo = f"{str(ordBook[0]['FCPREFIX']).strip()}{fccodeNo}"### PR TEST REFNO
                msg = f"message=เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร {prNo} เรียบร้อยแล้วคะ"
                ordH = OrderH(
                    FCSKID=nanoid.generate(size=8),
                    FCREFTYPE=prefixRef,
                    FCDEPT=dept[0]['FCSKID'],
                    FCSECT=sect[0]['FCSKID'],
                    FCBOOK=ordBook[0]['FCSKID'],
                    FCCREATEBY=emp[0]['FCSKID'],
                    FCAPPROVEB=emp[0]['FCSKID'],
                    FCCODE=fccodeNo,
                    FCREFNO=prNo,
                    FCCOOR=supplier[0]['FCSKID'],
                    FDDATE=obj.forecast_date,
                    FDDUEDATE=obj.forecast_date,
                    FNAMT=obj.forecast_qty,
                )
                ordH.save()
                obj.ref_formula_id = ordH.FCSKID
                
            else:
                ordH = OrderH.objects.get(FCSKID=obj.ref_formula_id)
                ordH.FCREFTYPE=prefixRef
                ordH.FCDEPT=dept[0]['FCSKID']
                ordH.FCSECT=sect[0]['FCSKID']
                ordH.FCBOOK=ordBook[0]['FCSKID']
                ordH.FCCREATEBY=emp[0]['FCSKID']
                ordH.FCAPPROVEB=emp[0]['FCSKID']
                ordH.FCCOOR=supplier[0]['FCSKID']
                ordH.FDDATE=obj.forecast_date
                ordH.FDDUEDATE=obj.forecast_date
                ordH.FNAMT=obj.forecast_qty
                ordH.save()
                msg = f"message=เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร {ordH.FCREFNO} เรียบร้อยแล้วคะ"
                pass
            
            # ### OrderI
            # # Get Order Details
            ordDetail = ForecastDetail.objects.filter(forecast_id=obj).all()
            seq = 1
            qty = 0
            summary_price = 0
            for i in ordDetail:
                ### Create OrderI Formula
                try:
                    ordProd = PROD.objects.filter(FCCODE=i.product_id.code,FCTYPE=i.product_id.prod_type_id.code).values()
                    unitObj = UM.objects.filter(FCCODE=i.product_id.unit_id.code).values()
                    
                    ### Create PDS Detail
                    pdsDetail = None
                    try:
                        pdsDetail = PDSDetail.objects.get(pds_header_id=pdsHead,forecast_detail_id=i)
                        pdsDetail.seq = seq
                        pdsDetail.qty = i.request_qty
                        pdsDetail.price = ordProd[0]['FNPRICE']
                        pdsDetail.remark = i.remark
                        pdsDetail.is_active = True
                        
                    except PDSDetail.DoesNotExist:
                        pdsDetail = PDSDetail(
                            pds_header_id = pdsHead,
                            forecast_detail_id = i,
                            seq = seq,
                            qty = i.request_qty,
                            price = ordProd[0]['FNPRICE'],
                            remark = i.remark,
                            is_active = True,
                        )
                        pass
                    pdsDetail.save()
                    ### End PDS Detail
                
                    ordI = None
                    try:
                        ordI = OrderI.objects.get(FCSKID=i.ref_formula_id)
                        ordI.FCCOOR=supplier[0]['FCSKID']
                        ordI.FCDEPT=dept[0]['FCSKID']
                        ordI.FCORDERH=ordH.FCSKID
                        ordI.FCPROD=ordProd[0]["FCSKID"]
                        ordI.FCPRODTYPE=ordProd[0]["FCTYPE"]
                        ordI.FCREFTYPE=prefixRef
                        ordI.FCSECT=sect[0]['FCSKID']
                        ordI.FCSEQ=f"{seq:03d}"
                        ordI.FCSTUM=unitObj[0]["FCSKID"]
                        ordI.FCUM=unitObj[0]["FCSKID"]
                        ordI.FCUMSTD=unitObj[0]["FCSKID"]
                        ordI.FDDATE=obj.forecast_date
                        ordI.FNQTY=i.request_qty
                        ordI.FMREMARK=i.remark
                        #### Update Nagative to Positive
                        olderQty = int(ordI.FNBACKQTY)
                        ordI.FNBACKQTY=abs(int(i.request_qty)-olderQty)
                        ######
                        ordI.FNPRICE=ordProd[0]['FNPRICE']
                        ordI.FNPRICEKE=ordProd[0]['FNPRICE']
                        ordI.FCSHOWCOMP=""
                            
                    except OrderI.DoesNotExist as e:
                        ordI = OrderI(
                            FCSKID=nanoid.generate(size=8),
                            FCCOOR=supplier[0]['FCSKID'],
                            FCDEPT=dept[0]['FCSKID'],
                            FCORDERH=ordH.FCSKID,
                            FCPROD=ordProd[0]["FCSKID"],
                            FCPRODTYPE=ordProd[0]["FCTYPE"],
                            FCREFTYPE=prefixRef,
                            FCSECT=sect[0]['FCSKID'],
                            FCSEQ=f"{seq:03d}",
                            FCSTUM=unitObj[0]["FCSKID"],
                            FCUM=unitObj[0]["FCSKID"],
                            FCUMSTD=unitObj[0]["FCSKID"],
                            FDDATE=obj.forecast_date,
                            FNQTY=i.request_qty,
                            FMREMARK=i.remark,
                            FNBACKQTY=i.request_qty,
                            FNPRICE=ordProd[0]['FNPRICE'],
                            FNPRICEKE=ordProd[0]['FNPRICE'],
                            FCSHOWCOMP="",
                        )
                        pass
                    
                    ordI.save()
                    # Update Status Order Details
                    i.ref_formula_id = ordI.FCSKID
                    i.request_status = "1"
                    
                except Exception as e:
                    messages.error(request, str(e))
                    ordH.delete()
                    return
                # Summary Seq/Qty
                seq += 1
                qty += i.request_qty
                summary_price += float(ordProd[0]['FNPRICE'])
                i.save()
                
            pdsHead.item = (seq - 1)
            pdsHead.qty = qty
            pdsHead.summary_price = summary_price
            pdsHead.save()
                
            obj.forecast_no = ordH.FCREFNO
            obj.forecast_status = "1"
            obj.forecast_qty = qty
            obj.forecast_item = (seq - 1)
            obj.save()
            
            ### Message Notification
            msg = f"message=เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร {obj.forecast_no} เรียบร้อยแล้วคะ"
            requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
            # messages.success(request, f"บันทึกข้อมูลเรียบร้อยแล้ว")
        
    except Exception as ex:
        messages.error(request, str(ex))
        # pass
    
    return True