# nationscape-survey-tools
Read about and download the data here: https://www.voterstudygroup.org/publication/nationscape-data-set 

I wrote an article in medium based on my analysis using this module: https://adamfultz.medium.com/finding-common-ground-in-how-americans-view-abortion-52b10477d55f?source=friends_link&sk=a487c8b88846e53280ac946d6c7963ef

This repository contains Python code for Navigating the Nationscape Datasets, a massive public opinion survey created by a partnership between UCLA political scientists and the Democracy Fund Voter Study Group. 

The code takes the form of standard library functions largely built using pandas and matplotlib that are useful for analyzing, visualizing, and extracting views from the data.

#### DEMO
```python
import os
import matplotlib.pyplot as plt

import nationscape_tools as nat

# Assembling list of directories - each week's data is stored in a separate directory named nsYYYYMMDD (year, month, starting day)
path = r"C:\Users\Adam\Desktop\Python\NatlElectionData\Nationscape-DataRelease_WeeklyMaterials_DTA\combined"
os.chdir(path)
dirlist = [d for d in os.listdir(path) if not 
           os.path.isfile(os.path.join(path, d))]
# List of questions that I'm interested in analyzing - see the codes for each question in the codebook PDF file in each week's directory
qlist = ['discrimination_blacks', 'discrimination_whites', 'discrimination_women',
         'discrimination_men', 'discrimination_muslims', 'discrimination_christians']
# frame_build summarizes and aggregates the responses to each of the questions we're interested in by combining the data in each directory
data = nat.frame_build(qlist, dirlist)

# Plotting the summary data over time
with plt.style.context('seaborn'):
    fig = plt.figure()
    fig.add_axes()
    # qplot2 builds subplots, 1 for each question and prompts the user if they want to create a unique title for each subplot
    nat.qplot2(fig, data)
    plt.suptitle(
        "How much Discrimination Exists in the U.S. Today Against:", fontsize = 16)
    plt.subplots_adjust(hspace = 0.4)
    plt.figtext(
        0.17, 0.01, s = 'Data from: Tausanovitch, Chris and Lynn Vavreck. 2020. Democracy Fund + UCLA Nationscape. Retrieved from https://www.voterstudygroup.org/publication/nationscape-data-set.')   
```
Here is a picture of the plot the above code will produce:
https://github.com/adamfultz/nationscape-survey-tools/blob/main/discrimination_graphic.png

```python
import os
import matplotlib.pyplot as plt

import nationscape_tools as nat

# Assembling list of directories - each week's data is stored in a separate directory named nsYYYYMMDD (year, month, starting day)
path = r"C:\Users\Adam\Desktop\Python\NatlElectionData\Nationscape-DataRelease_WeeklyMaterials_DTA\combined"
os.chdir(path)
dirlist = [d for d in os.listdir(path) if not 
           os.path.isfile(os.path.join(path, d))]
# fuse combines the data from each directory into one single DataFrame
data = nat.fuse(dirlist)
# compare breaks down how the responses to the question (ex. maternityleave) vary based on the identity of the respondants (ex. religion)
agg = nat.compare(data, 'maternityleave', 'religion')
# preprocess transposes data and adds a summation column
agg = nat.preprocess(agg)
# Removes columns with a nearly-negligible quantity of responses
agg = agg.drop(labels = ['Buddhist', 'Hindu', 'Eastern or Greek Orthodox',
                           'Something else:'])
agg = agg.rename(index = {
    'Christian, other than the above' : 'Other Christian',
    'Nothing in particular' : 'Nothing in Particular'})

with plt.style.context('ggplot'):
    fig = plt.figure()
    fig.add_axes()
    # complot builds stacked bar graph comparing reponses to the question by the respondant's identity
    nat.complot(fig, agg2)
    plt.xlabel('Religion')
    plt.title('Companies Should be Required to Provide 12 Weeks Paid Maternity Leave')
```
Here is a picture of the plot the above code will produce:
https://github.com/adamfultz/nationscape-survey-tools/blob/main/maternityleave_graphic.png
