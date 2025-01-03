#flask imports
from flask import Flask,render_template,request,url_for,flash,jsonify,session,redirect, Markup, send_file
from flask_session import Session

#custom imports
from funs import *
from forms import *

#python imports
from datetime import date

app = Flask(__name__, static_url_path='/static')
sk = ''.join(random.choices(string.ascii_uppercase +string.ascii_lowercase+string.digits, k=60))
app.secret_key = sk


@app.route('/',methods=['GET','POST']) 
def home():
	form=tickerForm()
	err=False
	today=date.today()
	if request.method=='GET':
		symbol='SPY'
		form.ticker.data=symbol
	else:
		symbol=form.ticker.data.replace(" ", "").upper()

	#get ticker data
	ticker=yf.Ticker(symbol).info

	if len(ticker)==1:
		err=True
		plot=False
		text=False
		return_=False
		latest_date=False
	else:
		plot, text, return_, latest_date, custom_return=plot_return(ticker=symbol, tail=form.tail.data, return_=form.return_.data)

	print(form.return_.data)

	return render_template("home.html", form=form, 
										ticker=ticker, 
										err=err, 
										plot=plot, 
										text=text, 
										return_=return_,
										custom_return=custom_return,
										latest_date=latest_date
										)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404


@app.errorhandler(500)
def server_error(e):
	return render_template("500.html"),500


if __name__ == "__main__":
	app.run(host='localhost', port=5000,debug = True)

