#python imports
import string
import random
import json
import numpy as np
import pandas as pd
import scipy.stats as stats
from datetime import date, timedelta

#app-specific imports
import yfinance as yf
import plotly
import plotly.figure_factory as ff

def plot_return(ticker, tail=None, return_=None):
    #get daily data for past 5 years and calculate change
    df_returns = yf.download(ticker, start=date.today()-timedelta(days=365*5), end=date.today())
    custom_return=False

    prev=[]
    change=[np.NaN]
    for index, row in df_returns.iterrows():
        prev.append(row['Close'][ticker])
        if len(prev)>1:
            chg=(row['Close'][ticker]-prev[-2])/prev[-2]
            change.append(chg)
    df_returns['change']=change
        
    #create plot
    fig = ff.create_distplot([df_returns.change.tolist()[1:]], group_labels=['returns'],show_hist=False,show_rug=False)

    #get latest return by default, else get return entered
    if return_ is None:
        ret=df_returns.iloc[-1].change.values[0]
    else:
        custom_return=True
        ret=float(return_)
        #convert percent to decimal before plugging into formula
        ret=ret/100
    
    print('return: ',round(ret*100,2),'%')
    #calculate z score and cumulative distribution
    x=ret
    u=df_returns.change.mean()
    std=df_returns.change.std()
    z=(x-u)/std
    right_tail=round(stats.norm.sf(z)*100,2)
    left_tail=round((1-stats.norm.sf(z))*100,2)

    #set tail default
    if not tail:
        if x > 0:
            tail='right'
        else:
            tail='left'
        
    #plot return and fill under curve   
    if tail=='right':
        x1 = [xc for xc in fig.data[0].x if xc >= ret]
        y1 = fig.data[0].y[-len(x1):]
        #print('probability that return would be equal or higher: ', right_tail,'%')
        text='probability that return would be equal or higher: '+str(right_tail)+'%'
    else:
        x1 = [xc for xc in fig.data[0].x if xc <= ret]
        y1 = fig.data[0].y[:len(x1)]
        #print('probability that return would be equal or lower: ', left_tail,'%')
        text='probability that return would be equal or lower: '+str(left_tail)+'%'
    fig.add_scatter(x=x1, y=y1,fill='tozeroy', mode='none' , fillcolor='rgba(158, 156, 157, 0.5)')

    # format plot
    fig.update_traces(  showlegend=False, line=dict(color='red',  width=3))
    fig.update_layout(  {'plot_bgcolor':'black', 
                       'paper_bgcolor':'grey'},
                       hovermode=False,
                        dragmode=False,
                        xaxis_title='Return (decimal)')
    fig.update_yaxes(showticklabels=False)

    return_display=round(x*100,2)

    #get most recent date in df
    latest_date=df_returns.index.max().date()
    latest_date_display=str(latest_date.day)+'/'+str(latest_date.month)+'/'+str(latest_date.year)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder), text, return_display, latest_date, custom_return