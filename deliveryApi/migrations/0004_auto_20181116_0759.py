# Generated by Django 2.0.6 on 2018-11-16 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApi', '0003_auto_20181114_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='RunsheetData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_id', models.CharField(max_length=40)),
                ('drop_id', models.CharField(blank=True, max_length=40, null=True)),
                ('log_date_time', models.DateTimeField()),
                ('log_type', models.DateTimeField(max_length=40)),
                ('status_old', models.CharField(blank=True, max_length=40, null=True)),
                ('status_new', models.CharField(blank=True, max_length=40, null=True)),
                ('log_text', models.CharField(max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'runsheet Data',
            },
        ),
        migrations.AlterField(
            model_name='questionresponse',
            name='drop_id',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
