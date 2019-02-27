#!/usr/bin/env python
# encoding: utf-8

import csv
import json
import os

OVER_WRITE = False


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def write_json(json_data, save_dir_path, filename):
    if not os.path.exists(save_dir_path):
        os.mkdir(save_dir_path)

    with open(save_dir_path + filename, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)


if __name__ == "__main__":
    year_generated = range(2005, 2018)
    month_key = [('0' + str(m))[-2:] for m in range(1, 13)]
    data_key = ['Temperature', 'Td dew point', 'Precp', 'PrecpHour', 'PrecpDay', 'RH', 'EvapA', 'SunShine', 'GloblRad']

    # read stations
    with open('CWB_Stations_171226.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        firstline = True
        for row in spamreader:
            if firstline:  # skip first line
                firstline = False
                continue

            station_id, station_name = row[0], row[1]
            save_dir_path = './CODiS-data/%s_%s/' % (station_id, station_name)
            print station_id, station_name,
            # if station_id != '467080':
                # continue

            # for each year
            sum_data = dict.fromkeys(month_key, {})
            sum_data_pass = dict.fromkeys(data_key, 0)
            avg_data = dict.fromkeys(month_key, {})
            for month in month_key:
                sum_data[month] = dict.fromkeys(data_key, 0.0)
                avg_data[month] = dict.fromkeys(data_key, 0.0)
            for year in year_generated:
                data = json.load(open(os.path.join(save_dir_path, '%s.json' % year)))
                if(len(data) == 0):
                    print 'Pass...'
                    break
                else:
                    print 'Counting...', year

                    # for each month
                    for m in data.keys():
                        if len(m.split('-')) > 1:
                            month = m.split('-')[1]
                        else:
                            month = m
                        for field in data_key:
                            if isfloat(data[m][field]):
                                sum_data[month][field] = sum_data[month][field] + float(data[m][field])
                            else:
                                sum_data_pass[field] = sum_data_pass[field] + 1

                    # avg year month data
                    for m in month_key:
                        for f in data_key:
                            if (len(year_generated) - sum_data_pass[f]) != 0:
                                avg_data[m][f] = round(sum_data[m][f] / (len(year_generated) - sum_data_pass[f]), 2)

                    write_json(avg_data, save_dir_path, '%s-%s.json' % (year_generated[0], year_generated[-1]))
