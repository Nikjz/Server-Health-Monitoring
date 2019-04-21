import pandas as pd
from flask import Flask, render_template
from bandwidths import BANDWIDTHS
from flask import Flask, request, url_for  
import json

app = Flask(__name__)
 

def calculate(num_windows,bytes_agg,window_end_time,window_start_time,window_time,data):
    
    for i in range(num_windows):
        sub_data = data[(data.timestamp > window_start_time) & (data.timestamp <= window_end_time)]
        bytes_agg['window_num'].append(i)
        bytes_agg['window_end'].insert(0, window_end_time)
        bytes_agg['bytes_ts'].insert(0, sum(sub_data.bytes_ts))
        bytes_agg['bytes_fs'].insert(0, sum(sub_data.bytes_fs))
        window_end_time -= window_time
        window_start_time -= window_time
        
    return bytes_agg
    
@app.route('/', methods=['POST'])
def content_post():    
    device = request.form['devid']
    window_end_time = int(request.form['endtime'])
    window_time = int(request.form['timewin'])
    num_windows = int(request.form['numwin'])
    json_string = json.dumps(BANDWIDTHS)
    data = pd.read_json(json_string, convert_dates=False)
    bytes_agg = {"window_num":[], "window_end": [], "bytes_ts": [], "bytes_fs": [], "device_id": device, "devid_found": 1}
    if device not in list(data.device_id):
        bytes_agg['devid_found'] = 0
        return render_template('content.html',dictionary=bytes_agg)
    if window_end_time is None:
        window_end_time = 1524835983
    if num_windows is None:
        num_windows = 10
    if window_time is None:
        window_time = 60
    window_start_time = window_end_time - window_time
    data = data[data.device_id == device]
    bytes_agg=calculate(num_windows,bytes_agg,window_end_time,window_start_time,window_time,data)
    return render_template('content.html',dictionary=bytes_agg)

@app.route('/')
def content():
    window_end_time = 1524835983
    window_time = 60
    window_start_time = window_end_time - window_time
    num_windows = 10
    json_string = json.dumps(BANDWIDTHS) 
    data = pd.read_json(json_string, convert_dates=False)
    device = data.device_id[0]
    data = data[data.device_id == device]
    bytes_agg = {"window_num":[], "window_end": [], "bytes_ts": [], "bytes_fs": [], "device_id": device, "devid_found": 1}       
    bytes_agg=calculate(num_windows,bytes_agg,window_end_time,window_start_time,window_time,data)        
    return render_template('content.html',dictionary=bytes_agg)
    
  
if __name__ == '__main__':
	app.run()
