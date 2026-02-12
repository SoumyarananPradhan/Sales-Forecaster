from django.urls import path
from .views import UploadAnalysisView, HistoryView, DownloadPDFView

urlpatterns = [
    path('analyze/', UploadAnalysisView.as_view(), name='analyze-sales'),
    path('history/', HistoryView.as_view(), name='history'),
    path("history/<str:report_id>/", HistoryView.as_view()),
    path("download/<str:report_id>/", DownloadPDFView.as_view()),
]