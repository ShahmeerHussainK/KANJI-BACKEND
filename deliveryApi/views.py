from django.shortcuts import render
import ftplib
import os
# from deliveryTrackingSystem import helpers

from django.http import Http404, request

# from django.contrib.auth import get_user_model
from deliveryApi.serializers import *
from .models import *
from rest_framework.permissions import AllowAny, IsAdminUser

from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter

# from deliveryApi.api.permissions import IsOwnerOrReadOnly
# from deliveryApi.api.pagination import PostLimitOffsetPagination, PostPageNumberPagination

from django.views.decorators.gzip import gzip_page
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.pagination import (LimitOffsetPagination, PageNumberPagination,)

#Forgot password imports
from deliveryApi.models import PasswordResetRequests
import datetime
from collections import Counter
from django.contrib.auth.hashers import make_password, check_password
from django.db import DatabaseError, IntegrityError
from django.db import DatabaseError, IntegrityError
import logging
import traceback
from django.db.models import Q
import random
from django.core.mail import send_mail

from deliveryTrackingSystem import settings
logger = logging.getLogger('deliveryApi')
# logger = logging.getLogger(__name__)
import _thread

from django.db import transaction
import xlwt
import xlsxwriter
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import rest_framework.authentication
import rest_framework.permissions

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from datetime import datetime, timedelta
import datetime
from deliveryTrackingSystem.settings import MEDIA_URL

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .pagination import PostLimitOffsetPagination, PostPageNumberPagination

def login(request):
    return render(request, 'login_page.html')

def dashboard_superuser(request):
    return render(request, 'dashboard_superuser.html')

def dashboard_organisation(request):
    return render(request, 'dashboard_organisation.html')

def dashboard_branch(request):
    return render(request, 'dashboard_branch.html')

def organisations(request):
    return render(request, 'organisations.html')

def view_organisation(request):
    return render(request, 'view_organisation.html')

def questions(request):
    return render(request, 'questions.html')

def create_question(request):
    return render(request, 'create_question.html')

def registered_devices(request):
    return render(request, 'registered_devices.html')

def registration_requests(request):
    return render(request, 'registration_requests.html')

def roles(request):
    return render(request, 'roles.html')

def answers(request):
    return render(request, 'answers.html')

class OrganisationAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        org_name = request.POST.get('org_name')
        org_logo = request.FILES.get('org_logo')
        days_to_delete_photos = request.POST.get('days')
        if days_to_delete_photos is None:
            days_to_delete_photos = 7
            days_to_delete_photos = int(days_to_delete_photos)
        else:
            days_to_delete_photos = int(days_to_delete_photos)

        if user:
            try:
                if request.user.is_active and request.user.is_superuser:
                    org = Organisation.objects.filter(organisation_name=org_name)
                    if org.exists():
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Organisation already exists"})

                    if org_name and org_logo:
                        Organisation.objects.create(organisation_name=org_name, organisation_logo=org_logo, days_to_delete_photos=days_to_delete_photos)
                        print(Organisation)
                        org = Organisation.objects.filter(organisation_name=org_name)
                        id = org[0].id
                        name = org[0].organisation_name
                        logo = str(org[0].organisation_logo)
                        days_to_delete_photos = org[0].days_to_delete_photos
                        return Response({"organisation_id":id, "organisation_name":name, "organisation_logo":logo, "organisation_days_to_delete_photos":days_to_delete_photos, "status":status.HTTP_200_OK, "Msg": "Organisation has been created successfully"})
                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Must provide organisation name and organisation logo. These are all required fields"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not create any organisation"})
            except:
                logger.debug("Error while creating organisation")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Create Organisation"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        org_id = request.GET.get('org_id')

        if user:
            try:
                if request.user.is_active and request.user.is_superuser:
                    if org_id:
                        orgs = Organisation.objects.filter(pk=org_id)
                        inactive_orgs_count = 0
                        for org in orgs:
                            if org.organisation_is_active is False:
                                inactive_orgs_count = inactive_orgs_count + 1

                        organisations = []
                        for org in orgs:
                            if org.organisation_is_active is True:
                                org_id = org.id
                                name = org.organisation_name
                                logo = str(org.organisation_logo)
                                days_to_delete_photos = org.days_to_delete_photos

                                organisation = {
                                    "organisation_id": org_id,
                                    "organisation_name": name,
                                    "organisation_logo": logo,
                                    "days_to_delete_photos": days_to_delete_photos
                                }
                                organisations.append(organisation)
                    else:
                        orgs = Organisation.objects.order_by("id").all()

                        total_orgas = orgs.count()
                        print('total_orgas')
                        print(total_orgas)
                        orgas = Paginator(orgs, 10)
                        page = request.GET.get('page')
                        # ques = quest.page(page)
                        print(page)

                        try:
                            orga = orgas.page(page)
                        except PageNotAnInteger:
                            orga = orgas.page(1)
                        except EmptyPage:
                            orga = orgas.page(orgas.num_pages)
                            
                        has_next = orga.has_next()
                        if has_next is True:
                            next_page_number = orga.next_page_number()
                        else:
                            next_page_number = "There is no next page. This is the last page"
                        print(next_page_number)

                        has_previous = orga.has_previous()
                        if has_previous is True:
                            previous_page_number = orga.previous_page_number()
                        else:
                            previous_page_number = "There is no previous page. This is the first page"
                        print(previous_page_number)

                        inactive_orgs_count = 0
                        for org in orgs:
                            if org.organisation_is_active is False:
                                inactive_orgs_count = inactive_orgs_count + 1

                        organisations = []
                        for org in orga:
                            if org.organisation_is_active is True:
                                org_id = org.id
                                name = org.organisation_name
                                logo = str(org.organisation_logo)
                                days_to_delete_photos = org.days_to_delete_photos

                                organisation = {
                                    "organisation_id": org_id,
                                    "organisation_name": name,
                                    "organisation_logo": logo,
                                    "days_to_delete_photos": days_to_delete_photos
                                }
                                organisations.append(organisation)
                    return Response({"organisations": organisations, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_orgs": total_orgas, "inactive_orgs_count": inactive_orgs_count, "status": status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    if org_id:
                        orgs = Organisation.objects.filter(pk=org_id)

                        inactive_orgs_count = 0
                        for org in orgs:
                            if org.organisation_is_active is False:
                                inactive_orgs_count = inactive_orgs_count + 1

                        organisations = []
                        for org in orgs:
                            if org.organisation_is_active is True:
                                org_id = org.id
                                name = org.organisation_name
                                logo = str(org.organisation_logo)
                                days_to_delete_photos = org.days_to_delete_photos

                                organisation = {
                                    "organisation_id": org_id,
                                    "organisation_name": name,
                                    "organisation_logo": logo,
                                    "days_to_delete_photos": days_to_delete_photos
                                }
                                organisations.append(organisation)
                    else:
                        print(user_id)
                        orgAdmin = OrganisationAdmins.objects.filter(user=user_id)
                        print(orgAdmin)
                        organisations = []
                        adminorgs = []
                        for orgs in orgAdmin:
                            org_id = orgs.organisation.id
                            orga = Organisation.objects.filter(pk=org_id)
                            print(orga)
                            adminorgs.append(org_id)

                            inactive_orgs_count = 0
                            for org in orga:
                                if org.organisation_is_active is False:
                                    inactive_orgs_count = inactive_orgs_count + 1


                        orgass = Organisation.objects.order_by("id").filter(id__in=adminorgs)

                        total_orgas = orgass.count()
                        print('total_orgas')
                        print(total_orgas)
                        orgas = Paginator(orgass, 10)
                        page = request.GET.get('page')
                        # ques = quest.page(page)
                        print(page)

                        try:
                            orga = orgas.page(page)
                        except PageNotAnInteger:
                            orga = orgas.page(1)
                        except EmptyPage:
                            orga = orgas.page(orgas.num_pages)

                        has_next = orga.has_next()
                        if has_next is True:
                            next_page_number = orga.next_page_number()
                        else:
                            next_page_number = "There is no next page. This is the last page"
                        print(next_page_number)

                        has_previous = orga.has_previous()
                        if has_previous is True:
                            previous_page_number = orga.previous_page_number()
                        else:
                            previous_page_number = "There is no previous page. This is the first page"
                        print(previous_page_number)

                        print(orgas)
                        for org in orga:
                            if org.organisation_is_active is True:
                                org_id = org.id
                                name = org.organisation_name
                                logo = str(org.organisation_logo)
                                days_to_delete_photos = org.days_to_delete_photos

                                organisation = {
                                    "organisation_id": org_id,
                                    "organisation_name": name,
                                    "organisation_logo": logo,
                                    "days_to_delete_photos": days_to_delete_photos
                                }
                                organisations.append(organisation)
                                print(organisations)

                    return Response({"organisations": organisations, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_orgs": total_orgas, "inactive_orgs_count": inactive_orgs_count, "status":status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not view organisations"})
            except:
                logger.debug("Error while retrieving organisation")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Organisation"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def put(self, request):
        user_id = request.POST.get('user_id')
        user = User.objects.filter(pk=user_id)

        org_id = request.POST.get('org_id')
        org_name = request.POST.get('org_name')
        org_logo = request.FILES.get('org_logo')
        print("org_logo")
        print(type(org_logo))
        days_to_delete_photos = request.POST.get('days')
        if days_to_delete_photos is None:
            days_to_delete_photos = 7
            days_to_delete_photos = int(days_to_delete_photos)
        else:
            days_to_delete_photos = int(days_to_delete_photos)
        org = Organisation.objects.filter(pk=org_id)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    if org and org_name:
                        if org[0].organisation_is_active is True:
                            logo = str(org[0].organisation_logo)
                            if org_logo is None:
                                org.update(organisation_name=org_name, organisation_logo=logo, days_to_delete_photos=days_to_delete_photos)
                            else:
                                org.update(organisation_name=org_name, days_to_delete_photos=days_to_delete_photos)
                                org[0].organisation_logo.delete()
                                org[0].organisation_logo.save(""+org_logo.name,org_logo)
                                org[0].save()
                            update_org = org
                            update_name = update_org[0].organisation_name
                            update_logo = str(update_org[0].organisation_logo)
                            update_days_to_delete_photos = org[0].days_to_delete_photos
                            return Response(
                                {"organisation_name": update_name, "organisation_logo": update_logo, "organisation_days_to_delete_photos":update_days_to_delete_photos, "status": status.HTTP_200_OK,
                                 "Msg": "Organisation has been updated successfully"})
                        else:
                            return Response({"status": status.HTTP_400_BAD_REQUEST,
                                             "Msg": "This Organisation is deactivated"})
                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST,
                                         "Msg": "Parameters missing"})
                else:
                    return Response(
                        {"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not update any organisation"})
            except:
                logger.debug("Error while updating organisation")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Update Organisation"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def delete(self, request):
        org_id = request.GET.get('org_id')
        org = Organisation.objects.filter(pk=org_id)
        print(org)

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    if org:
                        if org[0].organisation_is_active is True:
                            org.update(organisation_is_active = False)
                            org_id = org[0].id
                            print("org")
                            print(org_id)
                            branch = Branch.objects.filter(organisation=org_id)
                            for b in branch:
                                if b.branch_is_active is True:
                                    branch_id = b.id
                                    print("branch")
                                    print(branch_id)
                                    branch_obj = Branch.objects.filter(pk=branch_id)
                                    branch_obj.update(branch_is_active = False)

                                    device = Device.objects.filter(branch=branch_id)
                                    for dev in device:
                                        if dev.device_is_active is True:
                                            device_id  = dev.id
                                            print("device")
                                            print(device_id)
                                            device_obj = Device.objects.filter(pk=device_id)
                                            device_obj.update(device_is_active=False, device_is_inactive = True)

                            return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "Organisation is deleted successfully"})
                        else:
                            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This Organisation is already deactivated"})
                    else:
                        return Response(
                        {"status": status.HTTP_404_NOT_FOUND, "Msg": "This Organisation doesn't exist"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "This user can not delete any organisation"})
            except:
                logger.debug("Error while deleting organisation")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Delete Organisation"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class RevokedOrganisationAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        org_id = request.GET.get('org_id')

        if user:
            try:
                if request.user.is_active and request.user.is_superuser:
                    if org_id:
                        orgs = Organisation.objects.filter(pk=org_id)
                        organisations = []
                        for org in orgs:
                            if org.organisation_is_active is False:
                                org_id = org.id
                                name = org.organisation_name
                                logo = str(org.organisation_logo)
                                days_to_delete_photos = org.days_to_delete_photos

                                organisation = {
                                    "organisation_id": org_id,
                                    "organisation_name": name,
                                    "organisation_logo": logo,
                                    "days_to_delete_photos": days_to_delete_photos
                                }
                                organisations.append(organisation)
                    else:
                        orgs = Organisation.objects.all()
                        organisations = []
                        for org in orgs:
                            if org.organisation_is_active is False:
                                org_id = org.id
                                name = org.organisation_name
                                logo = str(org.organisation_logo)
                                days_to_delete_photos = org.days_to_delete_photos

                                organisation = {
                                    "organisation_id": org_id,
                                    "organisation_name": name,
                                    "organisation_logo": logo,
                                    "days_to_delete_photos": days_to_delete_photos
                                }
                                organisations.append(organisation)
                    return Response({"organisations": organisations, "status": status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not view revoked organisations"})
            except:
                logger.debug("Error while retrieving revoked organisation")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Revoked Organisation"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def put(self, request):
        org_id = request.GET.get('org_id')
        org = Organisation.objects.filter(pk=org_id)
        print(org)

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    if org:
                        if org[0].organisation_is_active is False:
                            org.update(organisation_is_active = True)
                            org_id = org[0].id
                            print("org")
                            print(org_id)
                            branch = Branch.objects.filter(organisation=org_id)
                            for b in branch:
                                if b.branch_is_active is False:
                                    branch_id = b.id
                                    print("branch")
                                    print(branch_id)
                                    branch_obj = Branch.objects.filter(pk=branch_id)
                                    branch_obj.update(branch_is_active=True)

                                    device = Device.objects.filter(branch=branch_id)
                                    for dev in device:
                                        if dev.device_is_inactive is True:
                                            device_id = dev.id
                                            print("device")
                                            print(device_id)
                                            device_obj = Device.objects.filter(pk=device_id)
                                            device_obj.update(device_is_active=True, device_is_inactive=False)
                            return Response({"status": status.HTTP_200_OK, "Msg": "Organisation is activated successfully"})
                        else:
                            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This Organisation is already activated"})
                    else:
                        return Response(
                        {"status": status.HTTP_404_NOT_FOUND, "Msg": "This Organisation doesn't exist"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "This user can not activate any organisation"})
            except:
                logger.debug("Error while activating organisation")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Activate Organisation"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class BranchAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request):
        user_id = request.POST.get('user_id')
        user = User.objects.filter(pk=user_id)

        org_id = request.POST.get('org_id')
        orgs = Organisation.objects.filter(pk=org_id)
        for orga in orgs:
            if orga.organisation_is_active is True:
                org = orga

        branch_name = request.POST.get('branch_name')
        branch_address = request.POST.get('branch_address')
        branch_latitude = request.POST.get('branch_latitude')
        branch_longitude = request.POST.get('branch_longitude')
        branch_api_server_ip = request.POST.get('api_server_ip')
        branch_photo_upload_ip = request.POST.get('photo_upload_ip')
        branch_photo_upload_user = request.POST.get('photo_upload_user')
        branch_photo_upload_password = request.POST.get('photo_upload_password')
        branch_photo_upload_directory = request.POST.get('photo_upload_directory')

        if user:
            try:
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin:
                    if Branch.objects.filter(branch_name=branch_name).exists():
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Branch already exists"})
                    # and branch_address and branch_latitude and branch_longitude and branch_api_server_ip and branch_photo_upload_ip and branch_photo_upload_user and branch_photo_upload_password and branch_photo_upload_directory
                    if org_id and branch_name:
                        new_branch = Branch.objects.create(organisation=org, branch_name=branch_name, branch_address=branch_address, branch_latitude=branch_latitude, branch_longitude=branch_longitude, branch_api_server_ip=branch_api_server_ip,
                                              branch_photo_upload_ip=branch_photo_upload_ip, branch_photo_upload_user=branch_photo_upload_user, branch_photo_upload_password=branch_photo_upload_password,
                                              branch_photo_upload_directory=branch_photo_upload_directory)
                        # branch = new_branch
                        branch = Branch.objects.filter(branch_name=branch_name)
                        id = branch[0].id
                        name = branch[0].branch_name
                        address = branch[0].branch_address
                        latitude = branch[0].branch_latitude
                        longitude = branch[0].branch_longitude
                        server_ip = branch[0].branch_api_server_ip
                        upload_ip = branch[0].branch_photo_upload_ip
                        upload_user = branch[0].branch_photo_upload_user
                        upload_password = branch[0].branch_photo_upload_password
                        upload_directory = branch[0].branch_photo_upload_directory
                        return Response({"branch_id":id, "branch_name":name,"branch_address":address, "branch_latitude":latitude, "branch_longitude":longitude, "branch_api_server_ip":server_ip,
                                         "branch_photo_upload_ip": upload_ip, "branch_photo_upload_user": upload_user, "branch_photo_upload_password": upload_password,
                                         "branch_photo_upload_directory": upload_directory,
                                         "status":status.HTTP_200_OK, "Msg": "Branch has been created successfully"})
                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Missing Fields for creating branch"})

                # elif request.user.is_active and request.user.is_organisation_admin:
                #     if Branch.objects.filter(branch_name=branch_name).exists():
                #         return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Branch already exists"})
                #
                #     if org_id and branch_name and branch_address and branch_api_server_ip and branch_photo_upload_ip and branch_photo_upload_user and branch_photo_upload_password and branch_photo_upload_directory:
                #         Branch.objects.create(organisation=org_id, branch_name=branch_name, branch_address=branch_address, branch_api_server_ip=branch_api_server_ip,
                #                               branch_photo_upload_ip=branch_photo_upload_ip, branch_photo_upload_user=branch_photo_upload_user, branch_photo_upload_password=branch_photo_upload_password,
                #                               branch_photo_upload_directory=branch_photo_upload_directory,)
                #         return Response({"status":status.HTTP_200_OK, "Msg": "Branch is created"})
                #     else:
                #         return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Missing Fields"})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not create any branch"})
            except:
                logger.debug("Error while creating branch")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Create Branch"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        org_id = request.GET.get('org_id')

        if user:
            try:
                if request.user.is_active and request.user.is_superuser:
                    if org_id:
                        branch = Branch.objects.order_by("branch_name").filter(organisation=org_id)

                        inactive_branch_count = 0
                        for branc in branch:
                            if branc.branch_is_active is False:
                                inactive_branch_count = inactive_branch_count + 1

                        total_branches = branch.count()
                        print('total_branches')
                        print(total_branches)
                        brancss = Paginator(branch, 20)
                        page = request.GET.get('page')
                        # ques = quest.page(page)
                        print(page)

                        try:
                            brancs = brancss.page(page)
                        except PageNotAnInteger:
                            brancs = brancss.page(1)
                        except EmptyPage:
                            brancs = brancss.page(brancss.num_pages)

                        has_next = brancs.has_next()
                        if has_next is True:
                            next_page_number = brancs.next_page_number()
                        else:
                            next_page_number = "There is no next page. This is the last page"
                        print(next_page_number)

                        has_previous = brancs.has_previous()
                        if has_previous is True:
                            previous_page_number = brancs.previous_page_number()
                        else:
                            previous_page_number = "There is no previous page. This is the first page"
                        print(previous_page_number)

                        branches = []
                        for branc in brancs:
                            if branc.branch_is_active is True:
                                org_id = branc.organisation.id
                                org_name = branc.organisation.organisation_name
                                branch_id = branc.id
                                branch_name = branc.branch_name
                                address = branc.branch_address
                                latitude = branc.branch_latitude
                                longitude = branc.branch_longitude
                                server_ip = branc.branch_api_server_ip
                                upload_ip = branc.branch_photo_upload_ip
                                upload_user = branc.branch_photo_upload_user
                                upload_password = branc.branch_photo_upload_password
                                upload_directory = branc.branch_photo_upload_directory

                                br = {
                                    "organisation_id": org_id,
                                    "organisation_name": org_name,
                                    "branch_id": branch_id,
                                    "branch_name": branch_name,
                                    "branch_address": address,
                                    "branch_latitude": latitude,
                                    "branch_longitude": longitude,
                                    "branch_api_server_ip": server_ip,
                                    "branch_photo_upload_ip": upload_ip,
                                    "branch_photo_upload_user": upload_user,
                                    "branch_photo_upload_password": upload_password,
                                    "branch_photo_upload_directory": upload_directory
                                }
                                branches.append(br)
                        return Response({"branches": branches, "has_next": has_next,
                                            "has_previous": has_previous,
                                            "next_page_number": next_page_number,
                                            "previous_page_number": previous_page_number,
                                            "total_branches": total_branches, "inactive_branch_count": inactive_branch_count, "status": status.HTTP_200_OK})
                    else:
                        
                        orgs = Organisation.objects.order_by("organisation_name").all()
                        
                        response = []
                        org_obj = {}
                        # branch_list = []
                        for orga in orgs:
                            if orga.organisation_is_active is True:

                                org_id = orga.id
                                org_name = orga.organisation_name
                                org_obj = {
                                    "org_id": org_id,
                                    "org_name": org_name,
                                }
                                # branch_list.append(org_obj)
                                branches = Branch.objects.order_by("branch_name").filter(organisation=org_id)

                                inactive_branch_count = 0
                                for b in branches:
                                    if b.branch_is_active is False:
                                        inactive_branch_count = inactive_branch_count + 1

                                # total_branches = branches.count()
                                # print('total_branches')
                                # print(total_branches)
                                # brancss = Paginator(branches, 5)
                                # page = request.GET.get('page')
                                # # ques = quest.page(page)
                                # print(page)
                                #
                                # try:
                                #     brancs = brancss.page(page)
                                # except PageNotAnInteger:
                                #     brancs = brancss.page(1)
                                # except EmptyPage:
                                #     brancs = brancss.page(brancss.num_pages)
                                #
                                # has_next = brancs.has_next()
                                # if has_next is True:
                                #     next_page_number = brancs.next_page_number()
                                # else:
                                #     next_page_number = "There is no next page. This is the last page"
                                # print(next_page_number)
                                #
                                # has_previous = brancs.has_previous()
                                # if has_previous is True:
                                #     previous_page_number = brancs.previous_page_number()
                                # else:
                                #     previous_page_number = "There is no previous page. This is the first page"
                                # print(previous_page_number)

                                branch_list = []
                                for b in branches:
                                    # org_name = b.organisation.organisation_name
                                    if b.branch_is_active is True:
                                        branch_id = b.id
                                        branch_name = b.branch_name
                                        address = b.branch_address
                                        latitude = b.branch_latitude
                                        longitude = b.branch_longitude
                                        server_ip = b.branch_api_server_ip
                                        upload_ip = b.branch_photo_upload_ip
                                        upload_user = b.branch_photo_upload_user
                                        upload_password = b.branch_photo_upload_password
                                        upload_directory = b.branch_photo_upload_directory

                                        br = {
                                            "branch_id": branch_id,
                                            "branch_name": branch_name,
                                            "branch_address": address,
                                            "branch_latitude": latitude,
                                            "branch_longitude": longitude,
                                            "branch_api_server_ip": server_ip,
                                            "branch_photo_upload_ip": upload_ip,
                                            "branch_photo_upload_user": upload_user,
                                            "branch_photo_upload_password": upload_password,
                                            "branch_photo_upload_directory": upload_directory
                                        }
                                        branch_list.append(br)
                                        temp = {
                                            "branches":branch_list,
                                            "inactive_branch_count": inactive_branch_count,
                                            # "has_next": has_next,
                                            # "has_previous": has_previous,
                                            # "next_page_number": next_page_number,
                                            # "previous_page_number": previous_page_number,
                                            # "total_branches": total_branches
                                        }
                                        org_obj.update(temp)

                                response.append(org_obj)
                                # org_obj = {}


                        return Response({"organisations": response, "status":status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_organisation_admin:
                    if org_id:
                        branch = Branch.objects.order_by("id").filter(organisation=org_id)

                        inactive_branch_count = 0
                        for branc in branch:
                            if branc.branch_is_active is False:
                                inactive_branch_count = inactive_branch_count + 1

                        total_branches = branch.count()
                        print('total_branches')
                        print(total_branches)
                        brancss = Paginator(branch, 20)
                        page = request.GET.get('page')
                        # ques = quest.page(page)
                        print(page)

                        try:
                            brancs = brancss.page(page)
                        except PageNotAnInteger:
                            brancs = brancss.page(1)
                        except EmptyPage:
                            brancs = brancss.page(brancss.num_pages)

                        has_next = brancs.has_next()
                        if has_next is True:
                            next_page_number = brancs.next_page_number()
                        else:
                            next_page_number = "There is no next page. This is the last page"
                        print(next_page_number)

                        has_previous = brancs.has_previous()
                        if has_previous is True:
                            previous_page_number = brancs.previous_page_number()
                        else:
                            previous_page_number = "There is no previous page. This is the first page"
                        print(previous_page_number)

                        branches = []
                        for branc in brancs:
                            if branc.branch_is_active is True:
                                org_id = branc.organisation.id
                                org_name = branc.organisation.organisation_name
                                branch_id = branc.id
                                branch_name = branc.branch_name
                                address = branc.branch_address
                                latitude = branc.branch_latitude
                                longitude = branc.branch_longitude
                                server_ip = branc.branch_api_server_ip
                                upload_ip = branc.branch_photo_upload_ip
                                upload_user = branc.branch_photo_upload_user
                                upload_password = branc.branch_photo_upload_password
                                upload_directory = branc.branch_photo_upload_directory

                                br = {
                                    "organisation_id": org_id,
                                    "organisation_name": org_name,
                                    "branch_id": branch_id,
                                    "branch_name": branch_name,
                                    "branch_address": address,
                                    "branch_latitude": latitude,
                                    "branch_longitude": longitude,
                                    "branch_api_server_ip": server_ip,
                                    "branch_photo_upload_ip": upload_ip,
                                    "branch_photo_upload_user": upload_user,
                                    "branch_photo_upload_password": upload_password,
                                    "branch_photo_upload_directory": upload_directory
                                }
                                branches.append(br)
                        return Response({"branches": branches, "has_next": has_next,
                                            "has_previous": has_previous,
                                            "next_page_number": next_page_number,
                                            "previous_page_number": previous_page_number,
                                            "total_branches": total_branches, "inactive_branch_count": inactive_branch_count, "status": status.HTTP_200_OK})
                    else:
                        orgadmin = OrganisationAdmins.objects.filter(user=user_id)
                        response = []
                        org_obj = {}
                        # branch_list = []
                        for org_obj in orgadmin:
                            org_id = org_obj.organisation.id
                            orgs = Organisation.objects.filter(pk=org_id).order_by("organisation_name")
                            print(orgs)
                            for orga in orgs:
                                if orga.organisation_is_active is True:
                                    org_id = orga.id
                                    org_name = orga.organisation_name
                                    org_obj = {
                                        "org_id": org_id,
                                        "org_name": org_name,
                                    }
                                    # branch_list.append(org_obj)
                                    branches = Branch.objects.filter(organisation=org_id)

                                    inactive_branch_count = 0
                                    for b in branches:
                                        if b.branch_is_active is False:
                                            inactive_branch_count = inactive_branch_count + 1

                                    branch_list = []
                                    for b in branches:
                                        # org_name = b.organisation.organisation_name
                                        if b.branch_is_active is True:
                                            branch_id = b.id
                                            branch_name = b.branch_name
                                            address = b.branch_address
                                            latitude = b.branch_latitude
                                            longitude = b.branch_longitude
                                            server_ip = b.branch_api_server_ip
                                            upload_ip = b.branch_photo_upload_ip
                                            upload_user = b.branch_photo_upload_user
                                            upload_password = b.branch_photo_upload_password
                                            upload_directory = b.branch_photo_upload_directory

                                            br = {
                                                "branch_id": branch_id,
                                                "branch_name": branch_name,
                                                "branch_address": address,
                                                "branch_latitude": latitude,
                                                "branch_longitude": longitude,
                                                "branch_api_server_ip": server_ip,
                                                "branch_photo_upload_ip": upload_ip,
                                                "branch_photo_upload_user": upload_user,
                                                "branch_photo_upload_password": upload_password,
                                                "branch_photo_upload_directory": upload_directory
                                            }
                                            branch_list.append(br)
                                            temp = {
                                                "branches":branch_list
                                            }
                                            org_obj.update(temp)

                                    response.append(org_obj)
                                    # org_obj = {}


                        return Response({"organisations": response, "inactive_branch_count": inactive_branch_count, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_branch_admin:
                    branchadmin = BranchAdmins.objects.filter(user=user_id)
                    response = []
                    org_obj = {}
                    for branch_obj in branchadmin:
                        branch_id = branch_obj.branch.id
                        branches = Branch.objects.filter(pk=branch_id)
                        print(branches)

                        inactive_branch_count = 0
                        for b in branches:
                            if b.branch_is_active is False:
                                inactive_branch_count = inactive_branch_count + 1

                        for b in branches:
                            if b.branch_is_active is True:
                                org_id = b.organisation.id
                                org_name = b.organisation.organisation_name
                                org_obj = {
                                    "organisation_id": org_id,
                                    "organisation_name": org_name,
                                }
                                branch_id = b.id
                                branch_name = b.branch_name
                                address = b.branch_address
                                latitude = b.branch_latitude
                                longitude = b.branch_longitude
                                server_ip = b.branch_api_server_ip
                                upload_ip = b.branch_photo_upload_ip
                                upload_user = b.branch_photo_upload_user
                                upload_password = b.branch_photo_upload_password
                                upload_directory = b.branch_photo_upload_directory

                                branch_list = []

                                br = {
                                    "inactive_branch_count": inactive_branch_count,
                                    "branch_id": branch_id,
                                    "branch_name": branch_name,
                                    "branch_address": address,
                                    "branch_latitude": latitude,
                                    "branch_longitude": longitude,
                                    "branch_api_server_ip": server_ip,
                                    "branch_photo_upload_ip": upload_ip,
                                    "branch_photo_upload_user": upload_user,
                                    "branch_photo_upload_password": upload_password,
                                    "branch_photo_upload_directory": upload_directory
                                }
                                branch_list.append(br)
                                temp = {
                                    "branches":branch_list
                                }
                                org_obj.update(temp)

                            response.append(org_obj)
                            org_obj = {}


                    return Response({"organisations": response, "status":status.HTTP_200_OK})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not view branches"})
            except:
                logger.debug("Error while retrieving branch")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Branch"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def put(self, request):
        user_id = request.POST.get('user_id')
        user = User.objects.filter(pk=user_id)

        branch_id = request.POST.get('branch_id')
        org_id = request.POST.get('org_id')
        orgs = Organisation.objects.filter(pk=org_id)
        for orga in orgs:
            if orga.organisation_is_active is True:
                org = orga

        branch_name = request.POST.get('branch_name')
        branch_address = request.POST.get('branch_address')
        branch_latitude = request.POST.get('branch_latitude')
        branch_longitude = request.POST.get('branch_longitude')
        branch_api_server_ip = request.POST.get('api_server_ip')
        branch_photo_upload_ip = request.POST.get('photo_upload_ip')
        branch_photo_upload_user = request.POST.get('photo_upload_user')
        branch_photo_upload_password = request.POST.get('photo_upload_password')
        branch_photo_upload_directory = request.POST.get('photo_upload_directory')

        br = Branch.objects.filter(pk=branch_id)
        print("filtered")
        print(br)

        if user:
            try:
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin:
                    if br:
                        if br[0].branch_is_active is True:
                            updated_branch = br.update(organisation=org, branch_name=branch_name,
                                                               branch_address=branch_address,
                                                               branch_latitude=branch_latitude,
                                                               branch_longitude=branch_longitude,
                                                               branch_api_server_ip=branch_api_server_ip,
                                                               branch_photo_upload_ip=branch_photo_upload_ip,
                                                               branch_photo_upload_user=branch_photo_upload_user,
                                                               branch_photo_upload_password=branch_photo_upload_password,
                                                               branch_photo_upload_directory=branch_photo_upload_directory)
                            branch = Branch.objects.filter(pk=branch_id)
                            id = branch[0].id
                            name = branch[0].branch_name
                            address = branch[0].branch_address
                            latitude = branch[0].branch_latitude
                            longitude = branch[0].branch_longitude
                            server_ip = branch[0].branch_api_server_ip
                            upload_ip = branch[0].branch_photo_upload_ip
                            upload_user = branch[0].branch_photo_upload_user
                            upload_password = branch[0].branch_photo_upload_password
                            upload_directory = branch[0].branch_photo_upload_directory
                            return Response({"branch_id": id, "branch_name": name, "branch_address": address,
                                             "branch_latitude": latitude,"branch_longitude": longitude,
                                             "branch_api_server_ip": server_ip,
                                             "branch_photo_upload_ip": upload_ip,
                                             "branch_photo_upload_user": upload_user,
                                             "branch_photo_upload_password": upload_password,
                                             "branch_photo_upload_directory": upload_directory,
                                             "status": status.HTTP_200_OK,
                                             "Msg": "Branch has been updated successfully"})
                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST,
                                         "Msg": "Branch does'nt exist"})
                else:
                    return Response(
                        {"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not create any branch"})
            except:
                logger.debug("Error while creating branch")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Create Branch"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def delete(self, request):
        branch_id = request.GET.get('branch_id')
        branch = Branch.objects.filter(pk=branch_id)
        print(branch)

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin:
                    if branch:
                        if branch[0].branch_is_active is True:
                            branch.update(branch_is_active = False)
                            branch_id = branch[0].id
                            device = Device.objects.filter(branch=branch_id)
                            for dev in device:
                                if dev.device_is_active is True:
                                    device_id = dev.id
                                    device_obj = Device.objects.filter(pk=device_id)
                                    device_obj.update(device_is_active=False, device_is_inactive = True)
                            return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "Branch is deleted successfully"})
                        else:
                            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This Branch is already deactivated"})
                    else:
                        return Response(
                        {"status": status.HTTP_404_NOT_FOUND, "Msg": "This Branch doesn't exist"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "This user can not delete any Branch"})
            except:
                logger.debug("Error while deleting branch")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Delete Branch"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class RevokedBranchAPIView(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        org_id = request.GET.get('org_id')

        if user:
            try:
                if request.user.is_active and request.user.is_superuser:
                    if org_id:
                        branch = Branch.objects.filter(organisation=org_id)
                        branches = []
                        for branc in branch:
                            if branc.branch_is_active is False:
                                org_id = branc.organisation.id
                                org_name = branc.organisation.organisation_name
                                branch_id = branc.id
                                branch_name = branc.branch_name
                                address = branc.branch_address
                                latitude = branc.branch_latitude
                                longitude = branc.branch_longitude
                                server_ip = branc.branch_api_server_ip
                                upload_ip = branc.branch_photo_upload_ip
                                upload_user = branc.branch_photo_upload_user
                                upload_password = branc.branch_photo_upload_password
                                upload_directory = branc.branch_photo_upload_directory

                                br = {
                                    "organisation_id": org_id,
                                    "organisation_name": org_name,
                                    "branch_id": branch_id,
                                    "branch_name": branch_name,
                                    "branch_address": address,
                                    "branch_latitude": latitude,
                                    "branch_longitude": longitude,
                                    "branch_api_server_ip": server_ip,
                                    "branch_photo_upload_ip": upload_ip,
                                    "branch_photo_upload_user": upload_user,
                                    "branch_photo_upload_password": upload_password,
                                    "branch_photo_upload_directory": upload_directory
                                }
                                branches.append(br)
                        return Response({"branches": branches, "status": status.HTTP_200_OK})
                    else:
                        orgs = Organisation.objects.all()
                        response = []
                        org_obj = {}
                        # branch_list = []
                        for orga in orgs:
                            if orga.organisation_is_active is True:
                                org_id = orga.id
                                org_name = orga.organisation_name
                                org_obj = {
                                    "org_id": org_id,
                                    "org_name": org_name,
                                }
                                # branch_list.append(org_obj)
                                branches = Branch.objects.filter(organisation=org_id)
                                branch_list = []
                                for b in branches:
                                    # org_name = b.organisation.organisation_name
                                    if b.branch_is_active is False:
                                        branch_id = b.id
                                        branch_name = b.branch_name
                                        address = b.branch_address
                                        latitude = b.branch_latitude
                                        longitude = b.branch_longitude
                                        server_ip = b.branch_api_server_ip
                                        upload_ip = b.branch_photo_upload_ip
                                        upload_user = b.branch_photo_upload_user
                                        upload_password = b.branch_photo_upload_password
                                        upload_directory = b.branch_photo_upload_directory

                                        br = {
                                            # "organisation_id": org_id,
                                            # "organisation_name": org_name,
                                            "branch_id": branch_id,
                                            "branch_name": branch_name,
                                            "branch_address": address,
                                            "branch_latitude": latitude,
                                            "branch_longitude": longitude,
                                            "branch_api_server_ip": server_ip,
                                            "branch_photo_upload_ip": upload_ip,
                                            "branch_photo_upload_user": upload_user,
                                            "branch_photo_upload_password": upload_password,
                                            "branch_photo_upload_directory": upload_directory
                                        }
                                        branch_list.append(br)
                                        temp = {
                                            "branches":branch_list
                                        }
                                        org_obj.update(temp)

                                response.append(org_obj)
                                # org_obj = {}


                        return Response({"organisations": response, "status":status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_organisation_admin:
                    if org_id:
                        branch = Branch.objects.filter(organisation=org_id)
                        branches = []
                        for branc in branch:
                            if branc.branch_is_active is False:
                                org_id = branc.organisation.id
                                org_name = branc.organisation.organisation_name
                                branch_id = branc.id
                                branch_name = branc.branch_name
                                address = branc.branch_address
                                latitude = branc.branch_latitude
                                longitude = branc.branch_longitude
                                server_ip = branc.branch_api_server_ip
                                upload_ip = branc.branch_photo_upload_ip
                                upload_user = branc.branch_photo_upload_user
                                upload_password = branc.branch_photo_upload_password
                                upload_directory = branc.branch_photo_upload_directory

                                br = {
                                    "organisation_id": org_id,
                                    "organisation_name": org_name,
                                    "branch_id": branch_id,
                                    "branch_name": branch_name,
                                    "branch_address": address,
                                    "branch_latitude": latitude,
                                    "branch_longitude": longitude,
                                    "branch_api_server_ip": server_ip,
                                    "branch_photo_upload_ip": upload_ip,
                                    "branch_photo_upload_user": upload_user,
                                    "branch_photo_upload_password": upload_password,
                                    "branch_photo_upload_directory": upload_directory
                                }
                                branches.append(br)
                        return Response({"branches": branches, "status": status.HTTP_200_OK})
                    else:
                        orgadmin = OrganisationAdmins.objects.filter(user=user_id)
                        response = []
                        org_obj = {}
                        for org_obj in orgadmin:
                            org_id = org_obj.organisation.id
                            orgs = Organisation.objects.filter(pk=org_id)
                            print(orgs)
                            for orga in orgs:
                                if orga.organisation_is_active is True:
                                    org_id = orga.id
                                    org_name = orga.organisation_name
                                    org_obj = {
                                        "org_id": org_id,
                                        "org_name": org_name,
                                    }
                                    # branch_list.append(org_obj)
                                    branches = Branch.objects.filter(organisation=org_id)
                                    branch_list = []
                                    for b in branches:
                                        # org_name = b.organisation.organisation_name
                                        if b.branch_is_active is False:
                                            branch_id = b.id
                                            branch_name = b.branch_name
                                            address = b.branch_address
                                            latitude = b.branch_latitude
                                            longitude = b.branch_longitude
                                            server_ip = b.branch_api_server_ip
                                            upload_ip = b.branch_photo_upload_ip
                                            upload_user = b.branch_photo_upload_user
                                            upload_password = b.branch_photo_upload_password
                                            upload_directory = b.branch_photo_upload_directory

                                            br = {
                                                # "organisation_id": org_id,
                                                # "organisation_name": org_name,
                                                "branch_id": branch_id,
                                                "branch_name": branch_name,
                                                "branch_address": address,
                                                "branch_latitude": latitude,
                                                "branch_longitude": longitude,
                                                "branch_api_server_ip": server_ip,
                                                "branch_photo_upload_ip": upload_ip,
                                                "branch_photo_upload_user": upload_user,
                                                "branch_photo_upload_password": upload_password,
                                                "branch_photo_upload_directory": upload_directory
                                            }
                                            branch_list.append(br)
                                            temp = {
                                                "branches":branch_list
                                            }
                                            org_obj.update(temp)

                                    response.append(org_obj)
                                    # org_obj = {}


                        return Response({"organisations": response, "status":status.HTTP_200_OK})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This User can not view branches"})
            except:
                logger.debug("Error while retrieving revoked branch")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Revoked Branch"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User"})

    def put(self, request):
        branch_id = request.GET.get('branch_id')
        branch = Branch.objects.filter(pk=branch_id)
        print(branch)

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin:
                    if branch:
                        if branch[0].branch_is_active is False:
                            branch.update(branch_is_active = True)
                            branch_id = branch[0].id
                            device = Device.objects.filter(branch=branch_id)
                            for dev in device:
                                if dev.device_is_inactive is True:
                                    device_id = dev.id
                                    device_obj = Device.objects.filter(pk=device_id)
                                    device_obj.update(device_is_active=True, device_is_inactive=False)
                            return Response({"status": status.HTTP_200_OK, "Msg": "Branch is activated successfully"})
                        else:
                            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This Branch is already activated"})
                    else:
                        return Response(
                        {"status": status.HTTP_404_NOT_FOUND, "Msg": "This Branch doesn't exist"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "This user can not activate any Branch"})
            except:
                logger.debug("Error while activating branch")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Activate Branch"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class StatusListAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):

        imei = request.GET.get('imei')
        device = Device.objects.filter(device_imei_no=imei)
        branch_api_server_ip = device[0].branch.branch_api_server_ip

        res = []

        if branch_api_server_ip is not None:
            data = {
            "device_id": "1234567892",
            "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
            }

            # or we can write it like data = json.dumps(data)
            response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_status_list_run.php', json=data)
            response1 = response1.json()
            response1['run_statuses'] = response1.pop('statuses')
            res.append(response1)
            response2 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_status_list_drop.php', json=data)
            response2 = response2.json()
            response2['drop_statuses'] = response2.pop('statuses')
            res.append(response2)

            # response3 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/get_run_log_type.php', json=data)
            # print(response3)
            # response3 = response3.json()
            # # response3['drop_statuses'] = response3.pop('statuses')
            # res.append(response3)


            # return Response({"run": response1, "drop": response2})
            return Response(res)
        else:
            return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "No api is found regarding this branch"})

class UpdateStatusAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        run_id = request.GET.get('run_id')
        drop_id = request.GET.get('drop_id')
        status_old = request.GET.get('status_old')
        status_new = request.GET.get('status_new')

        imei = request.GET.get('imei')
        device = Device.objects.filter(device_imei_no=imei)
        print(device)
        # print(device[0].branch)
        branch_api_server_ip = device[0].branch.branch_api_server_ip
        if branch_api_server_ip is not None:
            try:
                if drop_id:
                    print("i am in")
                    data = {
                        "device_id": "1234567892",
                        "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
                        "run_id": run_id,
                        "drop_id": drop_id,
                        "status_old": status_old,
                        "status_new": status_new
                    }

                    # or we can write it like data = json.dumps(data)
                    response2 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/update_drop_status.php', json=data)
                    response = response2.json()
                    # temp = {'status': status.HTTP_200_OK}
                    # response.update(temp)
                    print(response['status'])

                    if response['status'] == "OK":
                        temp = {'status': status.HTTP_200_OK}
                        response.update(temp)

                    elif response['status'] == "FAIL - New Status behind current status":
                        temp = {'status': status.HTTP_406_NOT_ACCEPTABLE}
                        response.update(temp)

                    else:
                        temp = {'status': status.HTTP_400_BAD_REQUEST}
                        response.update(temp)
                    return Response(response)

                else:
                    print("else i am here")
                    data = {
                    "device_id": "1234567892",
                    "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
                    "run_id": run_id,
                    "status_old": status_old,
                    "status_new": status_new
                    }

                    # or we can write it like data = json.dumps(data)
                    response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/update_run_status.php', json=data)
                    print(response1)
                    response = response1.json()
                    # temp = {'status': status.HTTP_200_OK}
                    # response.update(temp)
                    print(response['status'])

                    if response['status'] == "OK":
                        temp = {'status': status.HTTP_200_OK}
                        response.update(temp)

                    elif response['status'] == "FAIL - New Status behind current status":
                        temp = {'status': status.HTTP_406_NOT_ACCEPTABLE}
                        response.update(temp)

                    else:
                        temp = {'status': status.HTTP_400_BAD_REQUEST}
                        response.update(temp)
                    return Response(response)
            except:
                logger.debug("Error while updating status")
                print(traceback.format_exc())
                logger.debug("update_status{}".format(traceback.format_exc()))
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Update Status"})
        else:
            return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "No api is found regarding this branch"})

#----------------------------#
#----------------------------#
#----------------------------#
# class DriverData1APIView(APIView):
#
#     def get(self, request):
#
#         links = ['http://61.69.119.183:80/KJWeb/transport/api/get_run_list.php', 'http://61.69.119.183:80/KJWeb/transport/api/get_run_info.php']
#
#
#         driver_id = request.GET.get('driver_id')
#         date = request.GET.get('date')
#         run_id = request.GET.get('run_id')
#
#         data = {
#         "device_id": "1234567892",
#         "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
#         "driver_id": driver_id,
#         "date": date,
#         "run_id": run_id
#         }
#         response =[]
#         for url in links:
#             # or we can write it like data = json.dumps(data)
#             r = requests.post(url, json=data)
#             response.append(r.json())
#
#         return Response(response)
#----------------------------#
#----------------------------#
#----------------------------#




#----------------------------#
class RunDataAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        imei = request.GET.get('imei')
        device = Device.objects.filter(device_imei_no=imei)
        branch_api_server_ip = device[0].branch.branch_api_server_ip

        driver_id = request.GET.get('driver_id')
        driver_name = request.GET.get('driver_name')
        date = request.GET.get('date')

        print('parameters detail', imei, branch_api_server_ip, driver_id, driver_name, date)

        response = []
        response_object = {}

        if branch_api_server_ip is not None:

            data = {
            "device_id": "1234567892",
            "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
            "driver_id": driver_id,
            "date": date

            }
            print('server detail',branch_api_server_ip)
            # or we can write it like data = json.dumps(data)
            resp=requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_run_list.php', json=data)
            response1 = resp.json()
            # print(response1['runs'][0])

            # print(resp.text)
            # res = json.loads(resp.text)
            # print(res)
            for obj in response1['runs']:
                print('check thi is true ha or not', obj['run_id'])
                data = {
                    "device_id": "1234567892",
                    "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
                    "run_id": obj['run_id']
                }
                # print(obj['run_id'])

                # or we can write it like data = json.dumps(data)
                resp = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_run_info.php', json=data)
                response2 = resp.json()
                print('fsdjkfnjkfasdnfjnjkfnsdjk', response2)
                #*****************#
                # i = 2222
                # for c in response2['drops']:
                #     c['drop_customer_code'] = str(i)
                #     code = c['drop_customer_code']
                #     i = i + 1
                # for c in response2['drops']:
                #     code = c['drop_account_code']
                #     name = c['drop_customer']
                #     print(code)
                #     print(name)
                #     if CustomerCode.objects.filter(customer_code=code).exists():
                #         continue
                #     CustomerCode.objects.create(customer_code=code, customer_name=name)
                    # print(code)
                #*****************#
                obj.update(response2)
            response.append(response1)
            # print(response1['runs'][0])
            # print(response[0]["runs"])
            response_object.update(response[0])
            # print(response_object)
            # print (response1['runs'][0][0]['run_id'])
            # print ([run['run_id'] for run in response1['runs'][0]])

            device = Device.objects.filter(device_imei_no = imei)
            if device and device[0].device_is_active is True:
                try:
                    device_last_check_in = datetime.datetime.now()
                    print("now")
                    print(device_last_check_in)
                    device_last_driver = driver_name
                    print(device_last_driver)
                    device.update(device_last_check_in=device_last_check_in, device_last_driver=device_last_driver)

                    branch_id = device[0].branch.id
                    branch = Branch.objects.filter(pk=branch_id)

                    # branch_api_server_ip = branch[0].branch_api_server_ip
                    branch_photo_upload_ip = branch[0].branch_photo_upload_ip
                    branch_photo_upload_user = branch[0].branch_photo_upload_user
                    branch_photo_upload_password = branch[0].branch_photo_upload_password
                    branch_photo_upload_directory = branch[0].branch_photo_upload_directory

                    org_id = branch[0].organisation.id
                    org = Organisation.objects.filter(pk=org_id)
                    days_to_delete_photos = org[0].days_to_delete_photos
                    print(days_to_delete_photos)
                    for dev in device:
                        print("devbranch:" + str(dev.branch))
                        print("devbroorg:" + str(dev.branch.organisation))
                        # branch_id = dev.branch.id
                        # org_id = dev.branch.organisation.id
                        branch_id = Q(branch=dev.branch)
                        org_id = Q(organisation=dev.branch.organisation)
                        # customer = Q(customer_code=ccode)

                        all_branch = Q(branch=None)
                        all_org = Q(organisation=None)
                        # all_customer = Q(customer_code=None)

                        questions = Question.objects.order_by("question_sequence").filter(branch_id | all_branch & org_id | all_org)

                        question = []
                        for q in questions:
                            # print(q.id)
                            # cust = q.customer_code
                            # print("Here iit is:" + str(cust))
                            q_id = q.id
                            sequence = q.question_sequence
                            type = q.question_type.question_type
                            text1 = q.question_text
                            if text1 is not None:
                                text = text1
                            else:
                                text = ""

                            section_id = q.question_section.section_id
                            section = q.question_section.section_name

                            org_fk = q.organisation
                            if org_fk is not None:
                                organisation = org_fk.organisation_name
                            else:
                                organisation = "all"

                            branch_fk = q.branch
                            if branch_fk is not None:
                                branch = branch_fk.branch_name
                            else:
                                branch = "all"

                            customer1 = q.customer_code
                            if customer1 is not '':
                                customer = customer1
                            else:
                                customer = "all"

                            false_action_log_fk = q.question_false_action.question_action.question_action_log
                            if false_action_log_fk is not None:
                                false_action_log = false_action_log_fk.question_action_log

                                false_action_log_type_fk = q.question_false_action.question_action.question_action_log.question_action_log_type
                                if false_action_log_type_fk is not None:
                                    question_action_log_type1 = false_action_log_type_fk.type_id
                                    question_action_log_type2 = false_action_log_type_fk.type_name
                                else:
                                    question_action_log_type1 = 0
                                    question_action_log_type2 = ""
                                false_action_log_type = question_action_log_type1
                                false_action_log_type_name = question_action_log_type2


                                false_action_log_text = false_action_log_fk.question_action_log_text
                                false_action_log_driver_name = false_action_log_fk.question_action_log_driver_name
                                false_action_log_driver_gps = false_action_log_fk.question_action_log_driver_gps
                                false_action_log_packages = false_action_log_fk.question_action_log_no_of_packages
                                false_action_log_customer_name = false_action_log_fk.question_action_log_customer_name
                                false_action_log_date_time = false_action_log_fk.question_action_log_date_time
                            else:
                                false_action_log = False
                                false_action_log_type = 0
                                false_action_log_type_name = ""
                                false_action_log_text = ""
                                false_action_log_driver_name = False
                                false_action_log_driver_gps = False
                                false_action_log_packages = False
                                false_action_log_customer_name = False
                                false_action_log_date_time = False
                            # print("log %s" % false_action_log)

                            false_action_block_fk = q.question_false_action.question_action.question_action_block
                            if false_action_block_fk is not None:
                                false_action_block = false_action_block_fk.question_action_block
                                false_action_block_text = false_action_block_fk.question_action_block_text
                            else:
                                false_action_block = False
                                false_action_block_text = ""
                            # print("block %s" % false_action_block)

                            false_action_record = q.question_false_action.question_action.question_action_record
                            # print("record %s" % false_action_record)

                            false_action_status_fk = q.question_false_action.question_action.question_action_status
                            if false_action_status_fk is not None:
                                false_action_status = false_action_status_fk.question_action_status
                                false_action_run_status = false_action_status_fk.run_status
                                false_action_drop_status = false_action_status_fk.drop_status
                                if false_action_run_status is True:
                                    false_action_run_status_id = false_action_status_fk.run_status_id
                                    false_action_run_status_name = false_action_status_fk.run_status_name
                                else:
                                    false_action_run_status_id = 0
                                    false_action_run_status_name = ""
                                if false_action_drop_status is True:
                                    false_action_drop_status_id = false_action_status_fk.drop_status_id
                                    false_action_drop_status_name = false_action_status_fk.drop_status_name
                                else:
                                    false_action_drop_status_id = 0
                                    false_action_drop_status_name = ""
                            else:
                                false_action_status = False
                                false_action_run_status = False
                                false_action_drop_status = False
                                false_action_run_status_id = 0
                                false_action_run_status_name = ""
                                false_action_drop_status_id = 0
                                false_action_drop_status_name = ""
                            # print("status %s" % false_action_status)

                            false_action_take_photo = q.question_false_action.question_action.question_action_take_photo
                            # print("photo %s" % false_action_take_photo)
                            false_action_signature = q.question_false_action.question_action.question_action_signature
                            # print("sign %s" % false_action_signature)
                            false_action_no_action = q.question_false_action.question_action.question_action_no_action
                            # print("no action %s" % false_action_no_action)

                            true_action_log_fk = q.question_true_action.question_action.question_action_log
                            if true_action_log_fk is not None:
                                true_action_log = true_action_log_fk.question_action_log

                                true_action_log_type_fk = true_action_log_fk.question_action_log_type
                                if true_action_log_type_fk is not None:
                                    question_action_log_type1 = true_action_log_type_fk.type_id
                                    question_action_log_type2 = true_action_log_type_fk.type_name
                                else:
                                    question_action_log_type1 = 0
                                    question_action_log_type2 = ""
                                true_action_log_type = question_action_log_type1
                                true_action_log_type_name = question_action_log_type2

                                true_action_log_text = true_action_log_fk.question_action_log_text
                                true_action_log_driver_name = true_action_log_fk.question_action_log_driver_name
                                true_action_log_driver_gps = true_action_log_fk.question_action_log_driver_gps
                                true_action_log_packages = true_action_log_fk.question_action_log_no_of_packages
                                true_action_log_customer_name = true_action_log_fk.question_action_log_customer_name
                                true_action_log_date_time = true_action_log_fk.question_action_log_date_time
                            else:
                                true_action_log = False
                                true_action_log_type = 0
                                true_action_log_type_name = ""
                                true_action_log_text = ""
                                true_action_log_driver_name = False
                                true_action_log_driver_gps = False
                                true_action_log_packages = False
                                true_action_log_customer_name = False
                                true_action_log_date_time = False
                            # print("true log %s" % true_action_log)

                            true_action_block_fk = q.question_true_action.question_action.question_action_block
                            if true_action_block_fk is not None:
                                true_action_block = true_action_block_fk.question_action_block
                                true_action_block_text = true_action_block_fk.question_action_block_text
                            else:
                                true_action_block = False
                                true_action_block_text = ""
                            # print("true block %s" % true_action_block)

                            true_action_record = q.question_true_action.question_action.question_action_record
                            # print("true record %s" % true_action_record)

                            true_action_status_fk = q.question_true_action.question_action.question_action_status
                            if true_action_status_fk is not None:
                                true_action_status = true_action_status_fk.question_action_status
                                true_action_run_status = true_action_status_fk.run_status
                                true_action_drop_status = true_action_status_fk.drop_status
                                if true_action_run_status is True:
                                    true_action_run_status_id = true_action_status_fk.run_status_id
                                    true_action_run_status_name = true_action_status_fk.run_status_name
                                else:
                                    true_action_run_status_id = 0
                                    true_action_run_status_name = ""
                                if true_action_drop_status is True:
                                    true_action_drop_status_id = true_action_status_fk.drop_status_id
                                    true_action_drop_status_name = true_action_status_fk.drop_status_name
                                else:
                                    true_action_drop_status_id = 0
                                    true_action_drop_status_name = ""

                            else:
                                true_action_status = False
                                true_action_run_status = False
                                true_action_drop_status = False
                                true_action_run_status_id = 0
                                true_action_run_status_name = ""
                                true_action_drop_status_id = 0
                                true_action_drop_status_name = ""
                            # print("true status %s" % true_action_status)

                            true_action_take_photo = q.question_true_action.question_action.question_action_take_photo
                            # print("true photo %s" % true_action_take_photo)
                            true_action_signature = q.question_true_action.question_action.question_action_signature
                            # print("true sign %s" % true_action_signature)
                            true_action_no_action = q.question_true_action.question_action.question_action_no_action
                            # print("true no action %s" % true_action_no_action)

                            result1 = {
                                    "question_id": q_id,
                                    "organisation": organisation,
                                    "branch": branch,
                                    "customer_code": customer,
                                    "section_id": section_id,
                                    "section": section,
                                    "sequence": sequence,
                                    "type": type,
                                    "text": text,

                                    "false_action_log": false_action_log,
                                    "false_action_log_type": false_action_log_type,
                                    "false_action_log_type_name": false_action_log_type_name,
                                    "false_action_log_text": false_action_log_text,

                                    "false_action_log_driver_name": false_action_log_driver_name,
                                    "false_action_log_driver_gps": false_action_log_driver_gps,
                                    "false_action_log_no_of_packages": false_action_log_packages,
                                    "false_action_log_customer_name": false_action_log_customer_name,
                                    "false_action_log_date_time": false_action_log_date_time,

                                    "false_action_block": false_action_block,
                                    "false_action_block_text": false_action_block_text,

                                    "false_action_record": false_action_record,

                                    "false_action_status": false_action_status,
                                    "false_action_run_status": false_action_run_status,
                                    "false_action_drop_status": false_action_drop_status,
                                    "false_action_run_status_id": false_action_run_status_id,
                                    "false_action_run_status_name": false_action_run_status_name,
                                    "false_action_drop_status_id": false_action_drop_status_id,
                                    "false_action_drop_status_name": false_action_drop_status_name,

                                    "false_action_take_photo": false_action_take_photo,

                                    "false_action_signature": false_action_signature,

                                    "false_action_no_action": false_action_no_action,


                                    "true_action_log": true_action_log,
                                    "true_action_log_type": true_action_log_type,
                                    "true_action_log_type_name": true_action_log_type_name,
                                    "true_action_log_text": true_action_log_text,

                                    "true_action_log_driver_name": true_action_log_driver_name,
                                    "true_action_log_driver_gps": true_action_log_driver_gps,
                                    "true_action_log_no_of_packages": true_action_log_packages,
                                    "true_action_log_customer_name": true_action_log_customer_name,
                                    "true_action_log_date_time": true_action_log_date_time,

                                    "true_action_block": true_action_block,
                                    "true_action_block_text": true_action_block_text,

                                    "true_action_record": true_action_record,

                                    "true_action_status": true_action_status,
                                    "true_action_run_status": true_action_run_status,
                                    "true_action_drop_status": true_action_drop_status,
                                    "true_action_run_status_id": true_action_run_status_id,
                                    "true_action_run_status_name": true_action_run_status_name,
                                    "true_action_drop_status_id": true_action_drop_status_id,
                                    "true_action_drop_status_name": true_action_drop_status_name,

                                    "true_action_take_photo": true_action_take_photo,

                                    "true_action_signature": true_action_signature,

                                    "true_action_no_action": true_action_no_action

                            }

                            question.append(result1)

                        temp ={
                            'questions':question,
                            'days_to_delete_photos': days_to_delete_photos,
                            # 'branch_api_server_ip': branch_api_server_ip,
                            'branch_photo_upload_ip': branch_photo_upload_ip,
                            'branch_photo_upload_user': branch_photo_upload_user,
                            'branch_photo_upload_password': branch_photo_upload_password,
                            'branch_photo_upload_directory': branch_photo_upload_directory,
                            'status': status.HTTP_200_OK,
                        }
                        response_object.update(temp)
                        # print(response_object)
#                         response_object = {
#     "runs": [
#         {
#             "run_id": "10931",
#             "updated_at": "2018-09-11 14:47:58",
#             "driver_name": "Wazza",
#             "truck_name": "TRUCK 5",
#             "trailer_name": "EXTENDABLE",
#             "run_date": "2019-03-14 12:27:09",
#             "run_seq_int": "2",
#             "run_status_id": "100",
#             "run_comment_text": "preload for second run",
#             "run_distance": "600",
#             "run_start_time": "0001-01-01 00:00:00",
#             "drops": [
#                 {
#                     "drop_id": "445480",
#                     "drop_sequence": "3",
#                     "drop_type": "3",
#                     "drop_address": "BLUE ROCK QUARRY TAMAREE RD.CEDAR CREEK. 0478 766 568 , QLD , QLD",
#                     "drop_expected_time": "",
#                     "drop_so_text": "704540",
#                     "drop_customer": "RIJAK CONSTRUCTIONS",
#                     "drop_contact": "",
#                     "drop_note": " ",
#                     "drop_status": "100",
#                     "drop_weight": "14342.572",
#                     "drop_max_length": "1",
#                     "drop_num_packages": None,
#                     "drop_lat": None,
#                     "drop_lng": None,
#                     "drop_account_code": "RIJAK"
#                 }
#             ]
#         },
#         {
#             "run_id": "10932",
#             "updated_at": "2018-08-05 12:47:57",
#             "driver_name": "Wazza",
#             "truck_name": "TRUCK 5",
#             "trailer_name": "EXTENDABLE",
#             "run_date": "2019-03-14 12:27:09",
#             "run_seq_int": "1",
#             "run_status_id": "100",
#             "run_comment_text": "",
#             "run_distance": "2019",
#             "run_start_time": "0001-01-01 00:00:00",
#             "drops": [
#                 {
#                     "drop_id": "445481",
#                     "drop_sequence": "2",
#                     "drop_type": "2",
#                     "drop_address": "52 ROSE STREET ORMISTON (7AM DEL) DANNY - 0430 561 531 11/10 , QLD",
#                     "drop_expected_time": "",
#                     "drop_so_text": "712806",
#                     "drop_customer": "TURBO ROOFING (QLD) P/L",
#                     "drop_contact": "",
#                     "drop_note": "TURBO ROOFING (QLD) P/L DANNY - 0430 561 531",
#                     "drop_status": "100",
#                     "drop_weight": "4605.545",
#                     "drop_max_length": "1",
#                     "drop_num_packages": None,
#                     "drop_lat": "-27.495926",
#                     "drop_lng": "153.2528602",
#                     "drop_account_code": "TURBO"
#                 }
#             ]
#         },
#         {
#             "run_id": "12",
#             "updated_at": "2018-09-11 14:47:58",
#             "driver_name": "Wazza",
#             "truck_name": "TRUCK 5",
#             "trailer_name": "EXTENDABLE",
#             "run_date": "2019-03-14 12:27:09",
#             "run_seq_int": "2",
#             "run_status_id": "100",
#             "run_comment_text": "preload for second run",
#             "run_distance": "600",
#             "run_start_time": "0001-01-01 00:00:00",
#             "drops": [
#                 {
#                     "drop_id": "156",
#                     "drop_sequence": "3",
#                     "drop_type": "3",
#                     "drop_address": "BLUE ROCK QUARRY TAMAREE RD.CEDAR CREEK. 0478 766 568 , QLD , QLD",
#                     "drop_expected_time": "",
#                     "drop_so_text": "704540",
#                     "drop_customer": "RIJAK CONSTRUCTIONS",
#                     "drop_contact": "",
#                     "drop_note": " ",
#                     "drop_status": "100",
#                     "drop_weight": "14342.572",
#                     "drop_max_length": "1",
#                     "drop_num_packages": None,
#                     "drop_lat": None,
#                     "drop_lng": None,
#                     "drop_account_code": "RIJAK"
#                 }
#             ]
#         },
#         {
#             "run_id": "15",
#             "updated_at": "2018-08-05 12:47:57",
#             "driver_name": "Wazza",
#             "truck_name": "TRUCK 5",
#             "trailer_name": "EXTENDABLE",
#             "run_date": "2031-08-05 12:47:55",
#             "run_seq_int": "1",
#             "run_status_id": "100",
#             "run_comment_text": "",
#             "run_distance": "2019",
#             "run_start_time": "0001-01-01 00:00:00",
#             "drops": [
#                 {
#                     "drop_id": "160",
#                     "drop_sequence": "2",
#                     "drop_type": "2",
#                     "drop_address": "52 ROSE STREET ORMISTON (7AM DEL) DANNY - 0430 561 531 11/10 , QLD",
#                     "drop_expected_time": "",
#                     "drop_so_text": "712806",
#                     "drop_customer": "TURBO ROOFING (QLD) P/L",
#                     "drop_contact": "",
#                     "drop_note": "TURBO ROOFING (QLD) P/L DANNY - 0430 561 531",
#                     "drop_status": "100",
#                     "drop_weight": "4605.545",
#                     "drop_max_length": "1",
#                     "drop_num_packages": None,
#                     "drop_lat": "-27.495926",
#                     "drop_lng": "153.2528602",
#                     "drop_account_code": "TURBO"
#                 }
#             ]
#         }
#     ],
#     "questions": [
#         {
#             "question_id": 123,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 20,
#             "section": "return to base",
#             "sequence": 1,
#             "type": "text",
#             "text": "return",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 127,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 5,
#             "section": "ManualEntry",
#             "sequence": 1,
#             "type": "question",
#             "text": "Manual",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": True,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 126,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 4,
#             "section": "Note",
#             "sequence": 1,
#             "type": "text",
#             "text": "Note",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 125,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 3,
#             "section": "Break",
#             "sequence": 1,
#             "type": "text",
#             "text": "Break",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 124,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 2,
#             "section": "PickUp",
#             "sequence": 1,
#             "type": "text",
#             "text": "Pckup",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 129,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 10,
#             "section": "before departure",
#             "sequence": 1,
#             "type": "question",
#             "text": "Is the cargo strapped correctly?",
#             "false_action_log": True,
#             "false_action_log_type": 1,
#             "false_action_log_type_name": "ERROR",
#             "false_action_log_text": "Cargo not ready",
#             "false_action_log_driver_name": True,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 2,
#             "true_action_log_type_name": "LOG",
#             "true_action_log_text": "Cargo has been loaded",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": True,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": True,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 131,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 10,
#             "section": "before departure",
#             "sequence": 9,
#             "type": "question",
#             "text": "Are you fit to drive this vehicle?",
#             "false_action_log": True,
#             "false_action_log_type": 2,
#             "false_action_log_type_name": "LOG",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": True,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": True,
#             "false_action_block": True,
#             "false_action_block_text": "Please see your supervisor",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 2,
#             "true_action_log_type_name": "LOG",
#             "true_action_log_text": "None",
#             "true_action_log_driver_name": True,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 102,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 10,
#             "section": "before departure",
#             "sequence": 10,
#             "type": "question",
#             "text": "Is the truck roadworthy?",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": True,
#             "false_action_block_text": "Please discuss with Transport Manager before departing",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 2,
#             "true_action_log_type_name": "LOG",
#             "true_action_log_text": "Driver has confirmed road worthiness of Truck",
#             "true_action_log_driver_name": True,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": True,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 140,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 10,
#             "section": "before departure",
#             "sequence": 11,
#             "type": "button",
#             "text": "test",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": True,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 103,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 10,
#             "section": "before departure",
#             "sequence": 15,
#             "type": "question",
#             "text": "Load Secured?",
#             "false_action_log": True,
#             "false_action_log_type": 2,
#             "false_action_log_type_name": "LOG",
#             "false_action_log_text": "Insecure Load logged.",
#             "false_action_log_driver_name": True,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": True,
#             "false_action_block": True,
#             "false_action_block_text": "Please fix any defects before proceeding.",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 4,
#             "true_action_log_type_name": "INFO",
#             "true_action_log_text": "Load is Secure",
#             "true_action_log_driver_name": True,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 104,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 10,
#             "section": "before departure",
#             "sequence": 19,
#             "type": "button",
#             "text": "Departing Base",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": True,
#             "true_action_status": True,
#             "true_action_run_status": True,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 400,
#             "true_action_run_status_name": "Underway",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 115,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 3,
#             "section": "Break",
#             "sequence": 20,
#             "type": "button",
#             "text": "Start Break",
#             "false_action_log": True,
#             "false_action_log_type": 2,
#             "false_action_log_type_name": "LOG",
#             "false_action_log_text": "Break Started",
#             "false_action_log_driver_name": True,
#             "false_action_log_driver_gps": True,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": True,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": True,
#             "false_action_run_status": False,
#             "false_action_drop_status": True,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 200,
#             "false_action_drop_status_name": "On Site",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 2,
#             "true_action_log_type_name": "LOG",
#             "true_action_log_text": "Break Started",
#             "true_action_log_driver_name": True,
#             "true_action_log_driver_gps": True,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": True,
#             "true_action_run_status": False,
#             "true_action_drop_status": True,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 200,
#             "true_action_drop_status_name": "On Site",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 137,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 10,
#             "section": "before departure",
#             "sequence": 20,
#             "type": "text",
#             "text": "Have a nice day!",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 116,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 3,
#             "section": "Break",
#             "sequence": 21,
#             "type": "page",
#             "text": "next",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 117,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 3,
#             "section": "Break",
#             "sequence": 22,
#             "type": "button",
#             "text": "Break Finished",
#             "false_action_log": True,
#             "false_action_log_type": 2,
#             "false_action_log_type_name": "LOG",
#             "false_action_log_text": "Break Finished",
#             "false_action_log_driver_name": True,
#             "false_action_log_driver_gps": True,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": True,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": True,
#             "false_action_run_status": False,
#             "false_action_drop_status": True,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 400,
#             "false_action_drop_status_name": "POD  Recieved",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 2,
#             "true_action_log_type_name": "LOG",
#             "true_action_log_text": "Break Finished",
#             "true_action_log_driver_name": True,
#             "true_action_log_driver_gps": True,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": True,
#             "true_action_run_status": False,
#             "true_action_drop_status": True,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 400,
#             "true_action_drop_status_name": "POD  Recieved",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 105,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 1,
#             "section": "SalesOrder",
#             "sequence": 50,
#             "type": "button",
#             "text": "On Site",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": True,
#             "true_action_run_status": False,
#             "true_action_drop_status": True,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 200,
#             "true_action_drop_status_name": "On Site",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 107,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 1,
#             "section": "SalesOrder",
#             "sequence": 54,
#             "type": "question",
#             "text": "All goods unloaded?",
#             "false_action_log": True,
#             "false_action_log_type": 1,
#             "false_action_log_type_name": "ERROR",
#             "false_action_log_text": "Some goods missing off load - talk to driver",
#             "false_action_log_driver_name": True,
#             "false_action_log_driver_gps": True,
#             "false_action_log_no_of_packages": True,
#             "false_action_log_customer_name": True,
#             "false_action_log_date_time": True,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 2,
#             "true_action_log_type_name": "LOG",
#             "true_action_log_text": "All goods offloaded",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": True,
#             "true_action_log_no_of_packages": True,
#             "true_action_log_customer_name": True,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 108,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 1,
#             "section": "SalesOrder",
#             "sequence": 55,
#             "type": "question",
#             "text": "Customer in attendance?",
#             "false_action_log": True,
#             "false_action_log_type": 2,
#             "false_action_log_type_name": "LOG",
#             "false_action_log_text": "Customer not in attendance",
#             "false_action_log_driver_name": True,
#             "false_action_log_driver_gps": True,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": True,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": True,
#             "true_action_log_type": 2,
#             "true_action_log_type_name": "LOG",
#             "true_action_log_text": "Customer On-site",
#             "true_action_log_driver_name": True,
#             "true_action_log_driver_gps": True,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": True,
#             "true_action_log_date_time": True,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 110,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 1,
#             "section": "SalesOrder",
#             "sequence": 57,
#             "type": "question",
#             "text": "Ready to take Photos?",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": True,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 111,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 1,
#             "section": "SalesOrder",
#             "sequence": 58,
#             "type": "button",
#             "text": "Customer Signature",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": True,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 112,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 1,
#             "section": "SalesOrder",
#             "sequence": 59,
#             "type": "page",
#             "text": "next",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": True,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": False,
#             "true_action_status": False,
#             "true_action_run_status": False,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": True
#         },
#         {
#             "question_id": 113,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 1,
#             "section": "SalesOrder",
#             "sequence": 60,
#             "type": "question",
#             "text": "Ready to leave site? - You will not be able to access photos etc again after you leave",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": True,
#             "false_action_block_text": "Please go back and complete before departing",
#             "false_action_record": False,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": True,
#             "true_action_status": True,
#             "true_action_run_status": False,
#             "true_action_drop_status": True,
#             "true_action_run_status_id": 0,
#             "true_action_run_status_name": "",
#             "true_action_drop_status_id": 400,
#             "true_action_drop_status_name": "POD  Recieved",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         },
#         {
#             "question_id": 114,
#             "organisation": "all",
#             "branch": "all",
#             "customer_code": "all",
#             "section_id": 20,
#             "section": "return to base",
#             "sequence": 90,
#             "type": "button",
#             "text": "Back at base",
#             "false_action_log": False,
#             "false_action_log_type": 0,
#             "false_action_log_type_name": "",
#             "false_action_log_text": "",
#             "false_action_log_driver_name": False,
#             "false_action_log_driver_gps": False,
#             "false_action_log_no_of_packages": False,
#             "false_action_log_customer_name": False,
#             "false_action_log_date_time": False,
#             "false_action_block": False,
#             "false_action_block_text": "",
#             "false_action_record": True,
#             "false_action_status": False,
#             "false_action_run_status": False,
#             "false_action_drop_status": False,
#             "false_action_run_status_id": 0,
#             "false_action_run_status_name": "",
#             "false_action_drop_status_id": 0,
#             "false_action_drop_status_name": "",
#             "false_action_take_photo": False,
#             "false_action_signature": False,
#             "false_action_no_action": False,
#             "true_action_log": False,
#             "true_action_log_type": 0,
#             "true_action_log_type_name": "",
#             "true_action_log_text": "",
#             "true_action_log_driver_name": False,
#             "true_action_log_driver_gps": False,
#             "true_action_log_no_of_packages": False,
#             "true_action_log_customer_name": False,
#             "true_action_log_date_time": False,
#             "true_action_block": False,
#             "true_action_block_text": "",
#             "true_action_record": True,
#             "true_action_status": True,
#             "true_action_run_status": True,
#             "true_action_drop_status": False,
#             "true_action_run_status_id": 400,
#             "true_action_run_status_name": "Underway",
#             "true_action_drop_status_id": 0,
#             "true_action_drop_status_name": "",
#             "true_action_take_photo": False,
#             "true_action_signature": False,
#             "true_action_no_action": False
#         }
#     ],
#     "days_to_delete_photos": 7,
#     "branch_photo_upload_ip": "10.1.30.7",
#     "branch_photo_upload_user": "photos",
#     "branch_photo_upload_password": "Nwb24E33DxWeZxthrQ",
#     "branch_photo_upload_directory": "/tank/delivery-photos/DeliveryTrackingSystem/",
#     "status": 200
# }
                    return Response(response_object)

                except:
                    logger.debug("Error while getting run data")
                    print(traceback.format_exc())
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Get Run Data"})
            else:
                return Response({"status": status.HTTP_406_NOT_ACCEPTABLE, "Msg": "Your Device has been revoked"})
        else:
            return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "No api is found regarding this branch"})
#----------------------------#

class UpdatedQuestionsDataAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        imei = request.GET.get('imei')
        driver_name = request.GET.get('driver_name')

        last_updated_time = request.GET.get('last_updated_time')
        print('params',last_updated_time, imei, driver_name)

        device = Device.objects.filter(device_imei_no=imei)
        if device and device[0].device_is_active is True:
            try:
                device_last_check_in = datetime.datetime.now()
                print(device_last_check_in)
                device_last_driver = driver_name
                print(device_last_driver)
                device.update(device_last_check_in=device_last_check_in, device_last_driver=device_last_driver)

                for dev in device:
                    print("devbranch:" + str(dev.branch))
                    print("devbroorg:" + str(dev.branch.organisation))
                    # branch_id = dev.branch.id
                    # org_id = dev.branch.organisation.id
                    branch_id = Q(branch=dev.branch)
                    org_id = Q(organisation=dev.branch.organisation)
                    # customer = Q(customer_code=ccode)

                    all_branch = Q(branch=None)
                    all_org = Q(organisation=None)
                    # all_customer = Q(customer_code=None)

                    questions = Question.objects.order_by("question_sequence").filter(
                        branch_id | all_branch & org_id | all_org)

                    question = []
                    for q in questions:
                        if last_updated_time is not None:

                            last_updated_utc_time = last_updated_time.split(' ')
                            print('splitting it', last_updated_utc_time)
                            # print(last_updated_utc_time[0] + ' ' + last_updated_utc_time[1])
                            # print(''.join(last_updated_utc_time[3]))
                            # print(datetime.datetime.strptime(str(last_updated_utc_time[3]), '%H:%M'))

                            local_time = str(last_updated_utc_time[0]) + ' ' + str(last_updated_utc_time[1])

                            last = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S.%f')
                            # s = c.strftime('%Y-%m-%d %H:%M:%S.%f')
                            # print(s)
                            # tail = s[-4:]
                            # f = round(float(tail), 3)
                            # temp = "%.3f" % f
                            # print((s[:-4], temp[1:]))
                            # # print(type(s[-4:]))
                            # date_time = s[:-4]
                            # print(date_time)
                            print("last updated time")
                            print(last)

                            utc_time = datetime.datetime.strptime(str(last_updated_utc_time[1]), '%H:%M:%S.%f')


                            utc_last = last - utc_time
                            print(utc_last)
                            utc_last_str = str(last_updated_utc_time[0]) + ' ' +str(utc_last).split(' ')[2]
                            print('fsjkdbfasjbaflbll934y2895y', utc_last_str)
                            utc_last_object = datetime.datetime.strptime(utc_last_str, '%Y-%m-%d %H:%M:%S')

                            updated_at = q.updated_at
                            created_at = q.created_at

                            u = updated_at.strftime('%Y-%m-%d %H:%M:%S.%f')
                            print(u)
                            tail = u[-4:]
                            f = round(float(tail), 3)
                            temp = "%.3f" % f
                            print((u[:-4], temp[1:]))
                            # print(type(s[-4:]))
                            updated_at1 = u[:-4]
                            print("updated at")
                            print(updated_at1)

                            update = datetime.datetime.strptime(updated_at1, '%Y-%m-%d %H:%M:%S.%f')
                            print("up")
                            print(update)

                            c = created_at.strftime('%Y-%m-%d %H:%M:%S.%f')
                            print(c)
                            tail = c[-4:]
                            f = round(float(tail), 3)
                            temp = "%.3f" % f
                            print((c[:-4], temp[1:]))
                            # print(type(s[-4:]))
                            created_at1 = c[:-4]
                            print("crated at")
                            print(created_at1)
                            create = datetime.datetime.strptime(created_at1, '%Y-%m-%d %H:%M:%S.%f')
                            print("cr")
                            print(create)

                            print("kasjdbfhbfsdjkf")
                            # print(q.updated_at)
                            # print(q.created_at)

                            print('Check utc time',utc_last_object)

                            if utc_last_object < update or utc_last_object < create:
                                q_id = q.id
                                print("insdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdiosdio")
                                print(q.updated_at)
                                print(q.created_at)
                                print("check this out")
                                print(datetime.datetime.now())

                                q_update = q.updated_at       #this field is extra
                                sequence = q.question_sequence
                                type = q.question_type.question_type
                                text1 = q.question_text
                                if text1 is not None:
                                    text = text1
                                else:
                                    text = ""

                                section_id = q.question_section.section_id
                                section = q.question_section.section_name

                                org_fk = q.organisation
                                if org_fk is not None:
                                    organisation = org_fk.organisation_name
                                else:
                                    organisation = "all"

                                branch_fk = q.branch
                                if branch_fk is not None:
                                    branch = branch_fk.branch_name
                                else:
                                    branch = "all"

                                customer1 = q.customer_code
                                if customer1 is not '':
                                    customer = customer1
                                else:
                                    customer = "all"

                                false_action_log_fk = q.question_false_action.question_action.question_action_log
                                if false_action_log_fk is not None:
                                    false_action_log = false_action_log_fk.question_action_log

                                    false_action_log_type_fk = q.question_false_action.question_action.question_action_log.question_action_log_type
                                    if false_action_log_type_fk is not None:
                                        question_action_log_type1 = false_action_log_type_fk.type_id
                                        question_action_log_type2 = false_action_log_type_fk.type_name
                                    else:
                                        question_action_log_type1 = 0
                                        question_action_log_type2 = ""
                                    false_action_log_type = question_action_log_type1
                                    false_action_log_type_name = question_action_log_type2

                                    false_action_log_text = false_action_log_fk.question_action_log_text
                                    false_action_log_driver_name = false_action_log_fk.question_action_log_driver_name
                                    false_action_log_driver_gps = false_action_log_fk.question_action_log_driver_gps
                                    false_action_log_packages = false_action_log_fk.question_action_log_no_of_packages
                                    false_action_log_customer_name = false_action_log_fk.question_action_log_customer_name
                                    false_action_log_date_time = false_action_log_fk.question_action_log_date_time
                                else:
                                    false_action_log = False
                                    false_action_log_type = 0
                                    false_action_log_type_name = ""
                                    false_action_log_text = ""
                                    false_action_log_driver_name = False
                                    false_action_log_driver_gps = False
                                    false_action_log_packages = False
                                    false_action_log_customer_name = False
                                    false_action_log_date_time = False
                                # print("log %s" % false_action_log)

                                false_action_block_fk = q.question_false_action.question_action.question_action_block
                                if false_action_block_fk is not None:
                                    false_action_block = false_action_block_fk.question_action_block
                                    false_action_block_text = false_action_block_fk.question_action_block_text
                                else:
                                    false_action_block = False
                                    false_action_block_text = ""
                                # print("block %s" % false_action_block)

                                false_action_record = q.question_false_action.question_action.question_action_record
                                # print("record %s" % false_action_record)

                                false_action_status_fk = q.question_false_action.question_action.question_action_status
                                if false_action_status_fk is not None:
                                    false_action_status = false_action_status_fk.question_action_status
                                    false_action_run_status = false_action_status_fk.run_status
                                    false_action_drop_status = false_action_status_fk.drop_status
                                    if false_action_run_status is True:
                                        false_action_run_status_id = false_action_status_fk.run_status_id
                                        false_action_run_status_name = false_action_status_fk.run_status_name
                                    else:
                                        false_action_run_status_id = 0
                                        false_action_run_status_name = ""
                                    if false_action_drop_status is True:
                                        false_action_drop_status_id = false_action_status_fk.drop_status_id
                                        false_action_drop_status_name = false_action_status_fk.drop_status_name
                                    else:
                                        false_action_drop_status_id = 0
                                        false_action_drop_status_name = ""
                                else:
                                    false_action_status = False
                                    false_action_run_status = False
                                    false_action_drop_status = False
                                    false_action_run_status_id = 0
                                    false_action_run_status_name = ""
                                    false_action_drop_status_id = 0
                                    false_action_drop_status_name = ""
                                # print("status %s" % false_action_status)

                                false_action_take_photo = q.question_false_action.question_action.question_action_take_photo
                                # print("photo %s" % false_action_take_photo)
                                false_action_signature = q.question_false_action.question_action.question_action_signature
                                # print("sign %s" % false_action_signature)
                                false_action_no_action = q.question_false_action.question_action.question_action_no_action
                                # print("no action %s" % false_action_no_action)

                                true_action_log_fk = q.question_true_action.question_action.question_action_log
                                if true_action_log_fk is not None:
                                    true_action_log = true_action_log_fk.question_action_log

                                    true_action_log_type_fk = true_action_log_fk.question_action_log_type
                                    if true_action_log_type_fk is not None:
                                        question_action_log_type1 = true_action_log_type_fk.type_id
                                        question_action_log_type2 = true_action_log_type_fk.type_name
                                    else:
                                        question_action_log_type1 = 0
                                        question_action_log_type2 = ""
                                    true_action_log_type = question_action_log_type1
                                    true_action_log_type_name = question_action_log_type2

                                    true_action_log_text = true_action_log_fk.question_action_log_text
                                    true_action_log_driver_name = true_action_log_fk.question_action_log_driver_name
                                    true_action_log_driver_gps = true_action_log_fk.question_action_log_driver_gps
                                    true_action_log_packages = true_action_log_fk.question_action_log_no_of_packages
                                    true_action_log_customer_name = true_action_log_fk.question_action_log_customer_name
                                    true_action_log_date_time = true_action_log_fk.question_action_log_date_time
                                else:
                                    true_action_log = False
                                    true_action_log_type = 0
                                    true_action_log_type_name = ""
                                    true_action_log_text = ""
                                    true_action_log_driver_name = False
                                    true_action_log_driver_gps = False
                                    true_action_log_packages = False
                                    true_action_log_customer_name = False
                                    true_action_log_date_time = False
                                # print("true log %s" % true_action_log)

                                true_action_block_fk = q.question_true_action.question_action.question_action_block
                                if true_action_block_fk is not None:
                                    true_action_block = true_action_block_fk.question_action_block
                                    true_action_block_text = true_action_block_fk.question_action_block_text
                                else:
                                    true_action_block = False
                                    true_action_block_text = ""
                                # print("true block %s" % true_action_block)

                                true_action_record = q.question_true_action.question_action.question_action_record
                                # print("true record %s" % true_action_record)

                                true_action_status_fk = q.question_true_action.question_action.question_action_status
                                if true_action_status_fk is not None:
                                    true_action_status = true_action_status_fk.question_action_status
                                    true_action_run_status = true_action_status_fk.run_status
                                    true_action_drop_status = true_action_status_fk.drop_status
                                    if true_action_run_status is True:
                                        true_action_run_status_id = true_action_status_fk.run_status_id
                                        true_action_run_status_name = true_action_status_fk.run_status_name
                                    else:
                                        true_action_run_status_id = 0
                                        true_action_run_status_name = ""
                                    if true_action_drop_status is True:
                                        true_action_drop_status_id = true_action_status_fk.drop_status_id
                                        true_action_drop_status_name = true_action_status_fk.drop_status_name
                                    else:
                                        true_action_drop_status_id = 0
                                        true_action_drop_status_name = ""

                                else:
                                    true_action_status = False
                                    true_action_run_status = False
                                    true_action_drop_status = False
                                    true_action_run_status_id = 0
                                    true_action_run_status_name = ""
                                    true_action_drop_status_id = 0
                                    true_action_drop_status_name = ""
                                # print("true status %s" % true_action_status)

                                true_action_take_photo = q.question_true_action.question_action.question_action_take_photo
                                # print("true photo %s" % true_action_take_photo)
                                true_action_signature = q.question_true_action.question_action.question_action_signature
                                # print("true sign %s" % true_action_signature)
                                true_action_no_action = q.question_true_action.question_action.question_action_no_action
                                # print("true no action %s" % true_action_no_action)

                                result1 = {
                                    "question_id": q_id,
                                    "organisation": organisation,
                                    "branch": branch,
                                    "customer_code": customer,
                                    "section_id": section_id,
                                    "section": section,
                                    "sequence": sequence,
                                    "type": type,
                                    "text": text,

                                    "false_action_log": false_action_log,
                                    "false_action_log_type": false_action_log_type,
                                    "false_action_log_type_name": false_action_log_type_name,
                                    "false_action_log_text": false_action_log_text,

                                    "false_action_log_driver_name": false_action_log_driver_name,
                                    "false_action_log_driver_gps": false_action_log_driver_gps,
                                    "false_action_log_no_of_packages": false_action_log_packages,
                                    "false_action_log_customer_name": false_action_log_customer_name,
                                    "false_action_log_date_time": false_action_log_date_time,

                                    "false_action_block": false_action_block,
                                    "false_action_block_text": false_action_block_text,

                                    "false_action_record": false_action_record,

                                    "false_action_status": false_action_status,
                                    "false_action_run_status": false_action_run_status,
                                    "false_action_drop_status": false_action_drop_status,
                                    "false_action_run_status_id": false_action_run_status_id,
                                    "false_action_run_status_name": false_action_run_status_name,
                                    "false_action_drop_status_id": false_action_drop_status_id,
                                    "false_action_drop_status_name": false_action_drop_status_name,

                                    "false_action_take_photo": false_action_take_photo,

                                    "false_action_signature": false_action_signature,

                                    "false_action_no_action": false_action_no_action,

                                    "true_action_log": true_action_log,
                                    "true_action_log_type": true_action_log_type,
                                    "true_action_log_type_name": true_action_log_type_name,
                                    "true_action_log_text": true_action_log_text,

                                    "true_action_log_driver_name": true_action_log_driver_name,
                                    "true_action_log_driver_gps": true_action_log_driver_gps,
                                    "true_action_log_no_of_packages": true_action_log_packages,
                                    "true_action_log_customer_name": true_action_log_customer_name,
                                    "true_action_log_date_time": true_action_log_date_time,

                                    "true_action_block": true_action_block,
                                    "true_action_block_text": true_action_block_text,

                                    "true_action_record": true_action_record,

                                    "true_action_status": true_action_status,
                                    "true_action_run_status": true_action_run_status,
                                    "true_action_drop_status": true_action_drop_status,
                                    "true_action_run_status_id": true_action_run_status_id,
                                    "true_action_run_status_name": true_action_run_status_name,
                                    "true_action_drop_status_id": true_action_drop_status_id,
                                    "true_action_drop_status_name": true_action_drop_status_name,

                                    "true_action_take_photo": true_action_take_photo,

                                    "true_action_signature": true_action_signature,

                                    "true_action_no_action": true_action_no_action,
                                    "updated_time" : q_update # extra field

                                }

                                question.append(result1)
                        else:
                            return Response({"status": status.HTTP_406_NOT_ACCEPTABLE, "Msg": "No question is updated regarding this device"})

                deleted_qs = DeletedQuestion.objects.order_by("updated_at").all()
                deleted_questions = []
                for deleted_q in deleted_qs:

                    if last_updated_time is not None:

                        last_updated_utc_time = last_updated_time.split(' ')
                        # print('splitting it', last_updated_utc_time)
                        # print(last_updated_utc_time[0] + ' ' + last_updated_utc_time[1])
                        # print(''.join(last_updated_utc_time[3]))
                        # print(datetime.datetime.strptime(str(last_updated_utc_time[3]), '%H:%M'))

                        local_time = str(last_updated_utc_time[0]) + ' ' + str(last_updated_utc_time[1])

                        deleted_last = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S.%f')
                        print("last updated time")
                        print(deleted_last)

                        deleted_updated_at = deleted_q.updated_at

                        d_u = deleted_updated_at.strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(d_u)
                        tail = d_u[-4:]
                        d_f = round(float(tail), 3)
                        d_temp = "%.3f" % d_f
                        print((d_u[:-4], d_temp[1:]))
                        # print(type(s[-4:]))
                        deleted_updated_at1 = d_u[:-4]
                        print("deleted updated at")
                        print(deleted_updated_at1)

                        deleted_update = datetime.datetime.strptime(deleted_updated_at1, '%Y-%m-%d %H:%M:%S.%f')
                        print("deleted up")
                        print(deleted_update)

                        if deleted_last < deleted_update:
                            deleted_q_id = deleted_q.question_id

                            result6 = {
                                "question_id": deleted_q_id,
                                "status": status.HTTP_204_NO_CONTENT,
                                "Msg": "This Question is Deleted"
                            }
                            deleted_questions.append(result6)

                    else:
                        return Response({"status": status.HTTP_406_NOT_ACCEPTABLE,
                                         "Msg": "No question is deleted regarding this device"})

                return Response({"questions":question, "deleted_questions": deleted_questions, "status": status.HTTP_200_OK})

            except:
                logger.debug("Error while getting run data")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Get Run Data"})
        else:
            return Response({"status": status.HTTP_406_NOT_ACCEPTABLE, "Msg": "Your Device has been revoked"})

class QuestionPhotoAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request):
        run_id = request.POST.get('run_id')
        print(run_id)
        run_id = str(run_id)
        print(run_id)
        print(type(run_id))
        drop_id = request.POST.get('drop_id')
        print(drop_id)
        drop_id = str(drop_id)
        print(drop_id)
        print(type(drop_id))
        file = request.FILES.get('file')
        print(file)
        try:
            if file and run_id and drop_id:
                new_photo = Photo.objects.create(file=file, run_id=run_id, drop_id=drop_id)
                print(type(new_photo))
                photo_id = new_photo.id
                # print(new_photo_id)
                # print(type(new_photo))
                # photo = Photo.objects.filter(pk=new_photo_id)
                # photo_id = photo[0].id
                # print(photo_id)
                # print(type(photo_id))
                print("photo is uploading")
                return Response({"status": status.HTTP_200_OK, "photo_id": photo_id, "Msg": "Your data has been uploaded successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Parameters missing"})
        except:
            logger.debug("Error while saving response")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Saving Response"})

    # def get(self, request):
    #     data = request.body.decode('utf-8')
    #     print("before data")
    #     print(data)
    #     data = json.loads(data)
    #     print("after data")
    #     print(data)
    #     print(data['data'])
    #     print(type(data))
    #
    #     photos = Photo.objects.order_by("created_at").all()
    #     pics = []
    #     try:
    #         for url in data['urls']:
    #             # q_id = answers['q_id']
    #             run_id_check = url['runId']
    #             print("run")
    #             print(run_id)
    #
    #             drop_id_check = url['dropId']
    #             print("drop")
    #             print(drop_id)
    #
    #             file_check = url['file']
    #             # file_check = str(file_check)
    #             print("file")
    #             print(file)
    #
    #         for photo in photos:
    #             if photo.is_uploaded is True:
    #                 photo_id = photo.id
    #                 run_id = photo.run_id
    #                 drop_id = photo.drop_id
    #                 file = str(photo.file)
    #
    #                 if run_id == run_id_check and drop_id == drop_id_check and file == file_check:
    #                     result2 = {
    #                         "photo_id": photo_id,
    #                         "run_id": run_id,
    #                         "drop_id": drop_id,
    #                         "file": file
    #                     }
    #
    #                     pics.append(result2)
    #
    #         return Response({"uploaded_photos": pics, "status": status.HTTP_200_OK})
    #     except:
    #         logger.debug("Error while retrieving photos")
    #         print(traceback.format_exc())
    #         return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Photos"})

class QuestionPhotoCheckAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request):
        data = request.body.decode('utf-8')
        print("before data")
        print(data)
        data = json.loads(data)
        print("after data")
        print(data)
        print(data['data'])
        print(type(data))

        photos = Photo.objects.order_by("created_at").all()
        pics = []
        try:
            for url in data['data']:
                # q_id = answers['q_id']
                photo_id_check = url['photoId']
                print("Photo")
                print(photo_id_check)
                print(type(photo_id_check))

                for photo in photos:
                    if photo.is_uploaded is True:
                        photo_id = photo.id
                        if photo_id == photo_id_check:
                            picture_checked = Photo.objects.filter(pk=photo_id)
                            print(picture_checked)
                            picture_checked.update(is_checked=True)
                            print(picture_checked)
                            print("into if")
                            run_id = photo.run_id
                            drop_id = photo.drop_id
                            file = str(photo.file)
                            f = file.split("/")
                            filename = f[1]
                            print(type(filename))
                            print("db_file")
                            print(filename)

                            result2 = {
                                "photo_id": photo_id,
                                "run_id": run_id,
                                "drop_id": drop_id,
                                "file": filename
                            }

                            pics.append(result2)

            return Response({"uploaded_photos": pics, "status": status.HTTP_200_OK})
        except:
            logger.debug("Error while retrieving photos")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Photos"})


class QuestionAnswerAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request):
        data = request.body.decode('utf-8')
        print("before data =>>>>>>>>>")
        # print(data)
        data = json.loads(data)
        driver_name = data["data"][0]["driver_name"] if data["data"] and data["data"][0] else ""
        device_id =  data["data"][0]["device_id"] if data["data"] and data["data"][0] else ""
        device = Device.objects.filter(device_imei_no=device_id).first()
        branch_id = device.branch_id if device else None
        branch = Branch.objects.filter(id=branch_id).first()
        # print("driver name", data["data"][0]["driver_name"])
        # print("device is ", data["data"][0]["device_id"])
        print("device is ======>>>>>>>", type(device))

        try:
            for answers in data['data']:
                q_id = answers['qId']
                print("q")
                print(q_id)

                record_type = answers['recordType']
                record_type = True if record_type == 'true' else False
                print("record_type")
                print(record_type)

                log_type1 = answers['logType1']
                log_type1 = True if log_type1 == 'true' else False
                print("log_type1")
                print(log_type1)

                run_id = answers['runId']
                print("run")
                print(run_id)

                drop_id = answers['dropId']
                print("drop")
                print(drop_id)

                question_text = answers['questionText']
                print("question_text")
                print(question_text)
                question_text = None if question_text == '' else question_text

                question_section = answers['section']
                print("question_section")
                print(question_section)
                question_section = None if question_section == '' else question_section

                question_answer = answers['qAnswer']
                print("question_answer")
                print(question_answer)

                question_answer = True if question_answer == 'true' else False
                print("question_answer")
                print(question_answer)

                question_data = answers['questionData']
                print("question_data")
                print(question_data)

                answer_date_time = answers['dateTime']
                print("answer_date_time")
                print(answer_date_time)

                # type = answers['type']
                log_type = answers['logType']
                print("log_type")
                print(log_type)
                print("type of log type  here")
                print(type(log_type))
                log_type = '0' if log_type == '0' or log_type == "" else log_type
                log_type = int(log_type)

                log_text = answers['logText']
                print("log_text")
                print(log_text)
                log_text = None if log_text == '' else log_text


                log_date_time = answers['dateTime']
                print("log_date_time")
                print(log_date_time)
                log_date_time = None if log_date_time == '' else log_date_time

                status_old = answers['statusOld']
                print("status_old")
                print(status_old)

                status_new = answers['statusNew']
                print("status_new")
                print(status_new)

                if (record_type and run_id and question_section and question_text) or (log_type1 and run_id and log_date_time and log_type and log_text):
                    if record_type is True and run_id and question_section is not None and question_text is not None:
                        print("response")
                        # q_params = Q(q_id=q_id)
                        # run_params = Q(run_id=run_id)
                        # drop_params = Q(drop_id=drop_id)
                        # if QuestionResponse.objects.filter(q_params & run_params & drop_params).exists():
                        #     continue
                        # else:
                        QuestionResponse.objects.create(q_id=q_id, run_id=run_id, drop_id=drop_id,
                                                        question_section=question_section, question_text=question_text,
                                                        question_answer=question_answer,
                                                        question_data=question_data, answer_date_time=answer_date_time,
                                                        driver_name=driver_name, branch_id=branch)
                    # return Response({"status": status.HTTP_200_OK, "Msg": "Your answer is saved"})
                # else:
                #     return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Parameters missing"})

                # if log_date_time and log_type and log_text:
                    if log_type1 is True and run_id and log_date_time is not None and log_type is not 0 and log_text is not None:
                        print("log")
                        # q_params = Q(q_id=q_id)
                        # run_params = Q(run_id=run_id)
                        # drop_params = Q(drop_id=drop_id)
                        # if QuestionLog.objects.filter(q_params & run_params & drop_params).exists():
                        #     continue
                        # else:
                        QuestionLog.objects.create(run_id=run_id, drop_id=drop_id, log_date_time=log_date_time,
                                                log_type=log_type, status_old=status_old, status_new=status_new, log_text=log_text)
                else:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Parameters Missing."})
            return Response({"status": status.HTTP_200_OK, "Msg": "Your data has been uploaded successfully."})
                # else:
                #     return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Parameters missing"})
        except:
            logger.debug("Error while saving response")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Saving Response"})

# def get(self, response):
#     items = []
#
#     request = Request("http://61.69.119.183:80/KJWeb/transport/api/get_run_list.php", callback=self.parseDescription1)
#     request.meta['item'] = item
#     yield request
#
#     request = Request("http://61.69.119.183:80/KJWeb/transport/api/get_run_info.php", callback=self.parseDescription2, meta={'item': item})
#     yield request
#
#
# def parseDescription1(self, response):
#     item = response.meta['item']
#     item['desc1'] = "test"
#     return item
#
#
# def parseDescription2(self, response):
#     item = response.meta['item']
#     item['desc2'] = "test2"
#     return item


class RunInfoAPIView(APIView):

    def get(self, request):
        # run_id = request.GET.get('run_id')

        data = {
            "authentication": {"device_id": "1234567892",
            "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",},
            # "run_id": "1002",
            # "drop_id": "1022244",
            # "log_date_time": "2018-02-19 14:02:42.22",
            # "log_type": "CHANGE",
            # "status_old": "100",
            # "status_new": "150",
            # "log_text": "Status changed from NEW to EN-ROUTE"
            "run_id": "1002",
            "log_date_time": "2018-02-19 14:02:42.22"

        }

        # or we can write it like data = json.dumps(data)
        response = requests.post('http://61.69.119.183:80/KJWeb/transport/api/get_log_entry.php', json=data)

        # printing the output
        print(response.json())

        return Response(response.json())

# class RunAPIView(APIView):
#
#     def get(self, request):
#         run_list_response = requests.get('https://private-92563b-getrunlist.apiary-mock.com/questions')
#         run_list = run_list_response.json()
#         print(run_list)
#         print(type(run_list))
#
#         return Response(run_list)

class RunDetailAPIView(APIView):

    def get(self, request):
        # answers = QuestionResponse.objects.order_by("created_at").all()
        # for answer in answers:
        #     try:
        #         if answer.is_not_uploaded is True:
        #             run_id = answer.run_id
        #             drop_id = answer.drop_id
        #             # if drop_id is "0":
        #             #     drop_id = ""
        #             question_section = answer.question_section
        #             question_text = answer.question_text
        #             question_answer = answer.question_answer
        #             question_answer = "TRUE" if question_answer == True else "FALSE"
        #             # if question_answer is None:
        #             #     question_answer = ""
        #             print(question_answer)
        #             question_data = answer.question_data
        #             if question_data is None:
        #                 question_data = ""
        #
        #             if drop_id is not "0" and question_answer is not None:
        #                 data = {
        #                     "authentication": {"device_id": "1234567892",
        #                                        "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
        #                     "run_id": run_id,
        #                     "drop_id": drop_id,
        #                     "question_section": question_section,
        #                     "question_text": question_text,
        #                     "question_answer": question_answer,
        #                     "question_data": question_data,
        #                 }
        #                 # or we can write it like data = json.dumps(data)
        #                 response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
        #                                           json=data)
        #
        #             elif drop_id is not "0" and question_answer is None:
        #                 data = {
        #                     "authentication": {"device_id": "1234567892",
        #                                        "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
        #                     "run_id": run_id,
        #                     "drop_id": drop_id,
        #                     "question_section": question_section,
        #                     "question_text": question_text,
        #                     "question_data": question_data,
        #                 }
        #                 # or we can write it like data = json.dumps(data)
        #                 response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
        #                                           json=data)
        #
        #             elif drop_id is "0" and question_answer is not None:
        #                 print("runnning")
        #                 data = {
        #                     "authentication": {
        #                         "device_id": "1234567892",
        #                         "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie"
        #                     },
        #                     "run_id": run_id,
        #                     # "drop_id": "348220",
        #                     "question_section": question_section,
        #                     "question_text": question_text,
        #                     "question_answer": question_answer,
        #                     "question_data": question_data,
        #                     # "run_id": "1002",
        #                     # "drop_id": "348220",
        #                     # "question_section": "Before_Departure",
        #                     # "question_text": "Do you have all the pieces?",
        #                     # "question_answer": "TRUE",
        #                     # "question_data": ""
        #                 }
        #                 # or we can write it like data = json.dumps(data)
        #                 response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
        #                                           json=data)
        #                 print("check this")
        #                 print(response1.json())
        #
        #             else:
        #                 data = {
        #                     "authentication": {"device_id": "1234567892",
        #                                        "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
        #                     "run_id": run_id,
        #                     "question_section": question_section,
        #                     "question_text": question_text,
        #                     "question_data": question_data,
        #                 }
        #                 # or we can write it like data = json.dumps(data)
        #                 response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
        #                                           json=data)
        #
        #             print(response1)
        #             print("ok")
        #             response = response1.json()
        #             print(response)
        #             # if response['id'] and response['log_date_time']:
        #             if response:
        #                 if response['id'] and response['log_date_time']:
        #                     print("if part")
        #                     answer_id = answer.id
        #                     print("This is id")
        #                     print(answer_id)
        #                     answer_sent = QuestionResponse.objects.filter(pk=answer_id)
        #                     answer_sent.update(is_not_uploaded=False)
        #                     answer_sent.update(is_uploaded=True)
        #                     # logger.info("Uploaded Logs Data")
        #                 elif response['error']:
        #                     print("else error part")
        #                     continue
        #                 else:
        #                     print("else part")
        #                     return Response({"Msg": "All Data is uploaded"})
        #         return Response(response)
        #     except:
        #         logger.debug("Error while uploading answers data")
        #         print(traceback.format_exc())
        #         return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Upload Answer Data"})
        imei = request.GET.get('imei')
        device = Device.objects.filter(device_imei_no=imei)
        branch_api_server_ip = device[0].branch.branch_api_server_ip

        logs = QuestionLog.objects.order_by("-created_at").all()
        if branch_api_server_ip is not None:
            for log in logs:
                try:
                    if log.is_not_uploaded is True:
                        run_id = log.run_id
                        drop_id = log.drop_id
                        log_date_time = log.log_date_time
                        print("is it right or not?")
                        print(log_date_time)

                        s = log_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        # print(log_date_time)
                        # print(date_time[0])
                        print(log.id)
                        log_type = str(log.log_type)

                        status_old = log.status_old
                        status_new = log.status_new
                        log_text = log.log_text

                        if drop_id is not "0" and status_old is not None and status_new is not None:
                            print("no none")
                            data = {
                                "authentication": {"device_id": "1234567892",
                                                   "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
                                "run_id": run_id,
                                "drop_id": drop_id,
                                "log_date_time": date_time,
                                "log_type": log_type,
                                "status_old": status_old,
                                "status_new": status_new,
                                "log_text": log_text,
                            }
                            print(data)
                            # or we can write it like data = json.dumps(data)
                            response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/add_log_entry.php',
                                                      json=data)

                        elif drop_id is not "0" and status_old is None and status_new is None:
                            print("drop no none")
                            data = {
                                "authentication": {"device_id": "1234567892",
                                                   "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
                                "run_id": run_id,
                                "drop_id": drop_id,
                                "log_date_time": date_time,
                                "log_type": log_type,
                                "log_text": log_text,
                            }
                            # or we can write it like data = json.dumps(data)
                            response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/add_log_entry.php',
                                                      json=data)

                        elif drop_id is "0" and status_old is not None and status_new is not None:
                            print("drop none")
                            data = {
                                "authentication": {
                                    "device_id": "1234567892",
                                    "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie"
                                },
                                "run_id": run_id,
                                "log_date_time": date_time,
                                "log_type": log_type,
                                "status_old": status_old,
                                "status_new": status_new,
                                "log_text": log_text,
                            }
                            # or we can write it like data = json.dumps(data)
                            response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/add_log_entry.php',
                                                      json=data)
                            print("check this")
                            print(response1.json())

                        else:
                            print("all none")
                            data = {
                                "authentication": {"device_id": "1234567892",
                                                   "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
                                "run_id": run_id,
                                "log_date_time": date_time,
                                "log_type": log_type,
                                "log_text": log_text,
                            }
                            # or we can write it like data = json.dumps(data)
                            response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/add_log_entry.php',
                                                      json=data)

                        print(response1)
                        print("ok")
                        response = response1.json()
                        print(response)
                        # if response['id'] and response['log_date_time']:
                        if response:
                            if response['id'] and response['log_date_time']:
                                print("if part")
                                log_id = log.id
                                print("This is id")
                                print(log_id)
                                log_sent = QuestionLog.objects.filter(pk=log_id)
                                log_sent.update(is_not_uploaded=False)
                                log_sent.update(is_uploaded=True)
                                # logger.info("Uploaded Logs Data")
                            elif response['error']:
                                print("else error part")
                                continue
                            else:
                                print("else part")
                                return Response({"Msg": "All Data is uploaded"})
                    # else:
                    #     return Response({"Msg": "All Data is uploaded to runsheet"})
                        return Response(response)

                except:
                    logger.debug("Error while uploading logs data")
                    print(traceback.format_exc())
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Upload Logs Data"})
            # return Response(response)
        else:
            return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "No api is found regarding this branch"})

# class DropAPIView(APIView):
#
#     def get(self, request):
#         run_info_response = requests.get('https://private-91e99-getruninfo1.apiary-mock.com/questions')
#         run_info = run_info_response.json()
#         print(run_info)
#         print(type(run_info))
#
#         return Response(run_info)

# User = get_user_model()

# class UserLoginAPIView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserLoginSerializer
#
#     def post(self, request):
#         data = request.data
#         serializer = UserLoginSerializer(data=data)
#         if serializer.is_valid(raise_exception=True):
#             new_data = serializer.data
#             return Response(new_data, status = status.HTTP_200_OK)
#         return Response(serializer.error, status= status.Http_404_BAD_REQUEST)

# @method_decorator([login_required, superuser_required], name='dispatch')
class UserRegisterAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_superuser = request.POST.get('is_superuser')
        is_organisation_admin = request.POST.get('is_organisation_admin')
        is_branch_admin = request.POST.get('is_branch_admin')
        is_branch_view = request.POST.get('is_branch_view')
        is_branch_user = False
        print("check check")

        org_id = request.POST.get('org_id')
        if org_id:
            orgs = Organisation.objects.filter(pk=org_id)
            for orga in orgs:
                if orga.organisation_is_active is True:
                    org = orga
        else:
            org = None

        # print(org)

        branch_id = request.POST.get('branch_id')
        if branch_id:
            branches = Branch.objects.filter(pk=branch_id)
            for branc in branches:
                if branc.branch_is_active is True:
                    branch = branc
        else:
            branch = None

        print(branch)

        is_super = False
        if is_superuser == 'True':
            is_super = True
        is_org = False
        if is_organisation_admin == 'True':
            is_org = True
        is_branch = False
        if is_branch_admin == 'True':
            is_branch = True
        
        if is_branch_view == 'True':
            is_branch_user = True

        if User.objects.filter(username=username).exists():
            return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "The user with this username already exists."})
        elif User.objects.filter(email=email).exists():
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "Msg": "The user with this email already exists."})
        else:
            if username and email and password:
                try:
                    # user = authenticate(username=username, email=email, password=password)
                    # print(user)
                    print("email:" + email)
                    print("Password:" + password)

                    pwd = make_password(password)
                    print("this is my password: " + pwd)
                    check = check_password(password, pwd)
                    print("this is my check password.")
                    print(check)
                    user = User.objects.create(username=username, email=email, password=pwd, first_name=first_name, last_name=last_name, is_superuser= is_super, is_organisation_admin=is_org, is_branch_admin=is_branch, organisation=org, branch=branch, is_branch_user=is_branch_user)
                    role = User.objects.filter(username=username)
                    if is_org is True and org is not None:
                        org_obj = role[0].organisation
                        OrganisationAdmins.objects.create(user=role[0], organisation=org_obj)
                    if is_branch is True and branch is not None:
                        branch_obj = role[0].branch
                        BranchAdmins.objects.create(user=role[0], branch=branch_obj)
                    
                    if is_branch_user is True and branch is not None:
                        branch_obj = role[0].branch
                        BranchUsers.objects.create(user=role[0], branch=branch_obj)

                    check1 = user.check_password(password)
                    print("this is my 2nd check password.")
                    print(check1)
                    print(last_name)
                    print ("Can i get user id of new user registered" + str(user.id))
                    # user, created = User.objects.get_or_create(username=username, email=email)
                    # if created:
                    # user.set_password(password)  # This line will hash the password
                    # print(user.set_password(password))
                    # user.save()  # DO NOT FORGET THIS LINE

                    django_login(request, user)
                    token, created = Token.objects.get_or_create(user=user)
                    print("Token:" + token.key)
                    return Response({"status":status.HTTP_200_OK})

                except:
                    logger.debug("Error while registering user")
                    print(traceback.format_exc())
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Register User"})
            else:
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Must provide username, email and password. These are all required fields"})


class UserLoginAPIView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if username and password:
            print(username)
            print(password)
            try:
                user = User.objects.filter(username=username)
                print('logging in')
                print(username)
                print(user)
                print(password)
                if user:
                    # if user.is_active:
                    #     # data["user"] = user
                    if user[0].check_password(password):
                        print(user)
                        print(user[0].check_password(password))
                        django_login(request, user[0])

                        token = Token.objects.filter(user=user[0])
                        print(token)
                        if token.exists():
                            pk = request.user.pk
                            name = request.user.username
                            first_name = request.user.first_name
                            last_name = request.user.last_name
                            is_superuser = request.user.is_superuser
                            is_organisation_admin = request.user.is_organisation_admin
                            is_branch_admin = request.user.is_branch_admin
                            is_revoked = request.user.is_revoked
                            is_branch_user = request.user.is_branch_user

                            return Response({"user_id": pk,"username": name,"first_name": first_name,"last_name": last_name,
                                             "token": token[0].key, "is_superuser": is_superuser, "is_organisation_admin": is_organisation_admin,
                                             "is_branch_admin": is_branch_admin, "is_revoked": is_revoked, "is_branch_user": is_branch_user, "status": status.HTTP_200_OK})
                        else:
                            if request.user.is_superuser is True:
                                token, created = Token.objects.get_or_create(user=user)
                                print("Token:" + token.key)
                                pk = request.user.pk
                                name = request.user.username
                                first_name = request.user.first_name
                                last_name = request.user.last_name
                                is_superuser = request.user.is_superuser
                                is_organisation_admin = request.user.is_organisation_admin
                                is_branch_admin = request.user.is_branch_admin
                                is_revoked = request.user.is_revoked
                                is_branch_user = request.user.is_branch_user

                                return Response(
                                    {"user_id": pk, "username": name, "first_name": first_name, "last_name": last_name,
                                     "token": token.key, "is_superuser": is_superuser,
                                     "is_organisation_admin": is_organisation_admin, "is_branch_admin": is_branch_admin,
                                     "is_revoked": is_revoked,"is_branch_user": is_branch_user, "status": status.HTTP_200_OK})

                            elif request.user.is_organisation_admin is True:
                                token, created = Token.objects.get_or_create(user=user)
                                print("Token:" + token.key)
                                pk = request.user.pk
                                name = request.user.username
                                first_name = request.user.first_name
                                last_name = request.user.last_name
                                is_superuser = request.user.is_superuser
                                is_organisation_admin = request.user.is_organisation_admin
                                is_branch_admin = request.user.is_branch_admin
                                is_revoked = request.user.is_revoked
                                is_branch_user = request.user.is_branch_user

                                return Response(
                                    {"user_id": pk, "username": name, "first_name": first_name, "last_name": last_name,
                                     "token": token.key, "is_superuser": is_superuser,
                                     "is_organisation_admin": is_organisation_admin, "is_branch_admin": is_branch_admin,
                                     "is_revoked": is_revoked, "is_branch_user": is_branch_user, "status": status.HTTP_200_OK})

                            elif request.user.is_branch_admin is True:
                                token, created = Token.objects.get_or_create(user=user)
                                print("Token:" + token.key)
                                pk = request.user.pk
                                name = request.user.username
                                first_name = request.user.first_name
                                last_name = request.user.last_name
                                is_superuser = request.user.is_superuser
                                is_organisation_admin = request.user.is_organisation_admin
                                is_branch_admin = request.user.is_branch_admin
                                is_revoked = request.user.is_revoked
                                is_branch_user = request.user.is_branch_user

                                return Response(
                                    {"user_id": pk, "username": name, "first_name": first_name, "last_name": last_name,
                                     "token": token.key, "is_superuser": is_superuser,
                                     "is_organisation_admin": is_organisation_admin, "is_branch_admin": is_branch_admin,
                                     "is_revoked": is_revoked, "is_branch_user": is_branch_user, "status": status.HTTP_200_OK})
                            else:
                                return Response({"status": status.HTTP_401_UNAUTHORIZED, "Msg": "This user is revoked"})

                        # if user is is_organisation_admin:  # just a sudo code
                        #     return HttpResponseRedirect('org-dashboard')
                        # elif user is is_branch_admin:
                        #     return HttpResponseRedirect('branch-dashboard')
                        # else:
                        # # may be here you want to redirect somewhere
                        # # if not a organisation_admin or branch_admin

                        # return Response({"token": token.key}, status=status.HTTP_200_OK)
                        # else:
                        #     return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "User is not lgged in"})

                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Password Is Incorrect"})
                    # else:
                    #     msg = "User is deactivated."
                    #     raise exceptions.ValidationError(msg)
                        # return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Change Password baby"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "Unable to login with given credentials."})
            except:
                logger.debug("Error while logging in")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Logged In"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "Must provide username and password both."})

class UserRoleAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:

                    super_param = Q(is_superuser=True)
                    org_admin_param = Q(is_organisation_admin=True)
                    branch_admin_pram = Q(is_branch_admin=True)
                    revoke_pram = Q(is_revoked=True)
                    branch_user = Q(is_branch_user=True)
                    users = User.objects.order_by("-created_at").filter(super_param | org_admin_param | branch_admin_pram | revoke_pram | branch_user)

                    # total_users = users.count()
                    # print(total_users)
                    # user_page = Paginator(users, 50)
                    # # if page_size:
                    # #     quest = Paginator(users, page_size)
                    # page = request.GET.get('page')
                    # # ques = quest.page(page)
                    # print(page)
                    #
                    # try:
                    #     us = user_page.page(page)
                    # except PageNotAnInteger:
                    #     us = user_page.page(1)
                    # except EmptyPage:
                    #     us = user_page.page(user_page.num_pages)
                    #
                    # has_next = us.has_next()
                    # if has_next is True:
                    #     next_page_number = us.next_page_number()
                    # else:
                    #     next_page_number = "There is no next page. This is the last page"
                    # print(next_page_number)
                    #
                    # has_previous = us.has_previous()
                    # if has_previous is True:
                    #     previous_page_number = us.previous_page_number()
                    # else:
                    #     previous_page_number = "There is no previous page. This is the first page"
                    # print(previous_page_number)

                    all_users = []
                    for u in users:
                        u_id = u.id
                        username = u.username
                        first_name = u.first_name
                        last_name = u.last_name
                        is_super_admin = u.is_superuser
                        is_org_admin = u.is_organisation_admin
                        is_branch_admin = u.is_branch_admin
                        is_revoked = u.is_revoked
                        is_branch_user = u.is_branch_user

                        if int(user_id) != u_id:
                            user_orgs = []
                            if is_org_admin is True:
                                org_admin = OrganisationAdmins.objects.filter(user=u_id)
                                for orgs in org_admin:
                                    orgs_id = orgs.organisation.id
                                    org = Organisation.objects.order_by("-created_at").filter(pk=orgs_id)
                                    for orga in org:
                                        if orga.organisation_is_active is True:
                                            org_id = orga.id
                                            org_name = orga.organisation_name
                                            org_logo = orga.organisation_logo
                                            result3 = {
                                                "org_id": org_id,
                                                "org_name": org_name,
                                                "org_logo": str(org_logo),
                                            }

                                            user_orgs.append(result3)

                            user_branches = []
                            if is_branch_admin is True:
                                branch_admin = BranchAdmins.objects.filter(user=u_id)
                                print("getting branch for ", username, branch_admin)
                                print("user id is ", u_id)
                                for branches in branch_admin:
                                    branches_id = branches.branch.id
                                    branch = Branch.objects.order_by("-created_at").filter(pk=branches_id)
                                    for branc in branch:
                                        if branc.branch_is_active is True:
                                            org_id = branc.organisation.id
                                            org_name = branc.organisation.organisation_name
                                            branch_id = branc.id
                                            branch_name = branc.branch_name
                                            result4 = {
                                                "org_id": org_id,
                                                "org_name": org_name,
                                                "branch_id": branch_id,
                                                "branch_name": branch_name,
                                            }

                                            user_branches.append(result4)
                            if is_branch_user is True:
                                branch_admin = BranchUsers.objects.filter(user=u_id)
                                
                                
                                for branches in branch_admin:
                                    branches_id = branches.branch.id
                                    branch = Branch.objects.order_by("-created_at").filter(pk=branches_id)
                                    for branc in branch:
                                        if branc.branch_is_active is True:
                                            org_id = branc.organisation.id
                                            org_name = branc.organisation.organisation_name
                                            branch_id = branc.id
                                            branch_name = branc.branch_name
                                            result5 = {
                                                "org_id": org_id,
                                                "org_name": org_name,
                                                "branch_id": branch_id,
                                                "branch_name": branch_name,
                                            }

                                            user_branches.append(result5)

                            
                            result1 = {
                                "user_id": u_id,
                                "username": username,
                                "first_name": first_name,
                                "last_name": last_name,
                                "is_super_admin": is_super_admin,
                                "is_org_admin": is_org_admin,
                                "user_orgs": user_orgs,
                                "is_branch_admin": is_branch_admin,
                                "user_branches": user_branches,
                                "is_revoked": is_revoked,
                                "is_branch_user": is_branch_user
                            }

                            all_users.append(result1)

                    orgs = Organisation.objects.order_by("-created_at").all()
                    all_orgs = []
                    for org in orgs:
                        if org.organisation_is_active is True:
                            org_id = org.id
                            org_name = org.organisation_name
                            org_logo = org.organisation_logo
                            result2 = {
                                "org_id": org_id,
                                "org_name": org_name,
                                "org_logo": str(org_logo),
                            }

                            all_orgs.append(result2)

                    return Response({"organisations": all_orgs, "users": all_users, "status": status.HTTP_200_OK})
                    # "users": all_users, "has_next": has_next,
                    #         "has_previous": has_previous,
                    #         "next_page_number": next_page_number,
                    #         "previous_page_number": previous_page_number,
                    #         "total_users": total_users

                elif request.user.is_active and request.user.is_organisation_admin:
                    org_admin = OrganisationAdmins.objects.order_by("-created_at").filter(user=user_id)
                    # org_id = org_admin[0].organisation.id
                    all_users = []
                    all_orgs = []
                    user_ids = []
                    for orga_admin in org_admin:

                        if orga_admin.organisation.organisation_is_active is True:
                            org_id = orga_admin.organisation.id
                            org_name = orga_admin.organisation.organisation_name
                            org_logo = orga_admin.organisation.organisation_logo
                            result2 = {
                                "org_id": org_id,
                                "org_name": org_name,
                                "org_logo": str(org_logo),
                            }

                            all_orgs.append(result2)
                            print(org_id)
                            branches = Branch.objects.filter(organisation=org_id)
                            for branch in branches:
                                branch_id = branch.id
                                branch_admins = BranchAdmins.objects.filter(branch=branch_id)
                                for branch_admin in branch_admins:
                                    u_id = branch_admin.user.id
                                    users = User.objects.order_by("-created_at").filter(pk=u_id)
                                    print(users)
                                    # total_users = total_users + 1
                                    # print(total_users)

                                    # user_page = Paginator(users, 5)
                                    # # if page_size:
                                    # #     quest = Paginator(users, page_size)
                                    # page = request.GET.get('page')
                                    # # ques = quest.page(page)
                                    # print(page)
                                    #
                                    # try:
                                    #     us = user_page.page(page)
                                    # except PageNotAnInteger:
                                    #     us = user_page.page(1)
                                    # except EmptyPage:
                                    #     us = user_page.page(user_page.num_pages)
                                    #
                                    # has_next = us.has_next()
                                    # if has_next is True:
                                    #     next_page_number = us.next_page_number()
                                    # else:
                                    #     next_page_number = "There is no next page. This is the last page"
                                    # print(next_page_number)
                                    #
                                    # has_previous = us.has_previous()
                                    # if has_previous is True:
                                    #     previous_page_number = us.previous_page_number()
                                    # else:
                                    #     previous_page_number = "There is no previous page. This is the first page"
                                    # print(previous_page_number)

                                    # a = user_ids
                                    # bools = [x == u_id for x in a]
                                    if u_id in user_ids:
                                        bools = True
                                    else:
                                        bools = False
                                    print(bools)

                                    for user in users:
                                        user_id = user.id
                                        user_ids.append(user_id)
                                    print("users")
                                    print(user_ids)

                                    if bools is False:
                                        for u in users:
                                            user_id = u.id
                                            username = u.username
                                            first_name = u.first_name
                                            last_name = u.last_name
                                            is_super_admin = u.is_superuser
                                            is_org_admin = u.is_organisation_admin
                                            is_branch_admin = u.is_branch_admin
                                            is_revoked = u.is_revoked
                                            is_branch_user = u.is_branch_user

                                            user_branches = []
                                            user_orgs = []
                                            if is_branch_admin is True:
                                                branch_admin = BranchAdmins.objects.filter(user=user_id)
                                                branch_id = branch_admin[0].branch.id
                                                branch = Branch.objects.order_by("-created_at").filter(pk=branch_id)
                                                if branch[0].branch_is_active is True:
                                                    org_id = branch[0].organisation.id
                                                    orgs = Organisation.objects.order_by("-created_at").filter(
                                                        pk=org_id)
                                                    for org in orgs:
                                                        if org.organisation_is_active is True:
                                                            org_id = org.id
                                                            org_name = org.organisation_name
                                                            org_logo = org.organisation_logo

                                                            result5 = {
                                                                "org_id": org_id,
                                                                "org_name": org_name,
                                                                "org_logo": str(org_logo)
                                                            }
                                                            user_orgs.append(result5)

                                                for branches in branch_admin:
                                                    branches_id = branches.branch.id
                                                    branch = Branch.objects.order_by("-created_at").filter(pk=branches_id)
                                                    for branc in branch:
                                                        if branc.branch_is_active is True:
                                                            org_id = branc.organisation.id
                                                            org_name = branc.organisation.organisation_name
                                                            branch_id = branc.id
                                                            branch_name = branc.branch_name

                                                            result4 = {
                                                                "org_id": org_id,
                                                                "org_name": org_name,
                                                                "branch_id": branch_id,
                                                                "branch_name": branch_name,
                                                            }

                                                            user_branches.append(result4)

                                            result1 = {
                                                "user_id": user_id,
                                                "username": username,
                                                "first_name": first_name,
                                                "last_name": last_name,
                                                "is_super_admin": is_super_admin,
                                                "is_org_admin": is_org_admin,
                                                "user_orgs": user_orgs,
                                                "is_branch_admin": is_branch_admin,
                                                "user_branches": user_branches,
                                                "is_revoked": is_revoked,
                                                "is_branch_user": is_branch_user
                                            }

                                            all_users.append(result1)

                    return Response({"organisations": all_orgs, "users": all_users, "status": status.HTTP_200_OK})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no Role is defined for this user"})
            except:
                logger.debug("Error while retrieving devices")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Devices"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

    def post(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)
        is_super = request.POST.get('is_super')
        is_super = True if is_super == 'True' else False
        is_org = request.POST.get('is_org')
        is_org = True if is_org == 'True' else False
        print("2done")
        print(is_org)
        updated_orgs = request.POST.get('orgs')
        print(updated_orgs)
        print(type(updated_orgs))
        if updated_orgs is not None:
            updated_orgs = updated_orgs.split(',')
            #or we can convert string list into int through this  -->  results = [int(i) for i in results]
            updated_orgs = list(map(int, updated_orgs))
            print(updated_orgs)
            print(type(updated_orgs))
        is_branch = request.POST.get('is_branch')
        is_branch = True if is_branch == 'True' else False
        print("3done")
        print(is_branch)
        updated_branches = request.POST.get('branches')
        if updated_branches is not None:
            updated_branches = updated_branches.split(',')
            updated_branches = list(map(int, updated_branches))

        is_revoke = request.POST.get('is_revoke')
        is_revoke = True if is_revoke == 'True' else False
        is_branch_user = request.POST.get('is_branch_user')
        u_id = request.POST.get('u_id')
        print(is_branch_user," this needs noted")

        if user:
            try:
                # print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:

                    u = User.objects.filter(pk=u_id)
                    if is_super is True:
                        Token.objects.filter(user=u[0]).delete()
                        token, created = Token.objects.get_or_create(user=u[0])
                        
                        u.update(is_superuser=is_super, is_organisation_admin=False, is_branch_admin=False,
                                 is_revoked=False, is_branch_user=False)
                    elif is_org is True:
                        Token.objects.filter(user=u[0]).delete()
                        token, created = Token.objects.get_or_create(user=u[0])
                        
                        u.update(is_superuser=False, is_organisation_admin=is_org, is_branch_admin=False,
                                 is_revoked=False, is_branch_user=False)
                        current_orgs = []
                        org_admins = OrganisationAdmins.objects.filter(user=u_id)
                        for org_admin in org_admins:
                            org = org_admin.organisation.id
                            current_orgs.append(org)

                        # a = [x for x in current_orgs if x in updated_orgs]
                        # print("check tghis out")
                        # print(a)

                        print(current_orgs)
                        print(set(current_orgs))
                        print(set(updated_orgs))
                        print(list((set(current_orgs).difference(updated_orgs))))
                        print(list((set(updated_orgs).difference(current_orgs))))

                        delete_orgs = list((set(current_orgs).difference(updated_orgs)))
                        for i in delete_orgs:
                            
                            print(i)
                            print(type(i))
                            org_obj = Organisation.objects.filter(pk=i)
                            delete_org_admin_obj = OrganisationAdmins.objects.filter(organisation=org_obj[0], user=u_id)
                            print(delete_org_admin_obj)
                            delete_org_admin_obj.delete()

                        create_orgs = list((set(updated_orgs).difference(current_orgs)))
                        for i in create_orgs:
                            
                            
                            org_obj = Organisation.objects.filter(pk=i)
                            create_org_admin_obj = OrganisationAdmins.objects.create(user=u[0], organisation=org_obj[0])
                            print(create_org_admin_obj)

                    elif is_branch is True:
                        Token.objects.filter(user=u[0]).delete()
                        token, created = Token.objects.get_or_create(user=u[0])
                        
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=is_branch,
                                 is_revoked=False, is_branch_user=False)
                        current_branches = []
                        branch_admins = BranchAdmins.objects.filter(user=u_id)
                        for branch_admin in branch_admins:
                            branch = branch_admin.branch.id
                            current_branches.append(branch)

                        # a = [x for x in current_branches if x in updated_branches]
                        # print("check tghis out")
                        # print(a)

                        print(current_branches)
                        print(set(current_branches))
                        print(set(updated_branches))
                        print(list((set(current_branches).difference(updated_branches))))
                        print(list((set(updated_branches).difference(current_branches))))

                        delete_branches = list((set(current_branches).difference(updated_branches)))
                        for i in delete_branches:
                            print("delete")
                            print(i)
                            print(type(i))
                            branch_obj = Branch.objects.filter(pk=i)
                            delete_branch_admin_obj = BranchAdmins.objects.filter(branch=branch_obj[0], user=u_id)
                            print(delete_branch_admin_obj)
                            delete_branch_admin_obj.delete()

                        create_branches = list((set(updated_branches).difference(current_branches)))
                        for i in create_branches:
                            print("create")
                            print(i)
                            branch_obj = Branch.objects.filter(pk=i)
                            create_branch_admin_obj = BranchAdmins.objects.create(user=u[0], branch=branch_obj[0])
                            print(create_branch_admin_obj)
                    elif is_branch_user:
                        print("role branch view detected")
                        token, created = Token.objects.get_or_create(user=u[0])
                        print("Token:" + token.key)
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=False,
                                 is_revoked=False, is_branch_user=True)
                        current_branches = []
                        branch_admins = BranchUsers.objects.filter(user=u_id)
                        for branch_admin in branch_admins:
                            branch = branch_admin.branch.id
                            current_branches.append(branch)

                        # a = [x for x in current_branches if x in updated_branches]
                        # print("check tghis out")
                        # print(a)

                        print(current_branches)
                        print(set(current_branches))
                        print(set(updated_branches))
                        print(list((set(current_branches).difference(updated_branches))))
                        print(list((set(updated_branches).difference(current_branches))))

                        delete_branches = list((set(current_branches).difference(updated_branches)))
                        for i in delete_branches:
                            print("delete")
                            print(i)
                            print(type(i))
                            branch_obj = Branch.objects.filter(pk=i)
                            delete_branch_admin_obj = BranchUsers.objects.filter(branch=branch_obj[0], user=u_id)
                            print(delete_branch_admin_obj)
                            delete_branch_admin_obj.delete()

                        create_branches = list((set(updated_branches).difference(current_branches)))
                        for i in create_branches:
                            print("create")
                            print(i)
                            branch_obj = Branch.objects.filter(pk=i)
                            create_branch_admin_obj = BranchUsers.objects.create(user=u[0], branch=branch_obj[0])
                            print(create_branch_admin_obj)
                    elif is_revoke:
                        Token.objects.filter(user=u[0]).delete()
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=False,
                                 is_revoked=is_revoke,  is_branch_user=False)
                    else:
                        Token.objects.filter(user=u[0]).delete()
                        token, created = Token.objects.get_or_create(user=u[0])
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=False,
                                 is_revoked=False, is_branch_user=is_branch_user)

                    return Response({"status": status.HTTP_200_OK, "Msg": "Role is updated successfully"})

                elif request.user.is_active and request.user.is_organisation_admin:

                    u = User.objects.filter(pk=u_id)
                    if is_branch is True:
                        Token.objects.filter(user=u[0]).delete()
                        token, created = Token.objects.get_or_create(user=u[0])
                        print("Token:" + token.key)
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=is_branch,
                                 is_revoked=False, is_branch_user=False)
                        current_branches = []
                        branch_admins = BranchAdmins.objects.filter(user=u_id)
                        for branch_admin in branch_admins:
                            branch = branch_admin.branch.id
                            current_branches.append(branch)

                        # a = [x for x in current_branches if x in updated_branches]
                        # print("check tghis out")
                        # print(a)

                        print(current_branches)
                        print(set(current_branches))
                        print(set(updated_branches))
                        print(list((set(current_branches).difference(updated_branches))))
                        print(list((set(updated_branches).difference(current_branches))))

                        delete_branches = list((set(current_branches).difference(updated_branches)))
                        for i in delete_branches:
                            print("delete")
                            print(i)
                            print(type(i))
                            branch_obj = Branch.objects.filter(pk=i)
                            delete_branch_admin_obj = BranchAdmins.objects.filter(branch=branch_obj[0], user=u_id)
                            print(delete_branch_admin_obj)
                            delete_branch_admin_obj.delete()

                        create_branches = list((set(updated_branches).difference(current_branches)))
                        for i in create_branches:
                            print("create")
                            print(i)
                            branch_obj = Branch.objects.filter(pk=i)
                            create_branch_admin_obj = BranchAdmins.objects.create(user=u[0], branch=branch_obj[0])
                            print(create_branch_admin_obj)
                    elif is_branch_user:

                        
                        token, created = Token.objects.get_or_create(user=u[0])
                        print("Token:" + token.key)
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=False,
                                 is_revoked=False, is_branch_user=True)
                        current_branches = []
                        branch_admins = BranchUsers.objects.filter(user=u_id)
                        for branch_admin in branch_admins:
                            branch = branch_admin.branch.id
                            current_branches.append(branch)

                        # a = [x for x in current_branches if x in updated_branches]
                        # print("check tghis out")
                        # print(a)

                        print(current_branches)
                        print(set(current_branches))
                        print(set(updated_branches))
                        print(list((set(current_branches).difference(updated_branches))))
                        print(list((set(updated_branches).difference(current_branches))))

                        delete_branches = list((set(current_branches).difference(updated_branches)))

                        for i in delete_branches:
                            print("delete")
                            print(i)
                            print(type(i))
                            branch_obj = Branch.objects.filter(pk=i)

                            delete_branch_admin_obj = BranchUsers.objects.filter(branch=branch_obj[0], user=u_id)
                            print(delete_branch_admin_obj)
                            delete_branch_admin_obj.delete()

                        create_branches = list((set(updated_branches).difference(current_branches)))
                        
                        for i in create_branches:
                            
                            print(i)
                            branch_obj = Branch.objects.filter(pk=i)
                            create_branch_admin_obj = BranchUsers.objects.create(user=u[0], branch=branch_obj[0])
                            print(create_branch_admin_obj)
                    elif is_revoke:
                        Token.objects.filter(user=u[0]).delete()
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=False,
                                 is_revoked=is_revoke)
                    else:
                        Token.objects.filter(user=u[0]).delete()
                        token, created = Token.objects.get_or_create(user=u[0])
                        u.update(is_superuser=False, is_organisation_admin=False, is_branch_admin=False,
                                 is_revoked=False, is_branch_user=is_branch_user)

                    return Response({"status": status.HTTP_200_OK, "Msg": "Role is updated successfully"})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "This user can not manage roles"})
            except:
                logger.debug("Error while updating role")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Update Role"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})


class UserLogoutAPIView(APIView):
    authentication_classes = (TokenAuthentication, )

    def post(self, request):
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ForgotPasswordAPIView(APIView):
    # authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    # permission_classes = (rest_framework.permissions.IsAuthenticated,)

    # Define a function for the thread
    def sending_mail(self, FROM, TO, user, token):
        SENDMAIL = "/usr/sbin/sendmail"  # sendmail location
        print('thread user')
        print(user)

        # FROM = "Support@kgpl.com"
        # TO = [user[0].email]

        SUBJECT = "Password Change Request"

        TEXT = 'Dear ' + str(user[0].first_name) + ' ' + user[
            0].last_name + ',\n\nLooks like you have forgotten the password for your account with us at Kanji. In order to reset the password, please use following details in the app: \n\nUsername: ' + \
               user[0].username + '\nReset Code:  ' + token + '\n' \
                                                              '\n\nPlease note that this code is for one-time use and will be valid for one hour only. \n\n' + 'Regards, \n' + 'Kanji Team'

        print("Thread TEXT")
        print(TEXT)
        # Prepare actual message

        message = "From: %s\nTo: %s\nSubject: %s\n%s" % (FROM, ", ".join(TO), SUBJECT, TEXT)

        # Send the mail
        p = os.popen("%s -t -i" % SENDMAIL, "w")
        p.write(message)
        isSent = p.close()
        # if status:
        #     print("Sendmail exit status")
        #     print(status)

        # isSent = send_mail('Password Change Request', email_body, "Support@kgpl.com",
        #                    [user[0].email], fail_silently=False)

        if isSent is None:
            print("Sent")
            password_request_record = PasswordResetRequests.objects.create(reset_token=token, user=user[0]
                                                                           , date_time=datetime.datetime.now(
                    datetime.timezone.utc))
            password_request_record.save()
            logger.debug("Email Sent Successfully")
            print(traceback.format_exc())
            logger.debug("email{}".format(traceback.format_exc()))

            return Response({"username": user[0].username, "status": status.HTTP_200_OK, "Msg": "Email Sent in thread"})
        else:
            logger.debug("Email is not sent Error while sending email")
            print(traceback.format_exc())
            logger.debug("email{}".format(traceback.format_exc()))

            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "Msg": "Email Not Sent in thread"})

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email)
        print("email")
        print(email)
        print(user)

        if user:
            print(user[0].email)
            token = str(random.sample(range(100000), 1)[0])
            print("Reset token")
            print(token)
            # email_body = 'Dear '+str(user[0].first_name)+' '+user[0].last_name+',\n\nLooks like you have forgotten the password for your account with us at Kanji. In order to reset the password, please use following details in the app: \n\nUsername: '+user[0].username+'\nReset Code:  '+token+'\n' \
            #                                                             '\n\nPlease note that this code is for one-time use and will be valid for one hour only. \n\n'+'Regards, \n'+'Kanji Team'
            # print(email_body)

            try:
                # Create thread as follows
                _thread.start_new_thread(self.sending_mail, ("Support@kgpl.com", [user[0].email], user, token))
                return Response({"username": user[0].username, "status": status.HTTP_200_OK, "Msg": "Please Check Your Email"})
            except:
                logger.debug("Error while sending email for password reset")
                print(traceback.format_exc())
                logger.debug("email{}".format(traceback.format_exc()))
                return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "Msg": "Email Not Sent"})
            # while 1:
            #     pass
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User Found Having This Email"})


    # def post(self, request):
    #     email = request.data.get('email')
    #     user = User.objects.filter(email=email)
    #     print("email")
    #     print(email)
    #     print(user)
    #
    #     if user:
    #         print(user[0].email)
    #         token = str(random.sample(range(100000), 1)[0])
    #         print("Reset token")
    #         print(token)
    #         # email_body = 'Dear '+str(user[0].first_name)+' '+user[0].last_name+',\n\nLooks like you have forgotten the password for your account with us at Kanji. In order to reset the password, please use following details in the app: \n\nUsername: '+user[0].username+'\nReset Code:  '+token+'\n' \
    #         #                                                             '\n\nPlease note that this code is for one-time use and will be valid for one hour only. \n\n'+'Regards, \n'+'Kanji Team'
    #         # print(email_body)
    #
    #         try:
    #
    #             SENDMAIL = "/usr/sbin/sendmail"  # sendmail location
    #
    #             FROM = "Support@kgpl.com"
    #             TO = [user[0].email]
    #
    #             SUBJECT = "Password Change Request"
    #
    #             TEXT = 'Dear '+str(user[0].first_name)+' '+user[0].last_name+',\n\nLooks like you have forgotten the password for your account with us at Kanji. In order to reset the password, please use following details in the app: \n\nUsername: '+user[0].username+'\nReset Code:  '+token+'\n' \
    #                                                                     '\n\nPlease note that this code is for one-time use and will be valid for one hour only. \n\n'+'Regards, \n'+'Kanji Team'
    #
    #
    #             # Prepare actual message
    #
    #             message = """\
    #                     From: %s
    #                     To: %s
    #                     Subject: %s
    #
    #                     %s
    #                     """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    #
    #             # Send the mail
    #             p = os.popen("%s -t -i" % SENDMAIL, "w")
    #             p.write(message)
    #
    #             isSent = p.close()
    #             # if status:
    #             #     print("Sendmail exit status")
    #             #     print(status)
    #
    #             # isSent = send_mail('Password Change Request', email_body, "Support@kgpl.com",
    #             #                    [user[0].email], fail_silently=False)
    #
    #             if isSent is None:
    #                 print("Sent")
    #                 password_request_record = PasswordResetRequests.objects.create(reset_token=token, user=user[0]
    #                                                                                  ,date_time=datetime.datetime.now(datetime.timezone.utc))
    #                 password_request_record.save()
    #                 return Response({"username": user[0].username, "status": status.HTTP_200_OK, "Msg": "Email Sent"})
    #             else:
    #                 return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "Msg": "Email Not Sent"})
    #         except:
    #             logger.debug("Error while sending email for password reset")
    #             print(traceback.format_exc())
    #             logger.debug("email{}".format(traceback.format_exc()))
    #             return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "Msg": "Email Not Sent"})
    #     else:
    #         return Response({"status": status.HTTP_404_NOT_FOUND,"Msg":"No User Found Having This Email"})

    def put(self, request):
        print('resend check')
        if 'token' not in request.data or 'username' not in request.data:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Missing Request Parameters"})
        received_token = request.data.get('token')
        username = request.data.get('username')
        print(username)

        user = User.objects.filter(username=username)
        if user:
            user_id = user[0].id
        else:
            return Response({"status": status.HTTP_200_OK, "Msg": ""})
        try:
            user = User.objects.filter(id=user_id)
            token_param = Q(reset_token=received_token)
            user_param = Q(user=user[0])
            reset_token_object = PasswordResetRequests.objects.filter(token_param & user_param)
            if reset_token_object:
                token_time_stamp = reset_token_object[0].date_time
                current = datetime.datetime.now(datetime.timezone.utc)
                time_difference = str(current - token_time_stamp)
                print("time_difference")
                print(time_difference)
                time_tokens = time_difference.split(':')
                print("time_tokens")
                print(time_tokens)
                hours_elapsed = int(time_tokens[0])
                print("hours_elapsed")
                print(hours_elapsed)
                minutes_elapsed = int(time_tokens[1])
                print("Time elapsed "+str(hours_elapsed))
                print("minutes_elapsed")
                print(minutes_elapsed)
                if hours_elapsed <= 0:
                    return Response({"status": status.HTTP_200_OK, "Msg": "Code Valid"})
                else:
                    reset_token_object[0].delete()
                    return Response({"status": status.HTTP_401_UNAUTHORIZED, "Msg": "Invalid Code"})

            else:
                return Response({"status": status.HTTP_401_UNAUTHORIZED, "Msg": "Code Invalid"})
        except:
            logger.debug("Error while verifying password reset token")
            print(traceback.format_exc())
            logger.debug("email{}".format(traceback.format_exc()))
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "Msg": "Server Error"})


class ResetPasswordAPIView(APIView):
    # authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    # permission_classes = (rest_framework.permissions.IsAuthenticated,)
    def put(self, request):
        new_password = request.data.get('new_password')
        username = request.data.get('username')
        print(username)
        print('reseting')
        if request.data.get('old') is not None:
            try:
                old_password = request.data.get('old')
                hashed_password = make_password(new_password)
                print('reseting from in')
                user = User.objects.filter(username=username)
                if user:
                    if user[0].check_password(old_password):
                        user.update(password=hashed_password)
                        reset_token_object = PasswordResetRequests.objects.filter(user=user[0].id)
                        for rto in reset_token_object:
                            rto.delete()
                        return Response({"status": status.HTTP_200_OK, "Msg": "Password Changed"})
                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "Msg": "Old Password Is Incorrect"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Change Password"})
            except:
                logger.debug("Error while resetting password from with in")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Change Password"})
        if request.data.get('old') is None:
            try:
                print("this is my new password: " + str(new_password))
                hashed_password = make_password(new_password)
                print("this is my hashed password: " + hashed_password)
                check = check_password(new_password, hashed_password)
                print("this is my check password.: %s"  % check)

                user = User.objects.filter(username=username)

                # user = User.objects.create(password=hashed_password)

                print('resetting from out')
                print(username)
                print(user)
                if user:

                    # hashed_password = make_password(new_password)
                    user.update(password=hashed_password)
                    # user.password = hashed_password
                    # user[0].save(update_fields=['password'])
                    reset_token_object = PasswordResetRequests.objects.filter(user=user[0].id)
                    for rto in reset_token_object:
                        rto.delete()

                    return Response({"status": status.HTTP_200_OK, "Msg": "Password Changed"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Change Password"})
            except:
                logger.debug("Error while resetting password from with out")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Change Password"})


class ValidatePasswordAPIView(APIView):
    # authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    # permission_classes = (rest_framework.permissions.IsAuthenticated,)
    def post(self, request):
        password = request.data.get('password')
        username = request.data.get('username')
        print(username)
        user = User.objects.filter(username=username)
        print(user)
        if user:
            isPasswordCorrect = user[0].check_password(password)
            return Response({"status":status.HTTP_200_OK,"PasswordCorrect":isPasswordCorrect})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User Found"})

# from django.db.models import Count
# @method_decorator([login_required], name='dispatch')
class DashboardAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    serializer_class = DeviceSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['device_make', 'device_model', 'device_imei_no','device_last_check_in', 'device_last_driver']
    pagination_class = PageNumberPagination #LimitOffsetPagination

    def get(self, request):

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)
        if user:
            try:
                # print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    orgs = Organisation.objects.all()
                    total_orgs = 0
                    for org in orgs:
                        if org.organisation_is_active is True:
                            total_orgs = total_orgs + 1
                    print(total_orgs)

                    branches = Branch.objects.all()
                    total_branches = 0
                    for branch in branches:
                        if branch.branch_is_active is True:
                            total_branches = total_branches + 1
                    print(total_branches)

                    # devices = Device.objects.all()
                    # total_devices = 0
                    # for device in devices:
                    #     if device.device_is_active is True:
                    #         total_devices = total_devices + 1
                    # print(total_devices)

                    devices_list = []
                    devices = Device.objects.all()
                    total_devices = 0
                    count = 0
                    pending_devices_count = 0
                    for device in devices:
                        if device.device_is_active is False and device.device_is_inactive is False and device.device_is_revoke is False:
                            pending_devices_count = pending_devices_count + 1

                        if device.device_is_active is True:
                            total_devices = total_devices + 1
                            device_id = device.id
                            branch_id = device.branch.id
                            device_make =  device.device_make
                            device_model = device.device_model
                            device_imei_no = device.device_imei_no
                            device_last_check_in =  device.device_last_check_in
                            device_last_driver = device.device_last_driver
                            device_is_active = device.device_is_active

                            if device_last_check_in is not None:

                                s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                print(s)
                                tail = s[-4:]
                                f = round(float(tail), 3)
                                temp = "%.3f" % f
                                print((s[:-4], temp[1:]))
                                print(type(s[-4:]))
                                date_time = s[:-4]
                            else:
                                date_time = ""

                            result1 = {
                                "device_id": device_id,
                                "branch_id": branch_id,
                                "device_make": device_make,
                                "device_model": device_model,
                                "device_imei_no": device_imei_no,
                                "device_last_check_in": date_time,
                                "device_last_driver": device_last_driver,
                                "device_is_active": device_is_active,
                                "device_branch": device.branch.branch_name
                            }
                            # devices_list.append(result1)
                            if count <= 10:
                                devices_list.append(result1)
                            print("count " + str(count))
                            count = count - 1

                    # paginator = Paginator(device_list, 3)
                    # page = request.GET.get('page')
                    # device_list = paginator.get_page(page)

                    # page = request.GET.get('page', 1)
                    #
                    # paginator = Paginator(device_list, 10)
                    # try:
                    #     device = paginator.page(page)
                    # except PageNotAnInteger:
                    #     device = paginator.page(1)
                    # except EmptyPage:
                    #     device = paginator.page(paginator.num_pages)


                    #"orgs_list": orgs_list.data, "branches_list": branches_list.data,

                    return Response(
                        {"total_orgs": total_orgs,  "total_branches": total_branches, "total_devices": total_devices,
                         "pending_devices_count": pending_devices_count,"device_list": devices_list,"status": status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    org_admins = OrganisationAdmins.objects.filter(user=user_id)
                    total_orgs = 0
                    orgs = []
                    total_branches = 0

                    total_devices = 0
                    pending_devices_count = 0
                    devices_list = []
                    for org_admin in org_admins:
                        if org_admin.organisation.organisation_is_active is True:
                            total_orgs = total_orgs + 1
                            org_id = org_admin.organisation.id
                            org_name = org_admin.organisation.organisation_name
                            print(org_name)
                            # t_branches = Branch.objects.filter(organisation=org_id)
                            # # total_branches = 0
                            # for t_branch in t_branches:
                            #     if t_branch.branch_is_active is True:
                            #         total_branches = total_branches + 1

                            result1 = {"org_id": org_id,
                                       "org_name": org_name
                                       }
                            orgs.append(result1)


                            branches = Branch.objects.filter(organisation=org_id)
                        # print(branches)

                            for branch in branches:
                                if branch.branch_is_active is True:
                                    total_branches = total_branches + 1
                                    branch_id = branch.id
                                    # branch_name = branch.branch_name
                                    # print(branch_name)
                                    count = 10
                                    devices = Device.objects.filter(branch=branch_id).order_by('-device_last_check_in')
                                    for device in devices:
                                        if device.device_is_active is False and device.device_is_inactive is False and device.device_is_revoke is False:
                                            pending_devices_count = pending_devices_count + 1

                                        if device.device_is_active is True:
                                            total_devices = total_devices + 1
                                            device_id = device.id
                                            branch_id = device.branch.id
                                            device_make = device.device_make
                                            device_model = device.device_model
                                            device_imei_no = device.device_imei_no
                                            device_last_check_in = device.device_last_check_in
                                            device_last_driver = device.device_last_driver
                                            device_is_active = device.device_is_active

                                            if device_last_check_in is not None:
                                                s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                                print(s)
                                                tail = s[-4:]
                                                f = round(float(tail), 3)
                                                temp = "%.3f" % f
                                                print((s[:-4], temp[1:]))
                                                print(type(s[-4:]))
                                                date_time = s[:-4]
                                            else:
                                                date_time = ""

                                            result1 = {
                                                "device_id": device_id,
                                                "branch_id": branch_id,
                                                "device_make": device_make,
                                                "device_model": device_model,
                                                "device_imei_no": device_imei_no,
                                                "device_last_check_in": date_time,
                                                "device_last_driver": device_last_driver,
                                                "device_is_active": device_is_active
                                            }
                                            if count <= 10:
                                                devices_list.append(result1)
                                            print("count "+str(count))
                                            count = count - 1
                                        # total = total_devices + total
                                        print(total_devices)
                                        # devices = Device.objects.filter(branch=branch_id)
                                        # print(devices)
                                        # device_list = DeviceSerializer(devices, many=True)
                                        # for device in device_list.data:
                                        #     devices_detail.append(device)


                    return Response(
                        {"total_orgs": total_orgs, "orgs": orgs, "total_branches": total_branches, "total_devices": total_devices,
                         "pending_devices_count": pending_devices_count, "device_list": devices_list,
                         "status": status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_branch_admin:
                    branch_admins = BranchAdmins.objects.filter(user=user_id)
                    print(branch_admins)
                    total_branches = 0
                    branches = []
                    devices_list = []
                    total_devices = 0
                    pending_devices_count = 0
                    for branch_admin in branch_admins:
                        if branch_admin.branch.branch_is_active is True:
                            total_branches = total_branches + 1
                            branch_id = branch_admin.branch.id
                            branch_name = branch_admin.branch.branch_name
                            print(branch_name)
                            result1 = {"branch_id": branch_id,
                                       "branch_name": branch_name}
                            branches.append(result1)
                            devices = Device.objects.filter(branch=branch_id)
                            count = 0
                            for device in devices:
                                if device.device_is_active is False and device.device_is_inactive is False and device.device_is_revoke is False:
                                    pending_devices_count = pending_devices_count + 1

                                if device.device_is_active is True:
                                    total_devices = total_devices + 1
                                    device_id = device.id
                                    branch_id = device.branch.id
                                    device_make = device.device_make
                                    device_model = device.device_model
                                    device_imei_no = device.device_imei_no
                                    device_last_check_in = device.device_last_check_in
                                    device_last_driver = device.device_last_driver
                                    device_is_active = device.device_is_active

                                    if device_last_check_in is not None:
                                        s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                        print(s)
                                        tail = s[-4:]
                                        f = round(float(tail), 3)
                                        temp = "%.3f" % f
                                        print((s[:-4], temp[1:]))
                                        print(type(s[-4:]))
                                        date_time = s[:-4]
                                    else:
                                        date_time = ""

                                    result1 = {
                                        "device_id": device_id,
                                        "branch_id": branch_id,
                                        "device_make": device_make,
                                        "device_model": device_model,
                                        "device_imei_no": device_imei_no,
                                        "device_last_check_in": date_time,
                                        "device_last_driver": device_last_driver,
                                        "device_is_active": device_is_active
                                    }
                                    # devices_list.append(result1)
                                    if count <= 10:
                                        devices_list.append(result1)
                                    print("count " + str(count))
                                    count = count - 1
                            print(total_devices)

                            # devices = Device.objects.filter(branch=branch_id)
                            # # print(devices)
                            # # for device in devices:
                            # #     devices = Device.objects.filter(branch=branch_name)
                            # #     print(devices)
                            # device_list = DeviceSerializer(devices, many=True)
                            # for device in device_list.data:
                            #     devices_detail.append(device)

                    return Response(
                        {"total_branches": total_branches, "branches": branches, "total_devices": total_devices,
                         "pending_devices_count": pending_devices_count, "device_list": devices_list,
                         "status": status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_branch_user:
                    branch_admins = BranchAdmins.objects.filter(user=user_id)
                    print(branch_admins)
                    total_branches = 0
                    branches = []
                    devices_list = []
                    total_devices = 0
                    pending_devices_count = 0
                    for branch_admin in branch_admins:
                        if branch_admin.branch.branch_is_active is True:
                            total_branches = total_branches + 1
                            branch_id = branch_admin.branch.id
                            branch_name = branch_admin.branch.branch_name
                            print(branch_name)
                            result1 = {"branch_id": branch_id,
                                       "branch_name": branch_name}
                            branches.append(result1)
                            devices = Device.objects.filter(branch=branch_id)
                            count = 0
                            for device in devices:
                                if device.device_is_active is False and device.device_is_inactive is False and device.device_is_revoke is False:
                                    pending_devices_count = pending_devices_count + 1

                                if device.device_is_active is True:
                                    total_devices = total_devices + 1
                                    device_id = device.id
                                    branch_id = device.branch.id
                                    device_make = device.device_make
                                    device_model = device.device_model
                                    device_imei_no = device.device_imei_no
                                    device_last_check_in = device.device_last_check_in
                                    device_last_driver = device.device_last_driver
                                    device_is_active = device.device_is_active

                                    if device_last_check_in is not None:
                                        s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                        print(s)
                                        tail = s[-4:]
                                        f = round(float(tail), 3)
                                        temp = "%.3f" % f
                                        print((s[:-4], temp[1:]))
                                        print(type(s[-4:]))
                                        date_time = s[:-4]
                                    else:
                                        date_time = ""

                                    result1 = {
                                        "device_id": device_id,
                                        "branch_id": branch_id,
                                        "device_make": device_make,
                                        "device_model": device_model,
                                        "device_imei_no": device_imei_no,
                                        "device_last_check_in": date_time,
                                        "device_last_driver": device_last_driver,
                                        "device_is_active": device_is_active
                                    }
                                    # devices_list.append(result1)
                                    if count <= 10:
                                        devices_list.append(result1)
                                    print("count " + str(count))
                                    count = count - 1
                            print(total_devices)

                            # devices = Device.objects.filter(branch=branch_id)
                            # # print(devices)
                            # # for device in devices:
                            # #     devices = Device.objects.filter(branch=branch_name)
                            # #     print(devices)
                            # device_list = DeviceSerializer(devices, many=True)
                            # for device in device_list.data:
                            #     devices_detail.append(device)

                    return Response(
                        {"total_branches": total_branches, "branches": branches, "total_devices": total_devices,
                         "pending_devices_count": pending_devices_count, "device_list": devices_list,
                         "status": status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No Role Is Defined For This User"})
            except:
                logger.debug("Error while retrieving data")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Data"})

        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "No User Found Having This Id"})

        # query_list = Device.objects.all()
        # device_list = DeviceSerializer(query_list, many=True)
        # query = self.request.GET.get("page")
        #
        # if query:
        #     device_list = device_list.filter(
        #         Q(device_make__icontains = query)|
        #         Q(device_model__icontains=query)|
        #         Q(device_imei_no__icontains=query)|
        #         Q(device_last_check_in__icontains=query)|
        #         Q(device_last_driver__icontains=query)
        #     ).distinct()
        #
        # return Response({"device_list": device_list.data,})

# @method_decorator([login_required, superuser_required], name='dispatch')
# class OrganisationAPIView(APIView):
#
#     def get(self, request):
#         organisation = Organisation.objects.all()
#         # serializer_class = UserSerializer
#         serializer = OrganisationSerializer(organisation, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = OrganisationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator([login_required, superuser_required], name='dispatch')
class OrganisationAdminsAPIView(APIView):

    def get(self, request):
        organisation_admins = OrganisationAdmins.objects.all()
        # serializer_class = UserSerializer
        serializer = OrganisationAdminsSerializer(organisation_admins, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrganisationAdminsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator([login_required, superuser_required], name='dispatch')
# class BranchAPIView(APIView):
#
#     def get(self, request):
#         branch = Branch.objects.all()
#         # serializer_class = UserSerializer
#         serializer = BranchSerializer(branch, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = BranchSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator([login_required, superuser_required], name='dispatch')
class BranchAdminsAPIView(APIView):

    def get(self, request):
        branch_admins = BranchAdmins.objects.all()
        # serializer_class = UserSerializer
        serializer = BranchAdminsSerializer(branch_admins, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BranchAdminsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator([login_required, superuser_required], name='dispatch')
class DeviceAPIView(APIView):

    pagination_class = LimitOffsetPagination
    def get(self, request):
        device = Device.objects.all()
        # serializer_class = UserSerializer

        # device = Paginator(device,10)
        # page = request.GET.get('page')
        # device = device.page(page)
        # print(device)
        # print(type(device))

        serializer = DeviceSerializer(device, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator([login_required, superuser_required], name='dispatch')
# @method_decorator([gzip_page], name='dispatch')
# class QuestionAPIView(APIView):
#
#     def get(self, request):
#         questions = Question.objects.all()
#         # for t in questions.iterator():
#         #     print(t.question_text)
#
#         #serializer_class = UserSerializer
#         serializer = QuestionSerializer(questions, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = QuestionSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    '''
    def delete(self, request, u_id, format=None):
        user = self.get_object(pk =u_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    '''
import time
class QuestionWizardOrganisationAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        # time.sleep(2)
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        print("in API QuestionWizardOrganisationAPIView")
        # print(user_id)
        # print(user)

        # i = 2222
        # for c in response2['drops']:
        #     c['drop_customer_code'] = str(i)
        #     code = c['drop_customer_code']
        #     i = i + 1
        #     print(code)
        #     name = c['drop_customer']
        #     print(name)
        #     if CustomerCode.objects.filter(customer_code=code).exists():
        #         continue
        #     CustomerCode.objects.create(customer_code=code, customer_name=name)

        branch = Branch.objects.all()
        branch_api_server_ip = branch[0].branch_api_server_ip

        res = []
        data = {
            "device_id": "1234567892",
            "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
        }

        # or we can write it like data = json.dumps(data)
        print("hitting with ", branch_api_server_ip)
        response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_status_list_run.php', json=data)
        response1 = response1.json()
        print("RESPONSE RUN")
        print(response1)

        for run_status in response1['statuses']:
            run_status_id = run_status['status_id']
            run_status_id = int(run_status_id)
            print(type(run_status_id))
            run_status_name = run_status['status_name']
            run_status_obj = QuestionActionStatus.objects.filter(run_status_id=run_status_id)
            if run_status_obj.exists():
                run_status_obj.update(question_action_status=True, run_status_id=run_status_id,
                                                    run_status_name=run_status_name, run_status=True)
            else:
                QuestionActionStatus.objects.create(question_action_status= True, run_status_id=run_status_id, run_status_name=run_status_name, run_status=True)
            print("run statuses")
            print(QuestionActionStatus)

        response2 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_status_list_drop.php', json=data)
        response2 = response2.json()
        print("RESPONSE Drop")
        print(response2)

        for drop_status in response2['statuses']:
            drop_status_id = drop_status['status_id']
            drop_status_id = int(drop_status_id)
            print(type(drop_status_id))
            drop_status_name = drop_status['status_name']
            drop_status_obj = QuestionActionStatus.objects.filter(drop_status_id=drop_status_id)
            if drop_status_obj.exists():
                drop_status_obj.update(question_action_status=True, drop_status_id=drop_status_id,
                                                    drop_status_name=drop_status_name, drop_status=True)
            else:
                QuestionActionStatus.objects.create(question_action_status= True, drop_status_id=drop_status_id, drop_status_name=drop_status_name, drop_status=True)
            print("drop statuses")
            print(QuestionActionStatus)


        response3 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_run_log_type.php', json=data)
        response3 = response3.json()
        for log_entry_types in response3['types']:
            type_id = log_entry_types['type_id']
            type_id = int(type_id)
            print(type(type_id))
            type_name = log_entry_types['type_name']
            log_type_obj = QuestionActionLogType.objects.filter(type_id=type_id)
            if log_type_obj.exists():
                log_type_obj.update(type_id=type_id, type_name=type_name)
            else:
                QuestionActionLogType.objects.create(type_id=type_id, type_name=type_name)
            print("log types entry")
            print(QuestionActionLogType)

        response4 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_drop_type_list.php', json=data)
        response4 = response4.json()
        for drop_type in response4['types']:
            section_id = drop_type['type_id']
            section_id = int(section_id)
            print(section_id)
            print(type(section_id))
            section_name = drop_type['type_name']
            drop_type_obj = QuestionSection.objects.filter(section_id=section_id)
            if drop_type_obj.exists():
                drop_type_obj.update(section_id=section_id, section_name=section_name)
            else:
                QuestionSection.objects.create(section_id=section_id, section_name=section_name)
            print("question sections")
            print(QuestionSection)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    orgs = Organisation.objects.all()
                    # customer_codes = CustomerCode.objects.all()
                    sections = QuestionSection.objects.all()
                    types = QuestionType.objects.all()
                    log_types = QuestionActionLogType.objects.all()
                    statuses = QuestionActionStatus.objects.all()

                    organisations = []
                    # branches = []
                    # codes = []
                    question_sections = []
                    question_types = []
                    question_log_types = []
                    run_statuses = []
                    drop_statuses = []

                    for organisation in orgs:
                        if organisation.organisation_is_active is True:
                            org_id = organisation.id
                            org_name = organisation.organisation_name
                            org_logo = organisation.organisation_logo

                            result1 = {
                                    "org_id": org_id,
                                    "org_name": org_name,
                                    "org_logo": str(org_logo)
                                }

                            organisations.append(result1)

                    # for customer_code in customer_codes:
                    #     code = customer_code.customer_code
                    #     name = customer_code.customer_name
                    #
                    #     result2 = {
                    #             "customer_code": code,
                    #             "customer_name": name,
                    #         }
                    #
                    #     codes.append(result2)

                    for section in sections:
                        section_id = section.section_id
                        section_name = section.section_name

                        result3 = {
                            "question_section_id": section_id,
                            "question_section_type": section_name
                        }
                        question_sections.append(result3)

                    for question_type in types:
                        type_id = question_type.id
                        type_name = question_type.question_type

                        result1 = {
                            "question_type_id": type_id,
                            "question_type": type_name
                        }

                        question_types.append(result1)

                    for log_type in log_types:
                        type_id = log_type.type_id
                        type_name = log_type.type_name

                        result1 = {
                            "log_type_id": type_id,
                            "log_type": type_name
                        }

                        question_log_types.append(result1)

                    for stat in statuses:
                        if stat.run_status_id is not None:
                            run_status_id = stat.run_status_id
                            run_status_name = stat.run_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": run_status_id,
                                "status_name": run_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }
                            run_statuses.append(result1)

                    for stat in statuses:
                        if stat.drop_status_id is not None:
                            drop_status_id = stat.drop_status_id
                            drop_status_name = stat.drop_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": drop_status_id,
                                "status_name": drop_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }

                            drop_statuses.append(result1)

                    return Response({"organisations": organisations, "question_sections": question_sections, "question_types": question_types, "question_log_types": question_log_types, "run_statuses": run_statuses, "drop_statuses": drop_statuses, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    org_admin = OrganisationAdmins.objects.filter(user=user_id)
                    customer_codes = CustomerCode.objects.all()
                    sections = QuestionSection.objects.all()
                    types = QuestionType.objects.all()
                    log_types = QuestionActionLogType.objects.all()
                    statuses = QuestionActionStatus.objects.all()

                    organisations = []
                    # codes = []
                    question_sections = []
                    question_types = []
                    question_log_types = []
                    run_statuses = []
                    drop_statuses = []

                    for org in org_admin:
                        if org.organisation.organisation_is_active is True:
                            org_id = org.organisation.id
                            org_name = org.organisation.organisation_name
                            org_logo = org.organisation.organisation_logo

                            result1 = {
                                "org_id": org_id,
                                "org_name": org_name,
                                "org_logo": str(org_logo)
                            }

                            organisations.append(result1)

                    # for customer_code in customer_codes:
                    #     code = customer_code.customer_code
                    #     name = customer_code.customer_name
                    #
                    #     result2 = {
                    #         "customer_code": code,
                    #         "customer_name": name,
                    #     }
                    #
                    #     codes.append(result2)

                    for section in sections:
                        section_id = section.section_id
                        section_name = section.section_name

                        result3 = {
                            "question_section_id": section_id,
                            "question_section_type": section_name
                        }
                        question_sections.append(result3)

                    for question_type in types:
                        type_id = question_type.id
                        type_name = question_type.question_type

                        result1 = {
                            "question_type_id": type_id,
                            "question_type": type_name
                        }

                        question_types.append(result1)

                    for log_type in log_types:
                        type_id = log_type.type_id
                        type_name = log_type.type_name

                        result1 = {
                            "log_type_id": type_id,
                            "log_type": type_name
                        }

                        question_log_types.append(result1)

                    for stat in statuses:
                        if stat.run_status_id is not None:
                            run_status_id = stat.run_status_id
                            run_status_name = stat.run_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": run_status_id,
                                "status_name": run_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }
                            run_statuses.append(result1)

                    for stat in statuses:
                        if stat.drop_status_id is not None:
                            drop_status_id = stat.drop_status_id
                            drop_status_name = stat.drop_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": drop_status_id,
                                "status_name": drop_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }

                            drop_statuses.append(result1)

                    return Response({"organisations": organisations, "question_sections": question_sections, "question_types": question_types, "question_log_types": question_log_types, "run_statuses": run_statuses, "drop_statuses": drop_statuses, "status":status.HTTP_200_OK})


                elif request.user.is_active and request.user.is_branch_admin :
                    branch_admin = BranchAdmins.objects.filter(user=user_id)
                    customer_codes = CustomerCode.objects.all()
                    sections = QuestionSection.objects.all()
                    types = QuestionType.objects.all()
                    log_types = QuestionActionLogType.objects.all()
                    statuses = QuestionActionStatus.objects.all()

                    branches = []
                    # codes = []
                    question_sections = []
                    question_types = []
                    question_log_types = []
                    run_statuses = []
                    drop_statuses = []

                    for branc in branch_admin:
                        if branc.branch.branch_is_active is True:
                            branch_id = branc.branch.id
                            branch_name = branc.branch.branch_name

                            result1 = {
                                "branch_id": branch_id,
                                "branch_name": branch_name
                            }

                            branches.append(result1)

                    for customer_code in customer_codes:
                        code = customer_code.customer_code
                        name = customer_code.customer_name

                        result2 = {
                            "customer_code": code,
                            "customer_name": name,
                        }

                        codes.append(result2)

                    for section in sections:
                        section_id = section.section_id
                        section_name = section.section_name

                        result3 = {
                            "question_section_id": section_id,
                            "question_section_type": section_name
                        }
                        question_sections.append(result3)

                    for question_type in types:
                        type_id = question_type.id
                        type_name = question_type.question_type

                        result1 = {
                            "question_type_id": type_id,
                            "question_type": type_name
                        }

                        question_types.append(result1)

                    for log_type in log_types:
                        type_id = log_type.type_id
                        type_name = log_type.type_name

                        result1 = {
                            "log_type_id": type_id,
                            "log_type": type_name
                        }

                        question_log_types.append(result1)

                    for stat in statuses:
                        if stat.run_status_id is not None:
                            run_status_id = stat.run_status_id
                            run_status_name = stat.run_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": run_status_id,
                                "status_name": run_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }
                            run_statuses.append(result1)

                    for stat in statuses:
                        if stat.drop_status_id is not None:
                            drop_status_id = stat.drop_status_id
                            drop_status_name = stat.drop_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": drop_status_id,
                                "status_name": drop_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }

                            drop_statuses.append(result1)

                    return Response({"branches": branches, "question_sections": question_sections, "question_types": question_types, "question_log_types": question_log_types, "run_statuses": run_statuses, "drop_statuses": drop_statuses, "status":status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_branch_user :
                    
                    branch_admin = BranchUsers.objects.filter(user=user_id)
                    customer_codes = CustomerCode.objects.all()
                    sections = QuestionSection.objects.all()
                    types = QuestionType.objects.all()
                    log_types = QuestionActionLogType.objects.all()
                    statuses = QuestionActionStatus.objects.all()

                    branches = []
                    # codes = []
                    question_sections = []
                    question_types = []
                    question_log_types = []
                    run_statuses = []
                    drop_statuses = []

                    for branc in branch_admin:
                        if branc.branch.branch_is_active is True:
                            branch_id = branc.branch.id
                            branch_name = branc.branch.branch_name

                            result1 = {
                                "branch_id": branch_id,
                                "branch_name": branch_name
                            }

                            branches.append(result1)

                    for customer_code in customer_codes:
                        code = customer_code.customer_code
                        name = customer_code.customer_name

                        result2 = {
                            "customer_code": code,
                            "customer_name": name,
                        }

                        codes.append(result2)

                    for section in sections:
                        section_id = section.section_id
                        section_name = section.section_name

                        result3 = {
                            "question_section_id": section_id,
                            "question_section_type": section_name
                        }
                        question_sections.append(result3)

                    for question_type in types:
                        type_id = question_type.id
                        type_name = question_type.question_type

                        result1 = {
                            "question_type_id": type_id,
                            "question_type": type_name
                        }

                        question_types.append(result1)

                    for log_type in log_types:
                        type_id = log_type.type_id
                        type_name = log_type.type_name

                        result1 = {
                            "log_type_id": type_id,
                            "log_type": type_name
                        }

                        question_log_types.append(result1)

                    for stat in statuses:
                        if stat.run_status_id is not None:
                            run_status_id = stat.run_status_id
                            run_status_name = stat.run_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": run_status_id,
                                "status_name": run_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }
                            run_statuses.append(result1)

                    for stat in statuses:
                        if stat.drop_status_id is not None:
                            drop_status_id = stat.drop_status_id
                            drop_status_name = stat.drop_status_name
                            run_status = stat.run_status
                            drop_status = stat.drop_status

                            result1 = {
                                "status_id": drop_status_id,
                                "status_name": drop_status_name,
                                "run_status": run_status,
                                "drop_status": drop_status
                            }

                            drop_statuses.append(result1)

                    return Response({"branches": branches, "question_sections": question_sections, "question_types": question_types, "question_log_types": question_log_types, "run_statuses": run_statuses, "drop_statuses": drop_statuses, "status":status.HTTP_200_OK})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "not role is defined for this user"})

            except:
                logger.debug("Error while retrieving data")
                
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Data"})
        else:
            orgs = Organisation.objects.all()
            # customer_codes = CustomerCode.objects.all()
            sections = QuestionSection.objects.all()
            types = QuestionType.objects.all()
            log_types = QuestionActionLogType.objects.all()
            statuses = QuestionActionStatus.objects.all()

            organisations = []
            # branches = []
            # codes = []
            question_sections = []
            question_types = []
            question_log_types = []
            run_statuses = []
            drop_statuses = []

            for organisation in orgs:
                if organisation.organisation_is_active is True:
                    org_id = organisation.id
                    org_name = organisation.organisation_name

                    result1 = {
                        "org_id": org_id,
                        "org_name": org_name
                    }

                    organisations.append(result1)

            # for customer_code in customer_codes:
            #     code = customer_code.customer_code
            #     name = customer_code.customer_name
            #
            #     result2 = {
            #             "customer_code": code,
            #             "customer_name": name,
            #         }
            #
            #     codes.append(result2)

            for section in sections:
                section_id = section.section_id
                section_name = section.section_name

                result3 = {
                    "question_section_id": section_id,
                    "question_section_type": section_name
                }
                question_sections.append(result3)

            for question_type in types:
                type_id = question_type.id
                type_name = question_type.question_type

                result1 = {
                    "question_type_id": type_id,
                    "question_type": type_name
                }

                question_types.append(result1)

            for log_type in log_types:
                type_id = log_type.type_id
                type_name = log_type.type_name

                result1 = {
                    "log_type_id": type_id,
                    "log_type": type_name
                }

                question_log_types.append(result1)

            for stat in statuses:
                if stat.run_status_id is not None:
                    run_status_id = stat.run_status_id
                    run_status_name = stat.run_status_name
                    run_status = stat.run_status
                    drop_status = stat.drop_status

                    result1 = {
                        "status_id": run_status_id,
                        "status_name": run_status_name,
                        "run_status": run_status,
                        "drop_status": drop_status
                    }
                    run_statuses.append(result1)

            for stat in statuses:
                if stat.drop_status_id is not None:
                    drop_status_id = stat.drop_status_id
                    drop_status_name = stat.drop_status_name
                    run_status = stat.run_status
                    drop_status = stat.drop_status

                    result1 = {
                        "status_id": drop_status_id,
                        "status_name": drop_status_name,
                        "run_status": run_status,
                        "drop_status": drop_status
                    }

                    drop_statuses.append(result1)

            return Response({"organisations": organisations, "question_sections": question_sections,
                             "question_types": question_types, "question_log_types": question_log_types,
                             "run_statuses": run_statuses, "drop_statuses": drop_statuses,
                             "status": status.HTTP_200_OK})

class QuestionWizardBranchAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        # time.sleep(2)
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)

        org_id = request.GET.get('org_id')

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    b = Branch.objects.filter(organisation=org_id)
                    print(b)
                    branches = []
                    for branch in b:
                        if branch.branch_is_active is True:
                            branch_id = branch.id
                            branch_name = branch.branch_name

                            result = {
                                    "branch_id": branch_id,
                                    "branch_name": branch_name
                                }
                            branches.append(result)

                    return Response({"branches": branches, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    b = Branch.objects.filter(organisation=org_id)
                    print(b)
                    branches = []
                    for branch in b:
                        if branch.branch_is_active is True:
                            branch_id = branch.id
                            branch_name = branch.branch_name

                            result = {
                                    "branch_id": branch_id,
                                    "branch_name": branch_name
                                }
                            branches.append(result)

                    return Response({"branches": branches, "status":status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_branch_admin:
                    b = Branch.objects.filter(organisation=org_id)
                    print(b)
                    branches = []
                    for branch in b:
                        if branch.branch_is_active is True:
                            branch_id = branch.id
                            branch_name = branch.branch_name

                            result = {
                                    "branch_id": branch_id,
                                    "branch_name": branch_name
                                }
                            branches.append(result)

                    return Response({"branches": branches, "status":status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no role is defined for this user"})
            except:
                logger.debug("Error while retrieving data")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Data"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class QuestionWizardSequenceAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)
        section_id = request.GET.get('section_id')
        section_id = int(section_id)
        question_section = QuestionSection.objects.filter(section_id=section_id)
        print(question_section)
        print("section_id check")
        print(section_id)
        # question_section = Question.objects.filter(question_section=section_id)


        org_id = request.GET.get('org_id')
        org_id = None if org_id == '0' else org_id
        branch_id = request.GET.get('branch_id')
        branch_id = None if branch_id == '0' else branch_id
        customer_code = request.GET.get('customer_code')
        customer_code = None if customer_code == '' else customer_code

        print(customer_code)
        # print('-----------------')
        # print(question_section)
        # print('-----------------')
        # customers = CustomerCode.objects.filter(customer_code=customer_code)
        # for customer in customers:
        #     cust_code = customer.customer_code

        if user:
            try:
                # print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    section_param = Q(question_section=question_section[0])
                    org_param = Q(organisation=org_id)
                    branch_param = Q(branch=branch_id)
                    if customer_code is not None:
                        customer_list = customer_code.split(',')
                        customer_param = Q(customer_code__in=customer_list)
                    else:
                        customer_param = Q(customer_code='')

                    print(customer_param)
                    questions = Question.objects.order_by("question_sequence").filter(section_param & org_param & branch_param & customer_param)
                    # branches = Question.objects.order_by("question_sequence").filter(branch=branch_id)
                    # customer_codes = Question.objects.order_by("question_sequence").filter(customer_code=customer_code)
                    # print(questions)
                    total_questions = questions.count()
                    print('total_questions')
                    print(total_questions)
                    quest = Paginator(questions, 5)
                    # if page_size:
                    #     quest = Paginator(questions, page_size)
                    page = request.GET.get('page')
                    # ques = quest.page(page)
                    print(page)

                    try:
                        ques = quest.page(page)
                    except PageNotAnInteger:
                        ques = quest.page(1)
                    except EmptyPage:
                        ques = quest.page(quest.num_pages)

                    has_next = ques.has_next()
                    if has_next is True:
                        next_page_number = ques.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques.has_previous()
                    if has_previous is True:
                        previous_page_number = ques.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)

                    sequences = []
                    for question in ques:
                        print(question)

                        sequence = question.question_sequence

                        type = question.question_type.question_type

                        text = question.question_text

                        customer_code = question.customer_code

                        result1 = {
                            "sequence": sequence,
                            "type": type,
                            "text": text,
                            "customer_code": customer_code
                        }

                        sequences.append(result1)

                    return Response({"sequences": sequences, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_questions": total_questions, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    section_param = Q(question_section=section_id)
                    org_param = Q(organisation=org_id)
                    branch_param = Q(branch=branch_id)
                    if customer_code is not None:
                        customer_list = customer_code.split(',')
                        customer_param = Q(customer_code__in=customer_list)
                    else:
                        customer_param = Q(customer_code='')

                    print(customer_param)
                    questions = Question.objects.order_by("question_sequence").filter(section_param & org_param & branch_param & customer_param)
                    # branches = Question.objects.order_by("question_sequence").filter(branch=branch_id)
                    # customer_codes = Question.objects.order_by("question_sequence").filter(customer_code=customer_code)
                    print(questions)
                    total_questions = questions.count()
                    print(total_questions)
                    quest = Paginator(questions, 5)
                    # if page_size:
                    #     quest = Paginator(questions, page_size)
                    page = request.GET.get('page')
                    # ques = quest.page(page)
                    print(page)

                    try:
                        ques = quest.page(page)
                    except PageNotAnInteger:
                        ques = quest.page(1)
                    except EmptyPage:
                        ques = quest.page(quest.num_pages)

                    has_next = ques.has_next()
                    if has_next is True:
                        next_page_number = ques.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques.has_previous()
                    if has_previous is True:
                        previous_page_number = ques.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)

                    sequences = []
                    for question in ques:
                        # print(question)

                        sequence = question.question_sequence

                        type = question.question_type.question_type

                        text = question.question_text

                        customer_code = question.customer_code

                        result1 = {
                            "sequence": sequence,
                            "type": type,
                            "text": text,
                            "customer_code": customer_code
                        }

                        sequences.append(result1)

                    return Response({"sequences": sequences, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_questions": total_questions, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_branch_admin:
                    section_param = Q(question_section=section_id)
                    branch_param = Q(branch=branch_id)
                    if customer_code is not None:
                        customer_list = customer_code.split(',')
                        customer_param = Q(customer_code__in=customer_list)
                    else:
                        customer_param = Q(customer_code='')

                    print(customer_param)
                    questions = Question.objects.order_by("question_sequence").filter(section_param & branch_param & customer_param)
                    # branches = Question.objects.order_by("question_sequence").filter(branch=branch_id)
                    # customer_codes = Question.objects.order_by("question_sequence").filter(customer_code=customer_code)
                    print(questions)
                    total_questions = questions.count()
                    print(total_questions)
                    quest = Paginator(questions, 5)
                    # if page_size:
                    #     quest = Paginator(questions, page_size)
                    page = request.GET.get('page')
                    # ques = quest.page(page)
                    print(page)

                    try:
                        ques = quest.page(page)
                    except PageNotAnInteger:
                        ques = quest.page(1)
                    except EmptyPage:
                        ques = quest.page(quest.num_pages)

                    has_next = ques.has_next()
                    if has_next is True:
                        next_page_number = ques.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques.has_previous()
                    if has_previous is True:
                        previous_page_number = ques.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)

                    sequences = []
                    for question in ques:
                        # print(question)

                        sequence = question.question_sequence

                        type = question.question_type.question_type

                        text = question.question_text

                        customer_code = question.customer_code

                        result1 = {
                            "sequence": sequence,
                            "type": type,
                            "text": text,
                            "customer_code": customer_code
                        }

                        sequences.append(result1)

                    return Response({"sequences": sequences, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_questions": total_questions, "status":status.HTTP_200_OK})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "not role is defined for this user"})
            except:
                logger.debug("Error while retrieving data")
                print(traceback.format_exc())
                logger.debug("email{}".format(traceback.format_exc()))
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Data"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})


class QuestionWizardRunsheetAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        org_id = request.GET.get('org_id')
        org_id = None if org_id == '0' else org_id
        branch_id = request.GET.get('branch_id')
        branch_id = None if branch_id == '0' else branch_id

        if user:
            try:
                if request.user.is_active and request.user.is_superuser:
                    if branch_id:
                        branch = Branch.objects.filter(pk=branch_id)
                        print("id hai")

                    elif org_id is None and branch_id is None:
                        branch = Branch.objects.all()
                        print(branch)
                        # branch_id = branch[0].id
                        # print("check this out branch_id")
                        # print(branch_id)
                        print("org and branch id nhi hai")

                    elif org_id and branch_id is None:
                        print("what the hell ")
                        branch = Branch.objects.filter(organisation=org_id)
                        # branch_id = branch[0].id
                        # print("check this out branch_id2354")
                        # print(branch_id)
                        print("org hai but branch id nhi hai")
                    else:
                        return Response({"status": status.HTTP_204_NO_CONTENT,
                                         "Msg": "There is no api found regarding this branch"})

                elif request.user.is_active and request.user.is_organisation_admin:
                    if branch_id:
                        branch = Branch.objects.filter(pk=branch_id)
                        print("id hai")

                    elif org_id is None and branch_id is None:
                        org_admin = OrganisationAdmins.objects.filter(user=user_id)
                        org_id = org_admin[0].organisation.id
                        print("check thi out org_id")
                        print(org_id)
                        branch = Branch.objects.filter(organisation=org_id)
                        if branch:
                            print(branch)
                        else:
                            branch = Branch.objects.all()
                        print("org and branch id nhi hai")

                    elif org_id and branch_id is None:
                        print("what the hell ")
                        branch = Branch.objects.filter(organisation=org_id)
                        if branch:
                            print(branch)
                        else:
                            branch = Branch.objects.all()
                        print("org hai but branch id nhi hai")
                    else:
                        return Response({"status": status.HTTP_204_NO_CONTENT,
                                         "Msg": "There is no api found regarding this branch"})

                elif request.user.is_active and request.user.is_branch_admin:
                    if branch_id:
                        branch = Branch.objects.filter(pk=branch_id)
                        print("id hai")

                    elif branch_id is None:
                        branch_admin = BranchAdmins.objects.filter(user=user_id)
                        branch_id = branch_admin[0].branch_id
                        branch = Branch.objects.filter(pk=branch_id)
                        if branch:
                            print(branch)
                        else:
                            branch = Branch.objects.all()
                        print("branch id nhi hai for branch")
                        print(branch)

                    else:
                        return Response({"status": status.HTTP_204_NO_CONTENT,
                                         "Msg": "There is no api found regarding this branch"})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no role is defined for this user"})

                if branch:
                    branch_api_server_ip = branch[0].branch_api_server_ip
                else:
                    return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "No branch api found regarding this branch_id"})
                    
                if branch_api_server_ip:
                    data = {
                        "device_id": "1234567892",
                        "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie",
                    }

                    # or we can write it like data = json.dumps(data)
                    response1 = requests.post(
                        'http://' + branch_api_server_ip + ':80/KJWeb/transport/api/get_status_list_run.php',
                        json=data)
                    response1 = response1.json()
                    print("RESPONSE RUN")
                    print(response1)

                    for run_status in response1['statuses']:
                        run_status_id = run_status['status_id']
                        run_status_id = int(run_status_id)
                        # print(type(run_status_id))
                        run_status_name = run_status['status_name']
                        run_status_obj = QuestionActionStatus.objects.filter(run_status_id=run_status_id)
                        if run_status_obj.exists():
                            run_status_obj.update(question_action_status=True, run_status_id=run_status_id,
                                                  run_status_name=run_status_name, run_status=True)
                        else:
                            QuestionActionStatus.objects.create(question_action_status=True,
                                                                run_status_id=run_status_id,
                                                                run_status_name=run_status_name, run_status=True)
                        print("run statuses")
                        print(QuestionActionStatus)

                    response2 = requests.post(
                        'http://' + branch_api_server_ip + ':80/KJWeb/transport/api/get_status_list_drop.php',
                        json=data)
                    response2 = response2.json()
                    print("RESPONSE Drop")
                    print(response2)

                    for drop_status in response2['statuses']:
                        drop_status_id = drop_status['status_id']
                        drop_status_id = int(drop_status_id)
                        # print(type(drop_status_id))
                        drop_status_name = drop_status['status_name']
                        drop_status_obj = QuestionActionStatus.objects.filter(drop_status_id=drop_status_id)
                        if drop_status_obj.exists():
                            drop_status_obj.update(question_action_status=True, drop_status_id=drop_status_id,
                                                   drop_status_name=drop_status_name, drop_status=True)
                        else:
                            QuestionActionStatus.objects.create(question_action_status=True,
                                                                drop_status_id=drop_status_id,
                                                                drop_status_name=drop_status_name, drop_status=True)
                        print("drop statuses")
                        print(QuestionActionStatus)

                    response3 = requests.post(
                        'http://' + branch_api_server_ip + ':80/KJWeb/transport/api/get_run_log_type.php',
                        json=data)
                    response3 = response3.json()
                    for log_entry_types in response3['types']:
                        type_id = log_entry_types['type_id']
                        type_id = int(type_id)
                        # print(type(type_id))
                        type_name = log_entry_types['type_name']
                        log_type_obj = QuestionActionLogType.objects.filter(type_id=type_id)
                        if log_type_obj.exists():
                            log_type_obj.update(type_id=type_id, type_name=type_name)
                        else:
                            QuestionActionLogType.objects.create(type_id=type_id, type_name=type_name)
                        print("log types entry")
                        print(QuestionActionLogType)

                    response4 = requests.post(
                        'http://' + branch_api_server_ip + ':80/KJWeb/transport/api/get_drop_type_list.php',
                        json=data)
                    response4 = response4.json()
                    for drop_type in response4['types']:
                        section_id = drop_type['type_id']
                        section_id = int(section_id)
                        print(section_id)
                        # print(type(section_id))
                        section_name = drop_type['type_name']
                        drop_type_obj = QuestionSection.objects.filter(section_id=section_id)
                        if drop_type_obj.exists():
                            drop_type_obj.update(section_id=section_id, section_name=section_name)
                        else:
                            QuestionSection.objects.create(section_id=section_id, section_name=section_name)
                        print("question sections")
                        print(QuestionSection)
                else:
                    return Response(
                        {"status": status.HTTP_204_NO_CONTENT, "Msg": "No api found regarding this branch"})

                sections = QuestionSection.objects.all()
                log_types = QuestionActionLogType.objects.all()
                statuses = QuestionActionStatus.objects.all()

                question_sections = []
                question_log_types = []
                run_statuses = []
                drop_statuses = []

                for section in sections:
                    section_id = section.section_id
                    section_name = section.section_name

                    result3 = {
                        "question_section_id": section_id,
                        "question_section_type": section_name
                    }
                    question_sections.append(result3)

                for log_type in log_types:
                    type_id = log_type.type_id
                    type_name = log_type.type_name

                    result1 = {
                        "log_type_id": type_id,
                        "log_type": type_name
                    }

                    question_log_types.append(result1)

                for stat in statuses:
                    if stat.run_status_id is not None:
                        run_status_id = stat.run_status_id
                        run_status_name = stat.run_status_name
                        run_status = stat.run_status
                        drop_status = stat.drop_status

                        result1 = {
                            "status_id": run_status_id,
                            "status_name": run_status_name,
                            "run_status": run_status,
                            "drop_status": drop_status
                        }
                        run_statuses.append(result1)

                for stat in statuses:
                    if stat.drop_status_id is not None:
                        drop_status_id = stat.drop_status_id
                        drop_status_name = stat.drop_status_name
                        run_status = stat.run_status
                        drop_status = stat.drop_status

                        result1 = {
                            "status_id": drop_status_id,
                            "status_name": drop_status_name,
                            "run_status": run_status,
                            "drop_status": drop_status
                        }

                        drop_statuses.append(result1)

                return Response({"question_sections": question_sections,
                                 "question_log_types": question_log_types,
                                 "run_statuses": run_statuses, "drop_statuses": drop_statuses,
                                 "status": status.HTTP_200_OK})
            except:
                logger.debug("Error while retrieving data")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Data"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class QuestionCreateAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request):

        org_id = request.POST.get('org_id')
        org_id = None if org_id == '0' else org_id
        branch_id = request.POST.get('branch_id')
        print(type(branch_id))
        branch_id = None if branch_id == '0' else branch_id
        customer_code = request.POST.get('customer_code')
        customer_code = None if customer_code == '' else customer_code
        section_id = request.POST.get('section_id')
        sequence = request.POST.get('sequence')
        question_type = request.POST.get('question_type')
        question_text = request.POST.get('question_text')

        true_log = request.POST.get('true_log')
        true_log = True if true_log == 'true' else False

        true_log_type_id = request.POST.get('true_log_type_id')
        true_log_type_id = None if true_log_type_id == '0' else true_log_type_id

        true_log_GPS = request.POST.get('true_log_GPS')
        true_log_GPS = True if true_log_GPS == 'true' else False

        true_log_text = request.POST.get('true_log_text')

        true_log_no_packages = request.POST.get('true_log_no_packages')
        true_log_no_packages = True if true_log_no_packages == 'true' else False

        true_log_dateTime = request.POST.get('true_log_dateTime')
        true_log_dateTime = True if true_log_dateTime == 'true' else False

        true_log_driver_name = request.POST.get('true_log_driver_name')
        true_log_driver_name = True if true_log_driver_name == 'true' else False

        true_log_customer_name = request.POST.get('true_log_customer_name')
        true_log_customer_name = True if true_log_customer_name == 'true' else False

        true_block = request.POST.get('true_block')
        true_block = True if true_block == 'true' else False

        true_block_text = request.POST.get('true_block_text')

        true_status = request.POST.get('true_status')
        true_status = True if true_status == 'true' else False

        #1234567890-----------------------------------------------#

        true_status_id = request.POST.get('true_status_id')
        true_status_id = None if true_status_id == '0' else true_status_id

        # true_run_status_name = request.POST.get('true_run_status_name')
        # true_run_status_name = None if true_run_status_name == '0' else true_run_status_name

        # true_drop_status_id = request.POST.get('true_drop_status_id')
        # true_drop_status_id = None if true_drop_status_id == '0' else true_drop_status_id

        # true_drop_status_name = request.POST.get('true_drop_status_name')
        # true_drop_status_name = None if true_drop_status_name == '0' else true_drop_status_name

        true_run_status = request.POST.get('true_run_status')
        true_run_status = True if true_run_status == 'true' else False

        true_drop_status = request.POST.get('true_drop_status')
        true_drop_status = True if true_drop_status == 'true' else False

        #0987654321------------------------------------------------#

        true_record = request.POST.get('true_record')
        true_record = True if true_record == 'true' else False

        true_take_photo = request.POST.get('true_take_photo')
        true_take_photo = True if true_take_photo == 'true' else False

        true_take_signature = request.POST.get('true_take_signature')
        true_take_signature = True if true_take_signature == 'true' else False

        true_no_action = request.POST.get('true_no_action')
        true_no_action = True if true_no_action == 'true' else False

        false_log = request.POST.get('false_log')
        print(" did it thiod %s" % false_log)
        print(" did it thiod %s" % type(false_log))
        false_log = True if false_log == 'true' else False
        print(" did it thiod %s" % false_log)
        print(" did it thiod %s" % type(false_log))

        false_log_type_id = request.POST.get('false_log_type_id')
        false_log_type_id = None if false_log_type_id == '0' else false_log_type_id

        false_log_GPS = request.POST.get('false_log_GPS')
        false_log_GPS = True if false_log_GPS == 'true' else False

        false_log_text = request.POST.get('false_log_text')

        false_log_no_packages = request.POST.get('false_log_no_packages')
        false_log_no_packages = True if false_log_no_packages == 'true' else False

        false_log_dateTime = request.POST.get('false_log_dateTime')
        false_log_dateTime = True if false_log_dateTime == 'true' else False

        false_log_driver_name = request.POST.get('false_log_driver_name')
        false_log_driver_name = True if false_log_driver_name == 'true' else False

        false_log_customer_name = request.POST.get('false_log_customer_name')
        false_log_customer_name = True if false_log_customer_name == 'true' else False

        false_block = request.POST.get('false_block')
        false_block = True if false_block == 'true' else False

        false_block_text = request.POST.get('false_block_text')

        false_status = request.POST.get('false_status')
        false_status = True if false_status == 'true' else False

        # 1234567890-----------------------------------------------#

        false_status_id = request.POST.get('false_status_id')
        false_status_id = None if false_status_id == '0' else false_status_id

        # false_run_status_name = request.POST.get('false_run_status_name')
        # false_run_status_name = None if false_run_status_name == '0' else false_run_status_name

        # false_drop_status_id = request.POST.get('false_drop_status_id')
        # false_drop_status_id = None if false_drop_status_id == '0' else false_drop_status_id

        # false_drop_status_name = request.POST.get('false_drop_status_name')
        # false_drop_status_name = None if false_drop_status_name == '0' else false_drop_status_name

        false_run_status = request.POST.get('false_run_status')
        false_run_status = True if false_run_status == 'true' else False

        false_drop_status = request.POST.get('false_drop_status')
        false_drop_status = True if false_drop_status == 'true' else False

        # 0987654321------------------------------------------------#

        false_record = request.POST.get('false_record')
        false_record = True if false_record == 'true' else False

        false_take_photo = request.POST.get('false_take_photo')
        false_take_photo = True if false_take_photo == 'true' else False

        false_take_signature = request.POST.get('false_take_signature')
        false_take_signature = True if false_take_signature == 'true' else False

        false_no_action = request.POST.get('false_no_action')
        false_no_action = True if false_no_action == 'true' else False

        user_id = request.POST.get('user_id')
        user = User.objects.filter(pk=user_id)

        print("this is org %s" % org_id)
        if org_id is not None:
            orgs = Organisation.objects.filter(pk=org_id)
            for org in orgs:
                org1 = org
        else:
            org1 = None

        print("this is branch %s" % branch_id)
        if branch_id is not None:
            branches = Branch.objects.filter(pk=branch_id)
            for branch in branches:
                if branch.branch_is_active is True:
                    branch1 = branch
        else:
            branch1 = None

        # print("this is customer %s" % customer_code)
        # if customer_code is not None:
        #     custs = CustomerCode.objects.filter(customer_code=customer_code)
        #     for cust in custs:
        #         cust1 = cust
        # else:
        #     cust1 = None

        if section_id is not None:
            sections = QuestionSection.objects.filter(section_id=section_id)
            for sec in sections:
                sec1 = sec
        else:
            sec1 = None

        if question_type is not None:
            types = QuestionType.objects.filter(pk=question_type)
            for typ in types:
                typ1 = typ
        else:
            typ1 = None

        # print(user_id)
        # print(user)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:

                    if false_log is True:
                        if false_log_type_id is not None:
                            false_log_types = QuestionActionLogType.objects.filter(type_id=false_log_type_id)
                            for flt in false_log_types:
                                flt1 = flt
                        else:
                            flt1 = None
                        print(flt1)

                        false_question_action_log = QuestionActionLog.objects.create(question_action_log=false_log,
                                                                                 question_action_log_type=flt1,
                                                                                 question_action_log_text=false_log_text,
                                                                                 question_action_log_driver_name=false_log_driver_name,
                                                                                 question_action_log_driver_gps=false_log_GPS,
                                                                                 question_action_log_no_of_packages=false_log_no_packages,
                                                                                 question_action_log_customer_name=false_log_customer_name,
                                                                                 question_action_log_date_time= false_log_dateTime)
                        false_question_action_log_id = false_question_action_log
                    else:
                        false_question_action_log_id = None

                    if false_block is True:
                        false_question_action_block = QuestionActionBlock.objects.create(question_action_block=false_block, question_action_block_text=false_block_text)
                        false_question_action_block_id = false_question_action_block
                    else:
                        false_question_action_block_id = None

                    if false_status is True:
                        if false_run_status is True:
                            false_question_action_statuses = QuestionActionStatus.objects.filter(run_status_id=false_status_id)
                            for false_question_action_status_id in false_question_action_statuses:
                                false_question_action_status_id1 = false_question_action_status_id
                        elif false_drop_status is True:
                            false_question_action_statuses = QuestionActionStatus.objects.filter(drop_status_id=false_status_id)
                            for false_question_action_status_id in false_question_action_statuses:
                                false_question_action_status_id1 = false_question_action_status_id
                        else:
                            false_question_action_status_id1 = None

                        # false_question_action_status = QuestionActionStatus.objects.create(question_action_status=false_status, question_action_select_status=false_status_code)
                        # false_question_action_status_id = false_question_action_status
                    else:
                        false_question_action_status_id1 = None

                    false_question_action = QuestionAction.objects.create(question_action_log=false_question_action_log_id, question_action_block=false_question_action_block_id, question_action_record=false_record,
                                                              question_action_status=false_question_action_status_id1,
                                                              question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                                                              question_action_no_action=false_no_action)

                    false_action = QuestionFalseAction.objects.create(question_action=false_question_action)

                    if true_log is True:
                        if true_log_type_id is not None:
                            true_log_types = QuestionActionLogType.objects.filter(type_id=true_log_type_id)
                            for tlt in true_log_types:
                                tlt1 = tlt
                        else:
                            tlt1 = None
                        print("Why why why")
                        print(tlt1)

                        true_question_action_log = QuestionActionLog.objects.create(question_action_log=true_log,
                                                                                 question_action_log_type=tlt1,
                                                                                 question_action_log_text=true_log_text,
                                                                                 question_action_log_driver_name=true_log_driver_name,
                                                                                 question_action_log_driver_gps=true_log_GPS,
                                                                                 question_action_log_no_of_packages=true_log_no_packages,
                                                                                 question_action_log_customer_name=true_log_customer_name,
                                                                                 question_action_log_date_time=true_log_dateTime)
                        true_question_action_log_id = true_question_action_log
                    else:
                        true_question_action_log_id = None

                    if true_block is True:
                        true_question_action_block = QuestionActionBlock.objects.create(question_action_block=true_block,
                                                                                     question_action_block_text=true_block_text)
                        true_question_action_block_id = true_question_action_block
                    else:
                        true_question_action_block_id = None

                    if true_status is True:
                        if true_run_status is True:
                            true_question_action_statuses = QuestionActionStatus.objects.filter(run_status_id=true_status_id)
                            for true_question_action_status_id in true_question_action_statuses:
                                true_question_action_status_id1 = true_question_action_status_id
                        elif true_drop_status is True:
                            true_question_action_statuses = QuestionActionStatus.objects.filter(drop_status_id=true_status_id)
                            for true_question_action_status_id in true_question_action_statuses:
                                true_question_action_status_id1 = true_question_action_status_id
                        else:
                            true_question_action_status_id1 = None

                        # true_question_action_status = QuestionActionStatus.objects.create(question_action_status=true_status,
                        #                                                                question_action_select_status=true_status_code)
                        # true_question_action_status_id = true_question_action_status
                    else:
                        true_question_action_status_id1 = None


                    true_question_action = QuestionAction.objects.create(question_action_log=true_question_action_log_id,
                                                                          question_action_block=true_question_action_block_id,
                                                                          question_action_record=true_record,
                                                                          question_action_status=true_question_action_status_id1,
                                                                          question_action_take_photo=true_take_photo,
                                                                          question_action_signature=true_take_signature,
                                                                          question_action_no_action=true_no_action)

                    true_action = QuestionTrueAction.objects.create(question_action=true_question_action)

                    print("this is customer %s" % customer_code)
                    if customer_code is not None:
                        customer_list = customer_code.split(',')
                        for cust in customer_list:
                            cust1 = cust
                            print(customer_list)
                            Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                    question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                    question_text=question_text, question_false_action=false_action,
                                                    question_true_action=true_action)

                    else:
                        cust1 = ''
                        # print(customer_list)
                        Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                           question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                       question_text=question_text, question_false_action=false_action, question_true_action=true_action)


                    return Response({"status":status.HTTP_200_OK, "Msg": "Question has been created successfully."})

                elif request.user.is_active and request.user.is_organisation_admin:
                    # print("this is org %s" % org_id)
                    # if org_id is not None:
                    #     orgs = Organisation.objects.filter(pk=org_id)
                    #     for org in orgs:
                    #         org1 = org
                    #     # branchadmins = BranchAdmins.objects.filter(user=user_id)
                    #     # for branc in branchadmins:
                    #     #     org1 = branc.branch.organisation
                    #     #     print(org1)
                    # else:
                    #     # org1 = None
                    #     orgadmins = OrganisationAdmins.objects.filter(user=user_id)
                    #     for org in orgadmins:
                    #         org1 = org.organisation
                    #         print(org1)

                    if false_log is True:
                        if false_log_type_id is not None:
                            false_log_types = QuestionActionLogType.objects.filter(type_id=false_log_type_id)
                            for flt in false_log_types:
                                flt1 = flt
                        else:
                            flt1 = None
                        print(flt1)

                        false_question_action_log = QuestionActionLog.objects.create(question_action_log=false_log,
                                                                                 question_action_log_type=flt1,
                                                                                 question_action_log_text=false_log_text,
                                                                                 question_action_log_driver_name=false_log_driver_name,
                                                                                 question_action_log_driver_gps=false_log_GPS,
                                                                                 question_action_log_no_of_packages=false_log_no_packages,
                                                                                 question_action_log_customer_name=false_log_customer_name,
                                                                                 question_action_log_date_time= false_log_dateTime)
                        false_question_action_log_id = false_question_action_log
                    else:
                        false_question_action_log_id = None

                    if false_block is True:
                        false_question_action_block = QuestionActionBlock.objects.create(question_action_block=false_block, question_action_block_text=false_block_text)
                        false_question_action_block_id = false_question_action_block
                    else:
                        false_question_action_block_id = None

                    if false_status is True:
                        if false_run_status is True:
                            false_question_action_statuses = QuestionActionStatus.objects.filter(run_status_id=false_status_id)
                            for false_question_action_status_id in false_question_action_statuses:
                                false_question_action_status_id1 = false_question_action_status_id
                        elif false_drop_status is True:
                            false_question_action_statuses = QuestionActionStatus.objects.filter(drop_status_id=false_status_id)
                            for false_question_action_status_id in false_question_action_statuses:
                                false_question_action_status_id1 = false_question_action_status_id
                        else:
                            false_question_action_status_id1 = None

                        # false_question_action_status = QuestionActionStatus.objects.create(question_action_status=false_status, question_action_select_status=false_status_code)
                        # false_question_action_status_id = false_question_action_status
                    else:
                        false_question_action_status_id1 = None

                    false_question_action = QuestionAction.objects.create(question_action_log=false_question_action_log_id, question_action_block=false_question_action_block_id, question_action_record=false_record,
                                                              question_action_status=false_question_action_status_id1,
                                                              question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                                                              question_action_no_action=false_no_action)

                    false_action = QuestionFalseAction.objects.create(question_action=false_question_action)

                    if true_log is True:
                        if true_log_type_id is not None:
                            true_log_types = QuestionActionLogType.objects.filter(type_id=true_log_type_id)
                            for tlt in true_log_types:
                                tlt1 = tlt
                        else:
                            tlt1 = None
                        print("Why why why")
                        print(tlt1)

                        true_question_action_log = QuestionActionLog.objects.create(question_action_log=true_log,
                                                                                 question_action_log_type=tlt1,
                                                                                 question_action_log_text=true_log_text,
                                                                                 question_action_log_driver_name=true_log_driver_name,
                                                                                 question_action_log_driver_gps=true_log_GPS,
                                                                                 question_action_log_no_of_packages=true_log_no_packages,
                                                                                 question_action_log_customer_name=true_log_customer_name,
                                                                                 question_action_log_date_time=true_log_dateTime)
                        true_question_action_log_id = true_question_action_log
                    else:
                        true_question_action_log_id = None

                    if true_block is True:
                        true_question_action_block = QuestionActionBlock.objects.create(question_action_block=true_block,
                                                                                     question_action_block_text=true_block_text)
                        true_question_action_block_id = true_question_action_block
                    else:
                        true_question_action_block_id = None

                    if true_status is True:
                        if true_run_status is True:
                            true_question_action_statuses = QuestionActionStatus.objects.filter(run_status_id=true_status_id)
                            for true_question_action_status_id in true_question_action_statuses:
                                true_question_action_status_id1 = true_question_action_status_id
                        elif true_drop_status is True:
                            true_question_action_statuses = QuestionActionStatus.objects.filter(drop_status_id=true_status_id)
                            for true_question_action_status_id in true_question_action_statuses:
                                true_question_action_status_id1 = true_question_action_status_id
                        else:
                            true_question_action_status_id1 = None

                        # true_question_action_status = QuestionActionStatus.objects.create(question_action_status=true_status,
                        #                                                                question_action_select_status=true_status_code)
                        # true_question_action_status_id = true_question_action_status
                    else:
                        true_question_action_status_id1 = None


                    true_question_action = QuestionAction.objects.create(question_action_log=true_question_action_log_id,
                                                                          question_action_block=true_question_action_block_id,
                                                                          question_action_record=true_record,
                                                                          question_action_status=true_question_action_status_id1,
                                                                          question_action_take_photo=true_take_photo,
                                                                          question_action_signature=true_take_signature,
                                                                          question_action_no_action=true_no_action)

                    true_action = QuestionTrueAction.objects.create(question_action=true_question_action)

                    # print("this is branch %s" % branch_id)
                    # if branch_id is not None:
                    #     branches = Branch.objects.filter(pk=branch_id)
                    #     for branch in branches:
                    #         branch1 = branch
                    #         print(branch1)
                    #         org1 = branch.organisation
                    #     # branchadmins = BranchAdmins.objects.filter(user=user_id)
                    #     # for branc in branchadmins:
                    #     #     org1 = branc.branch.organisation
                    #     #     print(org1)
                    # else:
                    #     branch1 = None
                    #     # org1 = None
                    #     branchadmins = BranchAdmins.objects.filter(user=user_id)
                    #     for branc in branchadmins:
                    #         org1 = branc.branch.organisation
                    #         print(org1)

                    if org_id is not None:
                        orgs = Organisation.objects.filter(pk=org_id)
                        for org in orgs:
                            org1 = org
                            print("this is customer %s" % customer_code)
                            if customer_code is not None:
                                customer_list = customer_code.split(',')
                                for cust in customer_list:
                                    cust1 = cust
                                    print(customer_list)
                                    Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                            question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                            question_text=question_text, question_false_action=false_action,
                                                            question_true_action=true_action)

                            else:
                                cust1 = ''
                                # print(customer_list)
                                Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                                   question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                               question_text=question_text, question_false_action=false_action, question_true_action=true_action)
                    else:
                        # org1 = None
                        orgadmins = OrganisationAdmins.objects.filter(user=user_id)
                        for org in orgadmins:
                            org1 = org.organisation
                            print(org1)
                            print("this is customer %s" % customer_code)
                            if customer_code is not None:
                                customer_list = customer_code.split(',')
                                for cust in customer_list:
                                    cust1 = cust
                                    print(customer_list)
                                    Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                            question_sequence=sequence, question_section=sec1,
                                                            question_type=typ1,
                                                            question_text=question_text,
                                                            question_false_action=false_action,
                                                            question_true_action=true_action)

                            else:
                                cust1 = ''
                                # print(customer_list)
                                Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                        question_sequence=sequence, question_section=sec1,
                                                        question_type=typ1,
                                                        question_text=question_text, question_false_action=false_action,
                                                        question_true_action=true_action)

                    # print("this is customer %s" % customer_code)
                    # if customer_code is not None:
                    #     customer_list = customer_code.split(',')
                    #     for cust in customer_list:
                    #         cust1 = cust
                    #         print(customer_list)
                    #         Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                    #                                 question_sequence=sequence, question_section=sec1, question_type=typ1,
                    #                                 question_text=question_text, question_false_action=false_action,
                    #                                 question_true_action=true_action)
                    #
                    # else:
                    #     cust1 = ''
                    #     # print(customer_list)
                    #     Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                    #                                        question_sequence=sequence, question_section=sec1, question_type=typ1,
                    #                                    question_text=question_text, question_false_action=false_action, question_true_action=true_action)


                    return Response({"status":status.HTTP_200_OK, "Msg": "Question has been created successfully."})

                elif request.user.is_active and request.user.is_branch_admin:

                    # print("this is branch %s" % branch_id)
                    # if branch_id is not None:
                    #     branches = Branch.objects.filter(pk=branch_id)
                    #     for branch in branches:
                    #         branch1 = branch
                    #         print(branch1)
                    #         org1 = branch.organisation
                    #     # branchadmins = BranchAdmins.objects.filter(user=user_id)
                    #     # for branc in branchadmins:
                    #     #     org1 = branc.branch.organisation
                    #     #     print(org1)
                    # else:
                    #     branch1 = None
                    #     # org1 = None
                    #     branchadmins = BranchAdmins.objects.filter(user=user_id)
                    #     for branc in branchadmins:
                    #         org1 = branc.branch.organisation
                    #         print(org1)

                    if false_log is True:
                        if false_log_type_id is not None:
                            false_log_types = QuestionActionLogType.objects.filter(type_id=false_log_type_id)
                            for flt in false_log_types:
                                flt1 = flt
                        else:
                            flt1 = None
                        print(flt1)

                        false_question_action_log = QuestionActionLog.objects.create(question_action_log=false_log,
                                                                                 question_action_log_type=flt1,
                                                                                 question_action_log_text=false_log_text,
                                                                                 question_action_log_driver_name=false_log_driver_name,
                                                                                 question_action_log_driver_gps=false_log_GPS,
                                                                                 question_action_log_no_of_packages=false_log_no_packages,
                                                                                 question_action_log_customer_name=false_log_customer_name,
                                                                                 question_action_log_date_time= false_log_dateTime)
                        false_question_action_log_id = false_question_action_log
                    else:
                        false_question_action_log_id = None

                    if false_block is True:
                        false_question_action_block = QuestionActionBlock.objects.create(question_action_block=false_block, question_action_block_text=false_block_text)
                        false_question_action_block_id = false_question_action_block
                    else:
                        false_question_action_block_id = None

                    if false_status is True:
                        if false_run_status is True:
                            false_question_action_statuses = QuestionActionStatus.objects.filter(run_status_id=false_status_id)
                            for false_question_action_status_id in false_question_action_statuses:
                                false_question_action_status_id1 = false_question_action_status_id
                        elif false_drop_status is True:
                            false_question_action_statuses = QuestionActionStatus.objects.filter(drop_status_id=false_status_id)
                            for false_question_action_status_id in false_question_action_statuses:
                                false_question_action_status_id1 = false_question_action_status_id
                        else:
                            false_question_action_status_id1 = None

                        # false_question_action_status = QuestionActionStatus.objects.create(question_action_status=false_status, question_action_select_status=false_status_code)
                        # false_question_action_status_id = false_question_action_status
                    else:
                        false_question_action_status_id1 = None

                    false_question_action = QuestionAction.objects.create(question_action_log=false_question_action_log_id, question_action_block=false_question_action_block_id, question_action_record=false_record,
                                                              question_action_status=false_question_action_status_id1,
                                                              question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                                                              question_action_no_action=false_no_action)

                    false_action = QuestionFalseAction.objects.create(question_action=false_question_action)

                    if true_log is True:
                        if true_log_type_id is not None:
                            true_log_types = QuestionActionLogType.objects.filter(type_id=true_log_type_id)
                            for tlt in true_log_types:
                                tlt1 = tlt
                        else:
                            tlt1 = None
                        print("Why why why")
                        print(tlt1)

                        true_question_action_log = QuestionActionLog.objects.create(question_action_log=true_log,
                                                                                 question_action_log_type=tlt1,
                                                                                 question_action_log_text=true_log_text,
                                                                                 question_action_log_driver_name=true_log_driver_name,
                                                                                 question_action_log_driver_gps=true_log_GPS,
                                                                                 question_action_log_no_of_packages=true_log_no_packages,
                                                                                 question_action_log_customer_name=true_log_customer_name,
                                                                                 question_action_log_date_time=true_log_dateTime)
                        true_question_action_log_id = true_question_action_log
                    else:
                        true_question_action_log_id = None

                    if true_block is True:
                        true_question_action_block = QuestionActionBlock.objects.create(question_action_block=true_block,
                                                                                     question_action_block_text=true_block_text)
                        true_question_action_block_id = true_question_action_block
                    else:
                        true_question_action_block_id = None

                    if true_status is True:
                        if true_run_status is True:
                            true_question_action_statuses = QuestionActionStatus.objects.filter(run_status_id=true_status_id)
                            for true_question_action_status_id in true_question_action_statuses:
                                true_question_action_status_id1 = true_question_action_status_id
                        elif true_drop_status is True:
                            true_question_action_statuses = QuestionActionStatus.objects.filter(drop_status_id=true_status_id)
                            for true_question_action_status_id in true_question_action_statuses:
                                true_question_action_status_id1 = true_question_action_status_id
                        else:
                            true_question_action_status_id1 = None

                        # true_question_action_status = QuestionActionStatus.objects.create(question_action_status=true_status,
                        #                                                                question_action_select_status=true_status_code)
                        # true_question_action_status_id = true_question_action_status
                    else:
                        true_question_action_status_id1 = None


                    true_question_action = QuestionAction.objects.create(question_action_log=true_question_action_log_id,
                                                                          question_action_block=true_question_action_block_id,
                                                                          question_action_record=true_record,
                                                                          question_action_status=true_question_action_status_id1,
                                                                          question_action_take_photo=true_take_photo,
                                                                          question_action_signature=true_take_signature,
                                                                          question_action_no_action=true_no_action)

                    true_action = QuestionTrueAction.objects.create(question_action=true_question_action)

                    # if branch_id is not None:
                    #     branches = Branch.objects.filter(pk=branch_id)
                    #     for branch in branches:
                    #         branch1 = branch
                    #         print(branch1)
                    #         org1 = branch.organisation
                    #     # branchadmins = BranchAdmins.objects.filter(user=user_id)
                    #     # for branc in branchadmins:
                    #     #     org1 = branc.branch.organisation
                    #     #     print(org1)
                    # else:
                    #     branch1 = None
                    #     # org1 = None
                    #     branchadmins = BranchAdmins.objects.filter(user=user_id)
                    #     for branc in branchadmins:
                    #         org1 = branc.branch.organisation
                    #         print(org1)
                    if branch_id is not None:
                        branches = Branch.objects.filter(pk=branch_id)
                        for branch in branches:
                            branch1 = branch
                            print(branch1)
                            org1 = branch.organisation
                            print("this is customer %s" % customer_code)
                            if customer_code is not None:
                                customer_list = customer_code.split(',')
                                for cust in customer_list:
                                    cust1 = cust
                                    print(customer_list)
                                    Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                            question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                            question_text=question_text, question_false_action=false_action,
                                                            question_true_action=true_action)

                            else:
                                cust1 = ''
                                # print(customer_list)
                                Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                                   question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                               question_text=question_text, question_false_action=false_action, question_true_action=true_action)
                    else:
                        # branch1 = None
                        # org1 = None
                        branchadmins = BranchAdmins.objects.filter(user=user_id)
                        for branc in branchadmins:
                            branch1 = branc.branch
                            org1 = branc.branch.organisation
                            print(org1)
                            print("this is customer %s" % customer_code)
                            if customer_code is not None:
                                customer_list = customer_code.split(',')
                                for cust in customer_list:
                                    cust1 = cust
                                    print(customer_list)
                                    Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                            question_sequence=sequence, question_section=sec1,
                                                            question_type=typ1,
                                                            question_text=question_text,
                                                            question_false_action=false_action,
                                                            question_true_action=true_action)

                            else:
                                cust1 = ''
                                # print(customer_list)
                                Question.objects.create(organisation=org1, branch=branch1, customer_code=cust1,
                                                        question_sequence=sequence, question_section=sec1,
                                                        question_type=typ1,
                                                        question_text=question_text, question_false_action=false_action,
                                                        question_true_action=true_action)

                    return Response({"status":status.HTTP_200_OK, "Msg": "Question has been created successfully."})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no role is defined for this user"})
            except:
                logger.debug("Error while creating question")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Create Question"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class QuestionUpdateAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def put(self, request):
        question_id = request.POST.get('question_id')
        print("question id ok: ")
        print(question_id)
        org_id = request.POST.get('org_id')
        org_id = None if org_id == '0' else org_id
        branch_id = request.POST.get('branch_id')
        print(type(branch_id))
        branch_id = None if branch_id == '0' else branch_id
        customer_code = request.POST.get('customer_code')
        customer_code = None if customer_code == '' else customer_code
        section_id = request.POST.get('section_id')
        sequence = request.POST.get('sequence')
        question_type = request.POST.get('question_type')
        question_text = request.POST.get('question_text')

        true_log = request.POST.get('true_log')
        true_log = True if true_log == 'true' else False

        true_log_type_id = request.POST.get('true_log_type_id')
        true_log_type_id = None if true_log_type_id == '0' else true_log_type_id

        true_log_GPS = request.POST.get('true_log_GPS')
        true_log_GPS = True if true_log_GPS == 'true' else False

        true_log_text = request.POST.get('true_log_text')

        true_log_no_packages = request.POST.get('true_log_no_packages')
        true_log_no_packages = True if true_log_no_packages == 'true' else False

        true_log_dateTime = request.POST.get('true_log_dateTime')
        true_log_dateTime = True if true_log_dateTime == 'true' else False

        true_log_driver_name = request.POST.get('true_log_driver_name')
        true_log_driver_name = True if true_log_driver_name == 'true' else False

        true_log_customer_name = request.POST.get('true_log_customer_name')
        true_log_customer_name = True if true_log_customer_name == 'true' else False

        true_block = request.POST.get('true_block')
        true_block = True if true_block == 'true' else False

        true_block_text = request.POST.get('true_block_text')

        true_status = request.POST.get('true_status')
        true_status = True if true_status == 'true' else False

        # 1234567890-----------------------------------------------#

        true_status_id = request.POST.get('true_status_id')
        true_status_id = None if true_status_id == '0' else true_status_id

        # true_run_status_name = request.POST.get('true_run_status_name')
        # true_run_status_name = None if true_run_status_name == '0' else true_run_status_name

        # true_drop_status_id = request.POST.get('true_drop_status_id')
        # true_drop_status_id = None if true_drop_status_id == '0' else true_drop_status_id

        # true_drop_status_name = request.POST.get('true_drop_status_name')
        # true_drop_status_name = None if true_drop_status_name == '0' else true_drop_status_name

        true_run_status = request.POST.get('true_run_status')
        true_run_status = True if true_run_status == 'true' else False

        true_drop_status = request.POST.get('true_drop_status')
        true_drop_status = True if true_drop_status == 'true' else False

        # 0987654321------------------------------------------------#

        true_record = request.POST.get('true_record')
        true_record = True if true_record == 'true' else False

        true_take_photo = request.POST.get('true_take_photo')
        true_take_photo = True if true_take_photo == 'true' else False

        true_take_signature = request.POST.get('true_take_signature')
        true_take_signature = True if true_take_signature == 'true' else False

        true_no_action = request.POST.get('true_no_action')
        true_no_action = True if true_no_action == 'true' else False

        false_log = request.POST.get('false_log')
        print(" did it thiod %s" % false_log)
        print(" did it thiod %s" % type(false_log))
        false_log = True if false_log == 'true' else False
        print(" did it thiod %s" % false_log)
        print(" did it thiod %s" % type(false_log))

        false_log_type_id = request.POST.get('false_log_type_id')
        false_log_type_id = None if false_log_type_id == '0' else false_log_type_id

        false_log_GPS = request.POST.get('false_log_GPS')
        false_log_GPS = True if false_log_GPS == 'true' else False

        false_log_text = request.POST.get('false_log_text')

        false_log_no_packages = request.POST.get('false_log_no_packages')
        false_log_no_packages = True if false_log_no_packages == 'true' else False

        false_log_dateTime = request.POST.get('false_log_dateTime')
        false_log_dateTime = True if false_log_dateTime == 'true' else False

        false_log_driver_name = request.POST.get('false_log_driver_name')
        false_log_driver_name = True if false_log_driver_name == 'true' else False

        false_log_customer_name = request.POST.get('false_log_customer_name')
        false_log_customer_name = True if false_log_customer_name == 'true' else False

        false_block = request.POST.get('false_block')
        false_block = True if false_block == 'true' else False

        false_block_text = request.POST.get('false_block_text')

        false_status = request.POST.get('false_status')
        false_status = True if false_status == 'true' else False

        # 1234567890-----------------------------------------------#

        false_status_id = request.POST.get('false_status_id')
        false_status_id = None if false_status_id == '0' else false_status_id

        # false_run_status_name = request.POST.get('false_run_status_name')
        # false_run_status_name = None if false_run_status_name == '0' else false_run_status_name

        # false_drop_status_id = request.POST.get('false_drop_status_id')
        # false_drop_status_id = None if false_drop_status_id == '0' else false_drop_status_id

        # false_drop_status_name = request.POST.get('false_drop_status_name')
        # false_drop_status_name = None if false_drop_status_name == '0' else false_drop_status_name

        false_run_status = request.POST.get('false_run_status')
        false_run_status = True if false_run_status == 'true' else False

        false_drop_status = request.POST.get('false_drop_status')
        false_drop_status = True if false_drop_status == 'true' else False

        # 0987654321------------------------------------------------#

        false_record = request.POST.get('false_record')
        false_record = True if false_record == 'true' else False

        false_take_photo = request.POST.get('false_take_photo')
        false_take_photo = True if false_take_photo == 'true' else False

        false_take_signature = request.POST.get('false_take_signature')
        false_take_signature = True if false_take_signature == 'true' else False

        false_no_action = request.POST.get('false_no_action')
        false_no_action = True if false_no_action == 'true' else False

        user_id = request.POST.get('user_id')
        user = User.objects.filter(pk=user_id)

        print("this is org %s" % org_id)
        if org_id is not None:
            orgs = Organisation.objects.filter(pk=org_id)
            for org in orgs:
                org1 = org
        else:
            org1 = None

        print("this is branch %s" % branch_id)
        if branch_id is not None:
            branches = Branch.objects.filter(pk=branch_id)
            for branch in branches:
                if branch.branch_is_active is True:
                    branch1 = branch
        else:
            branch1 = None

        # print("this is customer %s" % customer_code)
        # if customer_code is not None:
        #     custs = CustomerCode.objects.filter(customer_code=customer_code)
        #     for cust in custs:
        #         cust1 = cust
        # else:
        #     cust1 = None

        if section_id is not None:
            sections = QuestionSection.objects.filter(section_id=section_id)
            for sec in sections:
                sec1 = sec
        else:
            sec1 = None

        if question_type is not None:
            types = QuestionType.objects.filter(pk=question_type)
            for typ in types:
                typ1 = typ
        else:
            typ1 = None

        # print(user_id)
        # print(user)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin:
                    question_obj = Question.objects.filter(pk=question_id)
                    print(question_obj)

                    false_question_action_log_id_updated = None
                    false_question_action_block_id_updated = None

                    true_question_action_log_id_updated = None
                    true_question_action_block_id_updated = None


                    if question_obj:
                        # for q in question_obj:
                            # if q.question_false_action.question_action.question_action_log is not None:
                            #     false_question_action_log_pk = q.question_false_action.question_action.question_action_log.id
                            #     false_question_action_log_obj = QuestionActionLog.objects.filter(pk=false_question_action_log_pk)

                            # if q.question_false_action.question_action.question_action_block is not None:
                            #     false_question_action_block_pk = q.question_false_action.question_action.question_action_block.id
                            #     false_question_action_block_obj = QuestionActionBlock.objects.filter(pk=false_question_action_block_pk)

                            # if q.question_false_action.question_action.question_action_status is not None:
                            #     false_question_action_status_pk = q.question_false_action.question_action.question_action_status.id
                            #     false_question_action_status_obj = QuestionActionStatus.objects.filter(pk=false_question_action_status_pk)

                            # if q.question_false_action.question_action is not None:
                            #     false_question_action_pk = q.question_false_action.question_action.id
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)

                            # if q.question_false_action is not None:
                            #     question_false_action_pk = q.question_false_action.id
                            #     question_false_action_obj = QuestionFalseAction.objects.filter(pk=question_false_action_pk)

                            # if q.question_true_action.question_action.question_action_log is not None:
                            #     true_question_action_log_pk = q.question_true_action.question_action.question_action_log.id
                            #     true_question_action_log_obj = QuestionActionLog.objects.filter(pk=true_question_action_log_pk)

                            # if q.question_true_action.question_action.question_action_block is not None:
                            #     true_question_action_block_pk = q.question_true_action.question_action.question_action_block.id
                            #     true_question_action_block_obj = QuestionActionBlock.objects.filter(pk=true_question_action_block_pk)

                            # if q.question_true_action.question_action.question_action_status is not None:
                            #     true_question_action_status_pk = q.question_true_action.question_action.question_action_status.id
                            #     true_question_action_status_obj = QuestionActionStatus.objects.filter(pk=true_question_action_status_pk)

                            # if q.question_true_action.question_action is not None:
                            #     true_question_action_pk = q.question_true_action.question_action.id
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)

                            # if q.question_true_action is not None:
                            #     question_true_action_pk = q.question_true_action.id
                            #     question_true_action_obj = QuestionTrueAction.objects.filter(pk=question_true_action_pk)

                        if false_log is True:
                            if false_log_type_id is not None:
                                false_log_types = QuestionActionLogType.objects.filter(type_id=false_log_type_id)
                                for flt in false_log_types:
                                    flt1 = flt
                            else:
                                flt1 = None
                            print("asddddddddddddddddddddddddddddddddddddddd1")
                            print(flt1)

                            for q in question_obj:
                                if q.question_false_action.question_action.question_action_log is not None:
                                    print("question_action_log:")
                                    print(question_obj)
                                    print(q.question_false_action.question_action)
                                    print(q.question_false_action.question_action.question_action_log)
                                    print(q.question_false_action.question_action.question_action_log.id)
                                    false_question_action_log_pk = q.question_false_action.question_action.question_action_log.id
                                    false_question_action_log_obj = QuestionActionLog.objects.filter(pk=false_question_action_log_pk)

                                    false_question_action_log = false_question_action_log_obj.update(question_action_log=false_log,
                                                                                     question_action_log_type=flt1,
                                                                                     question_action_log_text=false_log_text,
                                                                                     question_action_log_driver_name=false_log_driver_name,
                                                                                     question_action_log_driver_gps=false_log_GPS,
                                                                                     question_action_log_no_of_packages=false_log_no_packages,
                                                                                     question_action_log_customer_name=false_log_customer_name,
                                                                                     question_action_log_date_time= false_log_dateTime)
                                    false_question_action_log_id_updated = false_question_action_log
                                else:
                                    false_question_action_log = QuestionActionLog.objects.create(
                                        question_action_log=false_log,
                                        question_action_log_type=flt1,
                                        question_action_log_text=false_log_text,
                                        question_action_log_driver_name=false_log_driver_name,
                                        question_action_log_driver_gps=false_log_GPS,
                                        question_action_log_no_of_packages=false_log_no_packages,
                                        question_action_log_customer_name=false_log_customer_name,
                                        question_action_log_date_time=false_log_dateTime)
                                    false_question_action_log_id = false_question_action_log
                        else:
                            false_question_action_log_id = None
                        # print("false_question_action_log_id:")
                        # print(false_question_action_log_id)

                        if false_block is True:
                            for q in question_obj:
                                if q.question_false_action.question_action.question_action_block is not None:
                                    false_question_action_block_pk = q.question_false_action.question_action.question_action_block.id
                                    false_question_action_block_obj = QuestionActionBlock.objects.filter(pk=false_question_action_block_pk)
                                    false_question_action_block = false_question_action_block_obj.update(question_action_block=false_block, question_action_block_text=false_block_text)
                                    false_question_action_block_id_updated = false_question_action_block
                                else:
                                    false_question_action_block = QuestionActionBlock.objects.create(question_action_block=false_block, question_action_block_text=false_block_text)
                                    false_question_action_block_id = false_question_action_block
                        else:
                            false_question_action_block_id = None
                        # print("false_question_action_block_id:")
                        # print(false_question_action_block_id)

                        if false_status is True:
                            if false_run_status is True:
                                false_question_action_statuses = QuestionActionStatus.objects.filter(
                                    run_status_id=false_status_id)
                                for false_question_action_status_id in false_question_action_statuses:
                                    false_question_action_status_id1 = false_question_action_status_id
                            elif false_drop_status is True:
                                false_question_action_statuses = QuestionActionStatus.objects.filter(
                                    drop_status_id=false_status_id)
                                for false_question_action_status_id in false_question_action_statuses:
                                    false_question_action_status_id1 = false_question_action_status_id
                            else:
                                false_question_action_status_id1 = None
                        else:
                            false_question_action_status_id1 = None

                        # if false_status is True:
                        #     for q in question_obj:
                        #         if q.question_false_action.question_action.question_action_status is not None:
                        #             false_question_action_status_pk = q.question_false_action.question_action.question_action_status.id
                        #             false_question_action_status_obj = QuestionActionStatus.objects.filter(pk=false_question_action_status_pk)
                        #             false_question_action_status = false_question_action_status_obj.update(question_action_status=false_status, question_action_select_status=false_status_code)
                        #             false_question_action_status_id_updated = false_question_action_status
                        #         else:
                        #             false_question_action_status = QuestionActionStatus.objects.create(question_action_status=false_status, question_action_select_status=false_status_code)
                        #             false_question_action_status_id = false_question_action_status
                        # else:
                        #     false_question_action_status_id = None
                        # print("false_question_action_status_id:")
                        # print(false_question_action_status_id)

                        for q in question_obj:
                            # if q.question_false_action.question_action is not None:
                            false_question_action_pk = q.question_false_action.question_action.id

                            print("false must needed")
                            print(false_question_action_pk)
                            if false_question_action_log_id_updated is not None and false_question_action_block_id_updated is not None:
                                false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(question_action_record=false_record, question_action_status=false_question_action_status_id1,
                                                                  question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                                                                  question_action_no_action=false_no_action)
                                # print("false_question_action:")
                                # print(false_question_action)

                            # elif false_question_action_log_id_updated is not None and false_question_action_block_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_record=false_record,
                            #                                       question_action_status=false_question_action_status_id,question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)
                            # elif false_question_action_log_id_updated is not None and false_question_action_status_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_block=false_question_action_block_id, question_action_record=false_record,
                            #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)
                            elif false_question_action_log_id_updated is not None:
                                false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(question_action_block=false_question_action_block_id, question_action_record=false_record,
                                                                 question_action_status=false_question_action_status_id1,
                                                                  question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                                                                  question_action_no_action=false_no_action)
                            # elif false_question_action_block_id_updated is not None and false_question_action_status_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_record=false_record,
                            #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)

                            elif false_question_action_block_id_updated is not None:
                                false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_record=false_record,
                                                                 question_action_status=false_question_action_status_id1,
                                                                  question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                                                                  question_action_no_action=false_no_action)
                            # elif false_question_action_status_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_block=false_question_action_block_id, question_action_record=false_record,
                            #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)
                            else:
                                false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(
                                    question_action_log=false_question_action_log_id,
                                    question_action_block=false_question_action_block_id,
                                    question_action_record=false_record,
                                    question_action_status=false_question_action_status_id1,
                                    question_action_take_photo=false_take_photo,
                                    question_action_signature=false_take_signature,
                                    question_action_no_action=false_no_action)

                        # for q in question_obj:
                        #     if q.question_false_action is not None:
                        #         question_false_action_pk = q.question_false_action.id
                        #         print("question_false_action_pk")
                        #         print(question_false_action_pk)
                        #         question_false_action_obj = QuestionFalseAction.objects.filter(pk=question_false_action_pk)
                        #         false_action = question_false_action_obj.update(question_action=false_question_action)
                        #         print("false_action")

                        if true_log is True:
                            if true_log_type_id is not None:
                                true_log_types = QuestionActionLogType.objects.filter(type_id=true_log_type_id)
                                for tlt in true_log_types:
                                    tlt1 = tlt
                            else:
                                tlt1 = None
                            print("Why why why")
                            print(tlt1)

                            for q in question_obj:
                                if q.question_true_action.question_action.question_action_log is not None:
                                    true_question_action_log_pk = q.question_true_action.question_action.question_action_log.id
                                    true_question_action_log_obj = QuestionActionLog.objects.filter(pk=true_question_action_log_pk)

                                    true_question_action_log = true_question_action_log_obj.update(question_action_log=true_log,
                                                                                     question_action_log_type=tlt1,
                                                                                     question_action_log_text=true_log_text,
                                                                                     question_action_log_driver_name=true_log_driver_name,
                                                                                     question_action_log_driver_gps=true_log_GPS,
                                                                                     question_action_log_no_of_packages=true_log_no_packages,
                                                                                     question_action_log_customer_name=true_log_customer_name,
                                                                                     question_action_log_date_time=true_log_dateTime)
                                    true_question_action_log_id_updated = true_question_action_log
                                else:
                                    true_question_action_log = QuestionActionLog.objects.create(
                                        question_action_log=true_log,
                                        question_action_log_type=tlt1,
                                        question_action_log_text=true_log_text,
                                        question_action_log_driver_name=true_log_driver_name,
                                        question_action_log_driver_gps=true_log_GPS,
                                        question_action_log_no_of_packages=true_log_no_packages,
                                        question_action_log_customer_name=true_log_customer_name,
                                        question_action_log_date_time=true_log_dateTime)
                                    true_question_action_log_id = true_question_action_log
                        else:
                            true_question_action_log_id = None
                        # print("true_question_action_log_id")
                        # print(true_question_action_log_id)

                        if true_block is True:
                            for q in question_obj:
                                if q.question_true_action.question_action.question_action_block is not None:
                                    true_question_action_block_pk = q.question_true_action.question_action.question_action_block.id
                                    true_question_action_block_obj = QuestionActionBlock.objects.filter(pk=true_question_action_block_pk)
                                    true_question_action_block = true_question_action_block_obj.update(question_action_block=true_block,
                                                                                         question_action_block_text=true_block_text)
                                    true_question_action_block_id_updated = true_question_action_block
                                else:
                                    true_question_action_block = QuestionActionBlock.objects.create(question_action_block=true_block, question_action_block_text=true_block_text)
                                    true_question_action_block_id = true_question_action_block
                        else:
                            true_question_action_block_id = None

                        # print("true_question_action_block_id")
                        # print(true_question_action_block_id)

                        if true_status is True:
                            if true_run_status is True:
                                true_question_action_statuses = QuestionActionStatus.objects.filter(
                                    run_status_id=true_status_id)
                                for true_question_action_status_id in true_question_action_statuses:
                                    true_question_action_status_id1 = true_question_action_status_id
                            elif true_drop_status is True:
                                true_question_action_statuses = QuestionActionStatus.objects.filter(
                                    drop_status_id=true_status_id)
                                for true_question_action_status_id in true_question_action_statuses:
                                    true_question_action_status_id1 = true_question_action_status_id
                            else:
                                true_question_action_status_id1 = None
                        else:
                            true_question_action_status_id1 = None

                        # if true_status is True:
                        #     for q in question_obj:
                        #         if q.question_true_action.question_action.question_action_status is not None:
                        #             true_question_action_status_pk = q.question_true_action.question_action.question_action_status.id
                        #             true_question_action_status_obj = QuestionActionStatus.objects.filter(pk=true_question_action_status_pk)
                        #             true_question_action_status = true_question_action_status_obj.update(question_action_status=true_status,
                        #                                                                    question_action_select_status=true_status_code)
                        #             true_question_action_status_id_updated = true_question_action_status
                        #         else:
                        #             true_question_action_status = QuestionActionStatus.objects.create(question_action_status=true_status, question_action_select_status=true_status_code)
                        #             true_question_action_status_id = true_question_action_status
                        # else:
                        #     true_question_action_status_id = None

                        # print("true_question_action_status_id")
                        # print(true_question_action_status_id)

                        for q in question_obj:
                            # if q.question_true_action.question_action is not None:
                            true_question_action_pk = q.question_true_action.question_action.id
                            # if true_question_action_log_id_updated is not None and true_question_action_block_id_updated is not None and true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_record=true_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)
                                # print("true_question_action:")
                                # print(true_question_action)

                            if true_question_action_log_id_updated is not None and true_question_action_block_id_updated is not None:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(question_action_record=true_record,
                                                                  question_action_status=true_question_action_status_id1,question_action_take_photo=true_take_photo, question_action_signature=false_take_signature,
                                                                  question_action_no_action=true_no_action)
                            # elif true_question_action_log_id_updated is not None and true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_block=true_question_action_block_id, question_action_record=true_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)
                            elif true_question_action_log_id_updated is not None:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(question_action_block=true_question_action_block_id, question_action_record=true_record,
                                                                  question_action_status=true_question_action_status_id1,
                                                                  question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                                                                  question_action_no_action=true_no_action)
                            # elif true_question_action_block_id_updated is not None and true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_record=true_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)

                            elif true_question_action_block_id_updated is not None:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_record=true_record,
                                                                  question_action_status=true_question_action_status_id1,
                                                                  question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                                                                  question_action_no_action=true_no_action)
                            # elif true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_block=true_question_action_block_id, question_action_record=false_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)
                            else:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(
                                    question_action_log=true_question_action_log_id,
                                    question_action_block=true_question_action_block_id,
                                    question_action_record=true_record,
                                    question_action_status=true_question_action_status_id1,
                                    question_action_take_photo=true_take_photo,
                                    question_action_signature=true_take_signature,
                                    question_action_no_action=true_no_action)

                        # for q in question_obj:
                        #     # if q.question_true_action is not None:
                        #     question_true_action_pk = q.question_true_action.id
                        #     print("true must needed")
                        #     print(true_question_action_pk)
                        #     question_true_action_obj = QuestionTrueAction.objects.filter(pk=question_true_action_pk)
                        #     true_action = question_true_action_obj.update(question_action=true_question_action)
                        #     print("true_action")
                        #     print(true_action)

                        print("this is customer %s" % customer_code)
                        if customer_code is not None:
                            customer_list = customer_code.split(',')
                            for cust in customer_list:
                                cust1 = cust
                                print(customer_list)
                                question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                                                        question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                        question_text=question_text, updated_at=datetime.datetime.now())

                        else:
                            cust1 = ''
                            # print(customer_list)
                            question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                                                               question_sequence=sequence, question_section=sec1, question_type=typ1,
                                                           question_text=question_text, updated_at=datetime.datetime.now())

                        print("question")
                        print(question_obj)
                        return Response({"status":status.HTTP_200_OK, "Msg": "Question has been updated successfully."})

                    else:
                        return Response(
                            {"status": status.HTTP_404_NOT_FOUND, "Msg": "Question doesn't exist."})

                # elif request.user.is_active and request.user.is_organisation_admin:
                #     question_obj = Question.objects.filter(pk=question_id)
                #     print(question_obj)
                #
                #     false_question_action_log_id_updated = None
                #     false_question_action_block_id_updated = None
                #
                #     true_question_action_log_id_updated = None
                #     true_question_action_block_id_updated = None
                #
                #
                #     if question_obj:
                #         if false_log is True:
                #             if false_log_type_id is not None:
                #                 false_log_types = QuestionActionLogType.objects.filter(type_id=false_log_type_id)
                #                 for flt in false_log_types:
                #                     flt1 = flt
                #             else:
                #                 flt1 = None
                #             print("asddddddddddddddddddddddddddddddddddddddd1")
                #             print(flt1)
                #
                #             for q in question_obj:
                #                 if q.question_false_action.question_action.question_action_log is not None:
                #                     print("question_action_log:")
                #                     print(question_obj)
                #                     print(q.question_false_action.question_action)
                #                     print(q.question_false_action.question_action.question_action_log)
                #                     print(q.question_false_action.question_action.question_action_log.id)
                #                     false_question_action_log_pk = q.question_false_action.question_action.question_action_log.id
                #                     false_question_action_log_obj = QuestionActionLog.objects.filter(pk=false_question_action_log_pk)
                #
                #                     false_question_action_log = false_question_action_log_obj.update(question_action_log=false_log,
                #                                                                      question_action_log_type=flt1,
                #                                                                      question_action_log_text=false_log_text,
                #                                                                      question_action_log_driver_name=false_log_driver_name,
                #                                                                      question_action_log_driver_gps=false_log_GPS,
                #                                                                      question_action_log_no_of_packages=false_log_no_packages,
                #                                                                      question_action_log_customer_name=false_log_customer_name,
                #                                                                      question_action_log_date_time= false_log_dateTime)
                #                     false_question_action_log_id_updated = false_question_action_log
                #                 else:
                #                     false_question_action_log = QuestionActionLog.objects.create(
                #                         question_action_log=false_log,
                #                         question_action_log_type=flt1,
                #                         question_action_log_text=false_log_text,
                #                         question_action_log_driver_name=false_log_driver_name,
                #                         question_action_log_driver_gps=false_log_GPS,
                #                         question_action_log_no_of_packages=false_log_no_packages,
                #                         question_action_log_customer_name=false_log_customer_name,
                #                         question_action_log_date_time=false_log_dateTime)
                #                     false_question_action_log_id = false_question_action_log
                #         else:
                #             false_question_action_log_id = None
                #         # print("false_question_action_log_id:")
                #         # print(false_question_action_log_id)
                #
                #         if false_block is True:
                #             for q in question_obj:
                #                 if q.question_false_action.question_action.question_action_block is not None:
                #                     false_question_action_block_pk = q.question_false_action.question_action.question_action_block.id
                #                     false_question_action_block_obj = QuestionActionBlock.objects.filter(pk=false_question_action_block_pk)
                #                     false_question_action_block = false_question_action_block_obj.update(question_action_block=false_block, question_action_block_text=false_block_text)
                #                     false_question_action_block_id_updated = false_question_action_block
                #                 else:
                #                     false_question_action_block = QuestionActionBlock.objects.create(question_action_block=false_block, question_action_block_text=false_block_text)
                #                     false_question_action_block_id = false_question_action_block
                #         else:
                #             false_question_action_block_id = None
                #         # print("false_question_action_block_id:")
                #         # print(false_question_action_block_id)
                #
                #         if false_status is True:
                #             if false_run_status is True:
                #                 false_question_action_statuses = QuestionActionStatus.objects.filter(
                #                     run_status_id=false_status_id)
                #                 for false_question_action_status_id in false_question_action_statuses:
                #                     false_question_action_status_id1 = false_question_action_status_id
                #             elif false_drop_status is True:
                #                 false_question_action_statuses = QuestionActionStatus.objects.filter(
                #                     drop_status_id=false_status_id)
                #                 for false_question_action_status_id in false_question_action_statuses:
                #                     false_question_action_status_id1 = false_question_action_status_id
                #             else:
                #                 false_question_action_status_id1 = None
                #         else:
                #             false_question_action_status_id1 = None
                #
                #         # if false_status is True:
                #         #     for q in question_obj:
                #         #         if q.question_false_action.question_action.question_action_status is not None:
                #         #             false_question_action_status_pk = q.question_false_action.question_action.question_action_status.id
                #         #             false_question_action_status_obj = QuestionActionStatus.objects.filter(pk=false_question_action_status_pk)
                #         #             false_question_action_status = false_question_action_status_obj.update(question_action_status=false_status, question_action_select_status=false_status_code)
                #         #             false_question_action_status_id_updated = false_question_action_status
                #         #         else:
                #         #             false_question_action_status = QuestionActionStatus.objects.create(question_action_status=false_status, question_action_select_status=false_status_code)
                #         #             false_question_action_status_id = false_question_action_status
                #         # else:
                #         #     false_question_action_status_id = None
                #         # print("false_question_action_status_id:")
                #         # print(false_question_action_status_id)
                #
                #         for q in question_obj:
                #             # if q.question_false_action.question_action is not None:
                #             false_question_action_pk = q.question_false_action.question_action.id
                #
                #             print("false must needed")
                #             print(false_question_action_pk)
                #             if false_question_action_log_id_updated is not None and false_question_action_block_id_updated is not None:
                #                 false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #                 print("false_question_action_obj")
                #                 print(false_question_action_obj)
                #                 false_question_action_obj.update(question_action_record=false_record, question_action_status=false_question_action_status_id1,
                #                                                   question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                #                                                   question_action_no_action=false_no_action)
                #                 # print("false_question_action:")
                #                 # print(false_question_action)
                #
                #             # elif false_question_action_log_id_updated is not None and false_question_action_block_id_updated is not None:
                #             #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #             #     print("false_question_action_obj")
                #             #     print(false_question_action_obj)
                #             #     false_question_action_obj.update(question_action_record=false_record,
                #             #                                       question_action_status=false_question_action_status_id,question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                #             #                                       question_action_no_action=false_no_action)
                #             # elif false_question_action_log_id_updated is not None and false_question_action_status_id_updated is not None:
                #             #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #             #     print("false_question_action_obj")
                #             #     print(false_question_action_obj)
                #             #     false_question_action_obj.update(question_action_block=false_question_action_block_id, question_action_record=false_record,
                #             #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                #             #                                       question_action_no_action=false_no_action)
                #             elif false_question_action_log_id_updated is not None:
                #                 false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #                 print("false_question_action_obj")
                #                 print(false_question_action_obj)
                #                 false_question_action_obj.update(question_action_block=false_question_action_block_id, question_action_record=false_record,
                #                                                  question_action_status=false_question_action_status_id1,
                #                                                   question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                #                                                   question_action_no_action=false_no_action)
                #             # elif false_question_action_block_id_updated is not None and false_question_action_status_id_updated is not None:
                #             #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #             #     print("false_question_action_obj")
                #             #     print(false_question_action_obj)
                #             #     false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_record=false_record,
                #             #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                #             #                                       question_action_no_action=false_no_action)
                #
                #             elif false_question_action_block_id_updated is not None:
                #                 false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #                 print("false_question_action_obj")
                #                 print(false_question_action_obj)
                #                 false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_record=false_record,
                #                                                  question_action_status=false_question_action_status_id1,
                #                                                   question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                #                                                   question_action_no_action=false_no_action)
                #             # elif false_question_action_status_id_updated is not None:
                #             #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #             #     print("false_question_action_obj")
                #             #     print(false_question_action_obj)
                #             #     false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_block=false_question_action_block_id, question_action_record=false_record,
                #             #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                #             #                                       question_action_no_action=false_no_action)
                #             else:
                #                 false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                #                 print("false_question_action_obj")
                #                 print(false_question_action_obj)
                #                 false_question_action_obj.update(
                #                     question_action_log=false_question_action_log_id,
                #                     question_action_block=false_question_action_block_id,
                #                     question_action_record=false_record,
                #                     question_action_status=false_question_action_status_id1,
                #                     question_action_take_photo=false_take_photo,
                #                     question_action_signature=false_take_signature,
                #                     question_action_no_action=false_no_action)
                #
                #         # for q in question_obj:
                #         #     if q.question_false_action is not None:
                #         #         question_false_action_pk = q.question_false_action.id
                #         #         print("question_false_action_pk")
                #         #         print(question_false_action_pk)
                #         #         question_false_action_obj = QuestionFalseAction.objects.filter(pk=question_false_action_pk)
                #         #         false_action = question_false_action_obj.update(question_action=false_question_action)
                #         #         print("false_action")
                #
                #         if true_log is True:
                #             if true_log_type_id is not None:
                #                 true_log_types = QuestionActionLogType.objects.filter(type_id=true_log_type_id)
                #                 for tlt in true_log_types:
                #                     tlt1 = tlt
                #             else:
                #                 tlt1 = None
                #             print("Why why why")
                #             print(tlt1)
                #
                #             for q in question_obj:
                #                 if q.question_true_action.question_action.question_action_log is not None:
                #                     true_question_action_log_pk = q.question_true_action.question_action.question_action_log.id
                #                     true_question_action_log_obj = QuestionActionLog.objects.filter(pk=true_question_action_log_pk)
                #
                #                     true_question_action_log = true_question_action_log_obj.update(question_action_log=true_log,
                #                                                                      question_action_log_type=tlt1,
                #                                                                      question_action_log_text=true_log_text,
                #                                                                      question_action_log_driver_name=true_log_driver_name,
                #                                                                      question_action_log_driver_gps=true_log_GPS,
                #                                                                      question_action_log_no_of_packages=true_log_no_packages,
                #                                                                      question_action_log_customer_name=true_log_customer_name,
                #                                                                      question_action_log_date_time=true_log_dateTime)
                #                     true_question_action_log_id_updated = true_question_action_log
                #                 else:
                #                     true_question_action_log = QuestionActionLog.objects.create(
                #                         question_action_log=true_log,
                #                         question_action_log_type=tlt1,
                #                         question_action_log_text=true_log_text,
                #                         question_action_log_driver_name=true_log_driver_name,
                #                         question_action_log_driver_gps=true_log_GPS,
                #                         question_action_log_no_of_packages=true_log_no_packages,
                #                         question_action_log_customer_name=true_log_customer_name,
                #                         question_action_log_date_time=true_log_dateTime)
                #                     true_question_action_log_id = true_question_action_log
                #         else:
                #             true_question_action_log_id = None
                #         # print("true_question_action_log_id")
                #         # print(true_question_action_log_id)
                #
                #         if true_block is True:
                #             for q in question_obj:
                #                 if q.question_true_action.question_action.question_action_block is not None:
                #                     true_question_action_block_pk = q.question_true_action.question_action.question_action_block.id
                #                     true_question_action_block_obj = QuestionActionBlock.objects.filter(pk=true_question_action_block_pk)
                #                     true_question_action_block = true_question_action_block_obj.update(question_action_block=true_block,
                #                                                                          question_action_block_text=true_block_text)
                #                     true_question_action_block_id_updated = true_question_action_block
                #                 else:
                #                     true_question_action_block = QuestionActionBlock.objects.create(question_action_block=true_block, question_action_block_text=true_block_text)
                #                     true_question_action_block_id = true_question_action_block
                #         else:
                #             true_question_action_block_id = None
                #
                #         # print("true_question_action_block_id")
                #         # print(true_question_action_block_id)
                #
                #         if true_status is True:
                #             if true_run_status is True:
                #                 true_question_action_statuses = QuestionActionStatus.objects.filter(
                #                     run_status_id=true_status_id)
                #                 for true_question_action_status_id in true_question_action_statuses:
                #                     true_question_action_status_id1 = true_question_action_status_id
                #             elif true_drop_status is True:
                #                 true_question_action_statuses = QuestionActionStatus.objects.filter(
                #                     drop_status_id=true_status_id)
                #                 for true_question_action_status_id in true_question_action_statuses:
                #                     true_question_action_status_id1 = true_question_action_status_id
                #             else:
                #                 true_question_action_status_id1 = None
                #         else:
                #             true_question_action_status_id1 = None
                #
                #         # if true_status is True:
                #         #     for q in question_obj:
                #         #         if q.question_true_action.question_action.question_action_status is not None:
                #         #             true_question_action_status_pk = q.question_true_action.question_action.question_action_status.id
                #         #             true_question_action_status_obj = QuestionActionStatus.objects.filter(pk=true_question_action_status_pk)
                #         #             true_question_action_status = true_question_action_status_obj.update(question_action_status=true_status,
                #         #                                                                    question_action_select_status=true_status_code)
                #         #             true_question_action_status_id_updated = true_question_action_status
                #         #         else:
                #         #             true_question_action_status = QuestionActionStatus.objects.create(question_action_status=true_status, question_action_select_status=true_status_code)
                #         #             true_question_action_status_id = true_question_action_status
                #         # else:
                #         #     true_question_action_status_id = None
                #
                #         # print("true_question_action_status_id")
                #         # print(true_question_action_status_id)
                #
                #         for q in question_obj:
                #             # if q.question_true_action.question_action is not None:
                #             true_question_action_pk = q.question_true_action.question_action.id
                #             # if true_question_action_log_id_updated is not None and true_question_action_block_id_updated is not None and true_question_action_status_id_updated is not None:
                #             #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #             #     print("true_question_action_obj")
                #             #     print(true_question_action_obj)
                #             #     true_question_action_obj.update(question_action_record=true_record,
                #             #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                #             #                                       question_action_no_action=true_no_action)
                #                 # print("true_question_action:")
                #                 # print(true_question_action)
                #
                #             if true_question_action_log_id_updated is not None and true_question_action_block_id_updated is not None:
                #                 true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #                 print("true_question_action_obj")
                #                 print(true_question_action_obj)
                #                 true_question_action_obj.update(question_action_record=true_record,
                #                                                   question_action_status=true_question_action_status_id1,question_action_take_photo=true_take_photo, question_action_signature=false_take_signature,
                #                                                   question_action_no_action=true_no_action)
                #             # elif true_question_action_log_id_updated is not None and true_question_action_status_id_updated is not None:
                #             #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #             #     print("true_question_action_obj")
                #             #     print(true_question_action_obj)
                #             #     true_question_action_obj.update(question_action_block=true_question_action_block_id, question_action_record=true_record,
                #             #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                #             #                                       question_action_no_action=true_no_action)
                #             elif true_question_action_log_id_updated is not None:
                #                 true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #                 print("true_question_action_obj")
                #                 print(true_question_action_obj)
                #                 true_question_action_obj.update(question_action_block=true_question_action_block_id, question_action_record=true_record,
                #                                                   question_action_status=true_question_action_status_id1,
                #                                                   question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                #                                                   question_action_no_action=true_no_action)
                #             # elif true_question_action_block_id_updated is not None and true_question_action_status_id_updated is not None:
                #             #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #             #     print("true_question_action_obj")
                #             #     print(true_question_action_obj)
                #             #     true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_record=true_record,
                #             #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                #             #                                       question_action_no_action=true_no_action)
                #
                #             elif true_question_action_block_id_updated is not None:
                #                 true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #                 print("true_question_action_obj")
                #                 print(true_question_action_obj)
                #                 true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_record=true_record,
                #                                                   question_action_status=true_question_action_status_id1,
                #                                                   question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                #                                                   question_action_no_action=true_no_action)
                #             # elif true_question_action_status_id_updated is not None:
                #             #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #             #     print("true_question_action_obj")
                #             #     print(true_question_action_obj)
                #             #     true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_block=true_question_action_block_id, question_action_record=false_record,
                #             #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                #             #                                       question_action_no_action=true_no_action)
                #             else:
                #                 true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                #                 print("true_question_action_obj")
                #                 print(true_question_action_obj)
                #                 true_question_action_obj.update(
                #                     question_action_log=true_question_action_log_id,
                #                     question_action_block=true_question_action_block_id,
                #                     question_action_record=true_record,
                #                     question_action_status=true_question_action_status_id1,
                #                     question_action_take_photo=true_take_photo,
                #                     question_action_signature=true_take_signature,
                #                     question_action_no_action=true_no_action)
                #
                #         # for q in question_obj:
                #         #     # if q.question_true_action is not None:
                #         #     question_true_action_pk = q.question_true_action.id
                #         #     print("true must needed")
                #         #     print(true_question_action_pk)
                #         #     question_true_action_obj = QuestionTrueAction.objects.filter(pk=question_true_action_pk)
                #         #     true_action = question_true_action_obj.update(question_action=true_question_action)
                #         #     print("true_action")
                #         #     print(true_action)
                #
                #         print("this is customer %s" % customer_code)
                #         if customer_code is not None:
                #             customer_list = customer_code.split(',')
                #             for cust in customer_list:
                #                 cust1 = cust
                #                 print(customer_list)
                #                 question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                #                                         question_sequence=sequence, question_section=sec1, question_type=typ1,
                #                                         question_text=question_text)
                #
                #         else:
                #             cust1 = ''
                #             # print(customer_list)
                #             question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                #                                                question_sequence=sequence, question_section=sec1, question_type=typ1,
                #                                            question_text=question_text)
                #
                #         print("question")
                #         print(question_obj)
                #         return Response({"status":status.HTTP_200_OK, "Msg": "Question has been updated successfully."})

                elif request.user.is_active and request.user.is_branch_admin:
                    question_obj = Question.objects.filter(pk=question_id)
                    print(question_obj)

                    false_question_action_log_id_updated = None
                    false_question_action_block_id_updated = None

                    true_question_action_log_id_updated = None
                    true_question_action_block_id_updated = None

                    if question_obj:
                        if false_log is True:
                            if false_log_type_id is not None:
                                false_log_types = QuestionActionLogType.objects.filter(type_id=false_log_type_id)
                                for flt in false_log_types:
                                    flt1 = flt
                            else:
                                flt1 = None
                            print("asddddddddddddddddddddddddddddddddddddddd1")
                            print(flt1)

                            for q in question_obj:
                                if q.question_false_action.question_action.question_action_log is not None:
                                    print("question_action_log:")
                                    print(question_obj)
                                    print(q.question_false_action.question_action)
                                    print(q.question_false_action.question_action.question_action_log)
                                    print(q.question_false_action.question_action.question_action_log.id)
                                    false_question_action_log_pk = q.question_false_action.question_action.question_action_log.id
                                    false_question_action_log_obj = QuestionActionLog.objects.filter(
                                        pk=false_question_action_log_pk)

                                    false_question_action_log = false_question_action_log_obj.update(
                                        question_action_log=false_log,
                                        question_action_log_type=flt1,
                                        question_action_log_text=false_log_text,
                                        question_action_log_driver_name=false_log_driver_name,
                                        question_action_log_driver_gps=false_log_GPS,
                                        question_action_log_no_of_packages=false_log_no_packages,
                                        question_action_log_customer_name=false_log_customer_name,
                                        question_action_log_date_time=false_log_dateTime)
                                    false_question_action_log_id_updated = false_question_action_log
                                else:
                                    false_question_action_log = QuestionActionLog.objects.create(
                                        question_action_log=false_log,
                                        question_action_log_type=flt1,
                                        question_action_log_text=false_log_text,
                                        question_action_log_driver_name=false_log_driver_name,
                                        question_action_log_driver_gps=false_log_GPS,
                                        question_action_log_no_of_packages=false_log_no_packages,
                                        question_action_log_customer_name=false_log_customer_name,
                                        question_action_log_date_time=false_log_dateTime)
                                    false_question_action_log_id = false_question_action_log
                        else:
                            false_question_action_log_id = None
                        # print("false_question_action_log_id:")
                        # print(false_question_action_log_id)

                        if false_block is True:
                            for q in question_obj:
                                if q.question_false_action.question_action.question_action_block is not None:
                                    false_question_action_block_pk = q.question_false_action.question_action.question_action_block.id
                                    false_question_action_block_obj = QuestionActionBlock.objects.filter(
                                        pk=false_question_action_block_pk)
                                    false_question_action_block = false_question_action_block_obj.update(
                                        question_action_block=false_block,
                                        question_action_block_text=false_block_text)
                                    false_question_action_block_id_updated = false_question_action_block
                                else:
                                    false_question_action_block = QuestionActionBlock.objects.create(
                                        question_action_block=false_block,
                                        question_action_block_text=false_block_text)
                                    false_question_action_block_id = false_question_action_block
                        else:
                            false_question_action_block_id = None
                        # print("false_question_action_block_id:")
                        # print(false_question_action_block_id)

                        if false_status is True:
                            if false_run_status is True:
                                false_question_action_statuses = QuestionActionStatus.objects.filter(
                                    run_status_id=false_status_id)
                                for false_question_action_status_id in false_question_action_statuses:
                                    false_question_action_status_id1 = false_question_action_status_id
                            elif false_drop_status is True:
                                false_question_action_statuses = QuestionActionStatus.objects.filter(
                                    drop_status_id=false_status_id)
                                for false_question_action_status_id in false_question_action_statuses:
                                    false_question_action_status_id1 = false_question_action_status_id
                            else:
                                false_question_action_status_id1 = None
                        else:
                            false_question_action_status_id1 = None

                        # if false_status is True:
                        #     for q in question_obj:
                        #         if q.question_false_action.question_action.question_action_status is not None:
                        #             false_question_action_status_pk = q.question_false_action.question_action.question_action_status.id
                        #             false_question_action_status_obj = QuestionActionStatus.objects.filter(pk=false_question_action_status_pk)
                        #             false_question_action_status = false_question_action_status_obj.update(question_action_status=false_status, question_action_select_status=false_status_code)
                        #             false_question_action_status_id_updated = false_question_action_status
                        #         else:
                        #             false_question_action_status = QuestionActionStatus.objects.create(question_action_status=false_status, question_action_select_status=false_status_code)
                        #             false_question_action_status_id = false_question_action_status
                        # else:
                        #     false_question_action_status_id = None
                        # print("false_question_action_status_id:")
                        # print(false_question_action_status_id)

                        for q in question_obj:
                            # if q.question_false_action.question_action is not None:
                            false_question_action_pk = q.question_false_action.question_action.id

                            print("false must needed")
                            print(false_question_action_pk)
                            if false_question_action_log_id_updated is not None and false_question_action_block_id_updated is not None:
                                false_question_action_obj = QuestionAction.objects.filter(
                                    pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(question_action_record=false_record,
                                                                 question_action_status=false_question_action_status_id1,
                                                                 question_action_take_photo=false_take_photo,
                                                                 question_action_signature=false_take_signature,
                                                                 question_action_no_action=false_no_action)
                                # print("false_question_action:")
                                # print(false_question_action)

                            # elif false_question_action_log_id_updated is not None and false_question_action_block_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_record=false_record,
                            #                                       question_action_status=false_question_action_status_id,question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)
                            # elif false_question_action_log_id_updated is not None and false_question_action_status_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_block=false_question_action_block_id, question_action_record=false_record,
                            #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)
                            elif false_question_action_log_id_updated is not None:
                                false_question_action_obj = QuestionAction.objects.filter(
                                    pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(
                                    question_action_block=false_question_action_block_id,
                                    question_action_record=false_record,
                                    question_action_status=false_question_action_status_id1,
                                    question_action_take_photo=false_take_photo,
                                    question_action_signature=false_take_signature,
                                    question_action_no_action=false_no_action)
                            # elif false_question_action_block_id_updated is not None and false_question_action_status_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_record=false_record,
                            #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)

                            elif false_question_action_block_id_updated is not None:
                                false_question_action_obj = QuestionAction.objects.filter(
                                    pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(question_action_log=false_question_action_log_id,
                                                                 question_action_record=false_record,
                                                                 question_action_status=false_question_action_status_id1,
                                                                 question_action_take_photo=false_take_photo,
                                                                 question_action_signature=false_take_signature,
                                                                 question_action_no_action=false_no_action)
                            # elif false_question_action_status_id_updated is not None:
                            #     false_question_action_obj = QuestionAction.objects.filter(pk=false_question_action_pk)
                            #     print("false_question_action_obj")
                            #     print(false_question_action_obj)
                            #     false_question_action_obj.update(question_action_log=false_question_action_log_id, question_action_block=false_question_action_block_id, question_action_record=false_record,
                            #                                       question_action_take_photo=false_take_photo, question_action_signature=false_take_signature,
                            #                                       question_action_no_action=false_no_action)
                            else:
                                false_question_action_obj = QuestionAction.objects.filter(
                                    pk=false_question_action_pk)
                                print("false_question_action_obj")
                                print(false_question_action_obj)
                                false_question_action_obj.update(
                                    question_action_log=false_question_action_log_id,
                                    question_action_block=false_question_action_block_id,
                                    question_action_record=false_record,
                                    question_action_status=false_question_action_status_id1,
                                    question_action_take_photo=false_take_photo,
                                    question_action_signature=false_take_signature,
                                    question_action_no_action=false_no_action)

                        # for q in question_obj:
                        #     if q.question_false_action is not None:
                        #         question_false_action_pk = q.question_false_action.id
                        #         print("question_false_action_pk")
                        #         print(question_false_action_pk)
                        #         question_false_action_obj = QuestionFalseAction.objects.filter(pk=question_false_action_pk)
                        #         false_action = question_false_action_obj.update(question_action=false_question_action)
                        #         print("false_action")

                        if true_log is True:
                            if true_log_type_id is not None:
                                true_log_types = QuestionActionLogType.objects.filter(type_id=true_log_type_id)
                                for tlt in true_log_types:
                                    tlt1 = tlt
                            else:
                                tlt1 = None
                            print("Why why why")
                            print(tlt1)

                            for q in question_obj:
                                if q.question_true_action.question_action.question_action_log is not None:
                                    true_question_action_log_pk = q.question_true_action.question_action.question_action_log.id
                                    true_question_action_log_obj = QuestionActionLog.objects.filter(
                                        pk=true_question_action_log_pk)

                                    true_question_action_log = true_question_action_log_obj.update(
                                        question_action_log=true_log,
                                        question_action_log_type=tlt1,
                                        question_action_log_text=true_log_text,
                                        question_action_log_driver_name=true_log_driver_name,
                                        question_action_log_driver_gps=true_log_GPS,
                                        question_action_log_no_of_packages=true_log_no_packages,
                                        question_action_log_customer_name=true_log_customer_name,
                                        question_action_log_date_time=true_log_dateTime)
                                    true_question_action_log_id_updated = true_question_action_log
                                else:
                                    true_question_action_log = QuestionActionLog.objects.create(
                                        question_action_log=true_log,
                                        question_action_log_type=tlt1,
                                        question_action_log_text=true_log_text,
                                        question_action_log_driver_name=true_log_driver_name,
                                        question_action_log_driver_gps=true_log_GPS,
                                        question_action_log_no_of_packages=true_log_no_packages,
                                        question_action_log_customer_name=true_log_customer_name,
                                        question_action_log_date_time=true_log_dateTime)
                                    true_question_action_log_id = true_question_action_log
                        else:
                            true_question_action_log_id = None
                        # print("true_question_action_log_id")
                        # print(true_question_action_log_id)

                        if true_block is True:
                            for q in question_obj:
                                if q.question_true_action.question_action.question_action_block is not None:
                                    true_question_action_block_pk = q.question_true_action.question_action.question_action_block.id
                                    true_question_action_block_obj = QuestionActionBlock.objects.filter(
                                        pk=true_question_action_block_pk)
                                    true_question_action_block = true_question_action_block_obj.update(
                                        question_action_block=true_block,
                                        question_action_block_text=true_block_text)
                                    true_question_action_block_id_updated = true_question_action_block
                                else:
                                    true_question_action_block = QuestionActionBlock.objects.create(
                                        question_action_block=true_block,
                                        question_action_block_text=true_block_text)
                                    true_question_action_block_id = true_question_action_block
                        else:
                            true_question_action_block_id = None

                        # print("true_question_action_block_id")
                        # print(true_question_action_block_id)

                        if true_status is True:
                            if true_run_status is True:
                                true_question_action_statuses = QuestionActionStatus.objects.filter(
                                    run_status_id=true_status_id)
                                for true_question_action_status_id in true_question_action_statuses:
                                    true_question_action_status_id1 = true_question_action_status_id
                            elif true_drop_status is True:
                                true_question_action_statuses = QuestionActionStatus.objects.filter(
                                    drop_status_id=true_status_id)
                                for true_question_action_status_id in true_question_action_statuses:
                                    true_question_action_status_id1 = true_question_action_status_id
                            else:
                                true_question_action_status_id1 = None
                        else:
                            true_question_action_status_id1 = None

                        # if true_status is True:
                        #     for q in question_obj:
                        #         if q.question_true_action.question_action.question_action_status is not None:
                        #             true_question_action_status_pk = q.question_true_action.question_action.question_action_status.id
                        #             true_question_action_status_obj = QuestionActionStatus.objects.filter(pk=true_question_action_status_pk)
                        #             true_question_action_status = true_question_action_status_obj.update(question_action_status=true_status,
                        #                                                                    question_action_select_status=true_status_code)
                        #             true_question_action_status_id_updated = true_question_action_status
                        #         else:
                        #             true_question_action_status = QuestionActionStatus.objects.create(question_action_status=true_status, question_action_select_status=true_status_code)
                        #             true_question_action_status_id = true_question_action_status
                        # else:
                        #     true_question_action_status_id = None

                        # print("true_question_action_status_id")
                        # print(true_question_action_status_id)

                        for q in question_obj:
                            # if q.question_true_action.question_action is not None:
                            true_question_action_pk = q.question_true_action.question_action.id
                            # if true_question_action_log_id_updated is not None and true_question_action_block_id_updated is not None and true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_record=true_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)
                            # print("true_question_action:")
                            # print(true_question_action)

                            if true_question_action_log_id_updated is not None and true_question_action_block_id_updated is not None:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(question_action_record=true_record,
                                                                question_action_status=true_question_action_status_id1,
                                                                question_action_take_photo=true_take_photo,
                                                                question_action_signature=false_take_signature,
                                                                question_action_no_action=true_no_action)
                            # elif true_question_action_log_id_updated is not None and true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_block=true_question_action_block_id, question_action_record=true_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)
                            elif true_question_action_log_id_updated is not None:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(question_action_block=true_question_action_block_id,
                                                                question_action_record=true_record,
                                                                question_action_status=true_question_action_status_id1,
                                                                question_action_take_photo=true_take_photo,
                                                                question_action_signature=true_take_signature,
                                                                question_action_no_action=true_no_action)
                            # elif true_question_action_block_id_updated is not None and true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_record=true_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)

                            elif true_question_action_block_id_updated is not None:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(question_action_log=true_question_action_log_id,
                                                                question_action_record=true_record,
                                                                question_action_status=true_question_action_status_id1,
                                                                question_action_take_photo=true_take_photo,
                                                                question_action_signature=true_take_signature,
                                                                question_action_no_action=true_no_action)
                            # elif true_question_action_status_id_updated is not None:
                            #     true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                            #     print("true_question_action_obj")
                            #     print(true_question_action_obj)
                            #     true_question_action_obj.update(question_action_log=true_question_action_log_id, question_action_block=true_question_action_block_id, question_action_record=false_record,
                            #                                       question_action_take_photo=true_take_photo, question_action_signature=true_take_signature,
                            #                                       question_action_no_action=true_no_action)
                            else:
                                true_question_action_obj = QuestionAction.objects.filter(pk=true_question_action_pk)
                                print("true_question_action_obj")
                                print(true_question_action_obj)
                                true_question_action_obj.update(
                                    question_action_log=true_question_action_log_id,
                                    question_action_block=true_question_action_block_id,
                                    question_action_record=true_record,
                                    question_action_status=true_question_action_status_id1,
                                    question_action_take_photo=true_take_photo,
                                    question_action_signature=true_take_signature,
                                    question_action_no_action=true_no_action)

                        # for q in question_obj:
                        #     # if q.question_true_action is not None:
                        #     question_true_action_pk = q.question_true_action.id
                        #     print("true must needed")
                        #     print(true_question_action_pk)
                        #     question_true_action_obj = QuestionTrueAction.objects.filter(pk=question_true_action_pk)
                        #     true_action = question_true_action_obj.update(question_action=true_question_action)
                        #     print("true_action")
                        #     print(true_action)

                        if branch_id is not None:
                            branches = Branch.objects.filter(pk=branch_id)
                            for branch in branches:
                                branch1 = branch
                                print(branch1)
                                org1 = branch.organisation
                                print("this is customer %s" % customer_code)
                                if customer_code is not None:
                                    customer_list = customer_code.split(',')
                                    for cust in customer_list:
                                        cust1 = cust
                                        print(customer_list)
                                        question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                                                            question_sequence=sequence, question_section=sec1,
                                                            question_type=typ1,
                                                            question_text=question_text)

                                else:
                                    cust1 = ''
                                    # print(customer_list)
                                    question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                                                        question_sequence=sequence, question_section=sec1,
                                                        question_type=typ1,
                                                        question_text=question_text)
                        else:
                            branchadmins = BranchAdmins.objects.filter(user=user_id)
                            for branc in branchadmins:
                                if branc.branch.branch_is_active is True:
                                    branch1 = branc.branch
                                    org1 = branc.branch.organisation
                                    print(org1)
                                    print("this is customer %s" % customer_code)
                                    if customer_code is not None:
                                        customer_list = customer_code.split(',')
                                        for cust in customer_list:
                                            cust1 = cust
                                            print(customer_list)
                                            question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                                                                question_sequence=sequence, question_section=sec1,
                                                                question_type=typ1,
                                                                question_text=question_text)

                                    else:
                                        cust1 = ''
                                        # print(customer_list)
                                        question_obj.update(organisation=org1, branch=branch1, customer_code=cust1,
                                                            question_sequence=sequence, question_section=sec1,
                                                            question_type=typ1,
                                                            question_text=question_text)

                        print("question")
                        print(question_obj)
                        return Response(
                            {"status": status.HTTP_200_OK, "Msg": "Question has been updated successfully."})

                    else:
                        return Response(
                            {"status": status.HTTP_404_NOT_FOUND, "Msg": "Question doesn't exist."})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "not super"})
            except:
                logger.debug("Error while updating question")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Update Question"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

class QuestionAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    # pagination_class = PostPageNumberPagination  # PageNumberPagination

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)
        page_size = request.GET.get('page_size')
        print(page_size)

        org_id = request.GET.get('org_id')
        org_id = None if org_id == '0' else org_id
        branch_id = request.GET.get('branch_id')
        # print(type(branch_id))
        branch_id = None if branch_id == '0' else branch_id
        customer_code = request.GET.get('customer_code')
        customer_code = None if customer_code == '' else customer_code

        if user:
            try:
                # print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    org_param = Q(organisation=org_id)
                    branch_param = Q(branch=branch_id)
                    # customer_param = Q(customer_code=customer_code)
                    if customer_code is not None:
                        customer_list = customer_code.split(',')
                        customer_param = Q(customer_code__in=customer_list)
                    else:
                        customer_param = Q(customer_code='')

                    questions = Question.objects.order_by("question_sequence").filter(org_param & branch_param & customer_param)
                    # branches = Question.objects.order_by("question_sequence").filter(branch=branch_id)
                    # customer_codes = Question.objects.order_by("question_sequence").filter(customer_code=customer_code)
                    # print(questions)
                    total_questions = questions.count()
                    print(total_questions)
                    quest = Paginator(questions, 20)
                    if page_size:
                        quest = Paginator(questions, page_size)
                    page = request.GET.get('page')
                    # ques = quest.page(page)
                    print(page)


                    try:
                        ques = quest.page(page)
                    except PageNotAnInteger:
                        ques = quest.page(1)
                    except EmptyPage:
                        ques = quest.page(quest.num_pages)

                    has_next = ques.has_next()
                    if has_next is True:
                        next_page_number = ques.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques.has_previous()
                    if has_previous is True:
                        previous_page_number = ques.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)


                    # print(ques.has_other_pages())
                    # print(ques.start_index())
                    # print(ques.end_index())

                    # serializer = QuestionSerializer(ques, many=True)
                    # print(serializer.data)
                    # # return Response(serializer.data)
                    view_questions = []
                    for q in ques:
                        # print(question)
                        q_id = q.id
                        sequence = q.question_sequence
                        type = q.question_type.question_type
                        text1 = q.question_text
                        if text1 is not None:
                            text = text1
                        else:
                            text = ""

                        section_id = q.question_section.section_id
                        section = q.question_section.section_name

                        org_fk = q.organisation
                        if org_fk is not None:
                            organisation = org_fk.organisation_name
                        else:
                            organisation = "all"

                        branch_fk = q.branch
                        if branch_fk is not None:
                            branch = branch_fk.branch_name
                        else:
                            branch = "all"

                        # customer_fk = q.customer_code
                        # if customer_fk is not None:
                        #     customer = customer_fk.customer_code
                        # else:
                        #     customer = "all"
                        customer1 = q.customer_code
                        if customer1 is not '':
                            customer = customer1
                        else:
                            customer = "all"

                        false_action_log_fk = q.question_false_action.question_action.question_action_log
                        if false_action_log_fk is not None:
                            false_action_log = false_action_log_fk.question_action_log

                            false_action_log_type_fk = q.question_false_action.question_action.question_action_log.question_action_log_type
                            if false_action_log_type_fk is not None:
                                question_action_log_type1 = false_action_log_type_fk.type_id
                                question_action_log_type2 = false_action_log_type_fk.type_name
                            else:
                                question_action_log_type1 = 0
                                question_action_log_type2 = ""
                            false_action_log_type = question_action_log_type1
                            false_action_log_type_name = question_action_log_type2

                            false_action_log_text = false_action_log_fk.question_action_log_text
                            false_action_log_driver_name = false_action_log_fk.question_action_log_driver_name
                            false_action_log_driver_gps = false_action_log_fk.question_action_log_driver_gps
                            false_action_log_packages = false_action_log_fk.question_action_log_no_of_packages
                            false_action_log_customer_name = false_action_log_fk.question_action_log_customer_name
                            false_action_log_date_time = false_action_log_fk.question_action_log_date_time
                        else:
                            false_action_log = False
                            false_action_log_type = 0
                            false_action_log_type_name = ""
                            false_action_log_text = ""
                            false_action_log_driver_name = False
                            false_action_log_driver_gps = False
                            false_action_log_packages = False
                            false_action_log_customer_name = False
                            false_action_log_date_time = False
                        # print("log %s" % false_action_log)

                        false_action_block_fk = q.question_false_action.question_action.question_action_block
                        if false_action_block_fk is not None:
                            false_action_block = false_action_block_fk.question_action_block
                            false_action_block_text = false_action_block_fk.question_action_block_text
                        else:
                            false_action_block = False
                            false_action_block_text = ""
                        # print("block %s" % false_action_block)

                        false_action_record = q.question_false_action.question_action.question_action_record
                        # print("record %s" % false_action_record)

                        false_action_status_fk = q.question_false_action.question_action.question_action_status
                        if false_action_status_fk is not None:
                            false_action_status = false_action_status_fk.question_action_status
                            false_action_run_status = false_action_status_fk.run_status
                            false_action_drop_status = false_action_status_fk.drop_status
                            if false_action_run_status is True:
                                false_action_run_status_id = false_action_status_fk.run_status_id
                                false_action_run_status_name = false_action_status_fk.run_status_name
                            else:
                                false_action_run_status_id = 0
                                false_action_run_status_name = ""
                            if false_action_drop_status is True:
                                false_action_drop_status_id = false_action_status_fk.drop_status_id
                                false_action_drop_status_name = false_action_status_fk.drop_status_name
                            else:
                                false_action_drop_status_id = 0
                                false_action_drop_status_name = ""
                        else:
                            false_action_status = False
                            false_action_run_status = False
                            false_action_drop_status = False
                            false_action_run_status_id = 0
                            false_action_run_status_name = ""
                            false_action_drop_status_id = 0
                            false_action_drop_status_name = ""
                        # print("status %s" % false_action_status)

                        false_action_take_photo = q.question_false_action.question_action.question_action_take_photo
                        # print("photo %s" % false_action_take_photo)
                        false_action_signature = q.question_false_action.question_action.question_action_signature
                        # print("sign %s" % false_action_signature)
                        false_action_no_action = q.question_false_action.question_action.question_action_no_action
                        # print("no action %s" % false_action_no_action)

                        true_action_log_fk = q.question_true_action.question_action.question_action_log
                        if true_action_log_fk is not None:
                            true_action_log = true_action_log_fk.question_action_log

                            true_action_log_type_fk = true_action_log_fk.question_action_log_type
                            if true_action_log_type_fk is not None:
                                question_action_log_type1 = true_action_log_type_fk.type_id
                                question_action_log_type2 = true_action_log_type_fk.type_name
                            else:
                                question_action_log_type1 = 0
                                question_action_log_type2 = ""
                            true_action_log_type = question_action_log_type1
                            true_action_log_type_name = question_action_log_type2

                            true_action_log_text = true_action_log_fk.question_action_log_text
                            true_action_log_driver_name = true_action_log_fk.question_action_log_driver_name
                            true_action_log_driver_gps = true_action_log_fk.question_action_log_driver_gps
                            true_action_log_packages = true_action_log_fk.question_action_log_no_of_packages
                            true_action_log_customer_name = true_action_log_fk.question_action_log_customer_name
                            true_action_log_date_time = true_action_log_fk.question_action_log_date_time
                        else:
                            true_action_log = False
                            true_action_log_type = 0
                            true_action_log_type_name = ""
                            true_action_log_text = ""
                            true_action_log_driver_name = False
                            true_action_log_driver_gps = False
                            true_action_log_packages = False
                            true_action_log_customer_name = False
                            true_action_log_date_time = False
                        # print("true log %s" % true_action_log)

                        true_action_block_fk = q.question_true_action.question_action.question_action_block
                        if true_action_block_fk is not None:
                            true_action_block = true_action_block_fk.question_action_block
                            true_action_block_text = true_action_block_fk.question_action_block_text
                        else:
                            true_action_block = False
                            true_action_block_text = ""
                        # print("true block %s" % true_action_block)

                        true_action_record = q.question_true_action.question_action.question_action_record
                        # print("true record %s" % true_action_record)

                        true_action_status_fk = q.question_true_action.question_action.question_action_status
                        if true_action_status_fk is not None:
                            true_action_status = true_action_status_fk.question_action_status
                            true_action_run_status = true_action_status_fk.run_status
                            true_action_drop_status = true_action_status_fk.drop_status
                            if true_action_run_status is True:
                                true_action_run_status_id = true_action_status_fk.run_status_id
                                true_action_run_status_name = true_action_status_fk.run_status_name
                            else:
                                true_action_run_status_id = 0
                                true_action_run_status_name = ""
                            if true_action_drop_status is True:
                                true_action_drop_status_id = true_action_status_fk.drop_status_id
                                true_action_drop_status_name = true_action_status_fk.drop_status_name
                            else:
                                true_action_drop_status_id = 0
                                true_action_drop_status_name = ""

                        else:
                            true_action_status = False
                            true_action_run_status = False
                            true_action_drop_status = False
                            true_action_run_status_id = 0
                            true_action_run_status_name = ""
                            true_action_drop_status_id = 0
                            true_action_drop_status_name = ""
                        # print("true status %s" % true_action_status)

                        true_action_take_photo = q.question_true_action.question_action.question_action_take_photo
                        # print("true photo %s" % true_action_take_photo)
                        true_action_signature = q.question_true_action.question_action.question_action_signature
                        # print("true sign %s" % true_action_signature)
                        true_action_no_action = q.question_true_action.question_action.question_action_no_action
                        # print("true no action %s" % true_action_no_action)

                        result1 = {
                            "question_id": q_id,
                            "organisation": organisation,
                            "branch": branch,
                            "customer_code": customer,
                            "section_id": section_id,
                            "section": section,
                            "sequence": sequence,
                            "type": type,
                            "text": text,
                            "is_editable": True,

                            "false_action_log": false_action_log,
                            "false_action_log_type": false_action_log_type,
                            "false_action_log_type_name": false_action_log_type_name,
                            "false_action_log_text": false_action_log_text,

                            "false_action_log_driver_name": false_action_log_driver_name,
                            "false_action_log_driver_gps": false_action_log_driver_gps,
                            "false_action_log_no_of_packages": false_action_log_packages,
                            "false_action_log_customer_name": false_action_log_customer_name,
                            "false_action_log_date_time": false_action_log_date_time,

                            "false_action_block": false_action_block,
                            "false_action_block_text": false_action_block_text,

                            "false_action_record": false_action_record,

                            "false_action_status": false_action_status,
                            "false_action_run_status": false_action_run_status,
                            "false_action_drop_status": false_action_drop_status,
                            "false_action_run_status_id": false_action_run_status_id,
                            "false_action_run_status_name": false_action_run_status_name,
                            "false_action_drop_status_id": false_action_drop_status_id,
                            "false_action_drop_status_name": false_action_drop_status_name,

                            "false_action_take_photo": false_action_take_photo,

                            "false_action_signature": false_action_signature,

                            "false_action_no_action": false_action_no_action,

                            "true_action_log": true_action_log,
                            "true_action_log_type": true_action_log_type,
                            "true_action_log_type_name": true_action_log_type_name,
                            "true_action_log_text": true_action_log_text,

                            "true_action_log_driver_name": true_action_log_driver_name,
                            "true_action_log_driver_gps": true_action_log_driver_gps,
                            "true_action_log_no_of_packages": true_action_log_packages,
                            "true_action_log_customer_name": true_action_log_customer_name,
                            "true_action_log_date_time": true_action_log_date_time,

                            "true_action_block": true_action_block,
                            "true_action_block_text": true_action_block_text,

                            "true_action_record": true_action_record,

                            "true_action_status": true_action_status,
                            "true_action_run_status": true_action_run_status,
                            "true_action_drop_status": true_action_drop_status,
                            "true_action_run_status_id": true_action_run_status_id,
                            "true_action_run_status_name": true_action_run_status_name,
                            "true_action_drop_status_id": true_action_drop_status_id,
                            "true_action_drop_status_name": true_action_drop_status_name,

                            "true_action_take_photo": true_action_take_photo,

                            "true_action_signature": true_action_signature,

                            "true_action_no_action": true_action_no_action

                        }

                        view_questions.append(result1)

                    return Response({"view_questions": view_questions, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_questions": total_questions, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    org_param = Q(organisation=org_id)
                    branch_param = Q(branch=branch_id)
                    # customer_param = Q(customer_code=customer_code)
                    if customer_code is not None:
                        customer_list = customer_code.split(',')
                        customer_param = Q(customer_code__in=customer_list)
                    else:
                        customer_param = Q(customer_code='')

                    questions = Question.objects.order_by("question_sequence").filter(org_param & branch_param & customer_param)
                    # branches = Question.objects.order_by("question_sequence").filter(branch=branch_id)
                    # customer_codes = Question.objects.order_by("question_sequence").filter(customer_code=customer_code)
                    # print(questions)
                    total_questions = questions.count()
                    print(total_questions)
                    quest = Paginator(questions, 20)
                    if page_size:
                        quest = Paginator(questions, page_size)
                    page = request.GET.get('page')
                    # ques = quest.page(page)
                    print(page)


                    try:
                        ques = quest.page(page)
                    except PageNotAnInteger:
                        ques = quest.page(1)
                    except EmptyPage:
                        ques = quest.page(quest.num_pages)

                    has_next = ques.has_next()
                    if has_next is True:
                        next_page_number = ques.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques.has_previous()
                    if has_previous is True:
                        previous_page_number = ques.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)


                    # print(ques.has_other_pages())
                    # print(ques.start_index())
                    # print(ques.end_index())

                    # serializer = QuestionSerializer(ques, many=True)
                    # print(serializer.data)
                    # # return Response(serializer.data)
                    view_questions = []
                    for q in ques:
                        # print(question)
                        q_id = q.id
                        sequence = q.question_sequence
                        type = q.question_type.question_type
                        text1 = q.question_text
                        if text1 is not None:
                            text = text1
                        else:
                            text = ""

                        section = q.question_section.section_name

                        # branchadmin = BranchAdmins.objects.filter(user=user_id)
                        # for branches in branchadmin:
                        #     org = branches.branch.organisation
                        #
                        # org_fk = q.organisation
                        # if org_fk is not None:
                        #     if org == org_fk:
                        #         organisation = org_fk.organisation_name
                        #     else:
                        #         continue
                        # else:
                        #     organisation = "all"
                        #
                        # branch_fk = q.branch
                        # if branch_fk is not None:
                        #     branch = branch_fk.branch_name
                        # else:
                        #     branch = "all"
                        # print(branch)

                        org_fk = q.organisation
                        if org_fk is not None:
                            organisation = org_fk.organisation_name
                        else:
                            organisation = "all"

                        branch_fk = q.branch
                        if branch_fk is not None:
                            branch = branch_fk.branch_name
                        else:
                            branch = "all"

                        # customer_fk = q.customer_code
                        # if customer_fk is not None:
                        #     customer = customer_fk.customer_code
                        # else:
                        #     customer = "all"
                        customer1 = q.customer_code
                        if customer1 is not '':
                            customer = customer1
                        else:
                            customer = "all"

                        false_action_log_fk = q.question_false_action.question_action.question_action_log
                        if false_action_log_fk is not None:
                            false_action_log = false_action_log_fk.question_action_log

                            false_action_log_type_fk = q.question_false_action.question_action.question_action_log.question_action_log_type
                            if false_action_log_type_fk is not None:
                                question_action_log_type1 = false_action_log_type_fk.type_id
                                question_action_log_type2 = false_action_log_type_fk.type_name
                            else:
                                question_action_log_type1 = 0
                                question_action_log_type2 = ""
                            false_action_log_type = question_action_log_type1
                            false_action_log_type_name = question_action_log_type2

                            false_action_log_text = false_action_log_fk.question_action_log_text
                            false_action_log_driver_name = false_action_log_fk.question_action_log_driver_name
                            false_action_log_driver_gps = false_action_log_fk.question_action_log_driver_gps
                            false_action_log_packages = false_action_log_fk.question_action_log_no_of_packages
                            false_action_log_customer_name = false_action_log_fk.question_action_log_customer_name
                            false_action_log_date_time = false_action_log_fk.question_action_log_date_time
                        else:
                            false_action_log = False
                            false_action_log_type = 0
                            false_action_log_type_name = ""
                            false_action_log_text = ""
                            false_action_log_driver_name = False
                            false_action_log_driver_gps = False
                            false_action_log_packages = False
                            false_action_log_customer_name = False
                            false_action_log_date_time = False
                        # print("log %s" % false_action_log)

                        false_action_block_fk = q.question_false_action.question_action.question_action_block
                        if false_action_block_fk is not None:
                            false_action_block = false_action_block_fk.question_action_block
                            false_action_block_text = false_action_block_fk.question_action_block_text
                        else:
                            false_action_block = False
                            false_action_block_text = ""
                        # print("block %s" % false_action_block)

                        false_action_record = q.question_false_action.question_action.question_action_record
                        # print("record %s" % false_action_record)

                        false_action_status_fk = q.question_false_action.question_action.question_action_status
                        if false_action_status_fk is not None:
                            false_action_status = false_action_status_fk.question_action_status
                            false_action_run_status = false_action_status_fk.run_status
                            false_action_drop_status = false_action_status_fk.drop_status
                            if false_action_run_status is True:
                                false_action_run_status_id = false_action_status_fk.run_status_id
                                false_action_run_status_name = false_action_status_fk.run_status_name
                            else:
                                false_action_run_status_id = 0
                                false_action_run_status_name = ""
                            if false_action_drop_status is True:
                                false_action_drop_status_id = false_action_status_fk.drop_status_id
                                false_action_drop_status_name = false_action_status_fk.drop_status_name
                            else:
                                false_action_drop_status_id = 0
                                false_action_drop_status_name = ""
                        else:
                            false_action_status = False
                            false_action_run_status = False
                            false_action_drop_status = False
                            false_action_run_status_id = 0
                            false_action_run_status_name = ""
                            false_action_drop_status_id = 0
                            false_action_drop_status_name = ""
                        # print("status %s" % false_action_status)

                        false_action_take_photo = q.question_false_action.question_action.question_action_take_photo
                        # print("photo %s" % false_action_take_photo)
                        false_action_signature = q.question_false_action.question_action.question_action_signature
                        # print("sign %s" % false_action_signature)
                        false_action_no_action = q.question_false_action.question_action.question_action_no_action
                        # print("no action %s" % false_action_no_action)

                        true_action_log_fk = q.question_true_action.question_action.question_action_log
                        if true_action_log_fk is not None:
                            true_action_log = true_action_log_fk.question_action_log

                            true_action_log_type_fk = true_action_log_fk.question_action_log_type
                            if true_action_log_type_fk is not None:
                                question_action_log_type1 = true_action_log_type_fk.type_id
                                question_action_log_type2 = true_action_log_type_fk.type_name
                            else:
                                question_action_log_type1 = 0
                                question_action_log_type2 = ""
                            true_action_log_type = question_action_log_type1
                            true_action_log_type_name = question_action_log_type2

                            true_action_log_text = true_action_log_fk.question_action_log_text
                            true_action_log_driver_name = true_action_log_fk.question_action_log_driver_name
                            true_action_log_driver_gps = true_action_log_fk.question_action_log_driver_gps
                            true_action_log_packages = true_action_log_fk.question_action_log_no_of_packages
                            true_action_log_customer_name = true_action_log_fk.question_action_log_customer_name
                            true_action_log_date_time = true_action_log_fk.question_action_log_date_time
                        else:
                            true_action_log = False
                            true_action_log_type = 0
                            true_action_log_type_name = ""
                            true_action_log_text = ""
                            true_action_log_driver_name = False
                            true_action_log_driver_gps = False
                            true_action_log_packages = False
                            true_action_log_customer_name = False
                            true_action_log_date_time = False
                        # print("true log %s" % true_action_log)

                        true_action_block_fk = q.question_true_action.question_action.question_action_block
                        if true_action_block_fk is not None:
                            true_action_block = true_action_block_fk.question_action_block
                            true_action_block_text = true_action_block_fk.question_action_block_text
                        else:
                            true_action_block = False
                            true_action_block_text = ""
                        # print("true block %s" % true_action_block)

                        true_action_record = q.question_true_action.question_action.question_action_record
                        # print("true record %s" % true_action_record)

                        true_action_status_fk = q.question_true_action.question_action.question_action_status
                        if true_action_status_fk is not None:
                            true_action_status = true_action_status_fk.question_action_status
                            true_action_run_status = true_action_status_fk.run_status
                            true_action_drop_status = true_action_status_fk.drop_status
                            if true_action_run_status is True:
                                true_action_run_status_id = true_action_status_fk.run_status_id
                                true_action_run_status_name = true_action_status_fk.run_status_name
                            else:
                                true_action_run_status_id = 0
                                true_action_run_status_name = ""
                            if true_action_drop_status is True:
                                true_action_drop_status_id = true_action_status_fk.drop_status_id
                                true_action_drop_status_name = true_action_status_fk.drop_status_name
                            else:
                                true_action_drop_status_id = 0
                                true_action_drop_status_name = ""

                        else:
                            true_action_status = False
                            true_action_run_status = False
                            true_action_drop_status = False
                            true_action_run_status_id = 0
                            true_action_run_status_name = ""
                            true_action_drop_status_id = 0
                            true_action_drop_status_name = ""
                        # print("true status %s" % true_action_status)

                        true_action_take_photo = q.question_true_action.question_action.question_action_take_photo
                        # print("true photo %s" % true_action_take_photo)
                        true_action_signature = q.question_true_action.question_action.question_action_signature
                        # print("true sign %s" % true_action_signature)
                        true_action_no_action = q.question_true_action.question_action.question_action_no_action
                        # print("true no action %s" % true_action_no_action)

                        result1 = {
                            "question_id": q_id,
                            "organisation": organisation,
                            "branch": branch,
                            "customer_code": customer,
                            "section": section,
                            "sequence": sequence,
                            "type": type,
                            "text": text,
                            "is_editable": True,

                            "false_action_log": false_action_log,
                            "false_action_log_type": false_action_log_type,
                            "false_action_log_type_name": false_action_log_type_name,
                            "false_action_log_text": false_action_log_text,

                            "false_action_log_driver_name": false_action_log_driver_name,
                            "false_action_log_driver_gps": false_action_log_driver_gps,
                            "false_action_log_no_of_packages": false_action_log_packages,
                            "false_action_log_customer_name": false_action_log_customer_name,
                            "false_action_log_date_time": false_action_log_date_time,

                            "false_action_block": false_action_block,
                            "false_action_block_text": false_action_block_text,

                            "false_action_record": false_action_record,

                            "false_action_status": false_action_status,
                            "false_action_run_status": false_action_run_status,
                            "false_action_drop_status": false_action_drop_status,
                            "false_action_run_status_id": false_action_run_status_id,
                            "false_action_run_status_name": false_action_run_status_name,
                            "false_action_drop_status_id": false_action_drop_status_id,
                            "false_action_drop_status_name": false_action_drop_status_name,

                            "false_action_take_photo": false_action_take_photo,

                            "false_action_signature": false_action_signature,

                            "false_action_no_action": false_action_no_action,

                            "true_action_log": true_action_log,
                            "true_action_log_type": true_action_log_type,
                            "true_action_log_type_name": true_action_log_type_name,
                            "true_action_log_text": true_action_log_text,

                            "true_action_log_driver_name": true_action_log_driver_name,
                            "true_action_log_driver_gps": true_action_log_driver_gps,
                            "true_action_log_no_of_packages": true_action_log_packages,
                            "true_action_log_customer_name": true_action_log_customer_name,
                            "true_action_log_date_time": true_action_log_date_time,

                            "true_action_block": true_action_block,
                            "true_action_block_text": true_action_block_text,

                            "true_action_record": true_action_record,

                            "true_action_status": true_action_status,
                            "true_action_run_status": true_action_run_status,
                            "true_action_drop_status": true_action_drop_status,
                            "true_action_run_status_id": true_action_run_status_id,
                            "true_action_run_status_name": true_action_run_status_name,
                            "true_action_drop_status_id": true_action_drop_status_id,
                            "true_action_drop_status_name": true_action_drop_status_name,

                            "true_action_take_photo": true_action_take_photo,

                            "true_action_signature": true_action_signature,

                            "true_action_no_action": true_action_no_action

                        }

                        view_questions.append(result1)

                    return Response({"view_questions": view_questions, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_questions": total_questions, "status":status.HTTP_200_OK})

                elif request.user.is_active and (request.user.is_branch_admin or request.user.is_branch_user):
                    branch_param = Q(branch=branch_id)
                    # customer_param = Q(customer_code=customer_code)
                    if customer_code is not None:
                        customer_list = customer_code.split(',')
                        customer_param = Q(customer_code__in=customer_list)
                    else:
                        customer_param = Q(customer_code='')

                    questions = Question.objects.order_by("question_sequence").filter(branch_param & customer_param)
                    # branches = Question.objects.order_by("question_sequence").filter(branch=branch_id)
                    # customer_codes = Question.objects.order_by("question_sequence").filter(customer_code=customer_code)
                    # print(questions)
                    total_questions = questions.count()
                    print(total_questions)
                    quest = Paginator(questions, 20)
                    if page_size:
                        quest = Paginator(questions, page_size)
                    page = request.GET.get('page')
                    # ques = quest.page(page)
                    print(page)


                    try:
                        ques = quest.page(page)
                    except PageNotAnInteger:
                        ques = quest.page(1)
                    except EmptyPage:
                        ques = quest.page(quest.num_pages)

                    has_next = ques.has_next()
                    if has_next is True:
                        next_page_number = ques.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques.has_previous()
                    if has_previous is True:
                        previous_page_number = ques.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)


                    # print(ques.has_other_pages())
                    # print(ques.start_index())
                    # print(ques.end_index())

                    # serializer = QuestionSerializer(ques, many=True)
                    # print(serializer.data)
                    # # return Response(serializer.data)
                    view_questions = []
                    print("taht is not working?")
                    for q in ques:
                        print("taht is not in")
                        q_id = q.id
                        print("id is available or not")
                        print(q_id)
                        sequence = q.question_sequence
                        type = q.question_type.question_type
                        text1 = q.question_text
                        if text1 is not None:
                            text = text1
                        else:
                            text = ""

                        section = q.question_section.section_name

                        branchadmin = BranchAdmins.objects.filter(user=user_id)
                        for branches in branchadmin:
                            if branches.branch.branch_is_active is True:
                                org = branches.branch.organisation

                        org_fk = q.organisation
                        if org_fk is not None:
                            if org == org_fk:
                                organisation = org_fk.organisation_name
                            else:
                                continue
                        else:
                            organisation = "all"
                        print(organisation)

                        branch_fk = q.branch
                        print(branch_fk)
                        if branch_fk is not None:
                            branch = branch_fk.branch_name
                            print("if branch")
                            print(branch)
                        else:
                            branch = "all"
                            print("else branch")
                            print(branch)
                        print("out of condition branch")
                        print(branch)



                        # customer_fk = q.customer_code
                        # if customer_fk is not None:
                        #     customer = customer_fk.customer_code
                        # else:
                        #     customer = "all"
                        customer1 = q.customer_code
                        if customer1 is not '':
                            if organisation is "all":
                                customer = customer1
                            else:
                                continue
                        else:
                            customer = "all"

                        false_action_log_fk = q.question_false_action.question_action.question_action_log
                        if false_action_log_fk is not None:
                            false_action_log = false_action_log_fk.question_action_log

                            false_action_log_type_fk = q.question_false_action.question_action.question_action_log.question_action_log_type
                            if false_action_log_type_fk is not None:
                                question_action_log_type1 = false_action_log_type_fk.type_id
                                question_action_log_type2 = false_action_log_type_fk.type_name
                            else:
                                question_action_log_type1 = 0
                                question_action_log_type2 = ""
                            false_action_log_type = question_action_log_type1
                            false_action_log_type_name = question_action_log_type2

                            false_action_log_text = false_action_log_fk.question_action_log_text
                            false_action_log_driver_name = false_action_log_fk.question_action_log_driver_name
                            false_action_log_driver_gps = false_action_log_fk.question_action_log_driver_gps
                            false_action_log_packages = false_action_log_fk.question_action_log_no_of_packages
                            false_action_log_customer_name = false_action_log_fk.question_action_log_customer_name
                            false_action_log_date_time = false_action_log_fk.question_action_log_date_time
                        else:
                            false_action_log = False
                            false_action_log_type = 0
                            false_action_log_type_name = ""
                            false_action_log_text = ""
                            false_action_log_driver_name = False
                            false_action_log_driver_gps = False
                            false_action_log_packages = False
                            false_action_log_customer_name = False
                            false_action_log_date_time = False
                        # print("log %s" % false_action_log)

                        false_action_block_fk = q.question_false_action.question_action.question_action_block
                        if false_action_block_fk is not None:
                            false_action_block = false_action_block_fk.question_action_block
                            false_action_block_text = false_action_block_fk.question_action_block_text
                        else:
                            false_action_block = False
                            false_action_block_text = ""
                        # print("block %s" % false_action_block)

                        false_action_record = q.question_false_action.question_action.question_action_record
                        # print("record %s" % false_action_record)

                        false_action_status_fk = q.question_false_action.question_action.question_action_status
                        if false_action_status_fk is not None:
                            false_action_status = false_action_status_fk.question_action_status
                            false_action_run_status = false_action_status_fk.run_status
                            false_action_drop_status = false_action_status_fk.drop_status
                            if false_action_run_status is True:
                                false_action_run_status_id = false_action_status_fk.run_status_id
                                false_action_run_status_name = false_action_status_fk.run_status_name
                            else:
                                false_action_run_status_id = 0
                                false_action_run_status_name = ""
                            if false_action_drop_status is True:
                                false_action_drop_status_id = false_action_status_fk.drop_status_id
                                false_action_drop_status_name = false_action_status_fk.drop_status_name
                            else:
                                false_action_drop_status_id = 0
                                false_action_drop_status_name = ""
                        else:
                            false_action_status = False
                            false_action_run_status = False
                            false_action_drop_status = False
                            false_action_run_status_id = 0
                            false_action_run_status_name = ""
                            false_action_drop_status_id = 0
                            false_action_drop_status_name = ""
                        # print("status %s" % false_action_status)

                        false_action_take_photo = q.question_false_action.question_action.question_action_take_photo
                        # print("photo %s" % false_action_take_photo)
                        false_action_signature = q.question_false_action.question_action.question_action_signature
                        # print("sign %s" % false_action_signature)
                        false_action_no_action = q.question_false_action.question_action.question_action_no_action
                        # print("no action %s" % false_action_no_action)

                        true_action_log_fk = q.question_true_action.question_action.question_action_log
                        if true_action_log_fk is not None:
                            true_action_log = true_action_log_fk.question_action_log

                            true_action_log_type_fk = true_action_log_fk.question_action_log_type
                            if true_action_log_type_fk is not None:
                                question_action_log_type1 = true_action_log_type_fk.type_id
                                question_action_log_type2 = true_action_log_type_fk.type_name
                            else:
                                question_action_log_type1 = 0
                                question_action_log_type2 = ""
                            true_action_log_type = question_action_log_type1
                            true_action_log_type_name = question_action_log_type2

                            true_action_log_text = true_action_log_fk.question_action_log_text
                            true_action_log_driver_name = true_action_log_fk.question_action_log_driver_name
                            true_action_log_driver_gps = true_action_log_fk.question_action_log_driver_gps
                            true_action_log_packages = true_action_log_fk.question_action_log_no_of_packages
                            true_action_log_customer_name = true_action_log_fk.question_action_log_customer_name
                            true_action_log_date_time = true_action_log_fk.question_action_log_date_time
                        else:
                            true_action_log = False
                            true_action_log_type = 0
                            true_action_log_type_name = ""
                            true_action_log_text = ""
                            true_action_log_driver_name = False
                            true_action_log_driver_gps = False
                            true_action_log_packages = False
                            true_action_log_customer_name = False
                            true_action_log_date_time = False
                        # print("true log %s" % true_action_log)

                        true_action_block_fk = q.question_true_action.question_action.question_action_block
                        if true_action_block_fk is not None:
                            true_action_block = true_action_block_fk.question_action_block
                            true_action_block_text = true_action_block_fk.question_action_block_text
                        else:
                            true_action_block = False
                            true_action_block_text = ""
                        # print("true block %s" % true_action_block)

                        true_action_record = q.question_true_action.question_action.question_action_record
                        # print("true record %s" % true_action_record)

                        true_action_status_fk = q.question_true_action.question_action.question_action_status
                        if true_action_status_fk is not None:
                            true_action_status = true_action_status_fk.question_action_status
                            true_action_run_status = true_action_status_fk.run_status
                            true_action_drop_status = true_action_status_fk.drop_status
                            if true_action_run_status is True:
                                true_action_run_status_id = true_action_status_fk.run_status_id
                                true_action_run_status_name = true_action_status_fk.run_status_name
                            else:
                                true_action_run_status_id = 0
                                true_action_run_status_name = ""
                            if true_action_drop_status is True:
                                true_action_drop_status_id = true_action_status_fk.drop_status_id
                                true_action_drop_status_name = true_action_status_fk.drop_status_name
                            else:
                                true_action_drop_status_id = 0
                                true_action_drop_status_name = ""

                        else:
                            true_action_status = False
                            true_action_run_status = False
                            true_action_drop_status = False
                            true_action_run_status_id = 0
                            true_action_run_status_name = ""
                            true_action_drop_status_id = 0
                            true_action_drop_status_name = ""
                        # print("true status %s" % true_action_status)

                        true_action_take_photo = q.question_true_action.question_action.question_action_take_photo
                        # print("true photo %s" % true_action_take_photo)
                        true_action_signature = q.question_true_action.question_action.question_action_signature
                        # print("true sign %s" % true_action_signature)
                        true_action_no_action = q.question_true_action.question_action.question_action_no_action
                        # print("true no action %s" % true_action_no_action)

                        if branch is "all":
                            print("for all questions")
                            result1 = {
                                "question_id": q_id,
                                "organisation": organisation,
                                "branch": branch,
                                "customer_code": customer,
                                "section": section,
                                "sequence": sequence,
                                "type": type,
                                "text": text,
                                "is_editable": False,

                                "false_action_log": false_action_log,
                                "false_action_log_type": false_action_log_type,
                                "false_action_log_type_name": false_action_log_type_name,
                                "false_action_log_text": false_action_log_text,

                                "false_action_log_driver_name": false_action_log_driver_name,
                                "false_action_log_driver_gps": false_action_log_driver_gps,
                                "false_action_log_no_of_packages": false_action_log_packages,
                                "false_action_log_customer_name": false_action_log_customer_name,
                                "false_action_log_date_time": false_action_log_date_time,

                                "false_action_block": false_action_block,
                                "false_action_block_text": false_action_block_text,

                                "false_action_record": false_action_record,

                                "false_action_status": false_action_status,
                                "false_action_run_status": false_action_run_status,
                                "false_action_drop_status": false_action_drop_status,
                                "false_action_run_status_id": false_action_run_status_id,
                                "false_action_run_status_name": false_action_run_status_name,
                                "false_action_drop_status_id": false_action_drop_status_id,
                                "false_action_drop_status_name": false_action_drop_status_name,

                                "false_action_take_photo": false_action_take_photo,

                                "false_action_signature": false_action_signature,

                                "false_action_no_action": false_action_no_action,

                                "true_action_log": true_action_log,
                                "true_action_log_type": true_action_log_type,
                                "true_action_log_type_name": true_action_log_type_name,
                                "true_action_log_text": true_action_log_text,

                                "true_action_log_driver_name": true_action_log_driver_name,
                                "true_action_log_driver_gps": true_action_log_driver_gps,
                                "true_action_log_no_of_packages": true_action_log_packages,
                                "true_action_log_customer_name": true_action_log_customer_name,
                                "true_action_log_date_time": true_action_log_date_time,

                                "true_action_block": true_action_block,
                                "true_action_block_text": true_action_block_text,

                                "true_action_record": true_action_record,

                                "true_action_status": true_action_status,
                                "true_action_run_status": true_action_run_status,
                                "true_action_drop_status": true_action_drop_status,
                                "true_action_run_status_id": true_action_run_status_id,
                                "true_action_run_status_name": true_action_run_status_name,
                                "true_action_drop_status_id": true_action_drop_status_id,
                                "true_action_drop_status_name": true_action_drop_status_name,

                                "true_action_take_photo": true_action_take_photo,

                                "true_action_signature": true_action_signature,

                                "true_action_no_action": true_action_no_action

                            }
                        else:
                            result1 = {
                                "question_id": q_id,
                                "organisation": organisation,
                                "branch": branch,
                                "customer_code": customer,
                                "section": section,
                                "sequence": sequence,
                                "type": type,
                                "text": text,
                                "is_editable": True,

                                "false_action_log": false_action_log,
                                "false_action_log_type": false_action_log_type,
                                "false_action_log_type_name": false_action_log_type_name,
                                "false_action_log_text": false_action_log_text,

                                "false_action_log_driver_name": false_action_log_driver_name,
                                "false_action_log_driver_gps": false_action_log_driver_gps,
                                "false_action_log_no_of_packages": false_action_log_packages,
                                "false_action_log_customer_name": false_action_log_customer_name,
                                "false_action_log_date_time": false_action_log_date_time,

                                "false_action_block": false_action_block,
                                "false_action_block_text": false_action_block_text,

                                "false_action_record": false_action_record,

                                "false_action_status": false_action_status,
                                "false_action_run_status": false_action_run_status,
                                "false_action_drop_status": false_action_drop_status,
                                "false_action_run_status_id": false_action_run_status_id,
                                "false_action_run_status_name": false_action_run_status_name,
                                "false_action_drop_status_id": false_action_drop_status_id,
                                "false_action_drop_status_name": false_action_drop_status_name,

                                "false_action_take_photo": false_action_take_photo,

                                "false_action_signature": false_action_signature,

                                "false_action_no_action": false_action_no_action,

                                "true_action_log": true_action_log,
                                "true_action_log_type": true_action_log_type,
                                "true_action_log_type_name": true_action_log_type_name,
                                "true_action_log_text": true_action_log_text,

                                "true_action_log_driver_name": true_action_log_driver_name,
                                "true_action_log_driver_gps": true_action_log_driver_gps,
                                "true_action_log_no_of_packages": true_action_log_packages,
                                "true_action_log_customer_name": true_action_log_customer_name,
                                "true_action_log_date_time": true_action_log_date_time,

                                "true_action_block": true_action_block,
                                "true_action_block_text": true_action_block_text,

                                "true_action_record": true_action_record,

                                "true_action_status": true_action_status,
                                "true_action_run_status": true_action_run_status,
                                "true_action_drop_status": true_action_drop_status,
                                "true_action_run_status_id": true_action_run_status_id,
                                "true_action_run_status_name": true_action_run_status_name,
                                "true_action_drop_status_id": true_action_drop_status_id,
                                "true_action_drop_status_name": true_action_drop_status_name,

                                "true_action_take_photo": true_action_take_photo,

                                "true_action_signature": true_action_signature,

                                "true_action_no_action": true_action_no_action

                            }

                        view_questions.append(result1)

                    return Response({"view_questions": view_questions, "has_next": has_next,
                            "has_previous": has_previous,
                            "next_page_number": next_page_number,
                            "previous_page_number": previous_page_number,
                            "total_questions": total_questions, "status":status.HTTP_200_OK})

                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no role is defined for this user"})
            except:
                logger.debug("Error while retrieving questions")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Questions"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

    def delete(self, request):
        question_id = request.GET.get('question_id')
        question = Question.objects.filter(pk=question_id)

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin or request.user.is_active and request.user.is_branch_admin:
                    if question_id:
                        question[0].delete()
                        check_deleted = DeletedQuestion.objects.create(question_id=question_id, updated_at=datetime.datetime.now())
                        print(check_deleted)
                        return Response({"status":status.HTTP_204_NO_CONTENT, "Msg": "Question is deleted successfully"})
                    else:
                        return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This Question Doesn't exist"})
                # elif request.user.is_active and request.user.is_organisation_admin:
                #     if question_id:
                #         question[0].delete()
                #         return Response({"status":status.HTTP_204_NO_CONTENT, "Msg": "Question is deleted successfully"})
                #     else:
                #         return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This Question Doesn't exist"})
                # elif request.user.is_active and request.user.is_branch_admin:
                #     if question_id:
                #         question[0].delete()
                #         return Response({"status":status.HTTP_204_NO_CONTENT, "Msg": "Question is deleted successfully"})
                #     else:
                #         return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "This Question Doesn't exist"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "No role assigned to this user"})
            except:
                logger.debug("Error while deleting question")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Delete Question"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

#for admin panel...
class QuestionResponseAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        page_size = request.GET.get('page_size')

        # print(user_id)
        # print(user)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:

                    responses = QuestionResponse.objects.order_by("-answer_date_time").all()

                    query = request.GET.get('q')
                    if query:
                        responses = responses.filter(
                            Q(run_id__icontains=query) |
                            Q(drop_id__icontains=query) |
                            Q(question_section__icontains=query) |
                            Q(question_text__icontains=query) |
                            Q(question_answer__icontains=query) |
                            Q(question_data__icontains=query) |
                            Q(created_at__icontains=query)
                        ).distinct()

                    run = request.GET.get('run')
                    if run:
                        responses = responses.filter(
                            Q(run_id__icontains=run)
                        ).distinct()

                    drop = request.GET.get('drop')
                    if drop:
                        responses = responses.filter(
                            Q(drop_id__icontains=drop)
                        ).distinct()

                    section = request.GET.get('section')
                    if section:
                        responses = responses.filter(
                            Q(question_section__icontains=section)
                        ).distinct()

                    text = request.GET.get('text')
                    if text:
                        responses = responses.filter(
                            Q(question_text__icontains=text)
                        ).distinct()

                    answer = request.GET.get('answer')
                    if answer:
                        responses = responses.filter(
                            Q(question_answer__icontains=answer)
                        ).distinct()

                    data = request.GET.get('data')
                    if data:
                        responses = responses.filter(
                            Q(question_data__icontains=data)
                        ).distinct()

                    dateTime = request.GET.get('dateTime')
                    if dateTime:
                        responses = responses.filter(
                            Q(created_at__icontains=dateTime)
                        ).distinct()

                    total_responses = responses.count()
                    print(total_responses)

                    quest_ans = Paginator(responses, 20)
                    if page_size:
                        quest_ans = Paginator(responses, page_size)
                    page = request.GET.get('page')
                    # quest_ans = quest_ans.page(page)
                    print(page)

                    try:
                        ques_ans = quest_ans.page(page)
                    except PageNotAnInteger:
                        ques_ans = quest_ans.page(1)
                    except EmptyPage:
                        ques_ans = quest_ans.page(quest_ans.num_pages)

                    has_next = ques_ans.has_next()
                    if has_next is True:
                        next_page_number = ques_ans.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques_ans.has_previous()
                    if has_previous is True:
                        previous_page_number = ques_ans.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)

                    response = []
                    for ans in ques_ans:
                        response_id = ans.id
                        run_id = ans.run_id
                        drop_id = ans.drop_id
                        question_section = ans.question_section
                        question_text = ans.question_text
                        question_answer = ans.question_answer
                        question_data = ans.question_data
                        driver_name = ans.driver_name
                        branch_name = ans.branch_id.branch_name if ans.branch_id else ''
                        if question_data is None:
                            question_data = ""
                        date_time = ans.answer_date_time

                        s = date_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        result1 = {
                            "response_id": response_id,
                            "run_id": run_id,
                            "drop_id": drop_id,
                            "question_section": question_section,
                            "question_text": question_text,
                            "question_answer": question_answer,
                            "question_data": question_data,
                            "date_time": date_time,
                            "driver_name": driver_name,
                            "branch_name": branch_name
                            }
                        response.append(result1)

                    return Response({"question_responses": response, "has_next": has_next,
                            "has_previous": has_previous,"next_page_number": next_page_number,"total_responses": total_responses,
                            "previous_page_number": previous_page_number, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:

                    org_admin = OrganisationAdmins.objects.filter(user=user_id)
                    org_ids = []
                    branch_ids = []
                    for orgs in org_admin:
                        org_id = orgs.organisation.id
                        org_params = Q(organisation=org_id)
                        all_org_params = Q(organisation=None)
                        org_qs = Question.objects.filter(org_params | all_org_params)
                        for org_q in org_qs:
                            org_q_pk = org_q.id
                            org_ids.append(org_q_pk)

                        branches = Branch.objects.filter(organisation=org_id)
                        for branch in branches:
                            branch_id = branch.id
                            branch_params = Q(branch=branch_id)
                            all_branch_params = Q(branch=None)
                            branch_qs = Question.objects.filter(branch_params | all_branch_params)
                            for branch_q in branch_qs:
                                branch_q_pk = branch_q.id
                                branch_ids.append(branch_q_pk)

                    print("Fisrt")
                    print(org_ids)
                    print("Second")
                    print(branch_ids)

                    branch_q_params = Q(q_id__in=branch_ids)
                    org_q_params = Q(q_id__in=org_ids)
                    responses = QuestionResponse.objects.order_by("-answer_date_time").filter(branch_q_params | org_q_params)


                    query = request.GET.get('q')
                    if query:
                        responses = responses.filter(
                            Q(run_id__icontains=query) |
                            Q(drop_id__icontains=query) |
                            Q(question_section__icontains=query) |
                            Q(question_text__icontains=query) |
                            Q(question_answer__icontains=query) |
                            Q(question_data__icontains=query) |
                            Q(created_at__icontains=query)
                        ).distinct()

                    run = request.GET.get('run')
                    if run:
                        responses = responses.filter(
                            Q(run_id__icontains=run)
                        ).distinct()

                    drop = request.GET.get('drop')
                    if drop:
                        responses = responses.filter(
                            Q(drop_id__icontains=drop)
                        ).distinct()

                    section = request.GET.get('section')
                    if section:
                        responses = responses.filter(
                            Q(question_section__icontains=section)
                        ).distinct()

                    text = request.GET.get('text')
                    if text:
                        responses = responses.filter(
                            Q(question_text__icontains=text)
                        ).distinct()

                    answer = request.GET.get('answer')
                    if answer:
                        responses = responses.filter(
                            Q(question_answer__icontains=answer)
                        ).distinct()

                    data = request.GET.get('data')
                    if data:
                        responses = responses.filter(
                            Q(question_data__icontains=data)
                        ).distinct()

                    dateTime = request.GET.get('dateTime')
                    if dateTime:
                        responses = responses.filter(
                            Q(created_at__icontains=dateTime)
                        ).distinct()

                    total_responses = responses.count()
                    print(total_responses)

                    quest_ans = Paginator(responses, 20)
                    if page_size:
                        quest_ans = Paginator(responses, page_size)
                    page = request.GET.get('page')
                    # quest_ans = quest_ans.page(page)
                    print(page)

                    try:
                        ques_ans = quest_ans.page(page)
                    except PageNotAnInteger:
                        ques_ans = quest_ans.page(1)
                    except EmptyPage:
                        ques_ans = quest_ans.page(quest_ans.num_pages)

                    has_next = ques_ans.has_next()
                    if has_next is True:
                        next_page_number = ques_ans.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques_ans.has_previous()
                    if has_previous is True:
                        previous_page_number = ques_ans.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)

                    response = []
                    for ans in ques_ans:
                        response_id = ans.id
                        run_id = ans.run_id
                        drop_id = ans.drop_id
                        question_section = ans.question_section
                        question_text = ans.question_text
                        question_answer = ans.question_answer
                        question_data = ans.question_data
                        driver_name = ans.driver_name
                        branch_name = ans.branch_id.branch_name if ans.branch_id else ''
                        if question_data is None:
                            question_data = ""
                        date_time = ans.answer_date_time

                        s = date_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        result1 = {
                            "response_id": response_id,
                            "run_id": run_id,
                            "drop_id": drop_id,
                            "question_section": question_section,
                            "question_text": question_text,
                            "question_answer": question_answer,
                            "question_data": question_data,
                            "date_time": date_time,
                            "driver_name": driver_name,
                            "branch_name": branch_name

                            }
                        response.append(result1)

                    return Response({"question_responses": response, "has_next": has_next,
                            "has_previous": has_previous,"next_page_number": next_page_number,"total_responses": total_responses,
                            "previous_page_number": previous_page_number, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_branch_admin:

                    branch_admin = BranchAdmins.objects.filter(user=user_id)
                    # org_ids = []
                    branch_ids = []
                    # org_id = branch_admin[0].branch.organisation.id
                    # org_qs = Question.objects.filter(organisation=org_id)
                    # for org_q in org_qs:
                    #     org_q_pk = org_q.id
                    #     org_ids.append(org_q_pk)

                    for branches in branch_admin:
                        branch_id = branches.branch.id
                        org_params = Q(organisation=None)
                        branch_params = Q(branch=branch_id)
                        all_branch_params = Q(branch=None)
                        branch_qs = Question.objects.filter(branch_params | all_branch_params & org_params)
                        for branch_q in branch_qs:
                            branch_q_pk = branch_q.id
                            branch_ids.append(branch_q_pk)

                    # print("Fisrt")
                    # print(org_ids)
                    print("Second")
                    print(branch_ids)

                    # branch_q_params = Q(q_id__in=branch_ids)
                    # org_q_params = Q(q_id__in=org_ids)
                    responses = QuestionResponse.objects.order_by("-answer_date_time").filter(q_id__in=branch_ids)


                    query = request.GET.get('q')
                    if query:
                        responses = responses.filter(
                            Q(run_id__icontains=query) |
                            Q(drop_id__icontains=query) |
                            Q(question_section__icontains=query) |
                            Q(question_text__icontains=query) |
                            Q(question_answer__icontains=query) |
                            Q(question_data__icontains=query) |
                            Q(created_at__icontains=query)
                        ).distinct()

                    run = request.GET.get('run')
                    if run:
                        responses = responses.filter(
                            Q(run_id__icontains=run)
                        ).distinct()

                    drop = request.GET.get('drop')
                    if drop:
                        responses = responses.filter(
                            Q(drop_id__icontains=drop)
                        ).distinct()

                    section = request.GET.get('section')
                    if section:
                        responses = responses.filter(
                            Q(question_section__icontains=section)
                        ).distinct()

                    text = request.GET.get('text')
                    if text:
                        responses = responses.filter(
                            Q(question_text__icontains=text)
                        ).distinct()

                    answer = request.GET.get('answer')
                    if answer:
                        responses = responses.filter(
                            Q(question_answer__icontains=answer)
                        ).distinct()

                    data = request.GET.get('data')
                    if data:
                        responses = responses.filter(
                            Q(question_data__icontains=data)
                        ).distinct()

                    dateTime = request.GET.get('dateTime')
                    if dateTime:
                        responses = responses.filter(
                            Q(created_at__icontains=dateTime)
                        ).distinct()

                    total_responses = responses.count()
                    print(total_responses)

                    quest_ans = Paginator(responses, 20)
                    if page_size:
                        quest_ans = Paginator(responses, page_size)
                    page = request.GET.get('page')
                    # quest_ans = quest_ans.page(page)
                    print(page)

                    try:
                        ques_ans = quest_ans.page(page)
                    except PageNotAnInteger:
                        ques_ans = quest_ans.page(1)
                    except EmptyPage:
                        ques_ans = quest_ans.page(quest_ans.num_pages)

                    has_next = ques_ans.has_next()
                    if has_next is True:
                        next_page_number = ques_ans.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques_ans.has_previous()
                    if has_previous is True:
                        previous_page_number = ques_ans.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)

                    response = []
                    for ans in ques_ans:
                        response_id = ans.id
                        run_id = ans.run_id
                        drop_id = ans.drop_id
                        question_section = ans.question_section
                        question_text = ans.question_text
                        question_answer = ans.question_answer
                        question_data = ans.question_data
                        driver_name = ans.driver_name
                        branch_name = ans.branch_id.branch_name if ans.branch_id else ''
                        if question_data is None:
                            question_data = ""
                        date_time = ans.answer_date_time

                        s = date_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        result1 = {
                            "response_id": response_id,
                            "run_id": run_id,
                            "drop_id": drop_id,
                            "question_section": question_section,
                            "question_text": question_text,
                            "question_answer": question_answer,
                            "question_data": question_data,
                            "date_time": date_time,
                            "driver_name": driver_name,
                            "branch_name": branch_name
                            }
                        response.append(result1)

                    return Response({"question_responses": response, "has_next": has_next,
                            "has_previous": has_previous,"next_page_number": next_page_number,"total_responses": total_responses,
                            "previous_page_number": previous_page_number, "status":status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_branch_user:
                    branch_admin = BranchUsers.objects.filter(user=user_id)
                    # org_ids = []
                    branch_ids = []
                    # org_id = branch_admin[0].branch.organisation.id
                    # org_qs = Question.objects.filter(organisation=org_id)
                    # for org_q in org_qs:
                    #     org_q_pk = org_q.id
                    #     org_ids.append(org_q_pk)

                    for branches in branch_admin:
                        branch_id = branches.branch.id
                        org_params = Q(organisation=None)
                        branch_params = Q(branch=branch_id)
                        all_branch_params = Q(branch=None)
                        branch_qs = Question.objects.filter(branch_params | all_branch_params & org_params)
                        for branch_q in branch_qs:
                            branch_q_pk = branch_q.id
                            branch_ids.append(branch_q_pk)

                    # print("Fisrt")
                    # print(org_ids)
                    

                    # branch_q_params = Q(q_id__in=branch_ids)
                    # org_q_params = Q(q_id__in=org_ids)
                    
                    responses = QuestionResponse.objects.order_by("-answer_date_time").filter(q_id__in=branch_ids)
                    


                    query = request.GET.get('q')
                    if query:
                        responses = responses.filter(
                            Q(run_id__icontains=query) |
                            Q(drop_id__icontains=query) |
                            Q(question_section__icontains=query) |
                            Q(question_text__icontains=query) |
                            Q(question_answer__icontains=query) |
                            Q(question_data__icontains=query) |
                            Q(created_at__icontains=query)
                        ).distinct()

                    run = request.GET.get('run')
                    if run:
                        responses = responses.filter(
                            Q(run_id__icontains=run)
                        ).distinct()

                    drop = request.GET.get('drop')
                    if drop:
                        responses = responses.filter(
                            Q(drop_id__icontains=drop)
                        ).distinct()

                    section = request.GET.get('section')
                    if section:
                        responses = responses.filter(
                            Q(question_section__icontains=section)
                        ).distinct()

                    text = request.GET.get('text')
                    if text:
                        responses = responses.filter(
                            Q(question_text__icontains=text)
                        ).distinct()

                    answer = request.GET.get('answer')
                    if answer:
                        responses = responses.filter(
                            Q(question_answer__icontains=answer)
                        ).distinct()

                    data = request.GET.get('data')
                    if data:
                        responses = responses.filter(
                            Q(question_data__icontains=data)
                        ).distinct()

                    dateTime = request.GET.get('dateTime')
                    if dateTime:
                        responses = responses.filter(
                            Q(created_at__icontains=dateTime)
                        ).distinct()

                    total_responses = responses.count()
                    print(total_responses)

                    quest_ans = Paginator(responses, 20)
                    if page_size:
                        quest_ans = Paginator(responses, page_size)
                    page = request.GET.get('page')
                    # quest_ans = quest_ans.page(page)
                    print(page)

                    try:
                        ques_ans = quest_ans.page(page)
                    except PageNotAnInteger:
                        ques_ans = quest_ans.page(1)
                    except EmptyPage:
                        ques_ans = quest_ans.page(quest_ans.num_pages)

                    has_next = ques_ans.has_next()
                    if has_next is True:
                        next_page_number = ques_ans.next_page_number()
                    else:
                        next_page_number = "There is no next page. This is the last page"
                    print(next_page_number)

                    has_previous = ques_ans.has_previous()
                    if has_previous is True:
                        previous_page_number = ques_ans.previous_page_number()
                    else:
                        previous_page_number = "There is no previous page. This is the first page"
                    print(previous_page_number)

                    response = []
                    for ans in ques_ans:
                        response_id = ans.id
                        run_id = ans.run_id
                        drop_id = ans.drop_id
                        question_section = ans.question_section
                        question_text = ans.question_text
                        question_answer = ans.question_answer
                        question_data = ans.question_data
                        driver_name = ans.driver_name
                        branch_name = ans.branch_id.branch_name if ans.branch_id else ''
                        if question_data is None:
                            question_data = ""
                        date_time = ans.answer_date_time

                        s = date_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        result1 = {
                            "response_id": response_id,
                            "run_id": run_id,
                            "drop_id": drop_id,
                            "question_section": question_section,
                            "question_text": question_text,
                            "question_answer": question_answer,
                            "question_data": question_data,
                            "date_time": date_time,
                            "driver_name": driver_name,
                            "branch_name": branch_name
                            }
                        response.append(result1)

                    return Response({"question_responses": response, "has_next": has_next,
                            "has_previous": has_previous,"next_page_number": next_page_number,"total_responses": total_responses,
                            "previous_page_number": previous_page_number, "status":status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no Role is defined for this user"})
            except:
                logger.debug("Error while retrieving responses")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve responses"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

    def post(self,request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:

                    fromDate = request.data.get('from')
                    first = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
                    print(first)
                    # first_ago = first - timedelta(days=1)
                    toDate = request.data.get('to')
                    last = datetime.datetime.strptime(toDate, '%Y-%m-%d')
                    last_advent = last + timedelta(days=1)
                    date_param = Q(answer_date_time__range=[first, last_advent])
                    answers = QuestionResponse.objects.order_by("-answer_date_time").filter(date_param).select_related('branch_id')
                    print("answers")
                    print(answers)

                    if answers:

                        s = answers[0].answer_date_time.strftime('%Y%m%d%H%M%S%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        filename = "answers" + date_time + user_id + ".xlsx"
                        wb = xlsxwriter.Workbook('media/Downloads/' + filename)
                        ws = wb.add_worksheet("responses %s" % date_time + user_id)
                        row_num = 0

                        # font_style = xlsxwriter.XFStyle()
                        font_style = wb.add_format()
                        font_style.set_bold()
                        # font_style.font.bold = True
                        columns = ['run_id', 'drop_id', 'Branch','Driver','question_section', 'question_text', 'question_answer',
                                   'answer_date']
                        for col_num in range(len(columns)):
                            ws.write(row_num, col_num, columns[col_num], font_style)

                        font_style = wb.add_format()
                        font_style.set_bold(False)

                        for ans in answers:
                            print("ans is ", ans)
                            run_id = ans.run_id
                            drop_id = ans.drop_id
                            branch = ans.branch_id.branch_name
                            driver = ans.driver_name
                            question_section = ans.question_section
                            question_text = ans.question_text
                            question_answer = ans.question_answer
                            question_answer = 'yes' if question_answer == True else 'no'
                            answer_date_time = ans.answer_date_time
                            answer_date = str(answer_date_time).split(' ')
                            print(answer_date[0])

                            if row_num <= 1048574:
                                print("before increment")
                                print(row_num)
                                row_num += 1
                                print("after increment")
                                print(row_num)
                                # print(row)
                                ws.write(row_num, 0, run_id, font_style)
                                ws.write(row_num, 1, drop_id, font_style)
                                ws.write(row_num, 2, branch, font_style)
                                ws.write(row_num, 3, driver, font_style)
                                ws.write(row_num, 4, question_section, font_style)
                                ws.write(row_num, 5, question_text, font_style)
                                ws.write(row_num, 6, question_answer, font_style)
                                ws.write(row_num, 7, answer_date[0], font_style)
                        row_num += 2
                        wb.close()
                        return Response({"status": status.HTTP_200_OK, "link": "Downloads/" + filename})
                            # response.append(result1)
                    else:
                        return Response({"status": status.HTTP_204_NO_CONTENT,
                                         "Msg": "No question found"})

                    # filename = "answers" + date_time + user_id + ".xlsx"
                    # wb = xlsxwriter.Workbook('media/Downloads/' + filename)
                    # ws = wb.add_worksheet("responses %s" % date_time + user_id)
                    # row_num = 0
                    #
                    # # font_style = xlsxwriter.XFStyle()
                    # font_style = wb.add_format()
                    # font_style.set_bold()
                    # # font_style.font.bold = True
                    # columns = ['run_id', 'drop_id', 'question_section', 'question_text', 'question_answer',
                    #            'answer_date']
                    # for col_num in range(len(columns)):
                    #     ws.write(row_num, col_num, columns[col_num], font_style)
                    #
                    # font_style = wb.add_format()
                    # font_style.set_bold(False)
                    # for row in response:
                    #     if row_num <= 1048574:
                    #         print("before increment")
                    #         print(row_num)
                    #         row_num += 1
                    #         print("after increment")
                    #         print(row_num)
                    #         print(row)
                    #         ws.write(row_num, 0, row['run_id'], font_style)
                    #         ws.write(row_num, 1, row['drop_id'], font_style)
                    #         ws.write(row_num, 2, row['question_section'], font_style)
                    #         ws.write(row_num, 3, row['question_text'], font_style)
                    #         ws.write(row_num, 4, row['question_answer'], font_style)
                    #         ws.write(row_num, 5, row['answer_date'], font_style)
                    # row_num += 2
                    # wb.close()

                    # wb = xlwt.Workbook(encoding='utf-8')
                    # ws = wb.add_sheet("responses %s" %date_time+user_id)
                    # row_num = 0
                    #
                    # font_style = xlwt.XFStyle()
                    # font_style.font.bold = True
                    # columns = ['run_id', 'drop_id', 'question_section', 'question_text', 'question_answer', 'answer_date']
                    # for col_num in range(len(columns)):
                    #     ws.write(row_num, col_num, columns[col_num], font_style)
                    #
                    # font_style = xlwt.XFStyle()
                    # for row in response:
                    #     if row_num <= 65534:
                    #         print("before increment")
                    #         print(row_num)
                    #         row_num += 1
                    #         print("after increment")
                    #         print(row_num)
                    #         print(row)
                    #         ws.write(row_num, 0, row['run_id'], font_style)
                    #         ws.write(row_num, 1, row['drop_id'], font_style)
                    #         ws.write(row_num, 2, row['question_section'], font_style)
                    #         ws.write(row_num, 3, row['question_text'], font_style)
                    #         ws.write(row_num, 4, row['question_answer'], font_style)
                    #         ws.write(row_num, 5, row['answer_date'], font_style)
                    # row_num +=2
                    # font_style = xlwt.XFStyle()
                    # font_style.font.bold = True
                    # filename = "answers"+date_time+user_id+".xls"
                    # wb.save('media/Downloads/'+filename)

                    # email_body = 'Dear '+admin[0].first_name+' '+admin[0].last_name +',\n\nPlease find requested report attached with this email .\n\n' + 'Regards, \n' + 'Reading Hub Team'
                    # mail = EmailMessage('Sales Report', email_body,settings.EMAIL_HOST_USER , [admin[0].email])
                    # mail.attach_file('report.xls')
                    # mail.send()
                    # return Response({"status":status.HTTP_200_OK,"link":"Downloads/"+filename})

                elif request.user.is_active and request.user.is_organisation_admin:

                    org_admin = OrganisationAdmins.objects.filter(user=user_id)
                    org_ids = []
                    branch_ids = []
                    for orgs in org_admin:
                        org_id = orgs.organisation.id
                        org_params = Q(organisation=org_id)
                        all_org_params = Q(organisation=None)
                        org_qs = Question.objects.filter(org_params | all_org_params)
                        for org_q in org_qs:
                            org_q_pk = org_q.id
                            org_ids.append(org_q_pk)

                        branches = Branch.objects.filter(organisation=org_id)
                        for branch in branches:
                            branch_id = branch.id
                            branch_params = Q(branch=branch_id)
                            all_branch_params = Q(branch=None)
                            branch_qs = Question.objects.filter(branch_params | all_branch_params)
                            for branch_q in branch_qs:
                                branch_q_pk = branch_q.id
                                branch_ids.append(branch_q_pk)

                    print("Fisrt")
                    print(org_ids)
                    print("Second")
                    print(branch_ids)

                    branch_q_params = Q(q_id__in=branch_ids)
                    org_q_params = Q(q_id__in=org_ids)

                    fromDate = request.data.get('from')
                    first = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
                    toDate = request.data.get('to')
                    last = datetime.datetime.strptime(toDate, '%Y-%m-%d')
                    last_advent = last + timedelta(days=1)
                    date_param = Q(answer_date_time__range=[first, last_advent])
                    answers = QuestionResponse.objects.order_by("-answer_date_time").filter(date_param &
                                                                                            (branch_q_params | org_q_params))
                    # answers = QuestionResponse.objects.order_by("-answer_date_time").filter(date_param)
                    print("answers")
                    print(answers)
                    if answers:

                        s = answers[0].answer_date_time.strftime('%Y%m%d%H%M%S%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        filename = "answers" + date_time + user_id + ".xlsx"
                        wb = xlsxwriter.Workbook('media/Downloads/' + filename)
                        ws = wb.add_worksheet("responses %s" % date_time + user_id)
                        row_num = 0

                        # font_style = xlsxwriter.XFStyle()
                        font_style = wb.add_format()
                        font_style.set_bold()
                        # font_style.font.bold = True
                        columns = ['run_id', 'drop_id', 'question_section', 'question_text', 'question_answer',
                                   'answer_date']
                        for col_num in range(len(columns)):
                            ws.write(row_num, col_num, columns[col_num], font_style)

                        font_style = wb.add_format()
                        font_style.set_bold(False)

                        for ans in answers:
                            run_id = ans.run_id
                            drop_id = ans.drop_id
                            question_section = ans.question_section
                            question_text = ans.question_text
                            question_answer = ans.question_answer
                            question_answer = 'yes' if question_answer == True else 'no'
                            answer_date_time = ans.answer_date_time
                            answer_date = str(answer_date_time).split(' ')
                            print(answer_date[0])

                            if row_num <= 1048574:
                                print("before increment")
                                print(row_num)
                                row_num += 1
                                print("after increment")
                                print(row_num)
                                # print(row)
                                ws.write(row_num, 0, run_id, font_style)
                                ws.write(row_num, 1, drop_id, font_style)
                                ws.write(row_num, 2, question_section, font_style)
                                ws.write(row_num, 3, question_text, font_style)
                                ws.write(row_num, 4, question_answer, font_style)
                                ws.write(row_num, 5, answer_date[0], font_style)
                        row_num += 2
                        wb.close()
                        return Response({"status": status.HTTP_200_OK, "link": "Downloads/" + filename})
                        # response.append(result1)


                    else:
                        return Response({"status": status.HTTP_204_NO_CONTENT,
                                         "Msg": "No question found"})

                elif request.user.is_active and request.user.is_branch_admin:

                    branch_admin = BranchAdmins.objects.filter(user=user_id)
                    # org_ids = []
                    branch_ids = []
                    # org_id = branch_admin[0].branch.organisation.id
                    # org_qs = Question.objects.filter(organisation=org_id)
                    # for org_q in org_qs:
                    #     org_q_pk = org_q.id
                    #     org_ids.append(org_q_pk)

                    for branches in branch_admin:
                        branch_id = branches.branch.id
                        org_params = Q(organisation=None)
                        branch_params = Q(branch=branch_id)
                        all_branch_params = Q(branch=None)
                        branch_qs = Question.objects.filter(branch_params | all_branch_params & org_params)
                        for branch_q in branch_qs:
                            branch_q_pk = branch_q.id
                            branch_ids.append(branch_q_pk)

                    # print("Fisrt")
                    # print(org_ids)
                    print("Second")
                    print(branch_ids)

                    branch_q_params = Q(q_id__in=branch_ids)
                    # org_q_params = Q(q_id__in=org_ids)

                    fromDate = request.data.get('from')
                    first = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
                    toDate = request.data.get('to')
                    last = datetime.datetime.strptime(toDate, '%Y-%m-%d')
                    last_advent = last + timedelta(days=1)
                    date_param = Q(answer_date_time__range=[first, last_advent])
                    answers = QuestionResponse.objects.order_by("-answer_date_time").filter(branch_q_params & date_param)
                    # answers = QuestionResponse.objects.order_by("-answer_date_time").filter(date_param &
                    #     branch_q_params | org_q_params)
                    # answers = QuestionResponse.objects.order_by("-answer_date_time").filter(date_param)
                    print("answers")
                    print(answers)
                    if answers:
                        s = answers[0].answer_date_time.strftime('%Y%m%d%H%M%S%f')
                        print(s)
                        tail = s[-4:]
                        f = round(float(tail), 3)
                        temp = "%.3f" % f
                        print((s[:-4], temp[1:]))
                        print(type(s[-4:]))
                        date_time = s[:-4]

                        filename = "answers" + date_time + user_id + ".xlsx"
                        wb = xlsxwriter.Workbook('media/Downloads/' + filename)
                        ws = wb.add_worksheet("responses %s" % date_time + user_id)
                        row_num = 0

                        # font_style = xlsxwriter.XFStyle()
                        font_style = wb.add_format()
                        font_style.set_bold()
                        # font_style.font.bold = True
                        columns = ['run_id', 'drop_id', 'question_section', 'question_text', 'question_answer',
                                   'answer_date']
                        for col_num in range(len(columns)):
                            ws.write(row_num, col_num, columns[col_num], font_style)

                        font_style = wb.add_format()
                        font_style.set_bold(False)

                        for ans in answers:
                            run_id = ans.run_id
                            drop_id = ans.drop_id
                            question_section = ans.question_section
                            question_text = ans.question_text
                            question_answer = ans.question_answer
                            question_answer = 'yes' if question_answer == True else 'no'
                            answer_date_time = ans.answer_date_time
                            answer_date = str(answer_date_time).split(' ')
                            print(answer_date[0])

                            if row_num <= 1048574:
                                print("before increment")
                                print(row_num)
                                row_num += 1
                                print("after increment")
                                print(row_num)
                                # print(row)
                                ws.write(row_num, 0, run_id, font_style)
                                ws.write(row_num, 1, drop_id, font_style)
                                ws.write(row_num, 2, question_section, font_style)
                                ws.write(row_num, 3, question_text, font_style)
                                ws.write(row_num, 4, question_answer, font_style)
                                ws.write(row_num, 5, answer_date[0], font_style)
                        row_num += 2
                        wb.close()
                        return Response({"status": status.HTTP_200_OK, "link": "Downloads/" + filename})
                        # response.append(result1)
                    else:
                        return Response({"status": status.HTTP_204_NO_CONTENT,
                                         "Msg": "No question found"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no Role is defined for this user"})
            except:
                print(traceback.format_exc())
                return Response({"status":status.HTTP_500_INTERNAL_SERVER_ERROR,"Msg":"could not download the requested report"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

#for android...
class DeviceRegisterAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request):

        branches = Branch.objects.all().order_by('branch_name')
        branc = []
        try:
            for branch in branches:
                if branch.branch_is_active is True:
                    id = branch.id
                    name = branch.branch_name

                    result2 = {
                        "branch_id": id,
                        "branch_name": name
                    }

                    branc.append(result2)

            return Response({"branches": branc, "status":status.HTTP_200_OK})
        except:
            logger.debug("Error while retrieving branches")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Branches"})

    def post(self, request):

        branch_id = request.POST.get('branch_id')
        make = request.POST.get('make')
        model = request.POST.get('model')
        imei_no = request.POST.get('imei')
        print("branch_id")
        print(branch_id)
        print(type(branch_id))

        branch = Branch.objects.filter(pk=branch_id)
        for br in branch:
            br1 = br


        # user_id = request.GET.get('user_id')
        # user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)


        # print(request.user.is_superuser)
        # if request.user.is_active and request.user.is_superuser:



        if make and model and imei_no and branch_id:
            try:
                device = Device.objects.filter(device_imei_no=imei_no)
                for dev in device:
                    device_branch = dev.branch.id
                    print("branch_id")
                    print(device_branch)
                    print(type(device_branch))
                    is_active = dev.device_is_active
                    is_revoke = dev.device_is_revoke
                    is_inactive = dev.device_is_inactive
                if device:
                    print(imei_no)
                    print(device)
                    if is_active is True:
                        if branch_id == str(device_branch):
                            user = User.objects.filter(username=imei_no)
                            if user:
                                # if user.is_active:
                                #     # data["user"] = user
                                if user[0].check_password(imei_no):
                                    print(user)
                                    print(user[0].check_password(imei_no))
                                    token, created = Token.objects.get_or_create(user=user[0])
                                    print("Token:" + token.key)
                                    return Response({"token": token.key, "status": status.HTTP_200_OK,
                                                     "Msg": "Your request has been approved!"})
                            else:
                                imei = make_password(imei_no)
                                print("this is my password: " + imei)
                                check = check_password(imei_no, imei)
                                print("this is my check password.")
                                print("First: %s" % check)
                                user = User.objects.create(username=imei_no, password=imei)
                                check1 = user.check_password(imei_no)
                                print("Second: %s" % check1)

                                token, created = Token.objects.get_or_create(user=user)
                                print("Token:" + token.key)
                                return Response({"token": token.key, "status": status.HTTP_200_OK,
                                                 "Msg": "Your request has been approved!"})
                        else:
                            return Response({"status": status.HTTP_400_BAD_REQUEST,
                                             "Msg": "Please select right branch"})

                    elif is_revoke is True:

                        device.update(branch=br1, device_make=make, device_model=model, device_imei_no=imei_no, device_is_revoke=False)

                        return Response({"status": status.HTTP_406_NOT_ACCEPTABLE,
                                         "Msg": "Your request has been sent"})
                    elif is_inactive is True:

                        return Response({"status": status.HTTP_406_NOT_ACCEPTABLE,
                                         "Msg": "Your Device has been deactivated"})
                    else:
                        return Response({"status": status.HTTP_403_FORBIDDEN,
                                         "Msg": "Your request is pending"})
                    # return Response({"status": status.HTTP_403_FORBIDDEN, "Msg": "The Device with this imei number already exists."})
                else:
                    Device.objects.create(branch=br1, device_make=make, device_model=model, device_imei_no=imei_no)

                    # imei = make_password(imei_no)
                    # print("this is my password: " + imei)
                    # check = check_password(imei_no, imei)
                    # print("this is my check password.")
                    # print("First: %s" % check)
                    # user = User.objects.create(username=imei_no, password=imei)
                    # check1 = user.check_password(imei_no)
                    # print("Second: %s" % check1)
                    #
                    # token, created = Token.objects.get_or_create(user=user)
                    # print("Token:" + token.key)

                    return Response({"status": status.HTTP_401_UNAUTHORIZED, "Msg": "Your request has been sent. Pending Request!"})

            except:
                logger.debug("Error while sending request")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Send Request"})
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST,
                                 "Msg": "Branch, Make, Model and Imei no are required to registration request."})



#for admin panel...
class DeviceRegisterRequestAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)
        devices =  Device.objects.all()

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin or request.user.is_active and request.user.is_branch_admin:

                    dev = []
                    for device in devices:
                        if device.device_is_active is False and device.device_is_revoke is False and device.device_is_inactive is False:
                            branch_id = device.branch.id
                            branch_name = device.branch.branch_name
                            make = device.device_make
                            model = device.device_model
                            imei = device.device_imei_no
                            time = device.created_at

                            result1 = {
                                "branch_id": branch_id,
                                "branch_name": branch_name,
                                "make": make,
                                "model": model,
                                "imei": imei,
                                "time_of_request": time
                                }

                            dev.append(result1)

                    return Response({"device_pending_requests": dev, "status":status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no Role is defined for this user"})
            except:
                logger.debug("Error while retrieving devices")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Devices"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

    def post(self, request):
        branch_id = request.POST.get('branch_id')
        make = request.POST.get('make')
        model = request.POST.get('model')
        imei = request.POST.get('imei')
        is_revoke = request.POST.get('is_revoke')
        print("is revoke %s" % is_revoke)

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        dev = Device.objects.filter(device_imei_no=imei)
        # dev_param = Q(device_imei_no=imei)
        # dev = Device.objects.filter(dev_param)

        for device in dev:
            is_active = device.device_is_active
            device_imei_no = device.device_imei_no
            # print(device_imei_no)
            # print(is_active)

        if user:
            try:
                # print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin or request.user.is_active and request.user.is_branch_admin:

                    if branch_id and make and model and imei and is_revoke:
                        print(device_imei_no)
                        print(is_active)
                        if is_revoke == 'False':
                            if is_active is False:
                                print("approved")
                                dev.update(branch=branch_id, device_make=make, device_model=model, device_imei_no=imei,
                                            device_is_active=True, device_is_revoke=is_revoke)

                                return Response({"status": status.HTTP_200_OK, "Msg": "Device has been approved."})
                            else:
                                print("already registered")
                                return Response({"status": status.HTTP_400_BAD_REQUEST,
                                                 "Msg": "Device is already registered"})

                        else:
                            dev.update(branch=branch_id, device_make=make, device_model=model,
                                                  device_imei_no=imei, device_is_active=False, device_is_revoke=is_revoke)
                            print("ignored")
                            return Response({"status": status.HTTP_200_OK, "Msg": "Device has been revoked."})
                    else:
                        return Response({"status": status.HTTP_404_NOT_FOUND,
                                         "Msg": "Must provide branch, make, model and imei. These are all required fields"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                 "Msg": "No Role is assigned to this user"})
            except:
                logger.debug("Error while accepting or ignoring request")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Accept or Ignore Request"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

#for admin panel
class RegisteredDeviceAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)
        branch_id = request.GET.get('branch_id')

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    if branch_id:
                        device = Device.objects.filter(branch=branch_id)
                        branch_id = device[0].branch.id
                        branch_name = device[0].branch.branch_name

                        revoke_count = 0
                        for count in device:
                            if count.device_is_revoke is True:
                                revoke_count = revoke_count + 1

                        branch_obj = { "branch_id": branch_id,
                                        "branch_name": branch_name,
                                       "revoke_count": revoke_count
                                       }
                        total_devices = device.count()
                        print('total_devices')
                        print(total_devices)

                        branch_params = Q(branch=branch_id)
                        branch_is_active_params = Q(device_is_active=True)
                        device = Device.objects.order_by("id").filter(branch_params & branch_is_active_params)

                        devvs = Paginator(device, 10)
                        page = request.GET.get('page')
                        # ques = quest.page(page)
                        print(page)

                        try:
                            devv = devvs.page(page)
                        except PageNotAnInteger:
                            devv = devvs.page(1)
                        except EmptyPage:
                            devv = devvs.page(devvs.num_pages)

                        has_next = devv.has_next()
                        if has_next is True:
                            next_page_number = devv.next_page_number()
                        else:
                            next_page_number = "There is no next page. This is the last page"
                        print(next_page_number)

                        has_previous = devv.has_previous()
                        if has_previous is True:
                            previous_page_number = devv.previous_page_number()
                        else:
                            previous_page_number = "There is no previous page. This is the first page"
                        print(previous_page_number)

                        devices = []
                        for dev in devv:
                            if dev.device_is_active is True:
                                device_id = dev.id
                                make = dev.device_make
                                model = dev.device_model
                                imei = dev.device_imei_no
                                device_last_check_in = dev.device_last_check_in
                                device_last_driver = dev.device_last_driver

                                if device_last_check_in is not None:
                                    s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                    print(s)
                                    tail = s[-4:]
                                    f = round(float(tail), 3)
                                    temp = "%.3f" % f
                                    print((s[:-4], temp[1:]))
                                    print(type(s[-4:]))
                                    date_time = s[:-4]
                                    print("datetime formate")
                                    print(date_time)
                                else:
                                    date_time = ""

                                result1 = {
                                    # "branch_id": branch_id,
                                    # "branch_name": branch_name,
                                    "device_id": device_id,
                                    "make": make,
                                    "model": model,
                                    "imei": imei,
                                    "device_last_check_in": date_time,
                                    "device_last_driver": device_last_driver

                                }

                                devices.append(result1)
                                temp = {"registered_devices": devices,
                                        "has_next": has_next,
                                        "has_previous": has_previous,
                                        "next_page_number": next_page_number,
                                        "previous_page_number": previous_page_number,
                                        "total_devices": total_devices,
                                        "status": status.HTTP_200_OK}
                                branch_obj.update(temp)
                        return Response(branch_obj)
                    else:
                        branches = Branch.objects.all()
                        response = []
                        for branch in branches:
                            if branch.branch_is_active is True:
                                branch_id = branch.id
                                branch_name = branch.branch_name
                                device = Device.objects.filter(branch=branch_id)
                                revoke_count = 0
                                for count in device:
                                    if count.device_is_revoke is True:
                                        revoke_count = revoke_count + 1

                                branch_obj = {
                                    "branch_id": branch_id,
                                    "branch_name": branch_name,
                                    "revoke_count": revoke_count
                                }

                                devices = []
                                for dev in device:
                                    if dev.device_is_active is True:
                                        # branch_id = dev.branch.id
                                        # branch_name = dev.branch.branch_name
                                        device_id = dev.id
                                        make = dev.device_make
                                        model = dev.device_model
                                        imei = dev.device_imei_no
                                        device_last_check_in = dev.device_last_check_in
                                        device_last_driver = dev.device_last_driver

                                        if device_last_check_in is not None:

                                            s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                            print(s)
                                            tail = s[-4:]
                                            f = round(float(tail), 3)
                                            temp = "%.3f" % f
                                            print((s[:-4], temp[1:]))
                                            print(type(s[-4:]))
                                            date_time = s[:-4]
                                            print("datetime formate")
                                            print(date_time)
                                        else:
                                            date_time = ""

                                        result1 = {
                                            # "branch_id": branch_id,
                                            # "branch_name": branch_name,
                                            "device_id":device_id,
                                            "make": make,
                                            "model": model,
                                            "imei": imei,
                                            "device_last_check_in": date_time,
                                            "device_last_driver": device_last_driver
                                        }

                                        devices.append(result1)
                                        temp = {
                                            "registered_devices":devices
                                        }
                                        branch_obj.update(temp)
                                        # org_obj.update(branch_obj)

                                response.append(branch_obj)


                        return Response({"branch": response, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    if branch_id:
                        device = Device.objects.filter(branch=branch_id)
                        branch_id = device[0].branch.id
                        branch_name = device[0].branch.branch_name
                        revoke_count = 0
                        for count in device:
                            if count.device_is_revoke is True:
                                revoke_count = revoke_count + 1

                        branch_obj = {"branch_id": branch_id,
                                      "branch_name": branch_name,
                                      "revoke_count": revoke_count
                                      }
                        total_devices = device.count()
                        print('total_devices')
                        print(total_devices)

                        branch_params = Q(branch=branch_id)
                        branch_is_active_params = Q(device_is_active=True)
                        device = Device.objects.order_by("id").filter(branch_params & branch_is_active_params)

                        devvs = Paginator(device, 10)
                        page = request.GET.get('page')
                        # ques = quest.page(page)
                        print(page)

                        try:
                            devv = devvs.page(page)
                        except PageNotAnInteger:
                            devv = devvs.page(1)
                        except EmptyPage:
                            devv = devvs.page(devvs.num_pages)

                        has_next = devv.has_next()
                        if has_next is True:
                            next_page_number = devv.next_page_number()
                        else:
                            next_page_number = "There is no next page. This is the last page"
                        print(next_page_number)

                        has_previous = devv.has_previous()
                        if has_previous is True:
                            previous_page_number = devv.previous_page_number()
                        else:
                            previous_page_number = "There is no previous page. This is the first page"
                        print(previous_page_number)

                        devices = []
                        for dev in devv:
                            if dev.device_is_active is True:
                                device_id = dev.id
                                make = dev.device_make
                                model = dev.device_model
                                imei = dev.device_imei_no
                                device_last_check_in = dev.device_last_check_in
                                device_last_driver = dev.device_last_driver

                                if device_last_check_in is not None:

                                    s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                    print(s)
                                    tail = s[-4:]
                                    f = round(float(tail), 3)
                                    temp = "%.3f" % f
                                    print((s[:-4], temp[1:]))
                                    print(type(s[-4:]))
                                    date_time = s[:-4]
                                    print("datetime formate")
                                    print(date_time)
                                else:
                                    date_time = ""

                                result1 = {
                                    # "branch_id": branch_id,
                                    # "branch_name": branch_name,
                                    "device_id": device_id,
                                    "make": make,
                                    "model": model,
                                    "imei": imei,
                                    "device_last_check_in": date_time,
                                    "device_last_driver": device_last_driver
                                }

                                devices.append(result1)
                                temp = {"registered_devices": devices,
                                        "has_next": has_next,
                                        "has_previous": has_previous,
                                        "next_page_number": next_page_number,
                                        "previous_page_number": previous_page_number,
                                        "total_devices": total_devices,
                                        "status": status.HTTP_200_OK}
                                branch_obj.update(temp)
                        return Response(branch_obj)
                    else:
                        print("otherwise")
                        orgadmin = OrganisationAdmins.objects.filter(user=user_id)
                        response = []
                        for org_obj in orgadmin:
                            org_id = org_obj.organisation.id
                            orgs = Organisation.objects.filter(pk=org_id)
                            print(orgs)
                            for orga in orgs:
                                if orga.organisation_is_active is True:
                                    org_id = orga.id
                                    branches = Branch.objects.filter(organisation=org_id)
                                    for branch in branches:
                                        if branch.branch_is_active is True:
                                            branch_id = branch.id
                                            branch_name = branch.branch_name
                                            device = Device.objects.filter(branch=branch_id)
                                            revoke_count = 0
                                            for count in device:
                                                if count.device_is_revoke is True:
                                                    revoke_count = revoke_count + 1

                                            branch_obj = {
                                                "branch_id": branch_id,
                                                "branch_name": branch_name,
                                                "revoke_count": revoke_count
                                            }
                                            devices = []
                                            for dev in device:
                                                if dev.device_is_active is True:
                                                    # branch_id = dev.branch.id
                                                    # branch_name = dev.branch.branch_name
                                                    device_id = dev.id
                                                    make = dev.device_make
                                                    model = dev.device_model
                                                    imei = dev.device_imei_no
                                                    device_last_check_in = dev.device_last_check_in
                                                    device_last_driver = dev.device_last_driver

                                                    if device_last_check_in is not None:
                                                        s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                                        print(s)
                                                        tail = s[-4:]
                                                        f = round(float(tail), 3)
                                                        temp = "%.3f" % f
                                                        print((s[:-4], temp[1:]))
                                                        print(type(s[-4:]))
                                                        date_time = s[:-4]
                                                        print("datetime formate")
                                                        print(date_time)
                                                    else:
                                                        date_time = ""

                                                    result1 = {
                                                        # "branch_id": branch_id,
                                                        # "branch_name": branch_name,
                                                        "device_id": device_id,
                                                        "make": make,
                                                        "model": model,
                                                        "imei": imei,
                                                        "device_last_check_in": date_time,
                                                        "device_last_driver": device_last_driver
                                                    }

                                                    devices.append(result1)
                                                    temp = {
                                                        "registered_devices": devices
                                                    }
                                                    branch_obj.update(temp)

                                            response.append(branch_obj)

                        return Response({"branch": response, "status": status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_branch_admin:
                    if branch_id:
                        device = Device.objects.filter(branch=branch_id)
                        branch_id = device[0].branch.id
                        branch_name = device[0].branch.branch_name
                        revoke_count = 0
                        for count in device:
                            if count.device_is_revoke is True:
                                revoke_count = revoke_count + 1

                        branch_obj = {"branch_id": branch_id,
                                      "branch_name": branch_name,
                                      "revoke_count": revoke_count
                                      }
                        total_devices = device.count()
                        print('total_devices')
                        print(total_devices)

                        branch_params = Q(branch=branch_id)
                        branch_is_active_params = Q(device_is_active=True)
                        device = Device.objects.order_by("id").filter(branch_params & branch_is_active_params)

                        devvs = Paginator(device, 10)
                        page = request.GET.get('page')
                        # ques = quest.page(page)
                        print(page)

                        try:
                            devv = devvs.page(page)
                        except PageNotAnInteger:
                            devv = devvs.page(1)
                        except EmptyPage:
                            devv = devvs.page(devvs.num_pages)

                        has_next = devv.has_next()
                        if has_next is True:
                            next_page_number = devv.next_page_number()
                        else:
                            next_page_number = "There is no next page. This is the last page"
                        print(next_page_number)

                        has_previous = devv.has_previous()
                        if has_previous is True:
                            previous_page_number = devv.previous_page_number()
                        else:
                            previous_page_number = "There is no previous page. This is the first page"
                        print(previous_page_number)

                        devices = []
                        for dev in devv:
                            if dev.device_is_active is True:
                                device_id = dev.id
                                make = dev.device_make
                                model = dev.device_model
                                imei = dev.device_imei_no
                                device_last_check_in = dev.device_last_check_in
                                device_last_driver = dev.device_last_driver

                                if device_last_check_in is not None:
                                    s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                    print(s)
                                    tail = s[-4:]
                                    f = round(float(tail), 3)
                                    temp = "%.3f" % f
                                    print((s[:-4], temp[1:]))
                                    print(type(s[-4:]))
                                    date_time = s[:-4]
                                    print("datetime formate")
                                    print(date_time)
                                else:
                                    date_time = ""

                                result1 = {
                                    # "branch_id": branch_id,
                                    # "branch_name": branch_name,
                                    "device_id": device_id,
                                    "make": make,
                                    "model": model,
                                    "imei": imei,
                                    "device_last_check_in": date_time,
                                    "device_last_driver": device_last_driver
                                }

                                devices.append(result1)
                                temp = {"registered_devices": devices,
                                        "has_next": has_next,
                                        "has_previous": has_previous,
                                        "next_page_number": next_page_number,
                                        "previous_page_number": previous_page_number,
                                        "total_devices": total_devices,
                                        "status": status.HTTP_200_OK}
                                branch_obj.update(temp)
                        return Response(branch_obj)
                    else:
                        branchadmin = BranchAdmins.objects.filter(user=user_id)
                        response = []
                        for branch_obj in branchadmin:
                            branch_id = branch_obj.branch.id
                            branches = Branch.objects.filter(pk=branch_id)
                            print(branches)
                            for b in branches:
                                if b.branch_is_active is True:
                                    branch_id = b.id
                                    branch_name = b.branch_name
                                    device = Device.objects.filter(branch=branch_id)
                                    revoke_count = 0
                                    for count in device:
                                        if count.device_is_revoke is True:
                                            revoke_count = revoke_count + 1

                                    branch_obj = {
                                        "branch_id": branch_id,
                                        "branch_name": branch_name,
                                        "revoke_count": revoke_count
                                    }

                                    device = Device.objects.filter(branch=branch_id)
                                    devices = []
                                    for dev in device:
                                        if dev.device_is_active is True:
                                            device_id = dev.id
                                            make = dev.device_make
                                            model = dev.device_model
                                            imei = dev.device_imei_no
                                            device_last_check_in = dev.device_last_check_in
                                            device_last_driver = dev.device_last_driver

                                            if device_last_check_in is not None:
                                                s = device_last_check_in.strftime('%Y-%m-%d %H:%M:%S.%f')
                                                print(s)
                                                tail = s[-4:]
                                                f = round(float(tail), 3)
                                                temp = "%.3f" % f
                                                print((s[:-4], temp[1:]))
                                                print(type(s[-4:]))
                                                date_time = s[:-4]
                                                print("datetime formate")
                                                print(date_time)
                                            else:
                                                date_time = ""

                                            result1 = {
                                                "device_id": device_id,
                                                "make": make,
                                                "model": model,
                                                "imei": imei,
                                                "device_last_check_in": date_time,
                                                "device_last_driver": device_last_driver
                                            }

                                            devices.append(result1)
                                            temp = {
                                                "registered_devices": devices
                                            }
                                            branch_obj.update(temp)

                                    response.append(branch_obj)

                    return Response({"branch": response, "status": status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no role is assigned to this user"})
            except:
                logger.debug("Error while retrieving devices")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Devices"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

    def put(self, request):
        device_id = request.POST.get('device_id')

        user_id = request.GET.get('user_id')
        user = User.objects\
            .filter(pk=user_id)

        dev = Device.objects.filter(pk=device_id)

        for device in dev:
            is_active = device.device_is_active
            # is_revoke = device.device_is_revoke

        if user:
            try:
                # print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin or request.user.is_active and request.user.is_branch_admin:

                    if device_id:
                        if is_active is True:
                            print("approved")
                            dev.update(device_is_active=False, device_is_revoke=True)

                            return Response({"status": status.HTTP_200_OK, "Msg": "Device has been revoked."})
                        else:
                            print("already revoked")
                            return Response({"status": status.HTTP_400_BAD_REQUEST,
                                             "Msg": "Device is already revoked"})
                    else:
                        return Response({"status": status.HTTP_404_NOT_FOUND,
                                         "Msg": "Parameters missing"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                 "Msg": "No Role is assigned to this user"})
            except:
                logger.debug("Error while revoking request")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Revoke Request"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})


#for admin panel
class RevokedDeviceAPIView(APIView):
    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)
        # print(user_id)
        # print(user)
        branch_id = request.GET.get('branch_id')

        if user:
            try:
                print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser:
                    if branch_id:
                        device = Device.objects.filter(branch=branch_id)
                        branch_id = device[0].branch.id
                        branch_name = device[0].branch.branch_name
                        branch_obj = { "branch_id": branch_id,
                                        "branch_name": branch_name
                                       }
                        devices = []
                        for dev in device:
                            if dev.device_is_revoke is True:
                                device_id = dev.id
                                make = dev.device_make
                                model = dev.device_model
                                imei = dev.device_imei_no
                                time = dev.created_at
                                result1 = {
                                    # "branch_id": branch_id,
                                    # "branch_name": branch_name,
                                    "device_id": device_id,
                                    "make": make,
                                    "model": model,
                                    "imei": imei,
                                    "time_of_request": time
                                }

                                devices.append(result1)
                                temp = {"revoked_devices": devices,
                                        "status": status.HTTP_200_OK}
                                branch_obj.update(temp)
                        return Response(branch_obj)
                    else:
                        branches = Branch.objects.all()
                        response = []
                        for branch in branches:
                            if branch.branch_is_active is True:
                                branch_id = branch.id
                                branch_name = branch.branch_name
                                branch_obj = {
                                    "branch_id": branch_id,
                                    "branch_name": branch_name,
                                }
                                device = Device.objects.filter(branch=branch_id)
                                devices = []
                                for dev in device:
                                    if dev.device_is_revoke is True:
                                        # branch_id = dev.branch.id
                                        # branch_name = dev.branch.branch_name
                                        device_id = dev.id
                                        make = dev.device_make
                                        model = dev.device_model
                                        imei = dev.device_imei_no
                                        time = dev.created_at

                                        result1 = {
                                            # "branch_id": branch_id,
                                            # "branch_name": branch_name,
                                            "device_id" : device_id,
                                            "make": make,
                                            "model": model,
                                            "imei": imei,
                                            "time_of_request": time
                                        }

                                        devices.append(result1)
                                        temp = {
                                            "revoked_devices":devices
                                        }
                                        branch_obj.update(temp)
                                        # org_obj.update(branch_obj)

                                response.append(branch_obj)


                        return Response({"branch": response, "status":status.HTTP_200_OK})

                elif request.user.is_active and request.user.is_organisation_admin:
                    if branch_id:
                        device = Device.objects.filter(branch=branch_id)
                        branch_id = device[0].branch.id
                        branch_name = device[0].branch.branch_name
                        branch_obj = { "branch_id": branch_id,
                                        "branch_name": branch_name
                                       }
                        devices = []
                        for dev in device:
                            if dev.device_is_revoke is True:
                                device_id = dev.id
                                make = dev.device_make
                                model = dev.device_model
                                imei = dev.device_imei_no
                                time = dev.created_at
                                result1 = {
                                    # "branch_id": branch_id,
                                    # "branch_name": branch_name,
                                    "device_id": device_id,
                                    "make": make,
                                    "model": model,
                                    "imei": imei,
                                    "time_of_request": time
                                }

                                devices.append(result1)
                                temp = {"revoked_devices": devices,
                                        "status": status.HTTP_200_OK}
                                branch_obj.update(temp)
                        return Response(branch_obj)
                    else:
                        print("otherwise")
                        orgadmin = OrganisationAdmins.objects.filter(user=user_id)
                        response = []
                        for org_obj in orgadmin:
                            org_id = org_obj.organisation.id
                            orgs = Organisation.objects.filter(pk=org_id)
                            print(orgs)
                            for orga in orgs:
                                if orga.organisation_is_active is True:
                                    org_id = orga.id
                                    branches = Branch.objects.filter(organisation=org_id)
                                    for branch in branches:
                                        if branch.branch_is_active is True:
                                            branch_id = branch.id
                                            branch_name = branch.branch_name
                                            branch_obj = {
                                                "branch_id": branch_id,
                                                "branch_name": branch_name,
                                            }
                                            device = Device.objects.filter(branch=branch_id)
                                            devices = []
                                            for dev in device:
                                                if dev.device_is_revoke is True:
                                                    # branch_id = dev.branch.id
                                                    # branch_name = dev.branch.branch_name
                                                    device_id = dev.id
                                                    make = dev.device_make
                                                    model = dev.device_model
                                                    imei = dev.device_imei_no
                                                    time = dev.created_at

                                                    result1 = {
                                                        # "branch_id": branch_id,
                                                        # "branch_name": branch_name,
                                                        "device_id" : device_id,
                                                        "make": make,
                                                        "model": model,
                                                        "imei": imei,
                                                        "time_of_request": time
                                                    }

                                                    devices.append(result1)
                                                    temp = {
                                                        "revoked_devices": devices
                                                    }
                                                    branch_obj.update(temp)

                                            response.append(branch_obj)

                        return Response({"branch": response, "status": status.HTTP_200_OK})
                elif request.user.is_active and request.user.is_branch_admin:
                    if branch_id:
                        device = Device.objects.filter(branch=branch_id)
                        branch_id = device[0].branch.id
                        branch_name = device[0].branch.branch_name
                        branch_obj = { "branch_id": branch_id,
                                        "branch_name": branch_name
                                       }
                        devices = []
                        for dev in device:
                            if dev.device_is_revoke is True:
                                device_id = dev.id
                                make = dev.device_make
                                model = dev.device_model
                                imei = dev.device_imei_no
                                time = dev.created_at
                                result1 = {
                                    # "branch_id": branch_id,
                                    # "branch_name": branch_name,
                                    "device_id": device_id,
                                    "make": make,
                                    "model": model,
                                    "imei": imei,
                                    "time_of_request": time
                                }

                                devices.append(result1)
                                temp = {"revoked_devices": devices,
                                        "status": status.HTTP_200_OK}
                                branch_obj.update(temp)
                        return Response(branch_obj)
                    else:
                        branchadmin = BranchAdmins.objects.filter(user=user_id)
                        response = []
                        for branch_obj in branchadmin:
                            branch_id = branch_obj.branch.id
                            branches = Branch.objects.filter(pk=branch_id)
                            print(branches)
                            for b in branches:
                                if b.branch_is_active is True:
                                    branch_id = b.id
                                    branch_name = b.branch_name

                                    branch_obj ={"branch_id": branch_id,
                                                 "branch_name": branch_name}

                                    device = Device.objects.filter(branch=branch_id)
                                    devices = []
                                    for dev in device:
                                        if dev.device_is_revoke is True:
                                            device_id = dev.id
                                            make = dev.device_make
                                            model = dev.device_model
                                            imei = dev.device_imei_no
                                            time = dev.created_at

                                            result1 = {
                                                "device_id" : device_id,
                                                "make": make,
                                                "model": model,
                                                "imei": imei,
                                                "time_of_request": time
                                            }

                                            devices.append(result1)
                                            temp = {
                                                "revoked_devices": devices
                                            }
                                            branch_obj.update(temp)

                                    response.append(branch_obj)

                    return Response({"branch": response, "status": status.HTTP_200_OK})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                     "Msg": "no role is assigned to this user"})
            except:
                logger.debug("Error while retrieving devices")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Retrieve Devices"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

    def put(self, request):
        device_id = request.POST.get('device_id')

        user_id = request.GET.get('user_id')
        user = User.objects.filter(pk=user_id)

        dev = Device.objects.filter(pk=device_id)

        for device in dev:
            is_revoke = device.device_is_revoke
            # is_active = device.device_is_active

        if user:
            try:
                # print(request.user.is_superuser)
                if request.user.is_active and request.user.is_superuser or request.user.is_active and request.user.is_organisation_admin or request.user.is_active and request.user.is_branch_admin:

                    if device_id:
                        if is_revoke is True:
                            print("revoked")
                            dev.update(device_is_active=True, device_is_revoke=False)

                            return Response({"status": status.HTTP_200_OK, "Msg": "Device has been registered."})
                        else:
                            print("already registered")
                            return Response({"status": status.HTTP_400_BAD_REQUEST,
                                             "Msg": "Device is already registered"})
                    else:
                        return Response({"status": status.HTTP_404_NOT_FOUND,
                                         "Msg": "Parameters missing"})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND,
                                 "Msg": "No Role is assigned to this user"})
            except:
                logger.debug("Error while registering request")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not register Request"})
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND,
                             "Msg": "not user"})

#for android...
class DriverListAPIView(APIView):

    authentication_classes = (rest_framework.authentication.TokenAuthentication,)
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        imei = request.GET.get('imei')
        # password_imei = imei
        device = Device.objects.filter(device_imei_no=imei)
        branch_api_server_ip = device[0].branch.branch_api_server_ip
        for dev in device:
            is_active = dev.device_is_active
            is_revoke = dev.device_is_revoke
        if device:
            print(imei)
            if branch_api_server_ip is not None:
                try:
                    print(device)
                    if is_active is True:
                        # request.session['imei'] = imei
                        # print("IMEI NO STORED:" + request.session['imei'])
                        data = {
                            "device_id": "1234567892",
                            "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie"
                        }
                        # or we can write it like data = json.dumps(data)
                        response1 = requests.post('http://'+branch_api_server_ip+':80/KJWeb/transport/api/get_driver_list.php',
                                                 json=data)
                        print('response type', response1)
                        response = response1.json()
                        # user = User.objects.filter(username=imei)
                        # print('logging in')
                        # print(user)
                        # if user:
                        #     print(user)
                        #     check1 = user[0].check_password(password_imei)
                        #     print("Second: %s" % check1)
                        #     if user[0].check_password(password_imei):
                        #         print(user[0])
                        #         print(user[0].check_password(password_imei))
                        #
                        #         token, created = Token.objects.get_or_create(user=user[0])
                        #         print("Token:" + token.key)
                        #
                        #         device_token = {"token": token.key}
                        #         response.update(device_token)
                        temp ={'status': status.HTTP_200_OK}
                        response.update(temp)

                        return Response(response)
                    elif is_active is False and is_revoke is True:

                        return Response({"status": status.HTTP_406_NOT_ACCEPTABLE,
                                         "Msg": "Your request has been revoked"})

                    else:
                        return Response({"status": status.HTTP_403_FORBIDDEN,
                                         "Msg": "Your device has been revoked"})
                except:
                    logger.debug("Error while getting driver list")
                    print(traceback.format_exc())
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not get driver list"})
            else:
                return Response({"status": status.HTTP_204_NO_CONTENT, "Msg": "No api is found regarding this branch"})
        else:
            return Response({"status": status.HTTP_401_UNAUTHORIZED,
                             "Msg": "Your device has been revoked"})

class TestAPIView(APIView):

    def get(self, request):
        # photos = Photo.objects.order_by("created_at").all()
        # try:
        #     ftp = ftplib.FTP("61.69.119.183")
        #     print(ftp)
        #     ftp.login("photos", "ahJaeLeiseu8ie")
        #     print(ftp.login("photos", "ahJaeLeiseu8ie"))
        #     logger.debug("logging in")
        #     res = ftp.pwd()
        #     print(res)
        #
        #     res = ftp.cwd('/test')
        #     ftp.mkd(str(id))
        #     ftp.cwd('/test/'+str(id))
        #     res = ftp.pwd()
        #     print(res)
        #     return Response({"status": "ni lagy"})
        # except:
        #     print(traceback.format_exc())
        #     return Response({"status": "lag gy"})

        photos = Photo.objects.order_by("created_at").all()
        try:
            ftp = ftplib.FTP("61.69.119.183")
            print(ftp)
            ftp.login("photos", "ahJaeLeiseu8ie")
            print(ftp.login("photos", "ahJaeLeiseu8ie"))
            logger.debug("logging in")
            ftp.pwd()
            print(ftp.pwd())
            ftp.set_pasv(False)
            res = ftp.nlst()
            print(res)

            folderName1 = 'DeliveryTrackingSystem'
            if folderName1 in ftp.nlst():
                print('YES')
                ftp.cwd('/DeliveryTrackingSystem')
                ftp.pwd()
            else:
                print("No")
                ftp.mkd('DeliveryTrackingSystem')
                ftp.cwd('/DeliveryTrackingSystem')
                ftp.pwd()
        #     return Response({"status": "ni lagy"})
        # except:
        #     print(traceback.format_exc())
        #     return Response({"status": "lag gy"})

            try:
                for photo in photos:
                    if photo.is_uploaded is False:
                        photo_id = photo.id
                        run_id = photo.run_id
                        run_id = int(run_id)
                        print(run_id)
                        run_id = str(run_id)
                        print(run_id)
                        drop_id = photo.drop_id
                        f = str(photo.file)
                        f = f.split("/")
                        filename = f[1]
                        print(filename)
                        # cwd = os.getcwd()
                        # print(cwd)
                        folderName2 = run_id
                        if folderName2 in ftp.nlst():
                            print("yes it is")
                            ftp.cwd(run_id)
                            print(ftp.pwd())

                            folderName3 = drop_id
                            if folderName3 in ftp.nlst():
                                print("yes it is drop")
                                ftp.cwd(drop_id)
                                print(ftp.pwd())
                                print("uploading uploading")
                                myfile = open("media\Docs\\"+filename, 'rb')
                                print(myfile)
                                print("opening")
                                logger.debug("creating directory")
                                success = ftp.storbinary('STOR ' + filename, myfile)
                                if success == "226 Transfer complete":
                                    uploaded_photo = Photo.objects.filter(pk=photo_id)
                                    uploaded_photo.update(is_uploaded=True)
                                    logger.debug("file uploaded suucessfuly")
                                    print("file uploaded suucessfuly")
                                else:
                                    continue
                                myfile.close()
                                print("closing")
                                logger.debug("closing")
                            else:
                                print("No it is not drop")
                                ftp.mkd(drop_id)
                                ftp.cwd(drop_id)
                                print(ftp.pwd())
                                print("uploading uploading")
                                myfile = open("media\Docs\\" + filename, 'rb')
                                print(myfile)
                                print("opening")
                                logger.debug("creating directory")
                                success = ftp.storbinary('STOR ' + filename, myfile)
                                if success == "226 Transfer complete":
                                    uploaded_photo = Photo.objects.filter(pk=photo_id)
                                    uploaded_photo.update(is_uploaded=True)
                                    logger.debug("file uploaded suucessfuly")
                                    print("file uploaded suucessfuly")
                                else:
                                    continue
                                myfile.close()
                                print("closing")
                                logger.debug("closing")

                        else:
                            print("No it is not")
                            ftp.mkd(run_id)
                            ftp.cwd(run_id)
                            print(ftp.pwd())

                            folderName4 = drop_id
                            if folderName4 in ftp.nlst():
                                print("yes it is drop")
                                ftp.cwd(drop_id)
                                print(ftp.pwd())
                                print("uploading uploading")
                                myfile = open("media\Docs\\" + filename, 'rb')
                                print(myfile)
                                print("opening")
                                logger.debug("creating directory")
                                success = ftp.storbinary('STOR ' + filename, myfile)
                                if success == "226 Transfer complete":
                                    uploaded_photo = Photo.objects.filter(pk=photo_id)
                                    uploaded_photo.update(is_uploaded=True)
                                    logger.debug("file uploaded suucessfuly")
                                    print("file uploaded suucessfuly")
                                else:
                                    continue
                                myfile.close()
                                print("closing")
                                logger.debug("closing")
                            else:
                                print("No it is not drop")
                                ftp.mkd(drop_id)
                                ftp.cwd(drop_id)
                                print(ftp.pwd())
                                print("uploading uploading")
                                myfile = open("media\Docs\\" + filename, 'rb')
                                print(myfile)
                                print("opening")
                                logger.debug("creating directory")
                                success = ftp.storbinary('STOR ' + filename, myfile)
                                if success == "226 Transfer complete":
                                    uploaded_photo = Photo.objects.filter(pk=photo_id)
                                    uploaded_photo.update(is_uploaded=True)
                                    logger.debug("file uploaded suucessfuly")
                                    print("file uploaded suucessfuly")
                                else:
                                    continue
                                myfile.close()
                                print("closing")
                                logger.debug("closing")
                ftp.quit()
                print("quitting")
                return Response({"Msg": "Photo Data is uploaded"})

            except:
                logger.debug("Error while uploading data")
                print(traceback.format_exc())
                return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Upload Data"})
        except:
            logger.debug("Error while connecting to ftp server")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Connect FTP Server"})

class bulkQuestionAPIView(APIView):

    def post(self, request):
        section = QuestionSection.objects.all()
        q_type = QuestionType.objects.all()
        qfa = QuestionFalseAction.objects.all()
        qta = QuestionTrueAction.objects.all()

        # i = 0
        # j = 0
        # k = 0
        # l = 0
        q = 1000
        r = 123456789
        d = 987654321
        # sec1 = "before departure"
        # sec2 = "return to base"
        # sec3 = "Unknown"
        # sec4 = "SalesOrder"
        # sec5 = "PickUp"
        # sec6 = "Break"
        # sec7 = "Note"
        # sec8 = "ManualEntry"

        # s = 1
        a = 0

        while True:
            # Question.objects.all().delete()
            # break
            # if i>7:
            #     i=0
            # if j > 5:
            #     j = 0
            # # if k > 158:
            # #     k = 0
            # # if l > 143:
            # #     l = 0
            # Question.objects.create(customer_code='', question_sequence=35, question_section=section[i], question_type=q_type[j],
            #                         question_text="First bulk create", question_false_action=qfa[0],
            #                         question_true_action=qta[0])
            print("running")
            # i = i + 1
            # j = j + 1
            # k = k + 1
            # l = l + 1
            # print("i"+str(i))
            # print("j"+str(j))
            # print("k"+str(k))
            # print("l"+str(l))
            #
            # if s > 8:
            #     s = 1

            if a > 1:
                a = 0

            QuestionResponse.objects.create(q_id=q, run_id=r, drop_id=d,
                                            question_section="PickUp",
                                            question_text="Responses bulk create", question_answer=a)

            q = q + 1
            r = r + 1
            d = d - 1
            # s = s + 1
            a = a + 1
            print("responses creating")

        # return Response({"status": status.HTTP_200_OK, "Msg": "Question has been created successfully."})

# class QuestionWizardSequenceAPIView(APIView):
#
#     authentication_classes = (rest_framework.authentication.TokenAuthentication,)
#     permission_classes = (rest_framework.permissions.IsAuthenticated,)
#
#     def get(self, request):
#         user_id = request.GET.get('user_id')
#         user = User.objects.filter(pk=user_id)
#         # print(user_id)
#         # print(user)
#         section_id = request.GET.get('section_id')
#         question_section = Question.objects.filter(question_section=section_id)
#         print("i need this" + str(question_section))
#
#         org_id = request.GET.get('org_id')
#         branch_id = request.GET.get('branch_id')
#         customer_code = request.GET.get('customer_code')
#         # print('-----------------')
#         # print(question_section)
#         # print('-----------------')
#
#         if user and question_section:
#             print(request.user.is_superuser)
#             if request.user.is_active and request.user.is_superuser:
#                 orgs = Question.objects.order_by("question_sequence").filter(organisation=org_id)
#                 branches = Question.objects.order_by("question_sequence").filter(branch=branch_id)
#                 customer_codes = Question.objects.order_by("question_sequence").filter(customer_code=customer_code)
#
#                 if orgs and not branches and not customer_codes:
#                     print("1")
#                     br = Question.objects.order_by("question_sequence").filter(branch="")
#                     cuco = Question.objects.order_by("question_sequence").filter(customer_code="")
#                     sequences = []
#                     if br and cuco:
#                         for org in orgs:
#                             sequence = org.question_sequence
#
#                             type = org.question_type.question_type
#
#                             text = org.question_text
#
#                             result1 = {
#                                 "sequence": sequence,
#                                 "type": type,
#                                 "text": text
#                             }
#
#                             sequences.append(result1)
#
#                 elif orgs and branches and not customer_codes:
#                     print("2")
#                     print(branches)
#                     cuco = Question.objects.order_by("question_sequence").filter(customer_code="")
#                     sequences = []
#                     if cuco:
#                         for branch in branches:
#                             sequence = branch.question_sequence
#
#                             type = branch.question_type.question_type
#
#                             text = branch.question_text
#
#                             result1 = {
#                                 "sequence": sequence,
#                                 "type": type,
#                                 "text": text
#                             }
#
#                             sequences.append(result1)
#
#                 elif orgs and branches and customer_codes:
#                     print("3")
#                     print(branches)
#                     sequences = []
#                     for customer_code in customer_codes:
#                         sequence = customer_code.question_sequence
#
#                         type = customer_code.question_type.question_type
#
#                         text = customer_code.question_text
#
#                         result1 = {
#                             "sequence": sequence,
#                             "type": type,
#                             "text": text
#
#                         }
#
#                         sequences.append(result1)
#
#                 elif orgs and not branches and customer_codes:
#                     print("4")
#                     br = Question.objects.order_by("question_sequence").filter(branch="")
#                     print(customer_codes)
#                     sequences = []
#                     if br:
#                         for customer_code in customer_codes:
#                             sequence = customer_code.question_sequence
#
#                             type = customer_code.question_type.question_type
#
#                             text = customer_code.question_text
#
#                             result1 = {
#                                 "sequence": sequence,
#                                 "type": type,
#                                 "text": text
#                             }
#
#                             sequences.append(result1)
#
#                 elif not orgs and branches and not customer_codes:
#                     print("5")
#                     orga = Question.objects.order_by("question_sequence").filter(organisation="")
#                     cuco = Question.objects.filter(customer_code="")
#                     print(branches)
#                     sequences = []
#                     if orga and cuco:
#                         for branch in branches:
#                             sequence = branch.question_sequence
#
#                             type = branch.question_type.question_type
#
#                             text = branch.question_text
#
#                             result1 = {
#                                 "sequence": sequence,
#                                 "type": type,
#                                 "text": text
#                             }
#
#                             sequences.append(result1)
#
#                 elif not orgs and not branches and customer_codes:
#                     print("6")
#                     orga = Question.objects.order_by("question_sequence").filter(organisation="")
#                     br = Question.objects.filter(branch="")
#                     print(customer_codes)
#                     sequences = []
#                     if orga and br:
#                         for customer_code in customer_codes:
#                             sequence = customer_code.question_sequence
#
#                             type = customer_code.question_type.question_type
#
#                             text = customer_code.question_text
#
#                             result1 = {
#                                 "sequence": sequence,
#                                 "type": type,
#                                 "text": text
#                             }
#
#                             sequences.append(result1)
#
#                 elif not orgs and branches and customer_codes:
#                     print("7")
#                     orga = Question.objects.order_by("question_sequence").filter(organisation="")
#                     print(customer_codes)
#                     sequences = []
#                     if orga:
#                         for customer_code in customer_codes:
#                             sequence = customer_code.question_sequence
#
#                             type = customer_code.question_type.question_type
#
#                             text = customer_code.question_text
#
#                             result1 = {
#                                 "sequence": sequence,
#                                 "type": type,
#                                 "text": text
#                             }
#
#                             sequences.append(result1)
#
#                 else:
#                     print("8")
#                     orga = Question.objects.order_by("question_sequence").filter(organisation = "")
#                     br= Question.objects.order_by("question_sequence").filter(branch="")
#                     cuco = Question.objects.order_by("question_sequence").filter(customer_code="")
#                     print(cuco)
#                     sequences = []
#
#                     for customer_code in cuco:
#                         # if question_section == customer_code.question_section.id:
#                         if orga and br and cuco:
#                             print("checking.." + question_section)
#                             sequence = customer_code.question_sequence
#
#                             type = customer_code.question_type.question_type
#
#                             text = customer_code.question_text
#
#                             result1 = {
#                                 "sequence": sequence,
#                                 "type": type,
#                                 "text": text
#                             }
#
#                             sequences.append(result1)
#
#                 return Response({"sequences": sequences, "status":status.HTTP_200_OK})
#             else:
#                 return Response({"status": status.HTTP_404_NOT_FOUND,
#                                  "Msg": "not super"})
#         else:
#             return Response({"status": status.HTTP_404_NOT_FOUND,
#                              "Msg": "not user"})