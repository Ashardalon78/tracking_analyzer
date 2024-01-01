import tkinter as tk
from tkinter import filedialog
import os
import json
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime

class GoogleTracker():
    transportation_methods = ('drive', 'walk', 'subway', 'bus', 'train', 'bike')
    title_map = {'drive': 'Kilometers by car',
                 'walk': 'Kilometers walked',
                 'subway': 'Kilometers by subway',
                 'bus': 'Kilometers by bus',
                 'train': 'Kilometers by train',
                 'bike': 'Kilometrs by bike'}

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('320x160')
        self.root.title('Google Tracking Analyzer by Ashardalon78, Version 1.0')

        self.__add_button('Load Location History', self.__wrapper_load_data, row=0, column=0, sticky=tk.W, pady=4)
        self.__add_button('Plot Data', self.__wrapper_plot, row=1, column=0, sticky=tk.W, pady=4)

        self.data_selected = tk.StringVar(self.root)
        self.__add_dropdown(self.data_selected, self.transportation_methods,
                            self.transportation_methods[0], row=1, column=1, sticky=tk.W, pady=4)
        #self.dd_data = tk.OptionMenu(self.root, self.data_selected, *self.transportation_methods).grid(row=1,column=1)


        self.root.mainloop()

    def __add_button(self, name, function, **kwargs):
        tk.Button(self.root, text=name, command=function).grid(kwargs)

    def __add_dropdown(self, var, optlist, ini_val, **kwargs):
        var.set(ini_val)
        self.dd_data = tk.OptionMenu(self.root, var, *optlist).grid(kwargs)


    def __wrapper_load_data(self):
        rawdata = self.__load_data()
        dfs = self.__create_main_dfs(rawdata)
        self.__clean_data(dfs)

    def __load_data(self):
        path = filedialog.askdirectory()
        if not path:
            return

        filelist = []

        for root, dirs, files in os.walk(path):
            #if root[-4:].isdigit() and int(root[-4:]) < 2020: continue
            for name in files:
                filelist.append(os.path.join(root, name))

            filelist = sorted(filelist,
                              key=lambda month: datetime.strptime(month.split('\\')[-1].split('.')[0], '%Y_%B'))

        data = {}
        for month in filelist:
            with open(month, encoding='utf-8') as infile:
                data[month.split('\\')[-1].split('.')[0]] = json.load(infile)

        return data

    def __create_main_dfs(self, data):
        main_dfs = {}

        for monthstr, data_month in data.items():

            reduced_data = {}
            reduced_data['Vehicle'] = []
            reduced_data['Airline'] = []
            reduced_data['Movement'] = []
            reduced_data['TrueDistance'] = []
            reduced_data['Confidence'] = []

            for item0 in data_month['timelineObjects']:
                if not 'activitySegment' in item0.keys(): continue
                if not 'activityType' in item0['activitySegment'].keys(): continue
                if not 'distance' in item0['activitySegment'].keys(): continue

                reduced_data['Vehicle'].append(item0['activitySegment']['activityType'])
                reduced_data['Airline'].append(item0['activitySegment']['distance'] / 1000)

                if 'waypointPath' in item0['activitySegment'].keys():
                    if 'travelMode' in item0['activitySegment']['waypointPath'].keys() \
                            and 'distanceMeters' in item0['activitySegment']['waypointPath'].keys():
                        reduced_data['Movement'].append(item0['activitySegment']['waypointPath']['travelMode'])
                        reduced_data['TrueDistance'].append(
                            item0['activitySegment']['waypointPath']['distanceMeters'] / 1000)
                    else:
                        reduced_data['Movement'].append(None)
                        reduced_data['TrueDistance'].append(None)
                    if 'confidence' in item0['activitySegment']['waypointPath'].keys():
                        reduced_data['Confidence'].append(item0['activitySegment']['waypointPath']['confidence'])
                    else:
                        reduced_data['Confidence'].append(1.0)
                else:
                    reduced_data['Movement'].append(None)
                    reduced_data['TrueDistance'].append(None)
                    reduced_data['Confidence'].append(1.0)
                # break

            main_dfs[monthstr] = pd.DataFrame(reduced_data)

        return main_dfs

    def __clean_data(self, data):
        self.cleaned_dfs = copy.deepcopy(data)

        self.dist_dict = {'drive': [],
                          'walk': [],
                          'subway': [],
                          'bus':  [],
                          'train': [],
                          'bike': []}

        for df in self.cleaned_dfs.values():
            df['Remove'] = np.where(((df['Vehicle'] == 'IN_PASSENGER_VEHICLE') &
                                     (df['Movement'].isna())) |
                                    ((df['Vehicle'] == 'WALKING') &
                                     (df['Movement'].isna())) |
                                    ((df['Vehicle'] == 'CYCLING') &
                                     (df['Movement'].isna()))
                                    , 1, 0)
            df.drop(df[df['Remove'] == 1].index, inplace=True)
            df.drop(df[df['Confidence'] < 0.5].index, inplace=True)

            self.dist_dict['drive'].append(df[df['Vehicle'] == 'IN_PASSENGER_VEHICLE']['TrueDistance'].sum())
            self.dist_dict['walk'].append(df[df['Vehicle'] == 'WALKING']['TrueDistance'].sum())
            self.dist_dict['subway'].append(df[df['Vehicle'] == 'IN_SUBWAY']['Airline'].sum())
            self.dist_dict['bus'].append(df[df['Vehicle'] == 'IN_BUS']['Airline'].sum())
            self.dist_dict['train'].append(df[df['Vehicle'] == 'IN_TRAIN']['Airline'].sum())
            self.dist_dict['bike'].append(df[df['Vehicle'] == 'CYCLING']['TrueDistance'].sum())

    def __wrapper_plot(self):
        #get data from dropdown

        self.__plot_data(self.data_selected.get())

    def __plot_data(self, name):
        fig = plt.figure(figsize=[8, 5])
        plt.rcParams["figure.autolayout"] = True
        plt.subplots_adjust(bottom=0.30)
        plt.xticks(rotation=90)

        plt.title(self.title_map[name])
        plt.ylabel('km')
        # plt.ylim(0,500)
        x = list(self.cleaned_dfs.keys())
        plt.plot(x, self.dist_dict[name])
        divisor = (len(x)-1)//50 +1
        plt.xticks(x[::divisor])
        plt.grid()
        plt.show()


if __name__ == '__main__':
    gt = GoogleTracker()