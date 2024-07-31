from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.core.validators import URLValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
# from time import time
from datetime import datetime



QUESTION_TYPES = (
    ('select question type','SELECT QUESTION TYPE'),
    ('question','Question'),
    ('text', 'Text'),
    ('button','Button'),
    ('log','Log'),
    ('status','STATUS'),
    ('page','PAGE'),

)



class Organisation(models.Model):
    organisation_name = models.CharField(max_length=40)
    organisation_logo = models.ImageField(upload_to="organisation_pictures", default='organisation_pictures/no-img.jpg')
    days_to_delete_photos = models.IntegerField(default=7)
    organisation_is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.organisation_name

    class Meta:
      verbose_name_plural = 'organisation'

class Branch(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    branch_name = models.CharField(max_length=40)
    branch_address = models.CharField(max_length=300, blank=True, null=True)
    branch_api_server_ip = models.GenericIPAddressField(blank=True, null=True)
    branch_photo_upload_ip = models.GenericIPAddressField(blank=True, null=True)
    branch_photo_upload_user = models.CharField(max_length=40, blank=True, null=True)
    branch_photo_upload_password = models.CharField(max_length=40, blank=True, null=True)
    branch_photo_upload_directory = models.CharField(max_length=300, blank=True, null=True)
    branch_is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    branch_latitude = models.CharField(max_length=60, blank=True, null=True)
    branch_longitude = models.CharField(max_length=60, blank=True, null=True)

    def __str__(self):
        return self.branch_name

    class Meta:
      verbose_name_plural = 'branch'


class User(AbstractUser):
    is_organisation_admin = models.BooleanField(default=False)
    is_branch_admin = models.BooleanField(default=False)
    is_revoked = models.BooleanField(default=False)
    is_branch_user = models.BooleanField(default=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)

class PasswordResetRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=300)
    date_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = 'password Reset Requests'


class OrganisationAdmins(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organisation.organisation_name

    class Meta:
      verbose_name_plural = 'organisation Admins'

class BranchAdmins(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.branch.branch_name

    class Meta:
      verbose_name_plural = 'branch Admins'


class BranchUsers(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Device(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank = True, null=True)
    device_make = models.CharField(max_length=40)
    device_model = models.CharField(max_length=40)
    device_imei_no = models.CharField(max_length=40)
    device_last_check_in = models.DateTimeField(blank=True, null=True)
    device_last_driver = models.CharField(max_length=40, blank=True, null=True)
    device_is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    device_is_revoke = models.BooleanField(default=False)
    device_is_inactive = models.BooleanField(default=False)

    def __str__(self):
        return self.device_model

    class Meta:
      verbose_name_plural = 'device'

class QuestionType(models.Model):
    question_type = models.CharField(max_length=40, choices=QUESTION_TYPES, default='select question type')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_type

    class Meta:
      verbose_name_plural = 'question Type'

class QuestionActionLogType(models.Model):
    # question_action_log_type = models.CharField(max_length=40, choices=LOG_TYPES, default='select log type')
    type_id = models.IntegerField()
    type_name = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name_plural = 'question Action Log Type'

class QuestionActionLog(models.Model):
    question_action_log = models.BooleanField(default=False)
    question_action_log_type = models.ForeignKey(QuestionActionLogType, on_delete=models.CASCADE)
    question_action_log_text = models.CharField(max_length= 300)
    question_action_log_driver_name = models.BooleanField()
    question_action_log_driver_gps = models.BooleanField()
    question_action_log_no_of_packages = models.BooleanField()
    question_action_log_customer_name = models.BooleanField()
    question_action_log_date_time = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = 'question Action Log'

class QuestionActionBlock(models.Model):
    question_action_block = models.BooleanField(default=False)
    question_action_block_text = models.CharField(max_length= 300, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = 'question Action Block'

class QuestionActionStatus(models.Model):
    question_action_status = models.BooleanField(default=False)
    # question_action_select_status = models.CharField(max_length=40, choices=SELECT_STATUSES, default='select status')
    run_status_id = models.IntegerField(null=True, blank=True)
    run_status_name = models.CharField(max_length=40,null=True, blank=True)
    drop_status_id = models.IntegerField(null=True, blank=True)
    drop_status_name = models.CharField(max_length=40,null=True, blank=True)
    run_status = models.BooleanField(default=False)
    drop_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = 'question Action Status'

class QuestionAction(models.Model):
    question_action_log = models.ForeignKey(QuestionActionLog, on_delete=models.CASCADE, blank = True, null=True)
    question_action_block = models.ForeignKey(QuestionActionBlock, on_delete=models.CASCADE, blank = True, null=True)
    question_action_record = models.BooleanField(default=False)
    question_action_status = models.ForeignKey(QuestionActionStatus, on_delete=models.CASCADE, blank = True, null=True)
    question_action_take_photo = models.BooleanField(default=False)
    question_action_signature = models.BooleanField(default=False)
    question_action_no_action = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = 'question Action'

class QuestionSection(models.Model):
    # question_section = models.CharField(max_length=40, choices=QUESTION_SECTIONS, default='select question section')
    section_id = models.IntegerField(default = 10)
    section_name = models.CharField(max_length=40, default = "before departure")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.section_name

    class Meta:
      verbose_name_plural = 'question Section'

class QuestionFalseAction(models.Model):
    # question = models.ForeignKey(Question, on_delete=models.CASCADE)
    question_action = models.ForeignKey(QuestionAction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.question_action)

    class Meta:
      verbose_name_plural = 'question False Action'

class QuestionTrueAction(models.Model):
    # question = models.ForeignKey(Question, on_delete=models.CASCADE)
    question_action = models.ForeignKey(QuestionAction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.question_action)

    class Meta:
      verbose_name_plural = 'question True Action'

class CustomerCode(models.Model):
    customer_code = models.CharField(max_length=40)
    customer_name = models.CharField(max_length=40)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return str(self.customer_code)

    class Meta:
      verbose_name_plural = 'Customer'

class Question(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, default=None, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, default=None, blank=True, null=True)
    customer_code = models.CharField(max_length=300,default='FAKE_CODE', blank=True, null=True)
    question_sequence = models.IntegerField()
    question_section = models.ForeignKey(QuestionSection, on_delete =models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete =models.CASCADE)
    question_text = models.CharField(max_length=300, null = True, blank = True)
    question_false_action = models.ForeignKey(QuestionFalseAction, on_delete=models.CASCADE)
    question_true_action = models.ForeignKey(QuestionTrueAction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = 'question'

class DeletedQuestion(models.Model):
    question_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.question_id)

    class Meta:
      verbose_name_plural = 'deleted Question'

class QuestionResponse(models.Model):
    branch_id = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    driver_name = models.CharField(max_length=40, null=True, blank=True)
    question_section = models.CharField(max_length=40)
    run_id = models.CharField(max_length=40)
    drop_id = models.CharField(max_length=40, blank=True, null=True)
    question_text = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_not_uploaded = models.BooleanField(default=True)
    is_uploaded = models.BooleanField(default=False)
    question_answer = models.BooleanField(default=False,blank=True)
    question_data = models.CharField(max_length=40, blank=True, null=True)
    answer_date_time = models.DateTimeField(default=datetime.now)
    q_id = models.IntegerField(default=1)

    def __str__(self):
        return str(self.run_id)

    class Meta:
      verbose_name_plural = 'question Response'

class QuestionLog(models.Model):
    q_id = models.IntegerField(default=1)
    run_id = models.CharField(max_length=40)
    drop_id = models.CharField(max_length=40, blank=True, null=True)
    log_date_time = models.DateTimeField()
    log_type = models.IntegerField()
    status_old = models.CharField(max_length=40, blank=True, null=True)
    status_new = models.CharField(max_length=40, blank=True, null=True)
    log_text = models.CharField(max_length=300)
    is_uploaded = models.BooleanField(default=False)
    is_not_uploaded = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.run_id)

    class Meta:
      verbose_name_plural = 'question Log'


class Photo(models.Model):
    file = models.CharField(max_length=100)
    is_uploaded = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    drop_id = models.CharField(max_length=40)
    is_checked = models.BooleanField()
    run_id = models.CharField(max_length=40)

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = 'photo'