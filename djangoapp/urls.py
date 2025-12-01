from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # path for registration (chưa có)

    # path for login (chỉ giữ 1 bản chuẩn)
    path(route='login', view=views.login_user, name='login'),
    # path for logout (chỉ giữ 1 bản chuẩn)
    path(route='logout', view=views.logout_request, name='logout'),

    # path for get cars view
    path(route='get_cars', view=views.get_cars, name='getcars'),

    # path for get dealers
    path(
        route='get_dealers',
        view=views.get_dealerships,
        name='get_dealers'
    ),
    # path for get dealers by state
    path(
        route='get_dealers/<str:state>',
        view=views.get_dealerships,
        name='get_dealers_by_state'
    ),
    # path for dealer details
    path(
        route='dealer/<int:dealer_id>',
        view=views.get_dealer_details,
        name='get_dealer_details'
    ),
    # path for get reviews by dealer id
    path(
        route='reviews/dealer/<int:dealer_id>',
        view=views.get_dealer_reviews,
        name='get_dealer_reviews'
    ),
    # path for adding a review
    path(
        route='add_review',
        view=views.add_review,
        name='add_review'
    ),
    # path for post review (chỉ dùng nếu bạn gọi trực tiếp views.post_review)
    path(
        route='postreview',
        view=views.post_review,
        name='post_review'
    ),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
