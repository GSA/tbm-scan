# tbm-scan
Scripts to scan fbo.gov for solicitations related to Technology Business Management (TBM)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

We make use of [pipenv](https://docs.pipenv.org/en/latest/) for creating a virtual environment, although you could [convert our Pipfile to a requirements.txt](https://pypi.org/project/pipenv-to-requirements/) and use `venv`.


### Installing
Below, you can see how to use pipenv to install this project's requirements and start a shell session that utilizes the virtual environment:

```bash
cd ~/path/to/this/repo
pipenv install
pipenv shell
```

Now you can run the scans:

```bash
python tbm_scan.py
```

## Running the tests

To run the tests, activate the virtual environment and then run:

```bash
python -W ignore -m unittest discover tests -p '*_test.py'
```

## Deployment

TODO

## Contributing

Please read [CONTRIBUTING.md](https://github.com/GSA/tbm-scan/.github/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal License - see the [LICENSE.md](https://github.com/GSA/tbm-scan/.github/LICENSE.md) file for details.
