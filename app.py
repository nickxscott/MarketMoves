#flask imports
from flask import Flask,render_template,request,url_for,flash,jsonify,session,redirect, Markup, send_file

#scheduling imports
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

#custom imports
from funs import *
from forms import *
from get import get_request
from curl_cffi import requests

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
	session = requests.Session(impersonate="chrome")
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
								session=session).index.min()

	#get all max historical data for price plot
	df_max=yf.download(symbol, period='max', session=session)
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
		#get ticker data
		ticker=yf.Ticker(symbol,session=session).info
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
		ma_30=[]
		ma_50=[]
		ma_100=[]
		ma_200=[]
		for index, row in df_max.iterrows():
		    thirty=df_max.loc[index-29:index].Close
		    fifty=df_max.loc[index-49:index].Close
		    onehund=df_max.loc[index-99:index].Close
		    twohund=df_max.loc[index-199:index].Close
		    if len(thirty)==30:
		        ma_30.append(thirty.mean())
		    else:
		        ma_30.append(None)
		    if len(fifty)==50:
		        ma_50.append(fifty.mean())
		    else:
		        ma_50.append(None)
		    if len(onehund)==100:
		        ma_100.append(onehund.mean())
		    else:
		        ma_100.append(None)
		    if len(twohund)==200:
		        ma_200.append(twohund.mean())
		    else:
		        ma_200.append(None)
		df_max['ma_30']=ma_30
		df_max['ma_50']=ma_50
		df_max['ma_100']=ma_100
		df_max['ma_200']=ma_200
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

