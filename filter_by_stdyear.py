import sys


def main(filepath):
    years_x_file__out = {"1CP": None, "2CP": None, "1CS": None, "2CS": None}
    f = open(filepath, "r")
    data = f.readlines()

    for y in years_x_file__out.keys():
        try:
            years_x_file__out[y] = open("{}_{}.csv".format(filepath, y), "w")
        except Exception as e:
            print(y, e)

    for i in years_x_file__out.keys():
        years_x_file__out[i].write(data[0])

    for line in data[1:]:
        try:
            year = line.split(",")[3][1:4]
            if year in years_x_file__out.keys():
                years_x_file__out[year].write(line)
            else:
                print(line)
        except Exception as e:
            print(line, e)

    for i in years_x_file__out.keys():
        years_x_file__out[i].close()


if __name__ == "__main__":
    main(sys.argv[1])
