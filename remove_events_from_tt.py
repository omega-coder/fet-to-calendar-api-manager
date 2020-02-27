import argparse
import sys


def main(filepath, event_names):
    """Remove all events inside of event_names list parameter from the FET generated timetable csv file.  
    
    Args:
        filepath (str): path for the FET generated timetable csv file.
        event_names (list): a list containing the event names (string values) to be deleted. 
    """
    f = open(filepath, "r")
    data = f.readlines()

    # open a file for the resulting filtered file

    try:
        result_file = open(
            "{}_REMOVED_{}".format(filepath, "".join(event_names)), "w")
    except Exception as e:
        print("Exception while opening result file: {}".format(e))
        sys.exit(1)

    # write the first line of the csv containing columns
    result_file.write(data[0])

    for line in data[1:]:
        event__name__ = line.split(",")[4].replace('"', '')
        if event__name__ in event_names:
            continue
        else:
            result_file.write(line)


if __name__ == "__main__":
    # create an arguemnt parser
    parser = argparse.ArgumentParser(
        description="Script to filter/remove all events of a given name")
    parser.add_argument("-f",
                        "--file",
                        type=str,
                        metavar='Path',
                        dest='file',
                        help="Path to the FET generated csv timetable file.")
    parser.add_argument("-e",
                        "--event",
                        dest="event_names",
                        action='append',
                        default=[])

    # Parse arguments
    args = parser.parse_args()
    # call the main function
    main(args.file, args.event_names)
