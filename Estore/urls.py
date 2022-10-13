from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkOut, name='checkout'),

    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),

    path('login/', views.userLogin, name='login'),
    path('logout/', views.userLogout, name='logout'),
    path('register/', views.userRegister, name='register'),
]