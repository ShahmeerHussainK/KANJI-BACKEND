# Generated by Django 2.0.6 on 2018-12-08 20:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApi', '0045_auto_20181208_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionresponse',
            name='answer_date_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
