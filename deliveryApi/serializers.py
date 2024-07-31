
from .models import *
# from .models import Post
from rest_framework import serializers
# from rest_framework.serializers import(
# CharField,
# ValidationError
# )
# from django.db.models import Q
# from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate
from rest_framework import exceptions
# from django.contrib.auth.hashers import make_password

# User = get_user_model()

# class UserLoginSerializer(serializers.ModelSerializer):
#     token = CharField(allow_blank=True, read_only=True)
#     username = CharField(required=True)
#     class Meta:
#         model = User
#         fields = [
#             'username',
#             'password',
#             'token',
#         ]
#         extra_kwargs = {"password":
#                             {"write_only": True}
#                         }
#     def validate(self, data):
#         # user_obj = None
#         username = data.get("username", None)
#         password = data["password"]
#         if not username:
#             raise ValidationError("Username is required to login.")
#         user = User.objects.filter(
#             Q(username=username)
#             ).distinct()
#         if user.exists() and user.count() == 1:
#             user_obj = user.first()
#         else:
#             raise ValidationError("The username you entered is not valid.")
#
#         if user_obj:
#             if not user_obj.check_password(password):
#                 raise ValidationError("Your Password is incorrect, Please try again...")
#
#         data["token"] = "SOME RANDOM TOKEN"
#
#         return data

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")

        # try:
        #     user = User.objects.get(**kwargs)
        #     if user.check_password(password):
        #         return user
        # except User.DoesNotExist:
        #     return None


        if username and password:
            user = authenticate(username=username, password=password)
            print(user)
            print("User:" + username)
            print("Password:" + password)

            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    msg = "User is deactivated."
                    raise exceptions.ValidationError(msg)
            else:
                msg = "Unable to login with given credentials."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Must provide username and password both."
            raise exceptions.ValidationError(msg)

        return data

# class UserRegisterSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()
#
#     def create_user(self, username, password=None):
#
#         if username is None:
#             raise TypeError('Users must have a username.')
#
#         user = User.objects.create(
#             username=username,
#             password=make_password(password))
#
#         return user

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:

        image = serializers.ImageField(max_length=None, use_url=True)

        model = Organisation
        fields = ('id', 'organisation_name', 'organisation_logo', 'organisation_is_active')
        #fields = '__all__'

class OrganisationAdminsSerializer(serializers.ModelSerializer):
    # organisation_name = serializers.ReadOnlyField(source='org', read_only=True)
    class Meta:

        model = OrganisationAdmins
        fields = ('id', 'organisation', 'user')
        # fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:

        model = Branch
        fields = ('id', 'organisation', 'branch_name', 'branch_address', 'branch_api_server_ip', 'branch_photo_upload_ip', 'branch_photo_upload_user', 'branch_photo_upload_password', 'branch_photo_upload_directory', 'device_is_active')
        # fields = '__all__'

class BranchAdminsSerializer(serializers.ModelSerializer):
    # organisation_name = serializers.ReadOnlyField(source='org', read_only=True)
    class Meta:

        model = BranchAdmins
        fields = ('id', 'branch', 'user')
        # fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:

        model = Device
        fields = ('id', 'branch', 'device_make', 'device_model', 'device_imei_no', 'device_last_check_in', 'device_last_driver', 'device_is_active')
        # fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:

        model = Question
        fields = ('organisation', 'branch', 'customer_code', 'question_sequence', 'question_section', 'question_type', 'question_text', 'question_false_action', 'question_true_action')
        #fields = '__all__'

# class PostSerializer(serializers.ModelSerializer):
#     class Meta:
#
#         file = serializers.FileField(max_length=None, use_url=True)
#
#         model = Post
#         fields = ('add_photo', 'status', 'files', 'comments')
#         #fields = '__all__'
#
# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = ('cover_photo', 'add_photo', 'g_name', 'status', 'files', 'comments')
#         # fields = '__all__'
#
# class Acadamic_RecordSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Acadamic_Record
#         fields = ('attendance','quiz_number','quiz_marks')
#         # fields = '__all__'
