import logging
import utils
import os

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
    'walthamstow-leisure-centre',
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

if __name__ == "__main__":
    main()
