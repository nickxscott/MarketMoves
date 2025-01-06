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
	custom_return=False
	today=date.today()
	if request.method!='POST':
		symbol='SPY'
		form.ticker.data=symbol
		form.tail.data='auto'
	else:
		symbol=form.ticker.data.replace(" ", "").upper()
		symbol=symbol.replace(".", "-")

	#get ticker data
	ticker=yf.Ticker(symbol).info

	if len(ticker)<8:
		err=True
		plot=False
		price_plot=False
		text=False
		return_=False
		latest_date=False
	else:
		#get daily data for past 5 years and calculate change
		df_returns = yf.download(symbol, start=date.today()-timedelta(days=365*5), end=date.today())
		prev=[]
		change=[np.NaN]
		for index, row in df_returns.iterrows():
			prev.append(row['Close'][symbol])
			if len(prev)>1:
				chg=(row['Close'][symbol]-prev[-2])/prev[-2]
				change.append(chg*100)
		df_returns['change']=change
		
		plot, text, return_, latest_date, custom_return=plot_return(df=df_returns, tail=form.tail.data, return_=form.return_.data)

		price_plot=plot_price(df_returns)

	return render_template("home.html", form=form, 
										ticker=ticker, 
										err=err, 
										plot=plot, 
										text=text, 
										return_=return_,
										custom_return=custom_return,
										latest_date=latest_date,
										price_plot=price_plot
										)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404


@app.errorhandler(500)
def server_error(e):
	return render_template("500.html"),500


if __name__ == "__main__":
	app.run(host='localhost', port=5000,debug = True)

