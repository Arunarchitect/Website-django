# fees/migrations/0003_convert_promo_to_text.py
from django.db import migrations, models
import django.db.models.deletion

def forward_migration(apps, schema_editor):
    """Convert ForeignKey relations to text codes"""
    Fee = apps.get_model('fees', 'Fee')
    PromoCode = apps.get_model('fees', 'PromoCode')
    
    # Process in batches if you have many records
    for fee in Fee.objects.filter(promo_code__isnull=False).select_related('promo_code'):
        fee.promo_code_temp = fee.promo_code.code  # Copy the actual code text
        fee.save()

def reverse_migration(apps, schema_editor):
    """Attempt to restore ForeignKey relations (when possible)"""
    Fee = apps.get_model('fees', 'Fee')
    PromoCode = apps.get_model('fees', 'PromoCode')
    
    for fee in Fee.objects.filter(promo_code_temp__isnull=False):
        try:
            # Try to find matching PromoCode
            promo = PromoCode.objects.get(code=fee.promo_code_temp)
            fee.promo_code = promo
            fee.save()
        except PromoCode.DoesNotExist:
            # If no matching code exists, set to null
            fee.promo_code = None
            fee.save()

class Migration(migrations.Migration):
    dependencies = [
        ('fees', '0002_alter_fee_options_alter_promocode_options_and_more'),
    ]

    operations = [
        # Step 1: Add temporary text field
        migrations.AddField(
            model_name='fee',
            name='promo_code_temp',
            field=models.CharField(
                max_length=50,
                null=True,
                blank=True,
                verbose_name='Temporary Promo Code Storage'
            ),
        ),
        
        # Step 2: Copy data from ForeignKey to text field
        migrations.RunPython(forward_migration, reverse_migration),
        
        # Step 3: Remove the old ForeignKey field
        migrations.RemoveField(
            model_name='fee',
            name='promo_code',
        ),
        
        # Step 4: Rename temporary field to final name
        migrations.RenameField(
            model_name='fee',
            old_name='promo_code_temp',
            new_name='promo_code',
        ),
        
        # Step 5: Update the field attributes to match your desired final state
        migrations.AlterField(
            model_name='fee',
            name='promo_code',
            field=models.CharField(
                max_length=50,
                null=True,
                blank=True,
                verbose_name='Promo Code'
            ),
        ),
    ]