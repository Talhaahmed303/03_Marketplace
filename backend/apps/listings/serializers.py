from rest_framework import serializers
from .models import Category, Listing
from apps.users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'icon')

class ListingSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Listing
        fields = (
            'id', 'seller', 'category', 'category_id', 'category_slug', 'category_name',
            'title', 'slug', 'description', 'price', 'condition', 'status',
            'image_url', 'location', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'seller', 'slug', 'created_at', 'updated_at')

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
