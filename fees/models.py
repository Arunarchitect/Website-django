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
    base_fee_per_sqft = models.DecimalField("Base Fee per Sq.Ft", max_digits=10, decimal_places=2)
    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Associated Promo Code"
    )

    def __str__(self):
        return f"Fee: ₹{self.base_fee_per_sqft} per sq.ft"

    def get_discounted_fee(self, code):
        if self.promo_code and self.promo_code.code.lower() == code.lower():
            discount = (self.base_fee_per_sqft * self.promo_code.discount_percentage) / 100
            return self.base_fee_per_sqft - discount
        return self.base_fee_per_sqft

    class Meta:
        verbose_name = "Fee Entry"
        verbose_name_plural = "Fee Entries"
