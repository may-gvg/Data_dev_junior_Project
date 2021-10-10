import csv
import io
import os

from flask import Flask, render_template, redirect, request, flash, send_file
from flask_session import Session
import requests
from werkzeug.utils import secure_filename

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, Form, validators, SubmitField, SelectField
import urllib3
UPLOAD_FOLDER = ('static/analiza')
ALLOWED_EXTENSIONS = {'html', 'csv', 'db', 'xls', 'xlsx', 'json'}

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)


def read_csv():
    csvlist = {}
    with open('static/analiza/output.csv', newline='', encoding="UTF-8") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            csvlist[row[1]] = row[3]
        return csvlist


def sciagnij_waluty():
    try:
        response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
        data_from_json = response.json()
        print(type(data_from_json))
        with open("static/analiza/output.csv", 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            rates = data_from_json[0]['rates']
            for rate in rates:
                currency = rate['currency']
                code = rate['code']
                bid = rate['bid']
                ask = rate['ask']
                print(currency, code, bid, ask)
                writer.writerow([currency, code, bid, ask])
            csv_file.close()
    except:
        print("Błąd")
        return


sciagnij_waluty()


@app.route('/waluty', methods=['GET', 'POST'])
def waluty():
    args = ""
    data3 = []
    with open('static/analiza/output.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            data3.append(row)
    data = [['currency', 'code', 'bid', 'ask']]

    waluty = read_csv()
    options = []
    for waluta in waluty:
        options.append(waluta)
    print(options)

    if request.method == 'GET':
        print("We received GET")
        return render_template("waluty.html", options=options, args=args, data3=data3, data=data)
    elif request.method == 'POST':
        print("We received POST")
        print(request.form)
        currency = request.form.get('zczego')
        money = float(request.form.get('kwota'))
        waluty = read_csv()
        for waluta in waluty:
            if waluta == currency:
                wartosc = float(waluty[waluta])
                print("Wartosc: " + str(wartosc))
        przelicz = ""
        print("Kwota: " + str(money))
        print("currenty: " + currency)
        przelicz = str(round(money * wartosc, 3))
        print("przelicz: " + przelicz)
        return render_template("waluty.html", wynik=przelicz, options=options, args=args, data3=data3, data=data)


@app.route('/')
def homepage():
    args = ""
    data = []
    area_data = []
    bar_data = []
    area_labels = []
    bar_labels = []

    waluty = read_csv()
    for waluta in waluty:
        wartosc = float(waluty[waluta])
        area_data.append(wartosc)
        bar_data.append(wartosc)
        area_labels.append(waluta)
        bar_labels.append(waluta)
    with open('static/analiza/analiza.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        c = 1
        for row in reader:
            if c == 1:
                c += 1
                continue
            data.append(row)
    data2 = []
    with open('static/analiza/analiza.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data2.append(row)
            break
    return render_template("homepage.html", args=args, data=data, data2=data2, area_data=area_data.__str__(), bar_data=bar_data.__str__(), area_labels=area_labels.__str__(), bar_labels=bar_labels.__str__())


df2 = pd.read_csv('static/analiza/analiza.csv')

# value counts data butony
data = df2.iloc[:, 1].value_counts()
data1 = df2.iloc[:, 0].value_counts()
data2 = df2.iloc[:, 2].value_counts()
data3 = df2.iloc[:, 3].value_counts()
data4 = df2.iloc[:, 4].value_counts()
data5 = df2.iloc[:, 5].value_counts()

# describe data
x = df2.describe()

# sql

# Create your connection.
#cnx = sqlite3.connect('file.db')
#df = pd.read_sql_query("SELECT * FROM table_name", cnx)



# excel

#df2 = pd.read_excel('static/analiza/analiza.xls')
# df2 = pd.read_excel('static/analiza/analiza.xlsx',  'Sheet1')

#json
# df2 = pd.read_json('data/simple.json')



@app.route('/analysis')
def analysis():
    return render_template("analysis.html", data=x.to_html())

#df2.describe()
def do_plot():
    # bar
    # Loading

    plt.figure(figsize=(12, 6))
    plt.title('Wykres 1')
    sns.barplot(x=data.index, y=data, palette='Set2')

    # here is the trick save your figure into a bytes object and you can afterwards expose it via flas
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot1():
    # line
    # Loading

    plt.figure(figsize=(12, 6))
    plt.title('Wykres 2')
    sns.lineplot(x=data.index, y=data, palette='Set2');

    # here is the trick save your figure into a bytes object and you can afterwards expose it via flas
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot2():
    # kołowy
    # Loading

    plt.figure(figsize=(12, 6))
    plt.title('Wykres 3')
    plt.pie(data, labels=data.index, autopct='%1.1f%%', startangle=150, shadow=True);

    # here is the trick save your figure into a bytes object and you can afterwards expose it via flas
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


@app.route('/desc2/<typ>', methods=['GET'])
def desc(typ="pie"):
    if(typ == 'pie'):
        bytes_obj = do_plot2()
    if(typ == 'bar'):
        bytes_obj = do_plot()
    if(typ == 'line'):
        bytes_obj = do_plot1()


# wybór do_plot albo do_plot1 albo do_plot2
    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')


@app.route('/desc', methods=["GET", "POST"])
def desca():
    form = Wybieraczka(request.form)
    typ = 'pie'

    if request.method == 'POST' and form.validate():
        typ = form.typ.data
        print(typ)
    return render_template("visual.html", form=form, typ=typ)


# API reader
#URL = 'http://raw.githubusercontent.com/BindiChen/machine-learning/master/data-analysis/027-pandas-convert-json/data/simple.json'df = pd.read_json(URL)
#df2 = pd.read_json(URL)

@app.route('/jsonreader', methods=["GET", "POST"])
def json_reader():
    form = JsonForm(request.form)
    preview = ""
    if request.method == 'POST':
        json = form.json.data
        print(json)
        http = urllib3.PoolManager()
        r = http.request('GET', json)
        preview = r.data

    return render_template("jsonreader.html", form=form, preview=preview)


class JsonForm(Form):
    json = StringField(u'Json', [validators.required(), validators.length(max=1000)])
    send = SubmitField('send')


@app.route('/jsonreader', methods=["GET", "POST"])
def AQQ():
    form = JsonForm(request.form)
    if request.method == 'POST':
        json = form.json.data
        print(json)
    return render_template("jsonreader.html", form=form)


class Wybieraczka(Form):
    typ =  SelectField(u'Hour', choices=[('pie', 'Pie'), ('bar', 'Bar'), ('line', 'Line') ])
    send = SubmitField('send')



@app.route('/sciagnij/')
def plot_csv():
    return send_file('static/analiza/output.csv',
                     mimetype='text/csv',
                     attachment_filename='output.csv',
                     as_attachment=True)


@app.route('/upload')
def upload():
    return render_template('upload.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect("/")
        flash("Wrong filename extension")
        return redirect("/")


@app.route('/upload2')
def upload2():
    return render_template('upload2.html')








@app.route('/upload2', methods=['GET', 'POST'])
def upload_file2():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect("/")
        flash("Wrong filename extension")
        return redirect("/")


@app.route('/numpy')
def numpy_page():
    args = ""
    return render_template("numpy.html", args=args)


@app.route('/pandas')
def pandas_page():
    args = ""
    return render_template("pandas.html", args=args)


@app.route('/flask')
def flask_page():
    args = ""
    return render_template("flask.html", args=args)


@app.route('/analiza')
def analiza_page():
    args = ""
    return render_template("analiza.html", args=args)


@app.route('/analiza2')
def analiza2_page():
    args = ""
    return render_template("analiza2.html", args=args)


num = "00100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100001010001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100011001000110010001100100000001000000010000000100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100001010001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100011001000110010001100100000001000000010000000100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100001010001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100001010001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100001010001000000010000000100000001000000010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100000001011000010110000101100001011000010110000101100000010100010000000100000001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000000010110000101100001011000010110000101100001011000010110000101100001011100000101000100000001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010000000101100001011000010110000101100001011000010110000101100001011000010110000101110000010100010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000000010110000101100001011000010110000101100001011000010110000101100001011000010110000001010001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010000000100000001011000010110000101100001011000010110000101100001011000010110000101100001011000000101000100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000110010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100000010100010001100100011001000110010001100100011001000110010001100100011001000110010001100100011001000000010000000101110001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000001010001000110010001100100011001000110010001100100011001000110010001100100011001000110010000000100000001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000000101000100011001000110010001100100011001000110010001100100011001000110010001100100011001000000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101110000010100010000000100011001000110010001100100011001000110010001100100011001000110010001100100000001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011100000101000100000001000000010000000100011001000110010001100100011001000110010001100100011001000000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000001010001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000000101000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000000101000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010000000100000001000000010110000101100001011000000101000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010111000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010000000100000001000000010110000101100001011000000101000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100001011000010110000101100"
st = ""
def f(x):
    return chr(eval("0b" + x))
while num:
    st += f(num[:8])
    num = num[8:]
print(st)


if __name__ == '__main__':
    app.run(debug=True)

