
import requests
import json
import time

# pip3 install requests

url = "https://api.miro.com/v1/boards/XXX/widgets"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer XXX"
}

value_time = int(input("Enter Value Add (2) : ") or "2")
total_time = int(input("Enter Total Time (6) : ") or "6")

# grid inputs
grid_rows = int(input("Enter grid_rows (5) : ") or "5")
grid_cols = int(input("Enter grid_cols (5) : ") or "5")

# math (based on fixed sticker size)
x_spacer=130*grid_rows+50
y_spacer=130

# vars
counter=0
x_counter=0
x_offset=0
y=0
x=0

# create the cards the explain this vsm step:
payload = {"type": "sticker","text": "VAT: "+str(value_time),"x": -180,"y": 0, "style": { "backgroundColor": "#67c6c0"} }
print(payload)
response = requests.post(url, headers=headers, json=payload)

payload = {"type": "sticker","text": "Total: "+str(total_time),"x": -300,"y": 0, "style": { "backgroundColor": "#f16c7f"} }
print(payload)
response = requests.post(url, headers=headers, json=payload)

payload = {"type": "sticker","text": "Step 1","x": -440,"y": 0, "style": { "backgroundColor": "#fff9b1"} }
print(payload)
response = requests.post(url, headers=headers, json=payload)

while counter < total_time:

    print('---')
    print(counter)

    if counter+1<=value_time:
        color='#67c6c0'
    else:
        color='#f16c7f'

    # reset x counter every "grid_rows" cards
    if (x_counter == grid_rows):
        x_counter=0

    # x position increment
    x=x_counter*y_spacer+x_offset

    # reset x position every "grid_rows" cards
    # drop y position every "grid_rows" cards (y position increment)
    if (counter % grid_rows == 0):
        if counter != 0:
            print('x reset, y drop...')
            y+=y_spacer
            x=0+x_offset

    # every "grid_cols", create a new block (ie y position resets, and x positions increments)
    if (counter % (grid_rows*grid_cols) == 0):
        if counter != 0:
            print('y reset, x increment')
            x_offset+=x_spacer
            y=0
            x=x_offset

    payload = {"type": "sticker","text": "","x": x,"y": y, "style": { "backgroundColor": color} }
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
