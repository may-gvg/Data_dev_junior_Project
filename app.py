import csv
import io
import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import urllib3
from flask import Flask, render_template, redirect, request, flash, send_file, session
from json2html import *
from werkzeug.utils import secure_filename
from wtforms import StringField, Form, validators, SubmitField, SelectField

from flask_session import Session

UPLOAD_FOLDER = 'static/analiza'
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
        print("Kwota: " + str(money))
        print("currenty: " + currency)
        przelicz = str(round(money * wartosc, 3))
        print("przelicz: " + przelicz)
        return render_template("waluty.html", wynik=przelicz, options=options, args=args, data3=data3, data=data)


def nice_loader(loader):
    global df2, data, data1, data2, data3, data4, data5
    if loader == 'csv':
        df2 = pd.read_csv('static/analiza/analiza.csv')
    if loader == 'xls':
        df2 = pd.read_excel('static/analiza/analiza.xls')
    if loader == 'db':
        cnx = sqlite3.connect('static/analiza/analiza.db')
        df2 = pd.read_sql_query("SELECT * FROM courthouse_security_logs", cnx)
    data = df2.iloc[:, 0].value_counts().sort_values(ascending=False).head(50)
    data1 = df2.iloc[:, 1].value_counts().sort_values(ascending=False).head(50)
    data2 = df2.iloc[:, 2].value_counts().sort_values(ascending=False).head(50)
    data3 = df2.iloc[:, 3].value_counts().sort_values(ascending=False).head(50)
    data4 = df2.iloc[:, 4].value_counts().sort_values(ascending=False).head(50)
    data5 = df2.iloc[:, 5].value_counts().sort_values(ascending=False).head(50)


@app.route('/')
def homepage():
    global df2
    loader = request.args.get('loader', "none")
    if loader == "none":
        loader2 = session.get('loader')
        if not loader2:
            loader = 'csv'
        else:
            loader = loader2
    session['loader'] = loader
    nice_loader(loader)

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

    data3 = []
    for index, row in df2.iterrows():
        l = []
        for i in range(0, row.size):
            l.append(row[i])
        data3.append(l)

    data4 = []
    for c in df2.keys():
        data4.append(c)
    return render_template("homepage.html", args=args, data=data, data2=data3, data3=data3, data4=data4,
                           area_data=area_data.__str__(),
                           bar_data=bar_data.__str__(), area_labels=area_labels.__str__(),
                           bar_labels=bar_labels.__str__())


cmap = plt.get_cmap("Set2")
colors = cmap(np.array([1, 2, 3, 4, 5, 6, 7]))


@app.route('/analysis')
def analysis():
    global df2
    loader = session.get('loader')
    if not loader:
        loader = 'csv'
    nice_loader(loader)
    x = df2.describe()
    z = df2.median(numeric_only=True)
    z = pd.DataFrame(z)
    y = df2.mode().head(3)
    return render_template("analysis.html", data7=x.to_html(), data8=y.to_html(), data9=z.to_html())


# kolumna 1
def do_plot():
    # bar
    # Loading
    global df2, data
    plt.figure(figsize=(12, 6))
    plt.title('col 1 value count')
    sns.barplot(x=data.index, y=data, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot1():
    # line
    # Loading
    global df2, data
    plt.figure(figsize=(12, 6))
    plt.title('col 1 value count')
    sns.lineplot(x=data.index, y=data, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot2():
    # kołowy
    # Loading
    global df2, data
    plt.figure(figsize=(12, 6))
    plt.title('col 1 value count')
    plt.pie(data, labels=data.index, colors=colors, autopct='%1.1f%%', pctdistance=1.1, labeldistance=1.2,
            startangle=150, shadow=True)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


# kolumna 2

def do_plot3():
    # bar
    # Loading
    global df2, data1
    plt.figure(figsize=(12, 6))
    plt.title('col 2 value count')
    sns.barplot(x=data1.index, y=data1, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot4():
    # line
    # Loading
    global df2, data1
    plt.figure(figsize=(12, 6))
    plt.title('col 2 value count')
    sns.lineplot(x=data1.index, y=data1, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot5():
    # kołowy
    # Loading
    global df2, data1
    plt.figure(figsize=(12, 6))
    plt.title('col 2 value count')
    plt.pie(data1, labels=data1.index, colors=colors, autopct='%1.1f%%', pctdistance=1.1, labeldistance=1.2,
            startangle=150, shadow=True)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


# kolumna 3


def do_plot6():
    # bar
    # Loading
    global df2, data2
    plt.figure(figsize=(12, 6))
    plt.title('col 3 value count')
    sns.barplot(x=data2.index, y=data2, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot7():
    # line
    # Loading
    global df2, data2
    plt.figure(figsize=(12, 6))
    plt.title('col 3 value count')
    sns.lineplot(x=data2.index, y=data2, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot8():
    # kołowy
    # Loading
    global df2, data2
    plt.figure(figsize=(12, 6))
    plt.title('col 3 value count')
    plt.pie(data2, labels=data2.index, autopct='%1.1f%%', colors=colors, pctdistance=1.1, labeldistance=1.2,
            startangle=150, shadow=True)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


# kolumna 4

def do_plot9():
    # bar
    # Loading
    global df2, data3
    plt.figure(figsize=(12, 6))
    plt.title('col 4 value count')
    sns.barplot(x=data3.index, y=data3, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot10():
    # line
    # Loading
    global df2, data3
    plt.figure(figsize=(12, 6))
    plt.title('col 4 value count')
    sns.lineplot(x=data3.index, y=data3, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot11():
    # kołowy
    # Loading
    global df2, data3
    plt.figure(figsize=(12, 6))
    plt.title('col 4 value count')
    plt.pie(data3, labels=data3.index, autopct='%1.1f%%', colors=colors, pctdistance=1.1, labeldistance=1.2,
            startangle=150, shadow=True)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


# kolumna 5

def do_plot12():
    # bar
    # Loading
    global df2, data4
    plt.figure(figsize=(12, 6))
    plt.title('col 5 value count')
    sns.barplot(x=data4.index, y=data4, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot13():
    # line
    # Loading
    global df2, data4
    plt.figure(figsize=(12, 6))
    plt.title('col 5 value count')
    sns.lineplot(x=data4.index, y=data4, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot14():
    # kołowy
    # Loading
    global df2, data4
    plt.figure(figsize=(12, 6))
    plt.title('col 5 value count')
    plt.pie(data4, labels=data4.index, autopct='%1.1f%%', colors=colors, pctdistance=1.1, labeldistance=1.2,
            startangle=150, shadow=True)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


# kolumna 6

def do_plot15():
    # bar
    # Loading
    global df2, data5
    plt.figure(figsize=(12, 6))
    plt.title('col 6 value count')
    sns.barplot(x=data5.index, y=data5, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot16():
    # line
    # Loading
    global df2, data5
    plt.figure(figsize=(12, 6))
    plt.title('col 6 value count')
    sns.lineplot(x=data5.index, y=data5, palette='Set2')
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


def do_plot17():
    # kołowy
    # Loading
    global df2, data5
    plt.figure(figsize=(12, 6))
    plt.title('col 6 value count')
    plt.pie(data5, labels=data5.index, autopct='%1.1f%%', colors=colors, pctdistance=1.1, labeldistance=1.2,
            startangle=150, shadow=True)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


@app.route('/desc2/<typ>', methods=['GET'])
def desc(typ="bar"):
    loader = session.get('loader')
    if not loader:
        loader = 'csv'
    nice_loader(loader)
    if typ == 'bar':
        bytes_obj = do_plot()
    if typ == 'pie':
        bytes_obj = do_plot2()
    if typ == 'line':
        bytes_obj = do_plot1()
    # wybór do_plot albo do_plot1 albo do_plot2
    return send_file(bytes_obj,
                     download_name='plot.png',
                     mimetype='image/png')


@app.route('/desc3/<typ>', methods=['GET'])
def desc3(typ="bar"):
    if typ == 'bar':
        bytes_obj = do_plot3()
    if typ == 'pie':
        bytes_obj = do_plot5()
    if typ == 'line':
        bytes_obj = do_plot4()
    # wybór do_plot albo do_plot1 albo do_plot2
    return send_file(bytes_obj,
                     download_name='plot.png',
                     mimetype='image/png')


@app.route('/desc4/<typ>', methods=['GET'])
def desc4(typ="bar"):
    if typ == 'bar':
        bytes_obj = do_plot6()
    if typ == 'pie':
        bytes_obj = do_plot8()
    if typ == 'line':
        bytes_obj = do_plot7()
    # wybór do_plot albo do_plot1 albo do_plot2
    return send_file(bytes_obj,
                     download_name='plot.png',
                     mimetype='image/png')


@app.route('/desc5/<typ>', methods=['GET'])
def desc5(typ="bar"):
    if typ == 'bar':
        bytes_obj = do_plot9()
    if typ == 'pie':
        bytes_obj = do_plot11()
    if typ == 'bar':
        bytes_obj = do_plot9()
    if typ == 'line':
        bytes_obj = do_plot10()
    # wybór do_plot albo do_plot1 albo do_plot2
    return send_file(bytes_obj,
                     download_name='plot.png',
                     mimetype='image/png')


@app.route('/desc6/<typ>', methods=['GET'])
def desc6(typ="bar"):
    if typ == 'bar':
        bytes_obj = do_plot12()
    if typ == 'pie':
        bytes_obj = do_plot14()
    if typ == 'line':
        bytes_obj = do_plot13()
    # wybór do_plot albo do_plot1 albo do_plot2
    return send_file(bytes_obj,
                     download_name='plot.png',
                     mimetype='image/png')


@app.route('/desc7/<typ>', methods=['GET'])
def desc7(typ="bar"):
    if typ == 'bar':
        bytes_obj = do_plot15()
    if typ == 'pie':
        bytes_obj = do_plot17()
    if typ == 'line':
        bytes_obj = do_plot16()
    # wybór do_plot albo do_plot1 albo do_plot2
    return send_file(bytes_obj,
                     download_name='plot.png',
                     mimetype='image/png')


# kolumna 1
@app.route('/esc', methods=["GET", "POST"])
def desca():
    form = Wybieraczka(request.form)
    typ = 'bar'
    if request.method == 'POST' and form.validate():
        typ = form.typ.data
        print(typ)
    return render_template("visual.html", form=form, typ=typ)


# kolumna 2
@app.route('/esc1', methods=["GET", "POST"])
def desca1():
    form = Wybieraczka(request.form)
    typ = 'bar'
    if request.method == 'POST' and form.validate():
        typ = form.typ.data
        print(typ)
    return render_template("visual1.html", form=form, typ=typ)


# kolumna 3
@app.route('/esc2', methods=["GET", "POST"])
def desca2():
    form = Wybieraczka(request.form)
    typ = 'bar'
    if request.method == 'POST' and form.validate():
        typ = form.typ.data
        print(typ)
    return render_template("visual2.html", form=form, typ=typ)


# kolumna 4
@app.route('/esc3', methods=["GET", "POST"])
def desca3():
    form = Wybieraczka(request.form)
    typ = 'bar'
    if request.method == 'POST' and form.validate():
        typ = form.typ.data
        print(typ)
    return render_template("visual3.html", form=form, typ=typ)


# kolumna 5
@app.route('/esc4', methods=["GET", "POST"])
def desca4():
    form = Wybieraczka(request.form)
    typ = 'bar'
    if request.method == 'POST' and form.validate():
        typ = form.typ.data
        print(typ)
    return render_template("visual4.html", form=form, typ=typ)


# kolumna 6
@app.route('/esc5', methods=["GET", "POST"])
def desca5():
    form = Wybieraczka(request.form)
    typ = 'bar'
    if request.method == 'POST' and form.validate():
        typ = form.typ.data
        print(typ)
    return render_template("visual5.html", form=form, typ=typ)


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
        preview = json2html.convert(json=r.data.decode('UTF-8'),
                                    table_attributes="class=\"table table-bordered table-hover\"")
        with open('static/analiza/anal.json', 'wb') as f:
            f.write(r.data)
    return render_template("jsonreader.html", form=form, preview=preview)


class JsonForm(Form):
    json = StringField('json url:', [validators.InputRequired(), validators.length(max=1000)])
    send = SubmitField('send')


@app.route('/jsonreader', methods=["GET", "POST"])
def aqq():
    form = JsonForm(request.form)
    if request.method == 'POST':
        json = form.json.data
        print(json)
        p = pd.read_json(json)
        print(p)
    return render_template("jsonreader.html", form=form)


class Wybieraczka(Form):
    typ = SelectField('type:', choices=[('bar', 'Bar'), ('pie', 'Pie'), ('line', 'Line')])
    send = SubmitField("plot")


@app.route('/sciagnij/')
def plot_csv():
    return send_file('static/analiza/output.csv',
                     mimetype='text/csv',
                     download_name='output.csv',
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


@app.route('/numpy')
def numpy_page():
    args = ""
    return render_template("numpy.html", args=args)


@app.route('/pandas')
def pandas_page():
    args = ""
    return render_template("pandas.html", args=args)


@app.route('/pyspark')
def pyspark_page():
    args = ""
    return render_template("pyspark.html", args=args)


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
