from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing", views.view_listing, name="listing"),
    path("add_comment", views.add_comment, name="add_comment"),
    path("close_auction", views.close_auction, name="close_auction"),
    path("add_bid", views.add_bid, name="add_bid"),
    path("add_watch", views.add_watch, name="add_watch"),
    path("remove_watch", views.remove_watch, name="remove_watch"),
    path("watch_list", views.view_watch_list, name="watch_list"),
    path("my_list", views.view_my_list, name="my_list"),
]
