# Jenkins reporting

Failorama is for building reports from Jenkins builds. There are 
two types of reports:

1. ISO build report

   These type of reports download data from specified upstream jobs and
   corresponding downstream jobs. The result is is displayed in html table:

   | Upstream job # | Downstream job1 # | Downstream job2 # |
   |----------------|:-----------------:|:-----------------:|
   |     1/PASS     |      14/FAIL      |       12/PASS     |
   |     2/FAIL     |        N/A        |        N/A        |

2. Staging build reports

   Download information about failed builds from specific jobs and
   crawl linked LP bugs. For each failed build display: build number,
   linked bug title, bug status, bug assignee, target projects.

## Installation

Failorama is built on top of Python, Flask and MySQL.

#### Requirements

Make sure following dependencies are installed in your system:
* Python 2.7
* MySQL server (for production)
* SQLite (for testing)


#### Install dependencies on Ubuntu

1. Install system requirements:
    ```shell
    $ sudo apt-get install build-essential python-dev python-pip
    $ sudo pip install virtualenv
    $ sudo apt-get intsall libxml2-dev libxslt1-dev
    $ sudo apt-get install mysql-server libmysqlclient-dev
    ```

2. Install Python requirements:
    ```shell
    $ pip install -r failorama/requirements.txt
    ```


#### Configure MySQL database

Following command creates database `jenkins_reporting` and grants
full privilegies to user `reporting` identified by password `reporting`:

```shell
$ mysql -u root -p
```

```sql
mysql> CREATE DATABASE jenkins_reporting;
mysql> GRANT ALL PRIVILEGES ON jenkins_reporting.* TO 'reporting'@'localhost' \
            IDENTIFIED BY 'reporting';
mysql> exit;
```


#### Create configuration file

First, create configuration file `/etc/failorama/failorama.conf`:

```shell
$ mkdir /etc/failorama
$ touch /etc/failorama/failorama.conf
```

Here is how your `/etc/failorama/failorama.conf` might look like:
```python
SQLALCHEMY_DATABASE_URI = "mysql://reporting:reporting@127.0.0.1/jenkins_reporting"
PRODUCT_JENKINS = "http://myjenkins_url:8080"
ISO_VERSIONS = ['2.1', '2.0.1', '1.1.2']
IGNORED_ISO_JOBS = ['deploy_iso_on_cachers']
STAGING_JOBS = [
    '2.1.test_staging_mirror',
    '1.1.test_staging_mirror',
]
```

## Command line usage

    $ python manage.py syncdb # Creates database tables if they don't exist

    $ python manage.py update-iso # Download upstream ISO and corresponding downstream build jobs statuses and update them in the database

    $ python manage.py update-staging # Download staging jobs statuses and update them in the database

    $ python manage.py devserver [PORT] # Run development web server instance listening on [PORT]


# License
Apache License Version 2.0 http://www.apache.org/licenses/LICENSE-2.0
