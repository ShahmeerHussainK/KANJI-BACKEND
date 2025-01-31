# Generated by Django 2.0.6 on 2018-11-14 07:51

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_organisation_admin', models.BooleanField(default=False)),
                ('is_branch_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch_name', models.CharField(max_length=40)),
                ('branch_address', models.CharField(max_length=40)),
                ('branch_api_server_ip', models.GenericIPAddressField()),
                ('branch_photo_upload_ip', models.GenericIPAddressField()),
                ('branch_photo_upload_user', models.CharField(max_length=40)),
                ('branch_photo_upload_password', models.CharField(max_length=40)),
                ('branch_photo_upload_directory', models.FileField(upload_to='uploads')),
                ('device_is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'branch',
            },
        ),
        migrations.CreateModel(
            name='BranchAdmins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.Branch')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'branch Admins',
            },
        ),
        migrations.CreateModel(
            name='CustomerCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_code', models.CharField(max_length=40)),
                ('customer_name', models.CharField(max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Customer',
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_make', models.CharField(max_length=40)),
                ('device_model', models.CharField(max_length=40)),
                ('device_imei_no', models.CharField(max_length=40)),
                ('device_last_check_in', models.DateTimeField(blank=True, null=True)),
                ('device_last_driver', models.CharField(blank=True, max_length=40, null=True)),
                ('device_is_active', models.BooleanField(default=False)),
                ('device_is_revoke', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.Branch')),
            ],
            options={
                'verbose_name_plural': 'device',
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organisation_name', models.CharField(max_length=40)),
                ('organisation_logo', models.ImageField(default='static/project_pictures/no-img.jpg', upload_to='static/project_pictures')),
                ('organisation_is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'organisation',
            },
        ),
        migrations.CreateModel(
            name='OrganisationAdmins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.Organisation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'organisation Admins',
            },
        ),
        migrations.CreateModel(
            name='PasswordResetRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reset_token', models.CharField(max_length=300)),
                ('date_time', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_sequence', models.IntegerField()),
                ('question_text', models.CharField(blank=True, max_length=300, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.Branch')),
                ('customer_code', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.CustomerCode')),
                ('organisation', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.Organisation')),
            ],
            options={
                'verbose_name_plural': 'question',
            },
        ),
        migrations.CreateModel(
            name='QuestionAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_action_record', models.BooleanField(default=False)),
                ('question_action_take_photo', models.BooleanField(default=False)),
                ('question_action_signature', models.BooleanField(default=False)),
                ('question_action_no_action', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'question Action',
            },
        ),
        migrations.CreateModel(
            name='QuestionActionBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_action_block', models.BooleanField(default=False)),
                ('question_action_block_text', models.CharField(blank=True, max_length=300, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'question Action Block',
            },
        ),
        migrations.CreateModel(
            name='QuestionActionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_action_log', models.BooleanField(default=False)),
                ('question_action_log_text', models.CharField(blank=True, max_length=300, null=True)),
                ('question_action_log_driver_name', models.BooleanField()),
                ('question_action_log_driver_gps', models.BooleanField()),
                ('question_action_log_no_of_packages', models.BooleanField()),
                ('question_action_log_customer_name', models.BooleanField()),
                ('question_action_log_date_time', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'question Action Log',
            },
        ),
        migrations.CreateModel(
            name='QuestionActionLogType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_action_log_type', models.CharField(choices=[('log type', 'LOG TYPE'), ('error', 'ERROR'), ('warning', 'WARNING'), ('info', 'INFO'), ('action', 'ACTION'), ('gps coords', 'GPS COORDS')], default='select log type', max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'question Action Log Type',
            },
        ),
        migrations.CreateModel(
            name='QuestionActionStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_action_status', models.BooleanField(default=False)),
                ('question_action_select_status', models.CharField(choices=[('select status', 'SELECT STATUS'), ('50', '50'), ('100', '100'), ('150', '150'), ('200', '200'), ('300', '300'), ('500', '500')], default='select status', max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'question Action Status',
            },
        ),
        migrations.CreateModel(
            name='QuestionFalseAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question_action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionAction')),
            ],
            options={
                'verbose_name_plural': 'question False Action',
            },
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_id', models.CharField(max_length=40)),
                ('driver_name', models.CharField(max_length=40)),
                ('run_id', models.CharField(max_length=40)),
                ('drop_id', models.CharField(max_length=40)),
                ('answer', models.CharField(max_length=300)),
                ('date_time', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.Question')),
            ],
            options={
                'verbose_name_plural': 'question Response',
            },
        ),
        migrations.CreateModel(
            name='QuestionSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_section', models.CharField(choices=[('select question section', 'SELECT QUESTION SECTION'), ('before departure', 'BEFORE DEPARTURE'), ('drop delivery', 'DROP DELIVERY'), ('drop break', 'DROP BREAK'), ('drop pickup', 'DROP PICKUP'), ('return to base', 'RETURN TO BASE')], default='select question section', max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'question Section',
            },
        ),
        migrations.CreateModel(
            name='QuestionTrueAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question_action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionAction')),
            ],
            options={
                'verbose_name_plural': 'question True Action',
            },
        ),
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(choices=[('select question type', 'SELECT QUESTION TYPE'), ('question', 'Question'), ('text', 'Text'), ('button', 'Button'), ('log', 'Log'), ('status', 'STATUS'), ('page', 'PAGE')], default='select question type', max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'question Type',
            },
        ),
        migrations.AddField(
            model_name='questionactionlog',
            name='question_action_log_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionActionLogType'),
        ),
        migrations.AddField(
            model_name='questionaction',
            name='question_action_block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionActionBlock'),
        ),
        migrations.AddField(
            model_name='questionaction',
            name='question_action_log',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionActionLog'),
        ),
        migrations.AddField(
            model_name='questionaction',
            name='question_action_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionActionStatus'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_false_action',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionFalseAction'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionSection'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_true_action',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionTrueAction'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.QuestionType'),
        ),
        migrations.AddField(
            model_name='branch',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliveryApi.Organisation'),
        ),
    ]
