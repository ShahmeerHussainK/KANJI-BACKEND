# Generated by Django 2.0.6 on 2018-11-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApi', '0033_auto_20181129_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='days_to_delete_photos',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)], default=7),
        ),
    ]
