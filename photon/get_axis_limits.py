#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
############################
#####
#####       Photon
#####      R. THOMAS
#####        2018
#####
###########################
@License: GPL - see LICENCE.txt
'''

##third parties
from PyQt5.QtWidgets import QLineEdit

def get_axis_limits(loaded_plot, full):

        ###first we check in the configuration file 
        x = loaded_plot.plotconf['types']['xmin']
        try:
            ###try to convert to float --> means the axis have been loaded from a file
            xmin = float(loaded_plot.plotconf['types']['xmin'])
            ymin = float(loaded_plot.plotconf['types']['ymin'])
            xmax = float(loaded_plot.plotconf['types']['xmax'])
            ymax = float(loaded_plot.plotconf['types']['ymax'])
            loaded_plot.plotconf['types']['xmin'] = 'xmin'
            loaded_plot.plotconf['types']['ymin'] = 'ymin'
            loaded_plot.plotconf['types']['xmax'] = 'xmax'
            loaded_plot.plotconf['types']['ymax'] = 'ymax'
            return xmin, xmax, ymin, ymax  
        except:
            pass
        
        ##then we try from the axis widgets 
        try:
            xmin = float(full.properties.parentWidget().findChildren(QLineEdit, 'xmin')[0].text())
            xmax = float(full.properties.parentWidget().findChildren(QLineEdit, 'xmax')[0].text())
            ymin = float(full.properties.parentWidget().findChildren(QLineEdit, 'ymin')[0].text())
            ymax = float(full.properties.parentWidget().findChildren(QLineEdit, 'ymax')[0].text())
            return xmin, xmax, ymin, ymax  

        except:
            pass

        ##if none of the above worked we look at the plot elements
        xs = []
        ys = []

        for j in full.dico_widget.keys():
            if 'line_' in j[:-1]:
                for i in range(full.lineindex):
                    x = full.dico_widget['line_'+str(i+1)][0].get_xdata()
                    y = full.dico_widget['line_'+str(i+1)][0].get_ydata()
                    xs.append(min(x))
                    xs.append(max(x))
                    ys.append(min(y))
                    ys.append(max(y))
            if 'scat_' in j[:-1]:
                for i in range(full.scatterindex):
                    x ,y = full.dico_widget['scat_'+str(i+1)].get_offsets().T
                    xs.append(min(x))
                    xs.append(max(x))
                    ys.append(min(y))
                    ys.append(max(y))
            if 'hist_' in j[:-1]:
                for i in range(full.histindex):
                    y,x,c = full.dico_widget['hist_'+str(i+1)]
                    if min(x) == max(x):
                        try:
                            xs.append(min(xs))
                            xs.append(max(xs))
                        except:
                            xs.append(0)
                            xs.append(1)
                    else:
                        xs.append(min(x))
                        xs.append(max(x))
                    if min(y) == max(y):
                        try:
                            ys.append(min(ys))
                            ys.append(max(ys))
                        except:
                            ys.append(0)
                            ys.append(1)
                    else:
                        ys.append(min(y))
                        ys.append(max(y))

            if 'stra_' in j[:-1]:
                for i in range(full.straight_index):
                    x = full.dico_widget['stra_'+str(i+1)][0].get_xdata()
                    y = full.dico_widget['stra_'+str(i+1)][0].get_ydata()
                    xs.append(min(x))
                    xs.append(max(x))
                    ys.append(min(y))
                    ys.append(max(y))

            if 'stri_' in j[:-1]:
                for i in range(full.strip_index):
                    x,y = full.dico_widget['stri_'+str(i+1)]._path._vertices.T
                    xs.append(min(x))
                    xs.append(max(x))
                    ys.append(min(y))
                    ys.append(max(y))

        return min(xs), max(xs), min(ys), max(ys)
