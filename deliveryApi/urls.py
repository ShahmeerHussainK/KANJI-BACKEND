from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from deliveryApi import views


from django.conf.urls.static import static
# from django.conf.urls.static import media
from django.conf import settings

urlpatterns = [

    path('', views.login, name='login'),
    path('dashboard/super', views.dashboard_superuser, name='dashboard_superuser'),
    path('dashboard/org', views.dashboard_organisation, name='dashboard_organisation'),
    path('dashboard/branch', views.dashboard_branch, name='dashboard_branch'),

    path('organisations', views.organisations, name='organisations'),
    path('view/organisation', views.view_organisation, name='view_organisation'),
    path('questions', views.questions, name='questions'),
    path('create/question', views.create_question, name='create_question'),
    path('registered/devices', views.registered_devices, name='registered_devices'),
    path('registration/requests', views.registration_requests, name='registration_requests'),
    path('roles', views.roles, name='roles'),
    path('answers', views.answers, name='answers'),

    path('api/user/run_detail', views.RunDetailAPIView.as_view()),
    #for android
    path('api/user/get_driver_list', views.DriverListAPIView.as_view()),

    path('api/user/get_run_info', views.RunInfoAPIView.as_view()),

    #for android
    path('api/user/get_statuses', views.StatusListAPIView.as_view()),
    path('api/user/update_statuses', views.UpdateStatusAPIView.as_view()),
    path('api/user/get_run_data', views.RunDataAPIView.as_view()),
    path('api/user/get_updated_data', views.UpdatedQuestionsDataAPIView.as_view()),
    # path('api/user/get_driver_data1', views.DriverData1APIView.as_view()),

    # path('api/user/run', views.RunAPIView.as_view()),
    # path('api/user/drop', views.DropAPIView.as_view()),
    # path('api/user/driver', views.ApiaryAPIView.as_view()),

    path('api/user/register', views.UserRegisterAPIView.as_view()),
    path('api/user/login', views.UserLoginAPIView.as_view()),
    path('api/user/role', views.UserRoleAPIView.as_view()),
    path('api/user/logout', views.UserLogoutAPIView.as_view()),
    path('api/user/forgot_password', views.ForgotPasswordAPIView.as_view()),
    path('api/user/reset_password', views.ResetPasswordAPIView.as_view()),
    path('api/user/validate_password', views.ValidatePasswordAPIView.as_view()),

    path('api/dashboard', views.DashboardAPIView.as_view()),
    # path('api/organisation', views.OrganisationAPIView.as_view()),
    path('api/organisation_admins', views.OrganisationAdminsAPIView.as_view()),
    # path('api/branch', views.BranchAPIView.as_view()),
    path('api/branch_admins', views.BranchAdminsAPIView.as_view()),
    path('api/device', views.DeviceAPIView.as_view()),

    path('api/organisation', views.OrganisationAPIView.as_view()),
    path('api/organisation/revoked', views.RevokedOrganisationAPIView.as_view()),

    path('api/branch', views.BranchAPIView.as_view()),
    path('api/branch/revoked', views.RevokedBranchAPIView.as_view()),

    path('api/questions/wizard/organisation', views.QuestionWizardOrganisationAPIView.as_view()),
    path('api/questions/wizard/branch', views.QuestionWizardBranchAPIView.as_view()),
    path('api/questions/wizard/sequence', views.QuestionWizardSequenceAPIView.as_view()),
    path('api/questions/wizard/runsheet', views.QuestionWizardRunsheetAPIView.as_view()),

    path('api/questions/create', views.QuestionCreateAPIView.as_view()),
    path('api/questions/update', views.QuestionUpdateAPIView.as_view()),
    path('api/questions', views.QuestionAPIView.as_view()),

    #for android
    path('api/questions/answers', views.QuestionAnswerAPIView.as_view()),
    path('api/questions/photos', views.QuestionPhotoAPIView.as_view()),
    path('api/questions/photos/check', views.QuestionPhotoCheckAPIView.as_view()),
    path('api/device/register', views.DeviceRegisterAPIView.as_view()),

    #for admin panel
    path('api/device/register/request', views.DeviceRegisterRequestAPIView.as_view()),
    path('api/device/registered', views.RegisteredDeviceAPIView.as_view()),
    path('api/device/revoked', views.RevokedDeviceAPIView.as_view()),
    path('api/questions/responses', views.QuestionResponseAPIView.as_view()),
    path('api/test', views.TestAPIView.as_view()),
    path('api/bulk', views.bulkQuestionAPIView.as_view()),

    # path('post/', views.PostList.as_view()),
    # path('group/', views.GroupList.as_view()),
    # path('acadamic_record/', views.Acadamic_RecordList.as_view()),
    #url(r'^acadamic_record/?(P<id>[0-9]+)$', views.Acadamic_RecordList.as_view()),
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns = format_suffix_patterns(urlpatterns)
