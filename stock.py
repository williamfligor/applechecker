#!/usr/bin/env python
import httplib
import urllib
import os
import time
import sys
from socket import gaierror
import requests

# only tested for US stores and US text message
URL = "http://www.apple.com/shop/retail/pickup-message"
BUY = "http://store.apple.com/xc/product/"
SMS = "http://textbelt.com/text"

DATEFMT = "%m/%d/%Y %H:%M:%S"
LOADING = ['-', '\\', '|', '/']

def main(model, zipcode, sec=5):
    good_stores = []
    alert = Alert()
    initmsg = ("[{0}]start tracking {1} in {2}. ").format(time.strftime(DATEFMT), model, zipcode)
    print initmsg

    params = {'parts.0': model,
              'location': zipcode}

    sec = int(sec)
    i, cnt = 0, sec

    while True:
        if cnt < sec:
            # loading sign refreashes every second
            sys.stdout.write('\rChecking...{}'.format(LOADING[i]))
            sys.stdout.flush()
            i = i + 1 if i < 3 else 0
            cnt += 1
            time.sleep(1)
            continue
        cnt = 0

        try:
            stores = requests.get(URL, params=params).json()
            stores = stores['body']['stores'][:8]
        except (ValueError, KeyError, gaierror) as e:
            print 'error', e
            print "Failed to query Apple Store"
            time.sleep(sec)
            continue

        for store in stores:
            sname = store['storeName']
            item = store['partsAvailability'][model]['storePickupProductTitle']
            if store['partsAvailability'][model]['pickupDisplay'] == "available":
                if sname not in good_stores:
                    good_stores.append(sname)
                    msg = u"Found it! {store} has {item}! {buy}{model}".format(
                        store=sname, item=item, buy=BUY, model=model)
                    print u"{0} {1}".format(time.strftime(DATEFMT), msg)
                    alert.send(msg)
            else:
                if sname in good_stores:
                    good_stores.remove(sname)
                    msg = u"Oops all {item} in {store} are gone :( ".format(
                        item=item, store=sname)
                    print u"{0} {1}".format(time.strftime(DATEFMT), msg)
                    alert.send(msg)

        if good_stores:
            print "[{current}] Avaiable: {stores}".format(
                current=time.strftime(DATEFMT),
                stores=', '.join([s.encode('utf-8') for s in good_stores])
                        if good_stores else "None")

class Alert(object):
    def send(self, body):
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.urlencode({
            "token": os.environ['APP_TOKEN'],
            "user": os.environ['USER_TOKEN'],
            "message": body,
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

if __name__ == '__main__':
    main(*sys.argv[1:])
