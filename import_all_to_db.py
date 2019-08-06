from fet_api_to_gcal import db
from fet_api_to_gcal.models import Resource, Std_mail, Teacher
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


def import_calendars_with_std_sets(
        filename="fet_api_to_gcal/data/calendars_esi_with_std_sets.csv"):
    raise NotImplementedError


if __name__ == "__main__":
    try:
        import_resources_to_db()
    except NotImplementedError as e:
        print(e)
