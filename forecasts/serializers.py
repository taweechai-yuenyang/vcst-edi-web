from rest_framework import serializers

from forecasts.models import FileForecast, Forecast, ForecastDetail, ForecastErrorLogs

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

class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = (
            "edi_file_id",
            "supplier_id",
            "section_id",
            "book_id",
            "forecast_no",
            "forecast_date",
            "forecast_on_month",
            "forecast_item",
            "forecast_qty",
            "forecast_price",
            "remark",
            "forecast_by_id",
            "forecast_status",
            "supplier_download_count",
            "ref_formula_id",
            "is_po",
            "is_sync",
            "created_at",
            "updated_at",
        )

class ForecastDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastDetail
        fields = (
            "forecast_id",
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

class ForecastErrorLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastErrorLogs
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