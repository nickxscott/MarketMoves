#flask imports
from flask import Flask,render_template,request,url_for,flash,jsonify,redirect, Markup, send_file

#scheduling imports
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

#custom imports
from funs import *
from forms import *
from get import get_request
#from curl_cffi import requests

#python imports
from datetime import date

app = Flask(__name__, static_url_path='/static')
sk = ''.join(random.choices(string.ascii_uppercase +string.ascii_lowercase+string.digits, k=60))
app.secret_key = sk

#create schedule for get requests
scheduler = BackgroundScheduler()
trigger = CronTrigger(
        year="*", month="*", day="*", hour="*", minute="*/10", second="0"
    )
scheduler.add_job(get_request, trigger=trigger)
scheduler.start()


@app.route('/',methods=['GET','POST']) 
def home():
	form=tickerForm()
	err=False
	custom_return=False
	today=date.today()
	#session = requests.Session(impersonate="chrome")
	if request.method!='POST':
		symbol='SPY'
		form.ticker.data=symbol
		form.tail.data='auto'
		period='3mo'
		form.period.data=period
	else:
		symbol=form.ticker.data.replace(" ", "").upper()
		symbol=symbol.replace(".", "-")
		period=form.period.data
	#get daily data for past 5 years and calculate change
	start_date = yf.download(	symbol,
								period=period,
								auto_adjust=True
								#session=session
								).index.min()

	#get all max historical data for price plot
	df_max=yf.download(symbol, 
						period='max',
						auto_adjust=True
						#session=session
						)


	df_max.columns=df_max.columns.droplevel('Ticker')
	df_max=df_max.reset_index()
	#filter max dataset to only dates within selected period
	df_returns=df_max.loc[df_max.Date>=start_date]


	if len(df_returns)<1:
		err=True
		plot=False
		price_plot=False
		text=False
		return_=False
		latest_date=False
		ticker=False
	else:
		#get ticker data - try info method first, just use symbol input if it fails
		try:
			ticker=yf.Ticker(symbol).info['longName']
		except:
			ticker=symbol
		prev=[]
		change=[np.NaN]
		for index, row in df_returns.iterrows():
			prev.append(row['Close'])
			if len(prev)>1:
				chg=(row['Close']-prev[-2])/prev[-2]
				change.append(chg*100)
		df_returns['change']=change
		plot, text, return_, latest_date, custom_return=plot_return(df_returns=df_returns, tail=form.tail.data, return_=form.return_.data)

		#calculate moving averages
		df_max['ma_30']=df_max['Close'].rolling(30).mean()
		df_max['ma_50']=df_max['Close'].rolling(50).mean()
		df_max['ma_100']=df_max['Close'].rolling(100).mean()
		df_max['ma_200']=df_max['Close'].rolling(200).mean()
		df_max=df_max.loc[df_max.Date>=df_returns.Date.min()]

		price_plot=plot_price(df_max)

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

