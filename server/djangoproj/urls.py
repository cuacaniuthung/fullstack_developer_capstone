"""djangoproj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # Chỉ giữ một lần include djangoapp.urls
    path('djangoapp/', include('djangoapp.urls')),

    # Định nghĩa các route trả về HTML/React
    path('', TemplateView.as_view(template_name="Home.html")),
    path('about/', TemplateView.as_view(template_name="About.html")),
    path('contact/', TemplateView.as_view(template_name="Contact.html")),
    path('login/', TemplateView.as_view(template_name="index.html")),
    path('register/', TemplateView.as_view(template_name="index.html")),
    path('dealers/', TemplateView.as_view(template_name="index.html")),

    # Đường dẫn cho Dealer Detail và Review (chuyển hướng sang index.html để React xử lý)
    # Sửa lỗi E225: thêm khoảng trắng quanh dấu phẩy và toán tử
    path(
        'dealer/<int:dealer_id>',
        TemplateView.as_view(template_name="index.html")
    ),
    path(
        'postreview/<int:dealer_id>',
        TemplateView.as_view(template_name="index.html")
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
