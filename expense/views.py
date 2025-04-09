from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Expense, Category, Item, Brand, Shop
from django.contrib.auth.models import User
from .serializers import ExpenseSerializer, CategorySerializer, ItemSerializer, BrandSerializer, ShopSerializer
import csv
import io

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date_of_purchase')
    serializer_class = ExpenseSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

class ExpenseCSVUploadView(APIView):
    def post(self, request, *args, **kwargs):
        print("\n🟡 request.FILES:", request.FILES)
        print("🟡 request.FILES keys:", list(request.FILES.keys()))

        file = request.FILES.get("file")
        print("🟡 file:", file)
        print("🟡 file name:", getattr(file, "name", None))

        if not file or not file.name.endswith(".csv"):
            return Response({
                "error": "Upload a valid CSV file.",
                "details": {
                    "file_received": str(file),
                    "file_name": getattr(file, "name", None),
                    "files_keys": list(request.FILES.keys())
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(data))
            headers = reader.fieldnames
            print("🟢 CSV Headers:", headers)

            required_headers = ["Date", "Item", "Category", "Brand", "Shop", "Qty", "Unit", "Price", "Remarks", "Who"]
            missing_headers = [h for h in required_headers if h not in headers]
            if missing_headers:
                return Response({"error": f"Missing required CSV headers: {missing_headers}"}, status=400)

            rows = list(reader)
            expenses_to_create = []
            errors = []

            for i, row in enumerate(rows, start=1):
                print(f"\n🔹 Row {i} content:", row)

                item_name = row.get("Item", "").strip()
                category_name = row.get("Category", "").strip()
                user_name = row.get("Who", "").strip()

                if not item_name or not category_name or not user_name:
                    errors.append(f"Row {i}: 'Item', 'Category', and 'Who' are required.")
                    continue

                try:
                    user = User.objects.get(username=user_name)
                except User.DoesNotExist:
                    errors.append(f"Row {i}: User '{user_name}' does not exist.")
                    continue

                brand_name = row.get("Brand", "").strip() or "N.A"
                shop_name = row.get("Shop", "").strip() or "N.A"
                remarks = row.get("Remarks", "").strip() or "N.A"

                required_fields = ["Date", "Qty", "Unit", "Price"]
                missing = [field for field in required_fields if not row.get(field)]
                if missing:
                    errors.append(f"Row {i}: Missing required fields: {missing}")
                    continue

                try:
                    item, _ = Item.objects.get_or_create(name=item_name)
                    category, _ = Category.objects.get_or_create(name=category_name)
                    brand, _ = Brand.objects.get_or_create(name=brand_name)
                    shop, _ = Shop.objects.get_or_create(name=shop_name)

                    serializer = ExpenseSerializer(data={
                        "item_id": item.id,
                        "category_id": category.id,
                        "brand_id": brand.id,
                        "shop_id": shop.id,
                        "who_spent_id": user.id,
                        "date_of_purchase": row["Date"],
                        "quantity": row["Qty"],
                        "unit": row["Unit"],
                        "price": row["Price"],
                        "remarks": remarks,
                    })

                    if serializer.is_valid():
                        expenses_to_create.append(serializer)
                    else:
                        errors.append(f"Row {i}: {serializer.errors}")
                        continue

                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")
                    continue

            if errors:
                return Response({"error": "CSV upload failed", "details": errors}, status=status.HTTP_400_BAD_REQUEST)

            for serializer in expenses_to_create:
                serializer.save()

            return Response({"message": f"{len(expenses_to_create)} expenses created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("🔴 CSV processing error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
