# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.ForeignKey('DeliveryapiUser', models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class DeliveryapiBranch(models.Model):
    branch_name = models.CharField(max_length=40)
    branch_address = models.CharField(max_length=300, blank=True, null=True)
    branch_api_server_ip = models.GenericIPAddressField(blank=True, null=True)
    branch_photo_upload_ip = models.GenericIPAddressField(blank=True, null=True)
    branch_photo_upload_user = models.CharField(max_length=40, blank=True, null=True)
    branch_photo_upload_password = models.CharField(max_length=40, blank=True, null=True)
    branch_photo_upload_directory = models.CharField(max_length=300, blank=True, null=True)
    branch_is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    organisation = models.ForeignKey('DeliveryapiOrganisation', models.DO_NOTHING)
    branch_latitude = models.CharField(max_length=60, blank=True, null=True)
    branch_longitude = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deliveryApi_branch'


class DeliveryapiBranchadmins(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    branch = models.ForeignKey(DeliveryapiBranch, models.DO_NOTHING)
    user = models.ForeignKey('DeliveryapiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_branchadmins'


class DeliveryapiCustomercode(models.Model):
    customer_code = models.CharField(max_length=40)
    customer_name = models.CharField(max_length=40)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_customercode'


class DeliveryapiDeletedquestion(models.Model):
    question_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_deletedquestion'


class DeliveryapiDevice(models.Model):
    device_make = models.CharField(max_length=40)
    device_model = models.CharField(max_length=40)
    device_imei_no = models.CharField(max_length=40)
    device_last_check_in = models.DateTimeField(blank=True, null=True)
    device_last_driver = models.CharField(max_length=40, blank=True, null=True)
    device_is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    branch = models.ForeignKey(DeliveryapiBranch, models.DO_NOTHING, blank=True, null=True)
    device_is_revoke = models.BooleanField()
    device_is_inactive = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_device'


class DeliveryapiOrganisation(models.Model):
    organisation_name = models.CharField(max_length=40)
    organisation_logo = models.CharField(max_length=100)
    organisation_is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    days_to_delete_photos = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_organisation'


class DeliveryapiOrganisationadmins(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    organisation = models.ForeignKey(DeliveryapiOrganisation, models.DO_NOTHING)
    user = models.ForeignKey('DeliveryapiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_organisationadmins'


class DeliveryapiPasswordresetrequests(models.Model):
    reset_token = models.CharField(max_length=300)
    date_time = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.ForeignKey('DeliveryapiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_passwordresetrequests'


class DeliveryapiPhoto(models.Model):
    file = models.CharField(max_length=100)
    is_uploaded = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    drop_id = models.CharField(max_length=40)
    is_checked = models.BooleanField()
    run_id = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'deliveryApi_photo'


class DeliveryapiQuestion(models.Model):
    customer_code = models.CharField(max_length=300, blank=True, null=True)
    question_sequence = models.IntegerField()
    question_text = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    branch = models.ForeignKey(DeliveryapiBranch, models.DO_NOTHING, blank=True, null=True)
    organisation = models.ForeignKey(DeliveryapiOrganisation, models.DO_NOTHING, blank=True, null=True)
    question_false_action = models.ForeignKey('DeliveryapiQuestionfalseaction', models.DO_NOTHING)
    question_section = models.ForeignKey('DeliveryapiQuestionsection', models.DO_NOTHING)
    question_true_action = models.ForeignKey('DeliveryapiQuestiontrueaction', models.DO_NOTHING)
    question_type = models.ForeignKey('DeliveryapiQuestiontype', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_question'


class DeliveryapiQuestionaction(models.Model):
    question_action_record = models.BooleanField()
    question_action_take_photo = models.BooleanField()
    question_action_signature = models.BooleanField()
    question_action_no_action = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    question_action_block = models.ForeignKey('DeliveryapiQuestionactionblock', models.DO_NOTHING, blank=True, null=True)
    question_action_log = models.ForeignKey('DeliveryapiQuestionactionlog', models.DO_NOTHING, blank=True, null=True)
    question_action_status = models.ForeignKey('DeliveryapiQuestionactionstatus', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionaction'


class DeliveryapiQuestionactionblock(models.Model):
    question_action_block = models.BooleanField()
    question_action_block_text = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionactionblock'


class DeliveryapiQuestionactionlog(models.Model):
    question_action_log = models.BooleanField()
    question_action_log_type = models.ForeignKey('DeliveryapiQuestionactionlogtype', models.DO_NOTHING)
    question_action_log_text = models.CharField(max_length=300)
    question_action_log_driver_name = models.BooleanField()
    question_action_log_driver_gps = models.BooleanField()
    question_action_log_no_of_packages = models.BooleanField()
    question_action_log_customer_name = models.BooleanField()
    question_action_log_date_time = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionactionlog'


class DeliveryapiQuestionactionlogtype(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    type_id = models.IntegerField()
    type_name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionactionlogtype'


class DeliveryapiQuestionactionstatus(models.Model):
    question_action_status = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    drop_status = models.BooleanField()
    drop_status_id = models.IntegerField(blank=True, null=True)
    drop_status_name = models.CharField(max_length=40, blank=True, null=True)
    run_status = models.BooleanField()
    run_status_id = models.IntegerField(blank=True, null=True)
    run_status_name = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionactionstatus'


class DeliveryapiQuestionfalseaction(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    question_action = models.ForeignKey(DeliveryapiQuestionaction, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionfalseaction'


class DeliveryapiQuestionlog(models.Model):
    run_id = models.CharField(max_length=40)
    drop_id = models.CharField(max_length=40, blank=True, null=True)
    log_date_time = models.DateTimeField()
    log_type = models.IntegerField()
    status_old = models.CharField(max_length=40, blank=True, null=True)
    status_new = models.CharField(max_length=40, blank=True, null=True)
    log_text = models.CharField(max_length=300)
    is_uploaded = models.BooleanField()
    is_not_uploaded = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionlog'


class DeliveryapiQuestionresponse(models.Model):
    question_section = models.CharField(max_length=40)
    run_id = models.CharField(max_length=40)
    drop_id = models.CharField(max_length=40, blank=True, null=True)
    question_text = models.CharField(max_length=300)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_not_uploaded = models.BooleanField()
    is_uploaded = models.BooleanField()
    question_answer = models.BooleanField(blank=True)
    question_data = models.CharField(max_length=40, blank=True, null=True)
    answer_date_time = models.DateTimeField()
    q_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionresponse'


class DeliveryapiQuestionsection(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    section_id = models.IntegerField()
    section_name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'deliveryApi_questionsection'


class DeliveryapiQuestiontrueaction(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    question_action = models.ForeignKey(DeliveryapiQuestionaction, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_questiontrueaction'


class DeliveryapiQuestiontype(models.Model):
    question_type = models.CharField(max_length=40)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_questiontype'


class DeliveryapiUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    is_organisation_admin = models.BooleanField()
    is_branch_admin = models.BooleanField()
    branch = models.ForeignKey(DeliveryapiBranch, models.DO_NOTHING, blank=True, null=True)
    organisation = models.ForeignKey(DeliveryapiOrganisation, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    is_revoked = models.BooleanField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deliveryApi_user'


class DeliveryapiUserGroups(models.Model):
    user = models.ForeignKey(DeliveryapiUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_user_groups'
        unique_together = (('user', 'group'),)


class DeliveryapiUserUserPermissions(models.Model):
    user = models.ForeignKey(DeliveryapiUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'deliveryApi_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(DeliveryapiUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
