# Generated by Django 3.0.7 on 2020-07-02 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='items_json',
            field=models.TextField(),
        ),
    ]