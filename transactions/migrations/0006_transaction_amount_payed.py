# Generated by Django 2.2.1 on 2019-07-16 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_deposit_references'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='amount_payed',
            field=models.DecimalField(
                decimal_places=3, default=0, max_digits=14),
        ),
    ]
