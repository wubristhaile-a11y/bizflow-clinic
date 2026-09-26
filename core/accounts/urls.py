from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("post-login/", views.post_login, name="post_login"),
    path("logout/", views.logout_view, name="logout"),
]