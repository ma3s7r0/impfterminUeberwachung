# Impftermin-Überwachung

This little script watches the vaccination campaign at the ECE Center, the Kammertheater and the Stäadtisches Klinikum in Karlsruhe and alerts via eMail if there is a free appointment.

## Requirements
* `python` 2.7 or 3.x
* `pip`
* [`virtualenv`](https://virtualenv.pypa.io/en/latest/)

## Quickstart
### SetUp
```sh
# Windows (CMD.exe)
$ setup.bat
# Unix
$ chmod +x setup.sh && ./setup.sh
```
### Configure
Edit impftermin.env to fit your configuration

### Run
```sh
# Windows (CMD.exe)
(venv) $ python impfueberwachung.py
# Unix
(venv) $ ./impfueberwachung.py
```

## Create new virtual environment
The following command creates a new virtual environment named `.venv` in the current directory, usually this will be your project's directory.
```sh
$ python3 -m venv .venv
```

## Activate virtual environment
The following commands [activate](https://virtualenv.pypa.io/en/latest/userguide/#activate-script) an existing virtual environment on Windows and Unix systems. The command assume that the virtual environment is named `venv` and that its location is in a subdirectory `path/to/` of the current directory. 
```sh
# Windows (CMD.exe)
$ .venv\Scripts\activate.bat
# Unix
$ source .venv/bin/activate
```
Once the virtual environment has been actiated your console cursor might prepend the name of the virtual environment as shown below.
```sh
(venv) $ echo 'Hello World!'
```

## Deactivate virtual environment
The following command deactivates the current virtual environment, any dependency installed after this command will be installed globally.
```sh
(venv) $ deactivate
```

## Miscellaneous
To install dependencies using `pip` while being behind proxy add the following flags after `pip install`.
```sh
(venv) $ pip install --proxy http://user:pass@proxyAddress:proxyPort --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org boto3
```