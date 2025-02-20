# Generated by Django 5.1.4 on 2025-02-20 04:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchlist_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='update',
            new_name='updated',
        ),
        migrations.AlterField(
            model_name='review',
            name='description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='streamplatform',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='watchlist',
            name='avg_rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=3),
        ),
    ]
