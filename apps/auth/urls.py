from django.urls import path

from apps.auth.views import ResendVerificationView, SecureLoginView, VerifyAccountView

urlpatterns = [
    path("login/", SecureLoginView.as_view(), name="login"),
    path("verify-account/", VerifyAccountView.as_view(), name="verify-account"),
    path(
        "verify-account/resend/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),
]
