import jsonpickle
import glob
from snapshot import Snapshot
import matplotlib.pyplot as plt
from sklearn import preprocessing
import os
import numpy as np
from scipy.interpolate import interp1d

# Interesting items: 152507, 152577, 152510, 168487, 160053, 167738, 152877,
# 168649, 152577, 152497, 169299, 152506, 170318, 152507, 152877, 152541
# 169328, 152876, 169301, 168649, 152509, 52325, 168185, 170313,
ITEM_ID = '152577'


def get_trades():
    list_of_files = glob.glob('C:/Users/Faisal/PycharmProjects/wow/trades/*.json')
    hourly_trades = []

    for file in sorted(list_of_files):
        trades = {}
        with open(file, 'r') as entry:
            data = jsonpickle.decode(entry.read())
            for item_trade in data:
                if item_trade not in trades:
                    trades[item_trade] = data[item_trade]
        hourly_trades.append(trades)

    return hourly_trades


def get_trade_data(trades, item_id):
    trade_data = []
    trade_volume = []
    for date in trades:
        if (item_id in date):
            trade_data.append(date[item_id][0])
            trade_volume.append(date[item_id][1])
        else:
            trade_data.append(0)
            trade_volume.append(0)
    return [trade_data, trade_volume]


def get_averages():
    list_of_files = glob.glob('C:/Users/Faisal/PycharmProjects/wow/averages/*.json')
    hourly_avg = []

    for file in sorted(list_of_files):
        avg = {}
        with open(file, 'r') as entry:
            data = jsonpickle.decode(entry.read())
            for item_avg in data:
                if item_avg not in avg:
                    avg[item_avg] = data[item_avg]
        hourly_avg.append(avg)
    return hourly_avg


def get_average_data(averages, item_id):
    avg_data = []
    for date in averages:
        if (item_id in date):
            avg_data.append(date[item_id])
        else:
            avg_data.append(0)
    return avg_data


def get_overall():
    list_of_files = glob.glob('C:/Users/Faisal/PycharmProjects/wow/overall/*.json')
    hourly_item_volume = []
    hourly_overall_volume = []

    for file in sorted(list_of_files):
        with open(file, 'r') as entry:
            overall = jsonpickle.decode(entry.read())
        hourly_item_volume.append(overall[0])
        hourly_overall_volume.append(overall[1])
    return [hourly_item_volume, hourly_overall_volume]


def get_overall_item(overall_list, item_id):
    overall_item = []
    for date in overall_list:
        if item_id in date:
            overall_item.append(date[item_id])
        else:
            overall_item.append(0)
    return overall_item


def get_most_traded():
    trades = get_trades()
    items = {}
    for date in trades:
        for item in date:
            if item not in items:
                items[item] = 1
            else:
                items[item] += 1
    items = {k: v for k, v in sorted(items.items(), key=lambda item: item[1], reverse=True)}
    return items


def plot_volume(hourly_overall_volume, overall_item, trade_volume):
    # Defining x-axis
    x_hov = np.linspace(0, len(hourly_overall_volume) / 24, len(hourly_overall_volume))
    x_oi = np.linspace(0, len(overall_item) / 24, len(overall_item))
    x_tv = np.linspace(0, len(trade_volume) / 24, len(trade_volume))

    # Smoothen curves
    x_hov_new = np.linspace(min(x_hov), max(x_hov), 120)
    x_oi_new = np.linspace(min(x_oi), max(x_oi), 120)
    x_tv_new = np.linspace(min(x_tv), max(x_tv), 120)

    f1 = interp1d(x_hov, hourly_overall_volume, kind='cubic')
    f2 = interp1d(x_oi, overall_item, kind='cubic')
    f3 = interp1d(x_tv, trade_volume, kind='cubic')

    # First figure
    figure1 = plt.figure(1)
    plt.style.use('classic')

    # Plot amount of items on auction house at any given hour
    plt.plot(x_hov_new, preprocessing.scale(f1(x_hov_new)), color='yellow', label='overall market volume')

    # Plot amount of a specific item on auction house at any given hour
    plt.plot(x_oi_new, preprocessing.scale(f2(x_oi_new)), color='black', label='overall volume for item')

    plt.legend(loc='upper right', frameon=True)
    figure1.show()

    figure2 = plt.figure(2)
    # Plot trade volume for item
    plt.plot(x_tv_new, f3(x_tv_new), color='blue', label='trade volume')
    plt.legend(loc='upper right', frameon=True)
    figure2.show()


def plot_price(trade_data, avg_data):
    # Defining x-axis
    x_avg = np.linspace(0, len(avg_data) / 24, len(avg_data))
    x_trade = np.linspace(0, len(trade_data) / 24, len(trade_data))

    # Smoothen curves
    x_avg_new = np.linspace(min(x_avg), max(x_avg), 120)
    x_trade_new = np.linspace(min(x_trade), max(x_trade), 120)

    f1 = interp1d(x_trade, trade_data, kind='cubic')
    f2 = interp1d(x_avg, avg_data, kind='cubic')

    figure3 = plt.figure(3)
    plt.style.use('classic')
    # Plot trade price for item
    plt.plot(x_trade_new, f1(x_trade_new), color='green', label='trade price')

    # Plot average price for item
    plt.plot(x_avg_new, f2(x_avg_new), color='red', label='average price')

    plt.legend(loc='upper right', frameon=True)
    figure3.show()


test_avg_data = np.array(get_average_data(get_averages(), item_id=ITEM_ID))
test_trade_data = np.array(get_trade_data(get_trades(), item_id=ITEM_ID)[0])
test_trade_volume = np.array(get_trade_data(get_trades(), item_id=ITEM_ID)[1])

test_overall = np.array(get_overall())
test_hourly_overall_volume = np.array(test_overall[1])
test_overall_item = np.array(get_overall_item(test_overall[0], item_id=ITEM_ID))
print(get_most_traded())

plot_price(test_trade_data, test_avg_data)
plot_volume(test_hourly_overall_volume, test_overall_item, test_trade_volume)
plt.show()
