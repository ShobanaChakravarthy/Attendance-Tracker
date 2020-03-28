from flask import Flask,render_template,request,send_file
import requests
import json
import pandas
import csv
import datetime

app=Flask(__name__)

def chk_csv():
    with open('static/emp.csv') as f:
        data = dict(filter(None, csv.reader(f)))
    return data
    
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/capture',methods=['POST'])
def capture():
    if request.method == "POST":
        try:
            emp_id__ = request.form["emp_id"]
            data = chk_csv()
            if emp_id__ in data.keys():
                time__ = request.form["str_time"]
                newtime=time__[0:2]
                newtime+=time__[3:5]
                if int(newtime) <= 2400:
                    time_fin__=newtime
                inoff__ = request.form["inoff"]
                scrum__ = request.form["scrum"]
                if inoff__ == "login":
                    PARAMS = {
                    'Id': emp_id__,
                    'X': time_fin__,
                    'Y': "",
                    'Z': 'insert',
                    'A': scrum__
                    }
                else:
                    PARAMS = {
                    'Id': emp_id__,
                    'X': "",
                    'Y': time_fin__,
                    'Z': 'insert',
                    'A': scrum__
                    }
                r = requests.get('https://fsgrspskd7.execute-api.us-west-2.amazonaws.com/PostApiFinal/', json = PARAMS)
                return render_template("index.html",text=r.text)
                #return render_template("index.html",text="You are added Successfully")
            else:
                return render_template("index.html",text="Employee ID doesn't exist")
        except Exception as e:
            return render_template("index.html", text=str(e))

@app.route('/display',methods=["POST"])
def display():
    global filename
    if request.method == "POST":
        try:
            scrumfet__ = request.form["scrumfet"]
            print(scrumfet__)
            PARAMS = {
                'Id': "0",
                'X': "0",
                'Y': "0",
                'Z': scrumfet__,
                'A': "0"        }
            r = requests.get('https://fsgrspskd7.execute-api.us-west-2.amazonaws.com/PostApiFinal/', json = PARAMS)
            #b=str([{"Id": "679882", "LoginTime": "0900", "LogoutTime": "1800", "Scrum": "scrum1"}, {"Id": "681472", "LoginTime": "0900", "LogoutTime": "1800", "Scrum": "scrum1"}])
            b=r.text
            b = b.replace("'", '"')
            a = json.loads(b)
            df=pandas.DataFrame()
            Employee_Id = pandas.Series([]) 
            Login_Time = pandas.Series([]) 
            Logout_Time = pandas.Series([]) 
            Scrum = pandas.Series([]) 
            Employee_Name = pandas.Series([])
            j=0
            data = chk_csv()
            for i in a:
                Employee_Id[j]=i["Id"]
                Login_Time[j]=i["LoginTime"]
                Logout_Time[j]=i["LogoutTime"]
                Scrum[j]=i["Scrum"]
                Employee_Name[j] = data[Employee_Id[j]]
                j=j+1
            df.insert(0, "Employee Id", Employee_Id)
            df.insert(1, "Employee Name", Employee_Name)
            df.insert(2, "Login Time", Login_Time)
            df.insert(3, "Logout Time", Logout_Time)
            df.insert(4, "Scrum", Scrum) 
            filename=datetime.datetime.now().strftime("%Y-%m-%d"+".csv")
            df.to_csv(filename,index=None)
            return render_template("fetch.html",column_names=df.columns.values, row_data=list(df.values.tolist()), btn='download.html')
        except Exception as e:
            return render_template("index.html", text=str(e))

@app.route("/download-file/")
def download():
    return send_file(filename, attachment_filename=filename, as_attachment=True)


if __name__=='__main__':    
    app.run(debug=True)
