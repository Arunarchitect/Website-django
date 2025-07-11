from django.db import models

class PromoCode(models.Model):
    code = models.CharField("Promo Code", max_length=50, unique=True)
    discount_percentage = models.DecimalField("Discount (%)", max_digits=5, decimal_places=2)  # e.g. 10.00 for 10%

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"

    class Meta:
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"


class Fee(models.Model):
    base_fee_per_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    consultant = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    promo_code = models.CharField(max_length=50, blank=True, null=True)  # Now a plain text field
    url = models.URLField(max_length=200, blank=True, null=True)  # ✅ new field

    def __str__(self):
        return f"Fee: ₹{self.base_fee_per_sqft} per sq.ft"

    class Meta:
        verbose_name = "Fee Entry"
        verbose_name_plural = "Fee Entries"
