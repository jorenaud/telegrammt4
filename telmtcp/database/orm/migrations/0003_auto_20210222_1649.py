# Generated by Django 2.2.6 on 2021-02-22 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orm', '0002_auto_20210222_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbl_promo_email',
            name='message',
            field=models.TextField(blank=True, max_length=10240),
        ),
    ]