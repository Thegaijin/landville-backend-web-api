# Generated by Django 2.2.1 on 2019-07-24 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0008_auto_20190723_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='savings',
            name='balance',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount_payed',
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=14),
        ),
    ]
