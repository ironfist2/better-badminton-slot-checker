import logging
import utils
import os
import datetime
from flask import Flask, render_template, jsonify
import csv
import time
from multiprocessing.pool import ThreadPool as Pool

app = Flask(__name__)
app.config['TIMEOUT'] = 600

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

url = 'https://www.better.org.uk/book-activity'
locations = [
    # 'finsbury-leisure-centre',
    'britannia-leisure-centre',
    'john-orwell',
    # 'talacre-community-sports-centre',
    'whitechapel-sports-centre',
    'queensbridge-sports-community-centre',
    # 'clissold-leisure-centre',
    'mile-end-park-leisure-centre',
    # 'kings-hall-leisure-centre',
    'poplar-baths-leisure-centre',
    'copper-box-arena',
    # 'walthamstow-leisure-centre',
    # 'leytonstone-leisure-centre',
]


def main():
    log.info("Hello")
    # locations = utils.get_locations(url)
    slots = []
    pool_size = 8  # your "parallelness"
    pool = Pool(pool_size)
    availabilities = []
    for location in locations:
        availabilities.append(pool.apply_async(
            utils.get_availabilities, (location,)))

    for i in availabilities:
        i = i.get()
        for j in i:
            for k in j:
                processed_availability = utils.process_availability(k)
                slots = slots + processed_availability
    utils.pretty_print(slots)


def read_csv():
    data = []
    with open('data.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data


@app.route('/')
def hello():
    data = read_csv()
    modification_time = os.path.getmtime('data.csv')
    last_refreshed_time = time.ctime(modification_time)
    return render_template('index.html', data=data, last_refreshed_time=last_refreshed_time)


@app.route('/refresh', methods=['GET'])
def refresh():
    main()
    data = read_csv()
    modification_time = os.path.getmtime('data.csv')
    last_refreshed_time = time.ctime(modification_time)
    return jsonify({'data': data, 'last_refreshed_time': last_refreshed_time})


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
