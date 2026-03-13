from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    path("summary/", views.SummaryView.as_view(), name="analytics-summary"),
    path("by-user/", views.ByUserView.as_view(), name="analytics-by-user"),
    path("overdue/", views.OverdueView.as_view(), name="analytics-overdue"),
    path("schema/", SpectacularAPIView.as_view(), name="analytics-schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="analytics-schema"), name="analytics-docs"),
]
