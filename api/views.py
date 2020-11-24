from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets, mixins, filters, permissions, generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import CustomFilterBackend
from .models import User, Category, Genre, Title, Review, Comment
from .serializers import (UserSerializer, SignUpSerializer,
                          SignInSerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer)
from .permissions import (IsAdminUser, IsAdminOrReadOnlyPermission,
                          IsAuthorOrAdminOrModerator)


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.confirmation_code = serializer.validated_data[
                "confirmation_code"
            ]
            serializer.email = serializer.validated_data["email"]
            serializer.save()
            send_mail(
                "Авторизация",
                f"confirmation_code = {serializer.confirmation_code} email = {serializer.email}", # noqa
                "mi@mi.mi",
                [f"{serializer.email}"],
                fail_silently=False,
            )
        return Response(serializer.data)


class SignInView(APIView):
    queryset = User.objects.all()
    serializer_class = SignInSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({"token": serializer.validated_data["token"]})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", ]
    lookup_field = "username"


class UserMeViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    lookup_field = None

    def get_queryset(self):
        queryset = User.objects.filter(email=self.request.user).all()
        return queryset

    def get_object(self):
        obj = self.get_queryset().get()
        return obj


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnlyPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", ]
    lookup_field = "slug"


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet,):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnlyPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", ]
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnlyPermission]
    filter_backends = [CustomFilterBackend]
    filterset_fields = ["category", "genre", "year", "name"]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrAdminOrModerator)
    pagination_class = PageNumberPagination

    def get_title(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title

    def get_queryset(self):
        queryset = Review.objects.filter(title=self.get_title())
        return queryset

    def update_rating(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        average_rating = Review.objects.filter(
            title=title).aggregate(Avg("score"))
        title.rating = round(average_rating["score__avg"], 1)
        title.save()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title_id=title_id)
        self.update_rating()

    def perform_update(self, serializer):
        serializer.save()
        self.update_rating()

    def perform_destroy(self, instance):
        instance.delete()
        self.update_rating()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,
                          IsAuthenticatedOrReadOnly)

    def get_review(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        return review

    def get_queryset(self):
        queryset = Comment.objects.filter(review=self.get_review()).all()
        return queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_id")
        get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review_id=review_id)
