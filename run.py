import numpy as np
import pandas as pd

import datetime as dt
import plotnine as p9
from plotnine import ggplot, geom_point, aes, geom_line, element_text
from mizani.breaks import date_breaks
from mizani.formatters import date_format

import os
import shutil
import smtplib, ssl
import json
import praw
import requests
import tweepy

def plot_log_covid(county):
    temp_df = df[df['name']==county]
    
    temp_plot = (ggplot(temp_df, aes('sampling_week', 'effective_concentration_rolling_average', group=1))
     + geom_point()
     + geom_line()
     + p9.scale_x_datetime(breaks=date_breaks('1 month'), labels=date_format('%D'), name='Date')
     + p9.scale_y_log10(name = 'Rolling average COVID concentration in wastewater')
     + p9.ggtitle(f'Log Scale {county} COVID Wastewater Data up to {temp_df.sampling_week.to_list()[-1]}')
     + p9.theme(
         figure_size=(24,12),
         axis_title=element_text(size=14),
         plot_title=element_text(size=18),
         axis_text_x=element_text(size=7)
         )
    )
    
    return(temp_plot)

def plot_linear_covid(county):
    temp_df = df[df['name']==county]
    
    temp_plot = (ggplot(temp_df, aes('sampling_week', 'effective_concentration_rolling_average', group=1))
     + geom_point()
     + geom_line()
     + p9.scale_x_datetime(breaks=date_breaks('1 month'), labels=date_format('%D'), name='Date')
     + p9.labels.ylab('Rolling average COVID concentration in wastewater')
     + p9.ggtitle(f'Linear Scale {county} COVID Wastewater Data up to {temp_df.sampling_week.to_list()[-1]}')
     + p9.theme(
         figure_size=(24,12),
         axis_title=element_text(size=14),
         plot_title=element_text(size=18),
         axis_text_x=element_text(size=7)
         )
    )
    
    return(temp_plot)

def plot_log_facet(county_list):
    temp_df = df[df['name'].isin(county_list)]
    
    temp_plot = (ggplot(temp_df, aes('sampling_week', 'effective_concentration_rolling_average', group=1))
     + geom_point()
     + geom_line()
     + p9.facet_wrap('name', ncol=1)
     + p9.scale_x_datetime(breaks=date_breaks('1 month'), labels=date_format('%D'), name='Date')
     + p9.scale_y_log10(name = 'Rolling average COVID concentration in wastewater')
     + p9.ggtitle(f'Log Scale COVID Wastewater Data up to {temp_df.sampling_week.to_list()[-1]}')
     + p9.theme(
         figure_size=(24,24),
         axis_title=element_text(size=14),
         plot_title=element_text(size=18),
         axis_text_x=element_text(size=7)
         )
    )

    return(temp_plot)


df = pd.read_csv('~/projects/covid/wastewater_by_county.csv')
last_upload_date = pd.read_csv('~/projects/covidLogPlot/last_upload_date.csv')

# Hard coded to check against the last update for Suffolk County (Boston)
last_date = last_upload_date.iloc[-1, 0]
last_update = df[df['name'] == 'Suffolk County, MA']['sampling_week'].to_list()[-1]
print(last_update)

if last_date != last_update:
# if last_date == last_update: # for testing 

    # clear old images
    try: 
        shutil.rmtree('figures')
        os.mkdir('figures')
    except:
        print('No figures folder')

    ma_counties = [
        'Suffolk County, MA',
        'Essex County, MA',
        'Hampshire County, MA',
        'Middlesex County, MA',
        'Worcester County, MA',
        'Plymouth County, MA',
        'Barnstable County, MA',
        'Bristol County, MA',
        'Hampden County, MA'
        ]

    # splitting up counties into older and newer counties for facet plots    
    old_counties = [
        'Suffolk County, MA',
        'Essex County, MA',
        'Nantucket County, MA',
        'Hampshire County, MA',
        'Middlesex County, MA',
        ]

    new_counties = [
        'Worcester County, MA',
        'Plymouth County, MA',
        'Barnstable County, MA',
        'Bristol County, MA',
        ]
            
    df[df['state']=='MA'].name.value_counts().index.to_list()
    county_data = {}

    # plot individual plots
    for county in ma_counties:
        county_name = county.split()[0].lower()
        print(county_name)
        log_save_string = f"figures/{county_name}_log_{last_update}.jpg"
        linear_save_string = f"figures/{county_name}_linear_{last_update}.jpg"
        
        log_plot = plot_log_covid(county)
        log_plot.save(log_save_string, dpi=300)
        linear_plot = plot_linear_covid(county)
        linear_plot.save(linear_save_string, dpi=300)

        county_data[county] = {'log': log_save_string, 'linear':linear_save_string}

    # plot facet plots
    for group_name, group in zip(['old_counties', 'new_counties'], [old_counties, new_counties]):
        group_plot = plot_log_facet(group)
        group_plot.save(f"figures/{group_name}_log_{last_update}.jpg", dpi=300) 
    
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
#    subr = 'test'
    subreddit = reddit.subreddit(subr)
    title = f'{last_update} COVID-19 Wastewater Log & Linear Plots for MA Counties using Biobot data'
    images = [
        {'image_path': f"figures/old_counties_log_{last_update}.jpg", 'caption': f'Multi-County Log Plot'},
        {'image_path': f"figures/new_counties_log_{last_update}.jpg", 'caption': f'Multi-County Log Plot'},
         ]

    for county in ma_counties:
        images.append({'image_path': county_data[county]['log'], 'caption': f'{county.split()[0]} County Log Plot'})
        images.append({'image_path': county_data[county]['linear'], 'caption': f'{county.split()[0]} County Linear Plot'})

    subreddit.submit_gallery(title, images, flair_id='1d8891e0-80e4-11ea-8ad7-0e20863e7c8d')
#    subreddit.submit_gallery(title, images,)

    # Setting up to send email
    port = 465
    context = ssl.create_default_context()
    sender = creds['sender_email']
    receiver = creds['receiver_email']
    email = f"Subject: COVID Wastewater plots today \n\n There are new plots saved under projects/covidLogPlot/figures "

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, creds['email_password'])
        server.sendmail(sender, receiver, email)

    # Post to twitter via v1 API since v2 doesn't support images    
    auth = tweepy.OAuthHandler(creds['twitter_api_key'], creds['twitter_api_secret'])
    auth.set_access_token(creds['twitter_access_token'], creds['twitter_access_secret'])
    
    api = tweepy.API(auth, wait_on_rate_limit=True)

    image_files = [
        f'figures/suffolk_log_{last_update}.jpg', 
        f'figures/suffolk_linear_{last_update}.jpg', 
        f'figures/old_counties_log_{last_update}.jpg',
        f'figures/new_counties_log_{last_update}.jpg',
]
    media_ids = []
    for image_file in image_files:
        id = api.media_upload(image_file)
        media_ids.append(id.media_id)

    tweetText = f"""
    Updated COVID-19 Wastewater Log & Linear Plots for Suffolk County and broadly MA using Biobot data

    Data goes up to {last_update}

    Source: weekly data release from https://github.com/biobotanalytics/covid19-wastewater-data
   """

    api.update_status(status=tweetText, media_ids=media_ids) 

else:
    print('No new updates')