from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Expense, Category, Item, Brand, Shop

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

class ExpenseSerializer(serializers.ModelSerializer):
    # Read-only for nested display
    item = ItemSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    who_spent = UserSerializer(read_only=True)

    # Write-only input fields
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

    rate = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

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

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate(self, data):
        errors = {}

        if not data.get('item'):
            errors['item_id'] = 'Item must not be empty.'

        if not data.get('category'):
            errors['category_id'] = 'Category must not be empty.'

        if not data.get('who_spent'):
            errors['who_spent_id'] = 'who_spent must be a valid user.'

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        if not validated_data.get('remarks'):
            validated_data['remarks'] = "N.A"
        return super().create(validated_data)
