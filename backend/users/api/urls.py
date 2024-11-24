from django.urls import path
from users.api.views import DivisionalOfficeSignUpView,SubDivisionalOfficeSignUpView, CustomAuthToken,LogoutView,DivisionOnlyView,SubDivisionOnlyView
urlpatterns = [
    path('user-auth/signup/division/', DivisionalOfficeSignUpView.as_view(), name='div_register'),
    path('user-auth/signup/sub-division/', SubDivisionalOfficeSignUpView.as_view(), name='sub_div_register'),
    path('user-auth/login/', CustomAuthToken.as_view(), name='auth-token'),
    path('user-auth/logout/', LogoutView.as_view(), name='logout'),
    path('division/dashboard/', DivisionOnlyView.as_view(), name='division_dashboard'),
    path('sub-division/dashboard/', SubDivisionOnlyView.as_view(), name='sub_division_dashboard'),
    # Add other API paths here
]
 