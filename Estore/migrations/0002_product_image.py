# Generated by Django 4.1.2 on 2022-10-08 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Estore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='placeholder.png', null=True, upload_to='product_image/'),
        ),
    ]
