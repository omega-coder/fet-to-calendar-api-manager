import argparse
import sys


def main(filepath, event_names):

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
    parser = argparse.ArgumentParser(
        description="Script to filter/remove all events of a given name")
    parser.add_argument("-f", "--file", type=str, metavar='Path', dest='file')
    parser.add_argument("-e",
                        "--event",
                        dest="event_names",
                        action='append',
                        default=[])

    args = parser.parse_args()
    main(args.file, args.event_names)
