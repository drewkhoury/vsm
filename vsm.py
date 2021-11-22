from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests
import json
import time
import sys
import os

# pip3 install requests
# pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# python3 ./vsm.py

# user input required
miro_token=os.environ.get('MIRO_TOKEN')
miro_board=os.environ.get('MIRO_BOARD')

# these have defaults
sheet_id=os.environ.get('SHEET_ID')

def main():

    if "MIRO_TOKEN" not in os.environ or "MIRO_BOARD" not in os.environ:
        print('MIRO_TOKEN and MIRO_BOARD env vars are required')
        exit()

    if "SHEET_ID" not in os.environ:
        sheet_id='1uazcbZjvfpCHL2ZwPoVc0gWjK7R5pMO9D8cxkKQ40C0'

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SAMPLE_SPREADSHEET_ID = sheet_id
    SAMPLE_RANGE_NAME = 'Sheet1!A2:D'

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        index=0
        max=int(values[0][3])
        for row in values:
            index+=1
            print('sheet data=%s, %s, %s, %s,%s' % (index,row[0], row[1], row[2],max))
            vsm(index,row[0],int(row[1]), int(row[2]),max)

def vsm(step_number,step_name,value_time,total_time,max_time):

    # value_time: value-add time or process time
    # total_time: lead time, total or elapsed time, any time spend queuing or waiting

    # these have defaults
    grid_x=int(os.environ.get('GRID_X'))
    grid_y=int(os.environ.get('GRID_Y'))

    url = f"https://api.miro.com/v1/boards/{miro_board}/widgets"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": 'Bearer '+ miro_token
    }

    # each step has certian max rows and colums, if using just one step,
    # this allows for many row x cols combos which extend on the x-axis
    if "GRID_X" not in os.environ:
        grid_x = max_time
    if "GRID_Y" not in os.environ:
        grid_y = 1

    print (f"grid_x={grid_x} and grid_y={grid_y}")

    # math (based on fixed sticker size)
    x_spacer=130*grid_x+50
    y_spacer=130

    # vars
    counter=0
    x_counter=0
    x_offset=0
    y=0+(step_number *y_spacer*grid_y) + 130*step_number
    x=0

    # print the vsm data cards for this step
    while counter < total_time:

        print('---')
        print(counter)

        if counter+1<=value_time:
            color='#67c6c0'
        else:
            color='#f16c7f'

        # reset x counter every "grid_x" cards
        if (x_counter == grid_x):
            x_counter=0

        # x position increment
        x=x_counter*y_spacer+x_offset

        # reset x position for every row / "grid_x" cards
        # drop y position every "grid_x" cards (y position increment)
        if (counter % grid_x == 0):
            if counter != 0:
                print(f"NEW ROW: x ({x}) will reset, y ({y}) will drop")
                y+=y_spacer
                x=0+x_offset
                print(f" ---> new x ({x}), new y ({y})")

        # every "grid_y", create a new block (ie y position resets, and x positions increments)
        if (counter % (grid_x*grid_y) == 0):
            if counter != 0:
                print(f"NEW GRID: x ({x}) will increment, y ({y}) will reset")
                x_offset+=x_spacer
                y-=y_spacer*grid_y
                x=x_offset
                print(f" ---> new x ({x}), new y ({y})")

        if counter+1==value_time:
            text=value_time
        elif counter+1==total_time:
            text=total_time
        elif counter==0:
            text=step_name
            print(f"NEW STEP: x ({x}) will reset, y ({y}) will jump")
            print(f" ---> new x ({x}), new y ({y})")
        else:
            text=''
        payload = {"type": "sticker","text": str(text),"x": x,"y": y, "style": { "backgroundColor": color} }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200 or response.status_code == 201:
            print('Success!')
            print("%s credits remaining" % int(response.headers['X-RateLimit-Remaining'])  )

            if( int(response.headers['X-RateLimit-Remaining']) < 100):
                print('sleep, we do not want to upset the miro api gods')
                time.sleep(10)

        elif response.status_code == 429:
            print('Rate limited!')
            print(payload)
            print(response.headers)
            print(response.text)

            print('hail mary until proper try/catch and api step-back, we will just wait some more and try the request again...')
            time.sleep(30)
            payload = {"type": "sticker","text": "","x": x,"y": y, "style": { "backgroundColor": color} }
            response = requests.post(url, headers=headers, json=payload)

        else:
            print('???')
            print(payload)
            print(response.headers)
            print(response.text)

        counter+=1
        x_counter+=1

if __name__ == '__main__':
    main()
