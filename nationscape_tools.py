# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

'''
qfreq- Checks in how many weeks/waves (out of 50 total) each question was
asked. This is a good place to start for looking at how responses have
changed over time. The two CSV files need to be moved into the same directory
for this operation for work.
'''
def qfreq():
    # WAVE 1 DATA
    data = pd.read_csv("variable_presence_by_wave_r1.csv", skiprows = 5)
    data = data.rename(columns = {"Unnamed: 0" : "Question"})
    data = data.set_index("Question")
    
    # WAVE 2 DATA
    data2 = pd.read_csv("variable_presence_by_wave_r2.csv", skiprows = 5)
    data2 = data2.rename(columns = {"Unnamed: 0" : "Question"})
    data2 = data2.set_index("Question")
    
    # Combining first and second wave tables after changing indices
    datacomb = pd.concat([data, data2], axis=1)
    datacomb[pd.isna(datacomb)] = 0
    
    # EDA on combined table
    counts = datacomb.apply(np.sum, axis = 1)
    countrank = counts.sort_values(ascending = False)
    countrank.hist(bins = 50)
    return countrank
    

'''
fuse- Combines multiple waves of data into a single DataFrame. Given its
possible size (reaching over 300K rows if you combine everything), be very
careful about performing computationally intensive operations on the output.
The input dirlist is a list of directories containing each week's data.
'''
def fuse(dirlist):
    df = pd.DataFrame()
    for direct in dirlist:
        filename = direct + "\\" + direct + ".dta"
        data = pd.io.stata.read_stata(filename)
        df = pd.concat([df, data], axis = 0)
    # need to reset index so it doesn't repeat
    df.reset_index(drop = True, inplace = True)
    return df


'''
preprocess- Removes nan values, adds 'total' column (summing responses) and 
transposes DataFrame so that dates become index for easier analysis of 
responses over time.
'''
def preprocess(df):
    # transpose and replace nan with 0s
    df = df.transpose().fillna(value = 0)
    if 'Not Asked' in df:
        df = df.drop(columns = ['Not Asked'])
    total = df.sum(axis = 1).rename('Total')
    df = pd.concat([df, total], axis = 1)
    return df


'''
frame_build- Creates a DataFrame aggregrating the summary of responses for 
each week's data on the questions of interest, qlist. Uses the preprocess 
function. Uses the weighted sum to compute summary of responses.
'''
def frame_build(qlist, dirlist):
    data_dict = dict()
    for q in qlist:
        data_dict[q] = pd.DataFrame()
    qlist.append('weight')
    # reading in data for each week
    for direct in dirlist:
        filename = direct + "\\" + direct + ".dta"
        data = pd.io.stata.read_stata(filename)
        # Removing questions if they aren't in dataset to prevent key error
        newq = [q for q in qlist if q in data.columns]
        # Subsetting data with questions of interest
        subset = data.loc[:, newq]
        # Fixing clerical error in the data
        subset = subset.replace(to_replace = "Not sure", value = "Not Sure")
        # Creating each summary column
        date = pd.to_datetime(direct[2:], yearfirst = True)
        for colname in subset.columns[:-1]:
            summary = subset.groupby([colname])["weight"].sum()
            summary = summary.rename(date)
            data_dict[colname] = pd.concat([
                data_dict[colname], summary], axis = 1)
    # Preprocessing to get desired shape
    for key, df in data_dict.items():
        data_dict[key] = preprocess(df)        
    return data_dict


'''
qplot1- Produces a scatterplot of date vs. % of responses for a single
question only. qplot1 is called using an already-existing matplotlib object 
(fig). The input df_tuple corresponds to the key/value pair of a single item 
in data_dict.
'''
def qplot1(fig, df_tuple):
    title, df = df_tuple
    x = df.index
    ydict = dict()
    for response in df.columns:
        ydict[response] = 100 * df[response] / df['Total']
    ax = fig.add_subplot(111)
    for name, y in ydict.items():
        ax.scatter(x, y, label = name, marker = '.')
        plt.xlabel('Date')
        plt.ylabel('Percentage of Responses')
        fig.legend()
    opt_title = input(f'Default title: {title}. New title: ')
    if opt_title == '':
        plt.title(title)
    else:
        plt.title(opt_title)    


'''
qplot2- Produces scatterplots of date vs. % of responses for a series of 
questions assembled in frame_build. qplot2 is called using an already-existing 
matplotlib object (fig). The input df_set corresponds to a dictionary of the 
form key (string): value (DataFrame), such as data_dict or a subset. 
Recommend size(df_set) < 6. 
'''
def qplot2(fig, df_set):
    subarrange = {
        2: [121, 122],
        3: [131, 132, 133],
        4: [221, 222, 223, 224],
        5: [321, 322, 323, 324, 325],
        6: [321, 322, 323, 324, 325, 326]}
    i = 0
    for title, df in df_set.items():
        # preparing data to plot
        x = df.index
        ydict = dict()
        for response in df.columns[:-1]:
            ydict[response] = 100 * df[response] / df['Total'] 
        ax = fig.add_subplot(subarrange[len(df_set)][i])
        for name, y in ydict.items():
            ax.scatter(x, y, label = name, marker = '.')
        plt.xlabel('Date')
        plt.ylabel('Percentage of Responses')
        # plt.legend()
        opt_title = input(f'Default title: {title}. New title: ')
        if opt_title == '':
            plt.title(title)
        else:
            plt.title(opt_title)
        i += 1
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc = (0.32, 0.92), ncol = 5)
    # User may need to change loc and ncol depending on the number of 
    # plots/responses


'''
compare- Breaks down how different affinity groups (identity) responded to a 
question (question) from the input DataFrame (data) through a weighted
summary.
'''
def compare(data, question, identity):
    agg = pd.DataFrame()
    options = set(data[identity].values)
    options = {x for x in options if type(x) == str}
    for option in options:
        subset = data[data[identity] == option]
        subct = subset.groupby([question])['weight'].sum()
        subct = subct.rename(option)
        agg = pd.concat([agg, subct], axis = 1)
    return agg


'''
complot- Plots stacked bars comparing responses to a particular question
against responses to another/ affinity groups. complot is called using an
already-existing matplotlib object (fig).
'''
def complot(fig, data):
    ax = fig.add_subplot(111)
    x = data.index
    responses = list(data.columns)
    responses.remove('Total')
    btm = pd.Series(data = 0, index = x)
    for response in responses:
        ax.bar(x, data[response]/data['Total'], bottom = btm.tolist(), 
               label = response)
        btm += data[response]/data['Total']
    loc = range(len(x))
    plt.xticks(loc, x)
    plt.legend()
    plt.ylabel('Percentage of Responses')
