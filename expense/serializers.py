from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Expense, Category, Item, Brand, Shop

# --- Nested serializers for display ---
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

# --- Main Expense serializer ---
class ExpenseSerializer(serializers.ModelSerializer):
    # Read-only nested representations (for GET)
    item = ItemSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    who_spent = UserSerializer(read_only=True)

    # Write-only fields (for POST/PUT/PATCH)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(), source='item', write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), source='brand', write_only=True, allow_null=True, required=False
    )
    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), source='shop', write_only=True, allow_null=True, required=False
    )
    who_spent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='who_spent', write_only=True
    )

    class Meta:
        model = Expense
        fields = [
            'id',
            'item', 'item_id',
            'category', 'category_id',
            'brand', 'brand_id',
            'shop', 'shop_id',
            'who_spent', 'who_spent_id',
            'date_of_purchase',
            'quantity',
            'unit',
            'price',
            'rate',
            'remarks',
        ]
