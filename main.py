# project: p4
# submitter: ratushko
# partner: none
# hours: 11

# Dataset from https://data-cityofmadison.opendata.arcgis.com/datasets/cityofmadison::polling-places

import pandas as pd
from flask import Flask, request, Response, jsonify
import json
import re
import time
import matplotlib.pyplot as plt
import matplotlib
import io
matplotlib.use('Agg')

app = Flask(__name__)
df = pd.read_csv("main.csv")
ip_dict = {}

home_visits = 0
def count_visit():
    global home_visits
    home_visits += 1
    
num_subscribed = 0
def num():
    global num_subscribed
    num_subscribed += 1
    
click_thru_a = 0
click_thru_b = 0

@app.route('/')
def home():
    count_visit()
    if home_visits <= 10:
        if (home_visits % 2) == 0:
            with open("index1.html") as f:
                html = f.read()
                return """<html><body style="background-color:lightpink">""" + html
        else:
            with open("index2.html") as f:
                html = f.read()
                return """<html><body style="background-color:lightblue">""" + html
    
    if click_thru_a > click_thru_b:
        with open("index1.html") as f:
            html = f.read()
            return """<html><body style="background-color:lightpink">""" + html
    else: 
        with open("index2.html") as f:
            html = f.read()
            return """<html><body style="background-color:lightblue">""" + html

@app.route("/dashboard_1.svg")
def dashboard_1():  
    if "bins" in request.args:
        bins = int(request.args["bins"])
    else: 
        bins = 10
    
    fig, ax = plt.subplots(figsize=(15, 5))
    df.hist(ax=ax, bins=bins, column='X')
    
    plt.title("X-Coordinates of Polling Places in Dane County")
    plt.xlabel("Range of x-coordinates")
    plt.ylabel("Frequency")
    plt.tight_layout()
    
    f = io.StringIO() 
    fig.savefig(f, format="svg")
    plt.close()
    
    return Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})
            
@app.route("/dashboard_2.svg")
def dashboard_2():    
    fig, ax = plt.subplots(figsize=(21, 7))
    df["WARD"].plot.bar(ax=ax)
    ax.set_title("Ward #s of Polling Places in Dane County")
    ax.set_xlabel("Ward # (X-Axis)")
    ax.set_ylabel("Ward # (Y-Axis)")
    plt.tight_layout()
    
    f = io.StringIO() 
    fig.savefig(f, format="svg")
    plt.close()
    
    return Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]\w+[.]\w{2,3}$", email)) > 0:
        num()
        with open("emails.txt", "a") as f:
            f.write(email + "\n") 
        return jsonify(f"Thanks, your subscriber number is {num_subscribed}!")
    return jsonify(f"Oops, invalid email!")

@app.route('/browse.html')
def browse():
    with open("browse.html") as f:
        html_file = df.to_html()
    
    return "<h1>Browse</h1>" + html_file

@app.route('/browse.json')
def browse_json():
    browse_json = jsonify(df.to_dict("records")) 
    ip_address = request.remote_addr

    if ip_address not in ip_dict:
        curr_time = time.time()
        ip_dict[ip_address] = curr_time
        return browse_json
        
    if ip_address in ip_dict:
        curr_time = time.time()
        if curr_time - ip_dict[ip_address] > 60:
            return browse_json
        else:
            return Response("<b>Go away</b>",
                                      status=429,
                                      headers={"Retry-After": "60 seconds"})

@app.route('/visitors.json')
def visitors_json():
    return ip_dict

@app.route("/donate.html")
def donate():
    global click_thru_a
    global click_thru_b
    if "from" in request.args:
        version = request.args['from']
        if version == "A":
            click_thru_a += 1
        else:
            click_thru_b += 1

    return """<html><body>
              <h1>Donations</h1>
              Please make one to help save democracy!
              <body></html>"""

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.