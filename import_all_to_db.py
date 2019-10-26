from fet_api_to_gcal import db
from fet_api_to_gcal.models import Resource, Std_mail, Teacher, Calendar
import json


def import_student_sets_to_db(
        filename="fet_api_to_gcal/data/studentsEmail.csv"):
    f = open(filename, "r")
    lines = f.readlines()
    for line in lines[1::]:
        line_splitted = line.strip().split(",")
        student_set = line_splitted[0]
        student_set_email = line_splitted[1].replace('"', '')
        std_mail_obj = Std_mail(std_set=student_set,
                                std_email=student_set_email)
        if std_mail_obj is not None:
            db.session.add(std_mail_obj)
        else:
            print("[INFO] Student Set Already In database!!")
    f.close()
    db.session.commit()


def import_techers_to_db(
        filename="fet_api_to_gcal/data/map-name-fet-email.csv"):
    f = open(filename, "r")
    lines = f.readlines()
    for line in lines[1::]:
        line_splitted = line.strip().split(',')
        teacher_mail = line_splitted[0]
        fullname = line_splitted[1]
        fet_name = line_splitted[2]
        teacher_obj = Teacher(fullname=fullname,
                              teacher_email=teacher_mail,
                              fet_name=fet_name)
        if teacher_obj is not None:
            db.session.add(teacher_obj)
        else:
            print("[INFO] Teacher Already In database!!")
    f.close()
    db.session.commit()


def import_resources_to_db(filename="fet_api_to_gcal/data/resources.json"):
    f = open(filename, "r")
    data = json.load(f)
    for resource in data['items']:
        res = Resource(resource_name=str(resource["resourceName"]),
                       gen_resource_name=str(
                           resource["generatedResourceName"]),
                       resource_email=str(resource["resourceEmail"]),
                       capacity=int(resource["capacity"]),
                       building=resource["buildingId"])
        db.session.add(res)
    db.session.commit()
    f.close()


def import_calendars_from_google_json_resp(
        filename="fet_api_to_gcal/data/calendars.json"):
    f = open(filename, "r")
    data = json.load(f)
    for calendar in data["items"]:
        summary = calendar["summary"]
        calendar_id = calendar["id"]
        cal_obj = Calendar.query.filter_by(summary=summary).first()
        if cal_obj is None:
            # getting the student email from the summary
            student_set = Std_mail.query.filter_by(std_set=summary).first()
            if student_set is None:
                continue
            else:
                calendar = Calendar(summary=summary,
                                    calendar_id_google=calendar_id,
                                    std_email=student_set.std_email)
                db.session.add(calendar)
            db.session.commit()
        else:
            print("Calendar already in DB")


def update_all_calendars_from_json_resp(
        filename="fet_api_to_gcal/data/calendars_new.json"):
    f = open(filename, "r")
    data = json.load(f)
    for calendar in data["items"]:
        summary = calendar["summary"]
        if "1CPI" or "2CPI" in summary:
            if summary[-2] == "0":
                summary = summary[:-2:] + summary[-1]
        calendar_id = calendar["id"]
        cal_obj = Calendar.query.filter_by(summary=summary).first()
        if cal_obj is None:
            # getting the student email from the summary
            student_set = Std_mail.query.filter_by(std_set=summary).first()
            if student_set is None:
                print("std set {} none".format(summary))
                continue
            else:
                calendar = Calendar(summary=summary,
                                    calendar_id_google=calendar_id,
                                    std_email=student_set.std_email)
                db.session.add(calendar)
            db.session.commit()
        else:
            # updating calendar
            cal_obj.calendar_id_google = calendar_id
            db.session.commit()


def import_calendars_with_std_sets(
        filename="fet_api_to_gcal/data/calendars_esi_with_std_sets.csv"):
    raise NotImplementedError


if __name__ == "__main__":
    try:
        update_all_calendars_from_json_resp()
    except NotImplementedError as e:
        print(e)
