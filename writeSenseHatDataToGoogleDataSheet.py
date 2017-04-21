from googleapiclient import discovery
#from __future__ import print_function


import httplib2
import os
import time
import subprocess
import datetime

from pprint import pprint
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from sense_hat import SenseHat

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


#Google stuff
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API'

#USER CONSTANTS
SourceDevice ='Raspberry Pi'
PositionName = 'Skogaberg 38'
factor = float(5.466) #5.466
pollTime = 30


#Sense Hat variabler
sense = SenseHat()
n = 0

#For Sense Hat
def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# Get CPU Temp in Celsius
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

#Google creds
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

credentials = get_credentials()

service = discovery.build('sheets', 'v4', credentials=credentials)

# The ID of the spreadsheet to update.
spreadsheet_id = '1uanOeaz-7jtg_LDVyFsQCtIsW0bNKV1h2hP89bCkF1s'  # TODO: Update placeholder value.

# The A1 notation of a range to search for a logical table of data.
# Values will be appended after the last row of the table.
range_ = 'SenseHatData!A2:I'  # TODO: Update placeholder value.

# How the input data should be interpreted.
value_input_option = 'USER_ENTERED'  # TODO: Update placeholder value.

# How the input data should be inserted.
insert_data_option = 'INSERT_ROWS'  # TODO: Update placeholder value.

while n < 1000:   
    # Build the array
    temp1 = float(getCPUtemperature())
    temp  = round(sense.temperature,1)

    # -------------- Sense Hat --------------
    # Read the sensors
    SHtempC  = sense.get_temperature()
    humidity = round(sense.get_humidity() +17,1)
    pressure_mb = sense.get_pressure()
    cpu_temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
    temp_calibrated = float(SHtempC) - ((float(temp1) - SHtempC)/factor)
    temp_calibrated = temp_calibrated - 10
    SH_pressure = sense.get_pressure()
    value_range_body = {
    "values": [
        [
          str(datetime.datetime.now()),
          SourceDevice,
          PositionName,
          str(temp1),
          str(round(SHtempC,1)),
          factor,
          str(round(temp_calibrated,1)),
          str(humidity),
          SH_pressure
        ]
      ]
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    pprint(response)
    time.sleep(pollTime)
    n = n + 1
