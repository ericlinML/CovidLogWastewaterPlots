import tweepy
import json

last_update = '2022-08-17'

cred = 'client_secrets.json'
with open(cred) as f:
    creds = json.load(f)

# Post to twitter via v1 API since v2 doesn't support images    
auth = tweepy.OAuthHandler(creds['twitter_api_key'], creds['twitter_api_secret'])
auth.set_access_token(creds['twitter_access_token'], creds['twitter_access_secret'])

api = tweepy.API(auth, wait_on_rate_limit=True)

image_files = [
    f'figures/suffolk_log_{last_update}.jpg', 
    f'figures/suffolk_linear_{last_update}.jpg', 
    f'figures/middlesex_log_{last_update}.jpg', 
    f'figures/middlesex_linear_{last_update}.jpg',
]

id = api.media_upload("figures/suffolk_log_2022-08-17.jpg")
print(id.media_id)

media_ids = []
for image_file in image_files:
    id = api.media_upload(image_file)
    media_ids.append(id.media_id)

tweetText = f"""
Updated COVID-19 Wastewater Log & Linear Plots for Suffolk and Middlesex Counties, MA using Biobot data

Data goes up to {last_update}

Source: weekly data release from https://github.com/biobotanalytics/covid19-wastewater-data
"""

api.update_status(status=tweetText, media_ids=media_ids) 

