from flask import Flask, render_template, request
import pymongo
from bson.objectid import ObjectId
import datetime


def date_exceeded_one_year(date):
    date = datetime.datetime.strptime(date, "%d-%m-%Y")
    present = datetime.datetime.now()
    end_date = datetime.datetime(date.year + 1, date.month, date.day)
    return end_date < present


def date_exceeded_one_week(date):
    date = datetime.datetime.strptime(date, "%d-%m-%y")
    present = datetime.datetime.now()
    end_date = date + datetime.timedelta(days=7)

    return end_date < present


def find_certificate(certificate_id):
    global db

    try:
        certificate = db.certificates.find_one(
                            {
                                "_id": ObjectId(certificate_id)
                            }
                        )

        return certificate

    except:
        return -1


def verify_certificate_validity(certificate):
    doses = certificate['certificate']['doses']

    if len(doses) < 2:
        return False

    last_dose_date = doses[1]['dose']['date']

    if not date_exceeded_one_year(last_dose_date):
        return True

    tests = certificate['certificate']['tests']

    if len(tests) == 0:
        return False

    last_test_date = tests[-1]['date']
    last_test_result = tests[-1]['result']

    if not date_exceeded_one_week(last_test_date) and last_test_result == 'negative':
        return True

    return False


# Replace the uri string with your MongoDB deployment's connection string.
conn_str = "mongodb+srv://root:password1234*qwerty@cluster0.2fwff.mongodb.net/test"
# set a 5-second connection timeout
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to the server.")

db = client.SMUD

app = Flask(__name__)


@app.route('/home')
def home():
    if 'certificate_id' in request.args:
        certificate_id = request.args['certificate_id']
        certificate = find_certificate(certificate_id)
        if certificate == -1:
            return render_template('home.html', wrong_id=True)

        valid = verify_certificate_validity(certificate)
        return render_template('home.html', valid=valid, certificate_id=certificate_id)

    return render_template('home.html')


if __name__ == "__main__":
    app.run()