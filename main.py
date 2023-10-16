import logging
import utils
import os
import datetime
from flask import Flask, render_template, jsonify
import csv
import threading
import time


thread_event = threading.Event()

app = Flask(__name__)
app.config['TIMEOUT'] = 600

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

url = 'https://www.better.org.uk/book-activity'
locations = [
    'finsbury-leisure-centre',
    'britannia-leisure-centre',
    'john-orwell',
    'talacre-community-sports-centre',
    'whitechapel-sports-centre',
    'queensbridge-sports-community-centre',
    'clissold-leisure-centre',
    'mile-end-park-leisure-centre',
    'kings-hall-leisure-centre',
    'poplar-baths-leisure-centre',
    'copper-box-arena',
    # 'walthamstow-leisure-centre',
    'leytonstone-leisure-centre',
]

def main():
    log.info("Hello")
    # locations = utils.get_locations(url)
    slots = []
    for location in locations:
        availabilities = utils.get_availabilities(location)
        for availability in availabilities:
            processed_availability = utils.process_availability(location, availability)
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
    try:
        thread_event.set()
        thread = threading.Thread(target=main)
        thread.start()
        return {"message": "Fetching Latest slots in Background. Please check after few minutes"}
    except Exception as error:
        return {"error": error}

if __name__ == '__main__':
    app.run()