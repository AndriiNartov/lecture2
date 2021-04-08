from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create', views.create_listing, name='create'),
    path('watchlist', views.show_watchlist, name='watchlist'),
    path('categories', views.show_categories, name='categories'),
    path('category/<str:name>/', views.show_listings_in_category, name='category'),
    path('listing/<int:id>/', views.show_listing, name='listing'),
    path('close_auction/<int:id>/', views.close_auction, name='close_auction'),
    path('make_bid/<int:id>/', views.make_bid, name='make_bid'),
    path('leave_comment/<int:id>/', views.leave_comment, name='leave_comment'),
    path('add_to_watchlist/<int:id>', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/<int:id>', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('create_listing/', views.create_listing, name='create_listing'),
]
