import csv
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, abort, make_response
from flask import send_file
app = Flask(__name__)


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


@app.route('/sciagnij/')
def plot_csv():
    return send_file('static/analiza/output.csv',
                     mimetype='text/csv',
                     attachment_filename='output.csv',
                     as_attachment=True)


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


@app.route('/pytest')
def pytest_page():
    args = ""
    return render_template("pytest.html", args=args)


@app.route('/analiza')
def analiza_page():
    args = ""
    return render_template("analiza.html", args=args)


@app.route('/analiza2')
def analiza2_page():
    args = ""
    return render_template("analiza2.html", args=args)


if __name__ == '__main__':
    app.run(debug=True)

