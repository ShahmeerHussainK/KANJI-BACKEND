# Generated by Django 2.0.6 on 2018-12-22 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApi', '0053_deletedquestion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deletedquestion',
            options={'verbose_name_plural': 'deleted Question'},
        ),
        migrations.AddField(
            model_name='questionlog',
            name='q_id',
            field=models.IntegerField(default=1),
        ),
    ]
