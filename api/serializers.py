import random
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import (ValidationError,
                                       PermissionDenied,
                                       AuthenticationFailed)

from .models import User, Category, Genre, Title, Review, Comment


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def generate_code():
    random.seed()
    return str(random.randint(10000000, 99999999))


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username")

    def validate(self, data):
        confirmation_code = generate_code()
        data["confirmation_code"] = confirmation_code
        return data


class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = (
            "email",
            "confirmation_code",
        )

    def validate(self, data):
        email = data["email"]
        confirmation_code = data["confirmation_code"]
        profile = get_object_or_404(User, email=email)
        if profile.confirmation_code != confirmation_code:
            raise ValidationError("Неправильный confirmation code")
        else:
            token = get_tokens_for_user(profile)
            data["token"] = token
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("first_name", "last_name", "username",
                  "description", "email", "role")
        model = User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class CustomSlugRelatedField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return {"name": value.name, "slug": value.slug}


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()
    category = CustomSlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )
    genre = CustomSlugRelatedField(
        queryset=Genre.objects.all(), slug_field="slug", many=True
    )

    class Meta:
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    title = serializers

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review

    def create(self, validated_data):
        author = self.context["request"].user
        request = self.context.get("request")
        title_id = request.parser_context["kwargs"]["title_id"]
        method = request.method
        get_object_or_404(Title, pk=title_id)
        review = Review.objects.filter(title_id=title_id, author=author)
        if method == "POST" and review:
            raise ValidationError("Только один отзыв")
        return Review.objects.create(**validated_data)

    def update(self, instance, validated_data):
        print(instance)
        author = self.context["request"].user
        if not author.is_authenticated:
            raise AuthenticationFailed()
        if instance.author != author:
            raise PermissionDenied()
        instance.text = validated_data.get("text", instance.text)
        instance.score = validated_data.get("score", instance.score)
        instance.pub_date = validated_data.get("pub_date", instance.pub_date)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
