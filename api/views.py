from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse

from .utils import get_db_handle
from bson import ObjectId

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import io
import base64
import datetime
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


# ===============================
# UPLOAD + ANALYZE
# ===============================
class UploadAnalysisView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        file_obj = request.FILES.get("csv_file")

        if not file_obj:
            return Response({"error": "No CSV file uploaded"}, status=400)

        try:
            try:
                df = pd.read_csv(file_obj, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_obj, encoding="latin1")

            df.dropna(how="all", inplace=True)
            df.columns = df.columns.str.strip()

            if df.empty:
                return Response({"error": "CSV is empty"}, status=400)

            numeric_cols = []

            for col in df.columns:
                cleaned = (
                    df[col]
                    .astype(str)
                    .str.replace(r"[₹$€,]", "", regex=True)
                    .str.strip()
                )

                nums = pd.to_numeric(cleaned, errors="coerce")
                count = nums.notna().sum()

                if count > len(df) * 0.5:
                    numeric_cols.append((col, count))

            if not numeric_cols:
                return Response(
                    {"error": "No numeric column found"},
                    status=400
                )

            numeric_cols.sort(key=lambda x: x[1], reverse=True)
            value_col = numeric_cols[0][0]

            df[value_col] = (
                df[value_col]
                .astype(str)
                .str.replace(r"[₹$€,]", "", regex=True)
            )

            df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

            date_col = None
            for col in df.columns:
                if "date" in col.lower() or "time" in col.lower():
                    date_col = col
                    break

            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                df = df.sort_values(date_col)

            total = df[value_col].sum()
            avg = df[value_col].mean()

            if pd.isna(total): total = 0.0
            if pd.isna(avg): avg = 0.0

            total = float(total)
            avg = float(avg)

            plt.figure(figsize=(10, 5))

            if date_col:
                plt.plot(df[date_col], df[value_col], marker="o")
                plt.xlabel(date_col)
            else:
                plt.plot(df[value_col])
                plt.xlabel("Records")

            plt.title(f"Trend ({value_col})")
            plt.ylabel("Value")
            plt.grid(True)
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)

            chart_base64 = base64.b64encode(buffer.read()).decode("utf-8")
            plt.close()

            db, collection = get_db_handle()

            report = {
                "filename": file_obj.name,
                "upload_date": datetime.datetime.now(),
                "total_sales": total,
                "average_sales": avg,
                "chart_image": chart_base64,
            }

            collection.insert_one(report)

            return Response(
                {
                    "message": "Success",
                    "total": total,
                    "average": avg,
                    "chart": chart_base64,
                },
                status=201
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)


# ===============================
# HISTORY + DELETE
# ===============================
class HistoryView(APIView):

    def get(self, request):

        db, collection = get_db_handle()

        cursor = (
            collection
            .find({}, {"chart_image": 0})
            .sort("upload_date", -1)
            .limit(5)
        )

        history = []

        for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]

            doc["upload_date"] = doc["upload_date"].strftime(
                "%Y-%m-%d %H:%M"
            )

            history.append(doc)

        return Response(history, status=200)

    # DELETE FEATURE
    def delete(self, request, report_id):

        db, collection = get_db_handle()

        result = collection.delete_one(
            {"_id": ObjectId(report_id)}
        )

        if result.deleted_count == 1:
            return Response({"message": "Deleted"}, status=200)

        return Response({"error": "Not found"}, status=404)


# ===============================
# DOWNLOAD PDF
# ===============================
class DownloadPDFView(APIView):

    def get(self, request, report_id):

        db, collection = get_db_handle()

        report = collection.find_one({"_id": ObjectId(report_id)})

        if not report:
            return Response({"error": "Not found"}, status=404)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="report.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Sales Report", styles["Title"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Total: ${report['total_sales']}", styles["Heading2"]))
        elements.append(Paragraph(f"Average: ${report['average_sales']}", styles["Heading2"]))
        elements.append(Spacer(1, 20))

        img_data = base64.b64decode(report["chart_image"])
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp.write(img_data)
        temp.close()

        elements.append(Image(temp.name, width=400, height=250))
        doc.build(elements)

        return response








# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser

# from django.http import HttpResponse

# from .utils import get_db_handle

# from bson import ObjectId

# import pandas as pd
# import matplotlib

# matplotlib.use("Agg")
# import matplotlib.pyplot as plt

# import io
# import base64
# import datetime
# import tempfile

# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch


# # ===============================
# # UPLOAD + ANALYZE
# # ===============================
# class UploadAnalysisView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request):

#         file_obj = request.FILES.get("csv_file")

#         if not file_obj:
#             return Response({"error": "No CSV file uploaded"}, status=400)

#         try:

#             # ---------------- READ CSV ----------------
#             try:
#                 df = pd.read_csv(file_obj, encoding="utf-8")
#             except UnicodeDecodeError:
#                 df = pd.read_csv(file_obj, encoding="latin1")

#             df.dropna(how="all", inplace=True)
#             df.columns = df.columns.str.strip()

#             if df.empty:
#                 return Response({"error": "CSV is empty"}, status=400)

#             # ---------------- FIND NUMERIC COLUMN ----------------
#             numeric_cols = []

#             for col in df.columns:

#                 cleaned = (
#                     df[col]
#                     .astype(str)
#                     .str.replace(r"[₹$€,]", "", regex=True)
#                     .str.strip()
#                 )

#                 nums = pd.to_numeric(cleaned, errors="coerce")

#                 count = nums.notna().sum()

#                 if count > len(df) * 0.5:
#                     numeric_cols.append((col, count))

#             if not numeric_cols:
#                 return Response(
#                     {"error": "No numeric column found"},
#                     status=400
#                 )

#             numeric_cols.sort(key=lambda x: x[1], reverse=True)

#             value_col = numeric_cols[0][0]

#             df[value_col] = (
#                 df[value_col]
#                 .astype(str)
#                 .str.replace(r"[₹$€,]", "", regex=True)
#             )

#             df[value_col] = pd.to_numeric(
#                 df[value_col],
#                 errors="coerce"
#             )

#             # ---------------- FIND DATE COLUMN ----------------
#             date_col = None

#             for col in df.columns:
#                 if "date" in col.lower() or "time" in col.lower():
#                     date_col = col
#                     break

#             if date_col:
#                 df[date_col] = pd.to_datetime(
#                     df[date_col],
#                     errors="coerce"
#                 )

#                 df = df.sort_values(date_col)

#             # ---------------- CALCULATE ----------------
#             total = df[value_col].sum()
#             avg = df[value_col].mean()

#             if pd.isna(total):
#                 total = 0.0

#             if pd.isna(avg):
#                 avg = 0.0

#             total = float(total)
#             avg = float(avg)

#             # ---------------- CREATE CHART ----------------
#             plt.figure(figsize=(10, 5))

#             if date_col:
#                 plt.plot(df[date_col], df[value_col], marker="o")
#                 plt.xlabel(date_col)
#             else:
#                 plt.plot(df[value_col])
#                 plt.xlabel("Records")

#             plt.title(f"Trend ({value_col})")
#             plt.ylabel("Value")
#             plt.grid(True)
#             plt.tight_layout()

#             buffer = io.BytesIO()
#             plt.savefig(buffer, format="png")
#             buffer.seek(0)

#             chart_base64 = base64.b64encode(
#                 buffer.read()
#             ).decode("utf-8")

#             plt.close()

#             # ---------------- SAVE TO DB ----------------
#             db, collection = get_db_handle()

#             report = {
#                 "filename": file_obj.name,
#                 "upload_date": datetime.datetime.now(),
#                 "value_column": value_col,
#                 "date_column": date_col,
#                 "total_sales": total,
#                 "average_sales": avg,
#                 "chart_image": chart_base64,
#             }

#             collection.insert_one(report)

#             # ---------------- RESPONSE ----------------
#             return Response(
#                 {
#                     "message": "Success",
#                     "used_column": value_col,
#                     "date_column": date_col,
#                     "total": total,
#                     "average": avg,
#                     "chart": chart_base64,
#                 },
#                 status=201
#             )

#         except Exception as e:

#             print("UPLOAD ERROR:", e)

#             return Response({"error": str(e)}, status=400)


# # ===============================
# # HISTORY
# # ===============================
# class HistoryView(APIView):

#     def get(self, request):

#         try:

#             db, collection = get_db_handle()

#             cursor = (
#                 collection
#                 .find({}, {"chart_image": 0})
#                 .sort("upload_date", -1)
#                 .limit(5)
#             )

#             history = []

#             for doc in cursor:

#                 doc["id"] = str(doc["_id"])
#                 del doc["_id"]

#                 if "upload_date" in doc:
#                     doc["upload_date"] = doc[
#                         "upload_date"
#                     ].strftime("%Y-%m-%d %H:%M")

#                 history.append(doc)

#             return Response(history, status=200)

#         except Exception as e:

#             print("HISTORY ERROR:", e)

#             return Response({"error": str(e)}, status=500)


# # ===============================
# # DOWNLOAD PDF
# # ===============================
# class DownloadPDFView(APIView):

#     def get(self, request, report_id):

#         try:

#             db, collection = get_db_handle()

#             report = collection.find_one(
#                 {"_id": ObjectId(report_id)}
#             )

#             if not report:
#                 return Response(
#                     {"error": "Report not found"},
#                     status=404
#                 )

#             response = HttpResponse(
#                 content_type="application/pdf"
#             )

#             response[
#                 "Content-Disposition"
#             ] = 'attachment; filename="report.pdf"'

#             doc = SimpleDocTemplate(
#                 response,
#                 pagesize=A4,
#                 rightMargin=40,
#                 leftMargin=40,
#                 topMargin=40,
#                 bottomMargin=40,
#             )

#             styles = getSampleStyleSheet()
#             elements = []

#             # Title
#             elements.append(
#                 Paragraph("Sales Analysis Report", styles["Title"])
#             )

#             elements.append(Spacer(1, 20))

#             # Info
#             elements.append(
#                 Paragraph(f"File: {report['filename']}", styles["Normal"])
#             )

#             elements.append(
#                 Paragraph(
#                     f"Date: {report['upload_date'].strftime('%Y-%m-%d %H:%M')}",
#                     styles["Normal"],
#                 )
#             )

#             elements.append(Spacer(1, 10))

#             elements.append(
#                 Paragraph(
#                     f"Total: ${report['total_sales']}",
#                     styles["Heading2"],
#                 )
#             )

#             elements.append(
#                 Paragraph(
#                     f"Average: ${report['average_sales']}",
#                     styles["Heading2"],
#                 )
#             )

#             elements.append(Spacer(1, 20))

#             # Chart Image
#             img_data = base64.b64decode(report["chart_image"])

#             temp = tempfile.NamedTemporaryFile(
#                 delete=False,
#                 suffix=".png"
#             )

#             temp.write(img_data)
#             temp.close()

#             elements.append(
#                 Image(
#                     temp.name,
#                     width=5 * inch,
#                     height=3 * inch,
#                 )
#             )

#             elements.append(Spacer(1, 30))

#             doc.build(elements)

#             return response

#         except Exception as e:

#             print("PDF ERROR:", e)

#             return Response({"error": str(e)}, status=500)
