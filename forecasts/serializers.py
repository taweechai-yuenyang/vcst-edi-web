from rest_framework import serializers

from forecasts.models import FileForecast, OpenPDS, OpenPDSDetail, PDSErrorLogs



class FileForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileForecast
        fields = (
            "edi_file",
            "edi_filename",
            "document_no",
            "upload_date",
            "upload_on_month",
            "upload_seq",
            "description",
            "upload_by_id",
            "is_generated",
            "is_active",
            "created_at",
            "updated_at",
        )

class OpenPDSSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenPDS
        fields = (
            "edi_file_id",
            "supplier_id",
            "section_id",
            "book_id",
            "pds_no",
            "pds_date",
            "pds_on_month",
            "pds_item",
            "pds_qty",
            "pds_price",
            "remark",
            "pds_by_id",
            "pds_status",
            "supplier_download_count",
            "ref_formula_id",
            "is_po",
            "is_sync",
            "created_at",
            "updated_at",
        )

class OpenPDSDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenPDSDetail
        fields = (
            "pds_id",
            "product_id",
            "seq",
            "request_qty",
            "balance_qty",
            "price",
            "request_by_id",
            "request_status",
            "import_model_by_user",
            "remark",
            "is_selected",
            "is_sync",
            "ref_formula_id",
            "created_at",
            "updated_at",
        )

class PDSErrorLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDSErrorLogs
        fields = (
            "file_name",
            "row_num",
            "item",
            "part_code",
            "part_no",
            "part_name",
            "supplier",
            "model",
            "rev_0",
            "rev_1",
            "rev_2",
            "rev_3",
            "rev_4",
            "rev_5",
            "rev_6",
            "rev_7",
            "remark",
            "is_error",
            "is_success",
            "created_at",
            "updated_at",
        )
