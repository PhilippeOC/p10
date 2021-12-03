# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
# from users.views import registration_view
from users.views import UserCreate

urlpatterns = [
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('', registration_view, name='signup'),
    path('', UserCreate.as_view(), name='signup'),
]
