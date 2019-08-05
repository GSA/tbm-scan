# tbm-scan
Script to scan fbo.gov for solicitations related to Technology Business Management (TBM). As a CLI tool, a few flags can let you:
 - write to csv as opposed to json
 - specify a date range for the scan
 - filter for TBM-related solicitations or get everything
 
 You can also run the scans from with a Jupyter Notebook.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

>If you're going to use the CLI tool, we suggest using [pipenv](https://docs.pipenv.org/en/latest/) for creating a virtual environment, but we've also converted our Pipfile to a requirements.txt in case you'd like to use `venv`. Examples use `pipenv`.


### Clone the Repo

You can `git clone` this repo with:

```bash
git clone https://github.com/GSA/tbm-scan.git
cd tbm-scan
```

### Jupyter Notebook Instructions
Now that you've got the project locally, open jupyter notebook and open `TBM_Scan.ipynb`. Make sure you're using a Python 3 kernel.

### CLI Instructions
With the project cloned, you can use pipenv to install dependencies and then start a shell session that utilizes the virtual environment:

```bash
pipenv install
pipenv shell
```

Now you can run the scans. But, before doing so, view the options:

```bash
python tbm_scan.py -h
```

That should print out something like this:

```bash
usage: tbm_scan.py [-h] [-s START_DATE] [-e END_DATE] [-tf [TBM_FILTER]]
                   [--excel [EXCEL]]

Get solicitations from fbo.gov between two dates inclusive (if both flags are
used) or from the day before yesteday.

optional arguments:
  -h, --help            show this help message and exit
  -s START_DATE, --start-date START_DATE
                        the first date in the range you'd like to fetch
                        notices from. Supply as a string ('%Y-%m-%d')
  -e END_DATE, --end-date END_DATE
                        the last date in the range you'd like to fetch notices
                        from. Supply as a string ('%Y-%m-%d')
  -tf [TBM_FILTER], --tbm-filter [TBM_FILTER]
                        Whether or not to filter for TBM solicitations.
                        Default is False
  --excel [EXCEL]       Whether or not to write output to excel. Default is
                        False
```                        

As an example, let's say you wanted to get every solicitation between 10/01/2018 and 07/22/19 inclusive. And let's say you wanted to write these to excel without filtering for TBM-related solicitations. This would do that:

```bash
python tbm_scan.py -s 2018-10-01 -e 2019-07-12 -tf False --excel True
```

That'll take awhile to run, but when it' done you'll be able to find your results in `data.csv`. 

Now let's say a week passes and you want to get everything since your last scan. You could do:

```bash
python tbm_scan.py -tf False --excel True
```

That will get every solicitation since the most recent date in `data.csv`. *Note: this means that you need to keep `data.csv` within this project directory if you plan to intermittently run this script to accumlate recent solicitations.* 


## Running the tests

To run the tests, make sure you've activated the virtual environment and then run:

```bash
python -W ignore -m unittest discover tests -p '*_test.py'
```

## Contributing

Please read [CONTRIBUTING.md](https://github.com/GSA/tbm-scan/.github/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal License - see the [LICENSE.md](https://github.com/GSA/tbm-scan/.github/LICENSE.md) file for details.
