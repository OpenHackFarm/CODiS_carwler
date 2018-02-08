#!/usr/bin/env python
# encoding: utf-8

# 修改自 https://gist.github.com/wy36101299/e3b32c674d9e86ba581f

import requests
from time import sleep
from bs4 import BeautifulSoup
import csv
import json
import os

OVER_WRITE = False


def generate_query_month(year):
    month = []

    for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        month.append('-'.join([str(year), m]))

    return month


# https://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python
def mapping_two_list_to_dict(keys, values):
    return dict(zip(keys, values))


def crawler(url):
    json_data = {}

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)

    trs = soup.findAll('tr')

    ths = trs[2].findAll('th')
    title = [th.text.split(')')[1] for th in ths]

    for tr in trs[3:]:
        tds = tr.findAll('td')

        row = [td.text.strip() for td in tds]

        dictionary = mapping_two_list_to_dict(title, row)

        json_data[dictionary['ObsTime']] = dictionary

    return json_data


def write_json(json_data, save_dir_path, filename):
    if not os.path.exists(save_dir_path):
        os.mkdir(save_dir_path)

    with open(save_dir_path + filename, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)


if __name__ == "__main__":
    month_generated = generate_query_month(2018)

    hostUrl = "http://e-service.cwb.gov.tw/HistoryDataQuery/MonthDataController.do?command=viewMain"

    # read stations
    with open('CWB_Stations_171226.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        firstline = True
        for row in spamreader:
            if firstline:  # skip first line
                firstline = False
                continue

            station_id, station_name = row[0], row[1]
            print station_id, station_name

            # crawler
            for month in month_generated:
                url = '%s&station=%s&stname=%s&datepicker=%s' % (hostUrl, station_id, station_name, month)
                print(url)

                save_dir_path = './CODiS-data/%s_%s/' % (station_id, station_name)
                filename = '%s.json' % month

                if (not os.path.exists(save_dir_path + filename)) or (OVER_WRITE is True):
                    print save_dir_path + filename
                    try:
                        json_data = crawler(url)

                        write_json(json_data, save_dir_path, filename)
                    except Exception, e:
                        print e

                    sleep(0.4)
                else:
                    print 'pass'
