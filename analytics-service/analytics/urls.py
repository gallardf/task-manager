from django.urls import path
from . import views

urlpatterns = [
    path("summary/", views.SummaryView.as_view(), name="analytics-summary"),
    path("by-user/", views.ByUserView.as_view(), name="analytics-by-user"),
    path("overdue/", views.OverdueView.as_view(), name="analytics-overdue"),
]
