from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(PasswordResetRequests)
admin.site.register(Organisation)
admin.site.register(OrganisationAdmins)
admin.site.register(Branch)
admin.site.register(BranchAdmins)
admin.site.register(CustomerCode)
admin.site.register(Device)
admin.site.register(QuestionType)
admin.site.register(QuestionActionLog)
admin.site.register(QuestionActionBlock)
admin.site.register(QuestionActionStatus)
admin.site.register(QuestionAction)
admin.site.register(QuestionSection)
admin.site.register(Question)
admin.site.register(QuestionTrueAction)
admin.site.register(QuestionFalseAction)
admin.site.register(QuestionResponse)
admin.site.register(QuestionActionLogType)
admin.site.register(QuestionLog)
admin.site.register(Photo)
admin.site.register(DeletedQuestion)
admin.site.register(BranchUsers)
# admin.site.register(Profile)



# admin.site.register(Post)
# admin.site.register(Group)
# admin.site.register(Acadamic_Record)