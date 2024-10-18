from django.urls import path,include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserRegistrationView,
    LoginView

)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


