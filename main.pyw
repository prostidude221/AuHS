from datetime import time

import wowapi
import jsonpickle
from post import Post
from snapshot import Snapshot
import glob
import os
import numpy as np

seceret = 'eP74vMGpai3FD85XhZGE5UdyotPxf6Qh'
client_id = 'ee1355ee13264257ad5746fc7ad00538'
realmid = '1403'
realm_name = 'draenor'
character_name = 'prostidudee'
NEW_ITEM_LIST = False

ITEM_LIST = [
    154695, 154692, 154899, 21841, 152579, 168302, 154696, 152576, 154165, 4344, 152513, 152577, 152509, 168487, 154897,
    127035, 160053, 152631, 152877, 152875, 128316, 152541, 114821, 89112, 40772, 152505, 170302, 160298, 154898, 2459,
    33470, 170310, 109253, 2592, 153594, 152544, 152543, 152510, 165699, 52329, 142075, 116794, 170313, 153050, 152511,
    174351, 153647, 124671, 175007, 159959, 152512, 124120, 87213, 111820, 167738, 76061, 152507, 7909, 128313, 152876,
    168649, 152497, 174353, 175005, 124437, 112384, 152506, 168185, 4338, 170295, 160711, 158189, 175008, 152835,
    152542, 169299, 124104, 52325, 168190, 175006, 54443, 52328, 170301, 4306, 52327, 170350, 128311, 170318, 169301,
    128304, 124121, 167964, 42420, 4337, 138488, 10044, 168645, 21877, 163575, 169328
]

api = wowapi.WowApi(client_secret=seceret, client_id=client_id)
auction = api.get_auctions(region='eu', connected_realm_id=realmid, namespace='dynamic-eu')['auctions']


def run():
    snap = Snapshot(getData()[0], getData()[1], 0)
    average = getAveragePrices(snap)

    # Get trades if snapshot dir is not empty
    if (len(os.listdir('C:/Users/Faisal/PycharmProjects/wow/snapshots/')) != 0):
        trades = getTrades(snap)
        if len(trades) != 0:
            with open('C:/Users/Faisal/PycharmProjects/wow/trades/' + snap.date + '.json', "w") as file:
                save = jsonpickle.encode(trades)
                file.write(save)
                print('Trades data updated!')

    # Save current snapshot to snapshot dir
    with open('C:/Users/Faisal/PycharmProjects/wow/snapshots/' + snap.date + '.json', "w") as file:
        save = jsonpickle.encode(snap)
        file.write(save)
        print('snapshot data updated!')

    # Save 15th percentile averages for items to file
    with open('C:/Users/Faisal/PycharmProjects/wow/averages/' + snap.date + '.json', "w") as file:
        save = jsonpickle.encode(average)
        file.write(save)
        print('Average data updated!')

    # save overall data to file
    getOverall(snap)


def getData():
    counter = 0
    list = []
    itm = {}
    for post in auction:
        counter += 1
        if ('buyout' in post and 'unit_price' not in post and post['item']['id'] in ITEM_LIST):
            list.append(Post(post['id'], post['item']['id'], post['buyout'] / 10000, post['time_left'], post_quanity=1,
                             stack=1))
        else:
            if ('unit_price' in post and 'buyout' not in post and post['item']['id'] in ITEM_LIST):
                list.append(
                    Post(post['id'], post['item']['id'], post['unit_price'] / 10000, post['time_left'], post_quanity=1,
                         stack=post['quantity']))
    for post in list:

        if post.itemId not in itm:
            itm[post.itemId] = 1
        else:
            itm[post.itemId] += 1

    if (NEW_ITEM_LIST):
        itm = dict(sorted(itm.items(), key=lambda x: x[1], reverse=True)[:100])
        newList = []
        for post in list:
            if post.itemId in itm:
                newList.append(post)

    return [list, itm]


def getTrades(new_snapshot):
    # trades - {'itemId':[price, quantity]}
    trades = {}
    list_of_files = glob.glob('C:/Users/Faisal/PycharmProjects/wow/snapshots/*.json')
    latest_file = max(list_of_files, key=os.path.getctime)
    old_snapshot = 0
    with open(latest_file, "r") as file:
        old_snapshot = jsonpickle.decode(file.read())
    old_posts = old_snapshot.posts
    new_posts = new_snapshot.posts

    old_temp = []
    for post in old_posts:
        old_temp.append(post.postId)
    new_temp = []
    for post in new_posts:
        new_temp.append(post.postId)

    old_temp = [x for x in old_temp if x not in new_temp]

    for post in old_posts:
        if (post.postId in old_temp and (post.duration == 'LONG')):
            if post.itemId not in trades:
                trades[post.itemId] = [[post.price], post.stack]
            else:
                trades[post.itemId][0].append(post.price)
                trades[post.itemId][1] += post.stack

    for item in trades:
        if len(trades[item][0]) > 2:
            trades[item][0] = np.percentile(trades[item][0], 30).item()

        else:
            trades[item][0] = np.percentile(trades[item][0], 0.0001).item()
    return trades


def getTopItems(snapshot):
    output = ('\nMost sold items on the auction house: \n')
    previos = []
    counter = 1
    for post in snapshot.posts:
        currentId = post.itemId
        if (currentId not in previos):
            try:
                output += (str(counter) + '. ' +
                           api.get_item_data(region='eu', namespace='static-eu', id=post.itemId)['name'][
                               'en_US'] + '     ID: ' + str(post.itemId) + '     QUANT: ' + str(
                            snapshot.items[post.itemId]) + '\n')
            except:
                pass
            previos.append(currentId)
            counter += 1
    return output


def getAveragePrices(snapshot):
    average = {}
    previos = []
    for post in snapshot.posts:
        currentId = post.itemId
        if (currentId not in previos):
            average[currentId] = 0
            try:
                counter = 1
                value = []
                for POST in snapshot.posts:
                    if (POST.itemId == currentId):
                        value.append(POST.price)
                        counter += (1 * POST.stack)
                value = np.array(value)
                value = np.percentile(value, 15.01)
                average[currentId] = value.item()
            except Exception as e:
                print(e)
                pass
            previos.append(currentId)
    return average


def getOverall(snap):
    with open('C:/Users/Faisal/PycharmProjects/wow/overall/' + snap.date + '.json', "w") as file:
        overall = {}
        temp = 0
        for post in snap.posts:
            temp += post.stack
            if post.itemId not in overall:
                overall[post.itemId] = post.stack
            else:
                overall[post.itemId] += post.stack
        data = [overall, temp]
        save = jsonpickle.encode(data)
        file.write(save)


if __name__ == '__main__':
    run()
