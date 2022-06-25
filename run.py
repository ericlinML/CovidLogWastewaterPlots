import numpy as np
import pandas as pd

import datetime as dt
import plotnine as p9
from plotnine import ggplot, geom_point, aes, geom_line
from mizani.breaks import date_breaks
from mizani.formatters import date_format

import smtplib, ssl
import json
import praw
import requests

def plot_log_covid(county):
    temp_df = df[df['name']==county]
    
    temp_plot = (ggplot(temp_df, aes('sampling_week', 'effective_concentration_rolling_average', group=1))
     + geom_point()
     + geom_line()
     + p9.scale_x_datetime(breaks=date_breaks('1 month'), labels=date_format('%D'), name='Date')
     + p9.scale_y_log10(name = 'Rolling average COVID concentration in wastewater')
     + p9.theme(figure_size=(24,12))
     + p9.ggtitle(f'Log Scale {county} COVID Wastewater Data up to {temp_df.sampling_week.to_list()[-1]}')
    )
    
    return(temp_plot)

def plot_linear_covid(county):
    temp_df = df[df['name']==county]
    
    temp_plot = (ggplot(temp_df, aes('sampling_week', 'effective_concentration_rolling_average', group=1))
     + geom_point()
     + geom_line()
     + p9.scale_x_datetime(breaks=date_breaks('1 month'), labels=date_format('%D'), name='Date')
     + p9.labels.ylab('Rolling average COVID concentration in wastewater')
     + p9.theme(figure_size=(24,12))
     + p9.ggtitle(f'Linear Scale {county} COVID Wastewater Data up to {temp_df.sampling_week.to_list()[-1]}')
    )
    
    return(temp_plot)


df = pd.read_csv('~/projects/covid/wastewater_by_county.csv')
last_upload_date = pd.read_csv('last_upload_date.csv')

# Hard coded to check against the last update for Suffolk County (Boston)
last_date = last_upload_date.iloc[-1, 0]
last_update = df[df['name'] == 'Suffolk County, MA']['sampling_week'].to_list()[-1]

if last_date == last_update:
    suffolk = plot_log_covid('Suffolk County, MA')
    suffolk.save(f'figures/suffolk_log_{last_update}.png', dpi=300)
    suffolk_linear = plot_linear_covid('Suffolk County, MA')
    suffolk_linear.save(f'figures/suffolk_linear_{last_update}.png', dpi=300)

    middlesex = plot_log_covid('Middlesex County, MA')
    middlesex.save(f'figures/middlesex_log_{last_update}.png', dpi=300)
    middlesex_linear = plot_linear_covid('Middlesex County, MA')
    middlesex_linear.save(f'figures/middlesex_linear_{last_update}.png', dpi=300)

    last_upload_date.loc[len(last_upload_date.index), 'date'] = last_update
    last_upload_date.to_csv('last_upload_date.csv', index=False)

    print('Made new figures!')

    # Setting up Reddit post
    cred = 'client_secrets.json'
    with open(cred) as f:
        creds = json.load(f)
    
    reddit = praw.Reddit(
        client_id = creds['client_id'],
        client_secret=creds['client_secret'],
        user_agent=creds['user_agent'],
        redirect_uri=creds['redirect_uri'],
        refresh_token=creds['refresh_token']
        )

    subr = 'CoronavirusMa'
    subreddit = reddit.subreddit(subr)
    title = 'COVID-19 Wastewater Log & Linear Plots for Boston and Cambridge, MA'
    images = [
        {
            'image_path': f'figures/suffolk_log_{last_update}.png',
            'caption': f'Suffolk County Log Plot'
        },
        {
            'image_path': f'figures/suffolk_linear_{last_update}.png',
            'caption': f'Suffolk County Linear Plot testing'
        },
        {
            'image_path': f'figures/middlesex_log_{last_update}.png',
            'caption': f'Middlesex County Log Plot testing'
        },
        {
            'image_path': f'figures/middlesex_linear_{last_update}.png',
            'caption': f'Middlesex County Linear Plot testing'
        },
    ]
    subreddit.submit_gallery(title, images, flair_id='1d8891e0-80e4-11ea-8ad7-0e20863e7c8d')

    # Setting up to send email
    port = 465
    context = ssl.create_default_context()
    sender = creds['sender_email']
    receiver = creds['receiver_email']
    email = f"Subject: COVID Wastewater plots today \n\n There are new plots saved under projects/covidLogPlot/figures "

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, creds['email_password'])
        server.sendmail(sender, receiver, email)


else:
    print('No new updates')

