from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (SignUpView, SignInView,
                    UserViewSet, UserMeViewSet,
                    TitleViewSet, CategoryViewSet,
                    GenreViewSet, ReviewViewSet, CommentViewSet)


router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("categories", CategoryViewSet, basename="categories")
router.register("genres", GenreViewSet, basename="genres")
router.register("titles", TitleViewSet, basename="titles")
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename='reviews')
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet, basename='comments')


urlpatterns = [
    path('redoc/',
         TemplateView.as_view(template_name='redoc.html'), name='redoc'),
    path("auth/email/", SignUpView.as_view()),
    path("auth/token/", SignInView.as_view()),
    path("auth/token/refresh/",
         TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", UserMeViewSet.as_view({"get": "retrieve",
                                             "patch": "partial_update"})),
    path("", include(router.urls)),
]
