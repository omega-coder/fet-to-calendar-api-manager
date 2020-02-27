import argparse
import logging
import sys
from pprint import pprint

from fet_api_to_gcal import db
from fet_api_to_gcal.common.utils import getDate, perror, psuccess
from fet_api_to_gcal.models import Calendar, Resource, Std_mail, Teacher


# TODO: add proper logging to the script. (file + stdout).
# TODO: add an arguemt parser to script.



dates = {
    "2CPI": "2020/02/23",  # ! needs to be changed accordingly!
    "1CS": "2020/02/23",   # ! needs to be changed accordingly!
    "2CS": "2020/02/23",   # ! needs to be changed accordingly!
    "3CS": "2020/02/23"    # ! needs to be changed accordingly!
    "1CPI": "2020/02/23",  # ! needs to be changed accordingly!
}


def check_teachers(teacher_file):
    """Checks that all teachers from the FET timetable are present in the database
    
    Args:
        teacher_file (str, required): path to a FET generated csv file for teachers.
    
    Returns:
        dict: a dictionary with two keys, one for the operation status
        and one for missing teachers when status is False else returns None
    """
    not_found = []

    with open(teacher_file, "r") as teachers_f:
        teachers = teachers_f.readlines()
        total_teachers, i = len(teachers[1:]), 0
        for teacher_name in teachers[1:]:
            teacher_name = teacher_name.replace('"', '').strip()
            teacher_obj = Teacher.query.filter_by(
                fet_name=teacher_name).first()
            if teacher_obj is None:
                not_found.append(teacher_name)

        if len(not_found) != 0:
            return {"status": False, "missing_teachers": not_found}
        else:
            return {"status": True, "missing_teachers": None}


def check_timetable_validity(timetable_path,
                             dates,
                             events_freq=1,
                             max_events=None):
    """[summary]
    
    Args:
        timetable_path (str): path to the timetable csv file generated by FET.
        dates (dict): a dictionary type key: value with keys corresppnding to the study years
                      and a value corresponding to the starting study date of that year.
                      IMPORTANT: the starting date must correspond the the first day of the week (Sunday)  
        events_freq (int, optional): frequency of the generated google events. Defaults to 1.
        max_events (int, optional): maximum number of gogole events to be generated.If None, then all
                                    the event in timetable_path will be generated. Defaults to None.
    
    Returns:
        list: list of google styled events, each google event is a python dictionary.
    """

    timezone = "Africa/Algiers"
    f = open(timetable_path, "r")
    lines = f.readlines()[1::]
    all_events = []  # to hold all json gevents later!
    temp_dict_holder = {}
    for line in lines:
        line_splitted = list(
            map(lambda x: x.replace('"', ''),
                line.strip().split(",")))[:-1]
        if "Pause" not in line_splitted[2]:
            if line_splitted[0] not in list(temp_dict_holder.keys()):
                start_end = line_splitted[2].split("-")
                temp_dict_holder[line_splitted[0]] = {
                    "Day":
                    line_splitted[1],
                    "start":
                    start_end[0],
                    "end":
                    start_end[1],
                    "teachers":
                    line_splitted[5].split("+"),
                    "room":
                    line_splitted[-1].upper(),
                    "summary":
                    "{} {} {}".format(line_splitted[-2], line_splitted[-4],
                                      line_splitted[-3]),
                    "std_set":
                    line_splitted[3]
                }
            else:
                temp_dict_holder[
                    line_splitted[0]]["end"] = line_splitted[2].split("-")[1]
        else:
            # ? if pause in line record then ignore the line.
            # TODO: treat line records with Pause time as part of the event to prohibit reservations in Pause time
            continue

    # ? 2nd phase


    # ? indexes are used to allow non-ordered events to be generated successfully.
    indexes = list(map(int, list(temp_dict_holder.keys())))
    for event_inx in indexes:
        try:
            event___old = temp_dict_holder[str(event_inx)]
        except KeyError as e:
            print(e)
        __gevent__ = {"summary": event___old["summary"]}

        # ? get attendees emails
        __gevent__["attendees"] = []
        # teachers
        for teacher_name in event___old["teachers"]:
            teacher = Teacher.query.filter_by(fet_name=teacher_name).first()
            if teacher is not None:
                __gevent__["attendees"].append(
                    {"email": teacher.teacher_email})
            else:
                perror("Teacher {} not found (event index: {})".format(
                    teacher_name, event_inx))

        # students
        if event___old["std_set"] == "":
            perror("Std_set empty in event index : {}".format(event_inx))
            #pprint(event___old)
            continue
        for std_set__ in event___old["std_set"].split("+"):

            std_mails_obj = Std_mail.query.filter_by(std_set=std_set__).first()
            if std_mails_obj is not None:
                __gevent__["attendees"].append(
                    {"email": std_mails_obj.std_email})

        # add room if existing

        if event___old["room"] != "":
            res = Resource.query.filter_by(
                resource_name=event___old["room"]).first()
            if res is not None:
                __gevent__["attendees"].append({
                    "email": res.resource_email,
                    "resource": True
                })
        else:
            perror("Room empty in event index : {}".format(event_inx))
            #continue
        # recurrence rule
        __gevent__["recurrence"] = [
            "RRULE:FREQ=WEEKLY;COUNT=" + str(events_freq)
        ]
        # set start and time
        # print(event___old["std_set"].split(" ")[0])
        dateTime_start = getDate(dates, event___old["std_set"].split(" ")[0],
                                 event___old["Day"],
                                 event___old["start"].split("h")[0],
                                 event___old["start"].split("h")[1])
        dateTime_end = getDate(dates, event___old["std_set"].split()[0],
                               event___old["Day"],
                               event___old["end"].split("h")[0],
                               event___old["end"].split("h")[1])
        __gevent__["start"] = {
            "timeZone": timezone,
            "dateTime": dateTime_start,
        }
        __gevent__["end"] = {
            "timeZone": timezone,
            "dateTime": dateTime_end,
        }
        all_events.append(__gevent__)

        if len(all_events) == max_events:
            return all_events
    return all_events


def check_google_event(gevent):

    raise NotImplementedError


if __name__ == "__main__":
    tt_path = sys.argv[1]
    all_events = check_timetable_validity(timetable_path=tt_path)
    for event in all_events:
        resource = None
        teachers = []
        std_sets_emails = []
        if "resource" in event["attendees"][-1].keys():
            resource = event["attendees"][-1]
            event["attendees"].remove(resource)

        for ev_att in event["attendees"]:
            if Teacher.query.filter_by(teacher_email=ev_att["email"]).first():
                teachers.append(ev_att)
            else:
                std_sets_emails.append(ev_att)

        event["attendees"].clear()
        event["attendees"].extend(teachers)
        if resource is not None:
            event["attendees"].append(resource)

        for std_mail in std_sets_emails:
            cal_rec = Calendar.query.filter_by(
                std_email=std_mail["email"]).first()
            if cal_rec:
                calendar_id = cal_rec.calendar_id_google
                """
                #import pdb; pdb.set_trace()
                """
            else:
                print("Calendar does not exist")
                print("_________")
                continue
