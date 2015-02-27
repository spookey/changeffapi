
from sys import argv
from datetime import datetime
from requests import get as rget
from changeffapi import Loader

NODESJSON = 'http://map.freifunk-mainz.de/nodes.json'
FFAPIJSON = 'ffapi_file.json'

TWEETRESULT = True

def scrape(url):
    '''returns remote json'''
    try:
        return rget(url).json()
    except Exception as ex:
        print('Error: %s' %(ex))

if __name__ == '__main__':
    nodes = scrape(NODESJSON)

    if nodes:
        onlinenodes = 0
        onlineclients = 0

        for node in nodes['nodes']:
            if (node['flags']['online'] and not node['system']['role'] == 'gateway' and not node['system']['role'] == 'service'):
                onlinenodes += 1
            if node['clientcount']:
                onlineclients += node['clientcount']

        now = datetime.now().strftime('%H:%M %d.%m.%Y')
        resultmsg = 'Online-Status: %d Knoten, %d Teilnehmer %s' %(onlinenodes, onlineclients, now)
        if len(argv) > 1:
            print(resultmsg)
        else:
            loader = Loader(FFAPIJSON)
            if onlinenodes != int(loader.find(['state', 'nodes'])):
                loader.set(['state', 'nodes'], onlinenodes)
                loader.dump(overwrite=True)

            if TWEETRESULT:
                from notify.twitter import send_tweet
                send_tweet(resultmsg)
