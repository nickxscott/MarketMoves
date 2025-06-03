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

def plot_return(df_returns, tail=None, return_=None):
    #get daily data for past 5 years and calculate change
    custom_return=False
    #create plot
    fig = ff.create_distplot([df_returns.change.tolist()[1:]], group_labels=['returns'],show_hist=False,show_rug=False)

    #get latest return by default, else get return entered
    if return_ is None:
        ret=df_returns.iloc[-1].change#.values[0]
    else:
        custom_return=True
        ret=float(return_)
    
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
        text='Probability that a daily return would be equal or higher: '+str(right_tail)+'%'
    else:
        x1 = [xc for xc in fig.data[0].x if xc <= ret]
        y1 = fig.data[0].y[:len(x1)]
        #print('probability that return would be equal or lower: ', left_tail,'%')
        text='Probability that a daily return would be equal or lower: '+str(left_tail)+'%'
    fig.add_scatter(x=x1, y=y1,fill='tozeroy', mode='none' , fillcolor='rgba(158, 156, 157, 0.5)')

    # format plot
    fig.update_traces(  showlegend=False, line=dict(color='#0456d9',  width=4))
    fig.update_layout(  {'plot_bgcolor':'rgba(0, 0, 0, 0)', 
                       'paper_bgcolor':'rgba(0, 0, 0, 0)'},
                       font = {'color': "#a8a8a8", 'family': "Monospace"},
                       hovermode=False,
                        dragmode=False,
                        xaxis_title='Return (%)',
                        xaxis=dict(gridcolor='#4d4d4d'),
                       yaxis=dict(gridcolor='#4d4d4d'))
    fig.update_yaxes(showticklabels=False)

    return_display=round(x,2)

    #get most recent date in df
    latest_date=df_returns.Date.max()
    latest_date_display=str(latest_date.day)+'/'+str(latest_date.month)+'/'+str(latest_date.year)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder), text, return_display, latest_date, custom_return

def plot_price(df):
    #unpivot closing price and moving average columns
    df_line=pd.melt(df, id_vars=['Date'], value_vars=['Close', 'ma_30', 'ma_50','ma_100', 'ma_200'])
    m={'Close': 'Price', 'ma_30': '30-day Moving Avg','ma_50': '50-day Moving Avg','ma_100': '100-day Moving Avg','ma_200': '200-day Moving Avg'}
    df_line.Price=df_line.Price.map(m)
    category_orders={'Price': ['Price','30-day Moving Avg','50-day Moving Avg','100-day Moving Avg','200-day Moving Avg']}
    color_discrete_map = {  'Price': '#0456d9', 
                            '30-day Moving Avg': '#eeeeee', 
                            '50-day Moving Avg': '#cccccc', 
                            '100-day Moving Avg': '#bbbbbb', 
                            '200-day Moving Avg': '#aaaaa0', }
    fig = px.line(df_line, x="Date", y="value", color='Price',custom_data=['Price'],
                    hover_data={"Date":True, "Price":True, 'value':True},
                    color_discrete_map=color_discrete_map,category_orders=category_orders)
    #custom hover data
    fig.update_traces(  hovertemplate='%{customdata[0]}: %{y:$.2f}<br><extra></extra>',
                        hoverlabel = dict(bgcolor='#ffffff'),
                        marker_line=dict(width=2)
                     )
    fig.update_layout(  {'plot_bgcolor':'rgba(0, 0, 0, 0)', 
                       'paper_bgcolor':'rgba(0, 0, 0, 0)'},
                       font = {'color': "#a8a8a8", 'family': "Monospace"},
                       yaxis_title='Share Price ($)',
                       hovermode='x',
                       xaxis=dict(gridcolor='#4d4d4d'),
                       yaxis=dict(gridcolor='#4d4d4d'))

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)