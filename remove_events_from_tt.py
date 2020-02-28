import argparse
import logging
import ntpath
import sys

from fet_api_to_gcal.common.utils import timestamped_filename
from fet_api_to_gcal.common.utils import path_leaf


def main(filepath, event_names):
    """Remove all events inside of event_names list parameter from the FET generated timetable csv file.  
    
    Args:
        filepath (str): path for the FET generated timetable csv file.
        event_names (list): a list containing the event names (string values) to be deleted. 
    """

    log_filename = timestamped_filename(filename=path_leaf(filepath))

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filename="./logs/{}.log".format(log_filename),
                        filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    logging.info("[?] Opening file {}".format(path_leaf(filepath)))
    try:
        f = open(filepath, "r")
        data = f.readlines()
    except Exception as e:
        logging.exception("[!] Exception while opening file {}".format(filepath))
        logging.error("[!] Exiting script")
        sys.exit(1)
    # ? open a file for the resulting filtered file

    try:
        result_file = open(
            "{}_REMOVED_{}".format(filepath, "".join(event_names)), "w")
    except Exception as e:
        logging.error("[!] Exception while opening result file: {}".format(e))
        sys.exit(1)

    # write the first line of the csv containing columns
    logging.info("[?] started writing data to result file.")
    result_file.write(data[0])
    counter = 0
    for line in data[1:]:
        event__name__ = line.split(",")[4].replace('"', '')
        if event__name__ in event_names:
            counter += 1
            continue
        else:
            result_file.write(line)
    logging.info("[+] Finished writing to result file")
    logging.info("Removed {} event records from original file".format(counter))

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
                        default=[],
                        help="event name to be appended to the list of event names")

    # Parse arguments
    
    args = parser.parse_args()
    # call the main function
    main(args.file, args.event_names)
