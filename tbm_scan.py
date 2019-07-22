import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import timedelta, datetime
from functools import partial
import json
import logging
import os

def str_to_bool(v):
    '''
    Use with argpase
    '''
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

argparse_desc = ('Get solicitations from fbo.gov between two dates inclusive '
                 '(if both flags are used) or from the day before yesteday.')
parser = argparse.ArgumentParser(description = argparse_desc)
parser.add_argument('-s',
                    '--start-date',
                    dest = 'start_date',
                    type = str,
                    help = "the first date in the range you'd like to fetch notices from. Supply as a string ('%%Y-%%m-%%d')")
parser.add_argument('-e',
                    '--end-date',
                    dest = 'end_date',
                    type = str,
                    help = "the last date in the range you'd like to fetch notices from. Supply as a string ('%%Y-%%m-%%d')")
parser.add_argument('-tf',
                    '--tbm-filter',
                    type = str_to_bool,
                    nargs = '?',
                    const = True, 
                    default = False,
                    dest = 'tbm_filter',
                    help = "Whether or not to filter for TBM solicitations. Default is False") 
parser.add_argument('--excel',
                    type = str_to_bool,
                    nargs = '?',
                    const = True, 
                    default = False,
                    dest = 'excel',
                    help = "Whether or not to write output to excel. Default is False")                                     

from utils.get_nightly_data import get_nightly_data
from utils.writer import write_to_csv

logger = logging.getLogger(__name__)


def get_dates(start_date = None, end_date = None):
    """Return a list of dates between start_date and end_date inclusive 
    if params provided; else return a list with just the date from two days ago.
    
    Keyword Arguments:
        start_date {str} -- date in the "%Y-%m-%d" format. default: None
        end_date {str} -- date in the "%Y-%m-%d". default: None
    
    Returns:
        fbo_dates {list} -- list of dates as strings in the "%Y%m%d" format
    """
    fbo_dates = []
    if all([start_date, end_date]):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        delta = end_date - start_date
        for i in range(delta.days + 1):
            fbo_date = start_date + timedelta(i)
            fbo_date = fbo_date.strftime("%Y%m%d")
            fbo_dates.append(fbo_date)
    else:
        now_minus_two = datetime.utcnow() - timedelta(2)
        now_minus_two = now_minus_two.strftime("%Y%m%d")
        fbo_dates.append(now_minus_two)
    
    return fbo_dates

def main():
    """Void function that runs the nightly scraper using argparse to accept a user-defined date range
    and multiprocessing for a slight speed boost. Data is written to disk as JSON.
    
    Returns:
        None
    """
    args = parser.parse_args()
    fbo_dates = get_dates(start_date = args.start_date, end_date = args.end_date)
    tbm_filter = args.tbm_filter
    excel = args.excel
    # By default, the executor sets number of workers to the # of CPUs.
    with ProcessPoolExecutor() as executor:
        fn = partial(get_nightly_data, tbm_filtering = tbm_filter)
        executor.map(fn, fbo_dates)
    if excel:
        write_to_csv()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    main()