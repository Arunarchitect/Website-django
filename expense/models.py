from django.db import models
from django.contrib.auth import get_user_model  # Use get_user_model() to support custom user model

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Shop(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    SI_UNITS = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Litre'),
        ('ml', 'Millilitre'),
        ('m', 'Metre'),
        ('cm', 'Centimetre'),
        ('pcs', 'Pieces'),
        ('sq.m', 'Square Metre'),
    ]

    who_spent = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)  # Now mandatory
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_purchase = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=SI_UNITS, default='pcs')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.quantity > 0:
            self.rate = self.price / self.quantity
        else:
            self.rate = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} by {self.who_spent.email} on {self.date_of_purchase}"