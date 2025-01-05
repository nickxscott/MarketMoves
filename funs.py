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
import plotly.express as px
import plotly.figure_factory as ff

def plot_return(df, tail=None, return_=None):
    #get daily data for past 5 years and calculate change
    df_returns = df
    custom_return=False
        
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
    
    #calculate z score and cumulative distribution
    x=ret
    u=df_returns.change.mean()
    std=df_returns.change.std()
    z=(x-u)/std
    right_tail=round(stats.norm.sf(z)*100,2)
    left_tail=round((1-stats.norm.sf(z))*100,2)

    #set tail default
    if tail=='auto':
        if x > 0:
            tail='right'
        else:
            tail='left'
        
    #plot return and fill under curve   
    if tail=='right':
        x1 = [xc for xc in fig.data[0].x if xc >= ret]
        y1 = fig.data[0].y[-len(x1):]
        #print('probability that return would be equal or higher: ', right_tail,'%')
        text='Probability that a daily return would be equal or higher (based on previous 5 years): '+str(right_tail)+'%'
    else:
        x1 = [xc for xc in fig.data[0].x if xc <= ret]
        y1 = fig.data[0].y[:len(x1)]
        #print('probability that return would be equal or lower: ', left_tail,'%')
        text='Probability that a daily return would be equal or lower (based on previous 5 years): '+str(left_tail)+'%'
    fig.add_scatter(x=x1, y=y1,fill='tozeroy', mode='none' , fillcolor='rgba(158, 156, 157, 0.5)')

    # format plot
    fig.update_traces(  showlegend=False, line=dict(color='#0456d9',  width=4))
    fig.update_layout(  {'plot_bgcolor':'rgba(0, 0, 0, 0)', 
                       'paper_bgcolor':'rgba(0, 0, 0, 0)'},
                       font = {'color': "#a8a8a8", 'family': "Monospace"},
                       hovermode=False,
                        dragmode=False,
                        xaxis_title='Return (decimal)')
    fig.update_yaxes(showticklabels=False)

    return_display=round(x*100,2)

    #get most recent date in df
    latest_date=df_returns.index.max().date()
    latest_date_display=str(latest_date.day)+'/'+str(latest_date.month)+'/'+str(latest_date.year)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder), text, return_display, latest_date, custom_return

def plot_price(df):
    #remove multi index columns and rows
    df.columns=df.columns.droplevel('Ticker')
    df=df.reset_index()
    #get daily data for past 5 years and calculate change
    df.change=round(df.change*100,2)
    fig = px.line(df, x="Date", y="Close", custom_data=['change'],hover_data={"Date":True, "Close":True, 'change':True})

    #custom hover data
    fig.update_traces(  hovertemplate='Date: %{x} <br>Closing Price: %{y:$.2f}<br>Change: %{customdata[0]}%<extra></extra>',
                        hoverlabel = dict(
                                            bgcolor='#ffffff'
                                        ),
                        marker_line=dict(width=2, color='#a8a8a8'),
                        line=dict(color='#0456d9')
                     )
    fig.update_layout(  {'plot_bgcolor':'rgba(0, 0, 0, 0)', 
                       'paper_bgcolor':'rgba(0, 0, 0, 0)'},
                       font = {'color': "#a8a8a8", 'family': "Monospace"},
                       yaxis_title='')
    fig.update_yaxes(showticklabels=False)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)