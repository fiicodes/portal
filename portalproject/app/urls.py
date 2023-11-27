from django.urls import path
from .views import *


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', loginfunc, name='loginfunc'),
    path('toggle/',toggle_online,name='toggle_online'),
    path('logout/',user_logout,name='user_logout'),
    path('connected/',connected,name='connected'),
    path('connect/',connect_users,name='connect_users'),
    path('connect-establish/',connect_establish,name='connect-establish')








]