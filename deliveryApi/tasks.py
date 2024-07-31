# from __future__ import absolute_import
# 
# from celery import shared_task
# 
# @shared_task
# def test(param):
#     return 'The test task executed with argument "%s" ' % param

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from datetime import datetime
from .models import *
import logging
logger = logging.getLogger(__name__)
import traceback
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import ftplib
import os



@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="task_upload_answers",
    ignore_result=True
)
def task_upload_answers():
    """
    upload answers of questions
    """
    answers = QuestionResponse.objects.order_by("created_at").all()
    for answer in answers:
        try:
            if answer.is_not_uploaded is True:
                logger.info("Ready to Uploaded")
                run_id = answer.run_id
                drop_id = answer.drop_id
                # if drop_id is "0":
                #     drop_id = ""
                question_section = answer.question_section
                question_text = answer.question_text
                question_answer = answer.question_answer
                question_answer = "TRUE" if question_answer == True else "FALSE"
                # if question_answer is None:
                #     question_answer = ""
                print(question_answer)
                question_data = answer.question_data
                if question_data is None:
                    question_data = ""

                if drop_id is not "0" and question_answer is not None:
                    logger.debug("no none")
                    data = {
                        "authentication": {"device_id": "1234567892",
                                           "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
                        "run_id": run_id,
                        "drop_id": drop_id,
                        "question_section": question_section,
                        "question_text": question_text,
                        "question_answer": question_answer,
                        "question_data": question_data,
                    }
                    # or we can write it like data = json.dumps(data)
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
                                              json=data)

                elif drop_id is not "0" and question_answer is None:
                    logger.debug("drop no none")
                    data = {
                        "authentication": {"device_id": "1234567892",
                                           "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
                        "run_id": run_id,
                        "drop_id": drop_id,
                        "question_section": question_section,
                        "question_text": question_text,
                        "question_data": question_data,
                    }
                    # or we can write it like data = json.dumps(data)
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
                                              json=data)

                elif drop_id is "0" and question_answer is not None:
                    logger.debug("drop none")
                    print("runnning")
                    data = {
                        "authentication": {
                            "device_id": "1234567892",
                            "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie"
                        },
                        "run_id": run_id,
                        # "drop_id": "348220",
                        "question_section": question_section,
                        "question_text": question_text,
                        "question_answer": question_answer,
                        "question_data": question_data,
                        # "run_id": "1002",
                        # "drop_id": "348220",
                        # "question_section": "Before_Departure",
                        # "question_text": "Do you have all the pieces?",
                        # "question_answer": "TRUE",
                        # "question_data": ""
                    }
                    # or we can write it like data = json.dumps(data)
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
                                              json=data)
                    print("check this")
                    print(response1.json())

                else:
                    logger.debug("all none")
                    data = {
                        "authentication": {"device_id": "1234567892",
                                           "device_key": "hahcusa4queefa2taeghahhaigoRae7ul1chohxaesie", },
                        "run_id": run_id,
                        "question_section": question_section,
                        "question_text": question_text,
                        "question_data": question_data,
                    }
                    # or we can write it like data = json.dumps(data)
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_run_answers.php',
                                              json=data)

                print(response1)
                print("ok")
                response = response1.json()
                print(response)
                # if response['id'] and response['log_date_time']:
                if response:
                    if response['id'] and response['log_date_time']:
                        print("if part")
                        answer_id = answer.id
                        print("This is id")
                        print(answer_id)
                        answer_sent = QuestionResponse.objects.filter(pk=answer_id)
                        answer_sent.update(is_not_uploaded=False)
                        answer_sent.update(is_uploaded=True)
                        logger.debug("Uploaded Logs Data")
                    elif response['error']:
                        logger.debug("continue")
                        print("else error part")
                        continue
                    else:
                        print("else part")
                        logger.debug("All Data is uploaded")
                        return Response({"Msg": "All Data is uploaded"})
        except:
            logger.debug("Error while uploading answers data")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Upload Answer Data"})

    logs = QuestionLog.objects.order_by("created_at").all()
    for log in logs:
        try:
            if log.is_not_uploaded is True:
                logger.debug("Data is reday to uploaded")
                run_id = log.run_id
                drop_id = log.drop_id
                log_date_time = log.log_date_time

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
                    logger.debug("no none")
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
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_log_entry.php',
                                              json=data)

                elif drop_id is not "0" and status_old is None and status_new is None:
                    logger.debug("drop no none")
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
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_log_entry.php',
                                              json=data)

                elif drop_id is "0" and status_old is not None and status_new is not None:
                    logger.debug("drop none")
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
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_log_entry.php',
                                              json=data)
                    print("check this")
                    print(response1.json())

                else:
                    logger.debug("all none")
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
                    response1 = requests.post('http://61.69.119.183:80/KJWeb/transport/api/add_log_entry.php',
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
                        logger.debug("Uploaded Logs Data")
                    elif response['error']:
                        logger.debug("continue")
                        print("else error part")
                        continue
                    else:
                        logger.debug("All Data is uploaded")
                        print("else part")
                        return Response({"Msg": "All Data is uploaded"})
            # else:
            #     return Response({"Msg": "All Data is uploaded to runsheet"})

        except:
            logger.debug("Error while uploading logs data")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Upload Logs Data"})
    logger.debug("end of the game")
    return Response({"Msg": "Data is uploaded"})
    # upload_answers()
    # logger.debug("Uploaded Data")

@periodic_task(
    run_every=(crontab(hour='*/72')),
    name="task_delete_logs",
    ignore_result=True
)
def task_delete_logs():
    """
    Saves latest image from Flickr
    """
    logs = QuestionLog.objects.order_by("created_at").all()
    for log in logs:
        try:
            if log.is_uploaded is True:
                log_id = log.id
                log_obj = QuestionLog.objects.filter(pk=log_id)
                log_obj[0].delete()
        except:
            logger.debug("Error while deleting logs data")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Delete Logs Data"})

    return Response({"Msg": "Data is deleted"})

@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="task_upload_photos",
    ignore_result=True
)
def task_upload_photos():
    """
    Saves latest image from Flickr
    """
    photos = Photo.objects.order_by("created_at").all()
    try:
        ftp = ftplib.FTP("61.69.119.183")
        ftp.login("photos", "ahJaeLeiseu8ie")
        logger.debug("logging in")
        ftp.pwd()
        ftp.set_pasv(False)
        res = ftp.nlst()

        folderName1 = 'DeliveryTrackingSystem'
        if folderName1 in ftp.nlst():
            ftp.cwd('/DeliveryTrackingSystem')
            ftp.pwd()
        else:
            ftp.mkd('DeliveryTrackingSystem')
            ftp.cwd('/DeliveryTrackingSystem')
            ftp.pwd()

        try:
            for photo in photos:
                if photo.is_uploaded is False:
                    photo_id = photo.id
                    run_id = photo.run_id
                    run_id = int(run_id)
                    run_id = str(run_id)
                    drop_id = photo.drop_id
                    f = str(photo.file)
                    f = f.split("/")
                    filename = f[1]
                    # cwd = os.getcwd()
                    # print(cwd)
                    folderName2 = run_id
                    if folderName2 in ftp.nlst():
                        ftp.cwd(run_id)

                        folderName3 = drop_id
                        if folderName3 in ftp.nlst():
                            ftp.cwd(drop_id)
                            myfile = open("media\Docs\\" + filename, 'rb')
                            logger.debug("creating directory")
                            success = ftp.storbinary('STOR ' + filename, myfile)
                            if success == "226 Transfer complete":
                                uploaded_photo = Photo.objects.filter(pk=photo_id)
                                uploaded_photo.update(is_uploaded=True)
                                logger.debug("file uploaded suucessfuly")
                            else:
                                continue
                            myfile.close()
                            logger.debug("closing")
                        else:
                            ftp.mkd(drop_id)
                            ftp.cwd(drop_id)
                            myfile = open("media\Docs\\" + filename, 'rb')
                            logger.debug("creating directory")
                            success = ftp.storbinary('STOR ' + filename, myfile)
                            if success == "226 Transfer complete":
                                uploaded_photo = Photo.objects.filter(pk=photo_id)
                                uploaded_photo.update(is_uploaded=True)
                                logger.debug("file uploaded suucessfuly")
                            else:
                                continue
                            myfile.close()
                            logger.debug("closing")

                    else:
                        ftp.mkd(run_id)
                        ftp.cwd(run_id)

                        folderName4 = drop_id
                        if folderName4 in ftp.nlst():
                            ftp.cwd(drop_id)
                            myfile = open("media\Docs\\" + filename, 'rb')
                            logger.debug("creating directory")
                            success = ftp.storbinary('STOR ' + filename, myfile)
                            if success == "226 Transfer complete":
                                uploaded_photo = Photo.objects.filter(pk=photo_id)
                                uploaded_photo.update(is_uploaded=True)
                                logger.debug("file uploaded suucessfuly")
                            else:
                                continue
                            myfile.close()
                            logger.debug("closing")
                        else:
                            ftp.mkd(drop_id)
                            ftp.cwd(drop_id)
                            myfile = open("media\Docs\\" + filename, 'rb')
                            logger.debug("creating directory")
                            success = ftp.storbinary('STOR ' + filename, myfile)
                            if success == "226 Transfer complete":
                                uploaded_photo = Photo.objects.filter(pk=photo_id)
                                uploaded_photo.update(is_uploaded=True)
                                logger.debug("file uploaded suucessfuly")
                            else:
                                continue
                            myfile.close()
                            logger.debug("closing")

                    ftp.cwd('/DeliveryTrackingSystem')
            ftp.quit()
            logger.debug("quitting")
            return Response({"Msg": "Photo Data is uploaded"})

        except:
            logger.debug("Error while uploading data")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Upload Data"})
    except:
        logger.debug("Error while connecting to ftp server")
        print(traceback.format_exc())
        return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Connect FTP Server"})

@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="task_delete_photos",
    ignore_result=True
)
def task_delete_photos():
    """
    Saves latest image from Flickr
    """
    photos = Photo.objects.order_by("created_at").all()
    for photo in photos:
        try:
            if photo.is_uploaded is True and photo.is_checked is True:
                photo_id = photo.id
                photo_obj = Photo.objects.filter(pk=photo_id)
                logger.debug("deleting deleting")
                photo_obj[0].delete()
        except:
            logger.debug("Error while deleting photos data")
            print(traceback.format_exc())
            return Response({"status": status.HTTP_404_NOT_FOUND, "Msg": "Could Not Delete Photos"})
    logger.debug("Photos are deleted")
    return Response({"Msg": "Photos are deleted"})