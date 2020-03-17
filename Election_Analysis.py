# %% markdown
# # Election Analysis
# %% markdown
# ### This is an analysis project based on Data from the 2012 election.
# ### We'll analyze 2 datasets, one with the results of political polls, and the other one with donations.
# %% markdown
# ### For the first dataset we'll try to answer some questions like:
#
# - Who was being polled and what was their party affiliatio?
# - did the poll results favor Romney or Obama?
# - how do undecided voters affect the poll?
# - can we account for the undecided voters?
# - how did voter sentiment change over time?
# - can we see an effect in the pollsfrom the debates?
# %%
import pandas as pd
from pandas import Series,DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
%matplotlib inline
import requests
from io import StringIO
from datetime import datetime
# %%
url = "http://elections.huffingtonpost.com/pollster/2012-general-election-romney-vs-obama.csv"
# %%
source = requests.get(url).text

poll_data = StringIO(source)
# %%
poll_df = pd.read_csv(poll_data)
# %%
poll_df.info()
# %%
poll_df.head()
# %%
poll_df.drop(columns=['Other', 'Question Text', 'Question Iteration'], axis=1, inplace=True)
# %%
poll_df.info()
# %%
sns.countplot('Affiliation', data=poll_df)
plt.gcf().set_size_inches(15, 8)
# %%
sns.countplot('Affiliation', data=poll_df, hue='Population')
plt.gcf().set_size_inches(15, 8)
plt.legend(loc = 'upper right')
# %%
poll_df.head()
# %%
# Let's take a look at the averages for Romney, Obama and the ones undecided
# %%
avg = pd.DataFrame(poll_df.mean())
avg.head()
# %%
avg.drop('Number of Observations', axis=0, inplace=True)
avg.head()
# %%
std = pd.DataFrame(poll_df.std())
std.drop('Number of Observations', axis=0, inplace=True)
# %%
std.head()
# %%
# Now let's plot the averages and make the y error equals to the standard deviation we got
# %%
avg.plot(yerr=std, kind='bar', legend=False)
plt.gcf().set_size_inches(15, 8)
# %%
# As we can see the polls are really close, even considering the undecided factor. Let's take a look at those numbers
# %%
poll_avg = pd.concat([avg,std], axis=1)
poll_avg.columns = ['Average', 'STD']
poll_avg
# %%
# It looks like Obama and Romney are really close, but what about the undecided?
# %%
# Let's do a quick time series analysis of voter sentiment by plotting Obama, Romney favor versus the pool end dates.
# %%
poll_df.head()
# %%
poll_df.plot(x='End Date', y=['Obama', 'Romney', 'Undecided' ], linestyle='', marker='o')
plt.gcf().set_size_inches(15, 8)
# %%
# The above plot is just to have a general idea of how sentiment goes over time.
# Now, what we're gonna do is to plot out the difference between Obama and Romney and see how that changes as time moves along.
# %%
poll_df['Difference'] = (poll_df.Obama - poll_df.Romney) / 100
# %%
poll_df.head()
# %%
poll_df = poll_df.groupby(['Start Date'], as_index=False).mean()

poll_df.head()
# %%
poll_df.plot('Start Date', 'Difference', marker='o', linestyle='-', color='purple')
plt.gcf().set_size_inches(15,8)
# %%
# There are 2 particular points in October that are unusual.
# We know that the debates took place in October, so let's zoom in and see that specific month.
# %%
row_in = 0
xlimit = []

for date in poll_df['Start Date']:
    if date[0:7] == '2012-10':
        xlimit.append(row_in)
        row_in += 1
    else:
        row_in += 1
print(min(xlimit))
print(max(xlimit))
# %%
poll_df.plot('Start Date', 'Difference', marker='o', linestyle='-', color='red', xlim=(325,352))
plt.gcf().set_size_inches(15,8)

# Oct 3rd
plt.axvline(x=325+2, linewidth=4, color='grey')
# Oct 11th
plt.axvline(x=325+10, linewidth=4, color='grey')
# Oct 22nd
plt.axvline(x=325+21, linewidth=4, color='grey')
# %%
# Now we have the October month only, and markers on every debate point.
# It seems, based on the plot, that after the first debate that happened on October 3rd, the sentiment for Obama increased.
# After the second debate the sentiment for Romney became more favorable.
# After the third debate everyone was pretty even.
# %% markdown
# ## Now let's see the Donor's dataset
# %%
# The dataset can be found on this link:

url = 'https://www.dropbox.com/s/l29oppon2veaq4n/Election_Donor_Data.csv?dl=0'
# %% markdown
# ### Some of the questions we could answer are:
#
# - how much was donated and what was the average donation?
# - how did the donations differ between candidates?
# - how did the donations differ between Democrats and Republicans?
# - what were the demographics of the donors?
# - is there a pattern to donation amounts?
# %%
donor_df = pd.read_csv('Election_Donor_Data.csv')
# %%
donor_df.info()
# %%
donor_df.head()
# %%
donor_df['contb_receipt_amt'].value_counts()
# %%
# Let's take a look at the average and standar deviation
# %%
don_mean = donor_df['contb_receipt_amt'].mean()

don_std = donor_df['contb_receipt_amt'].std()

print('The average donation was %.2f with a std of %.2f' %(don_mean,don_std))
# %%
# This is a huge standard deviation. Let's investigate that
# %%
top_donor = donor_df['contb_receipt_amt'].copy()

top_donor.sort_values(ascending=True, inplace=True)

top_donor
# %%
# we have two issues here: negative refund amounts and very large donations. That's what is causing our big standard deviation.
# Let's get rid of the negative refund amounts so that our distribution can make sense.
# %%
top_donor = top_donor[top_donor > 0]
top_donor.sort_values(ascending=True, inplace=True)
# %%
top_donor.value_counts().head(10)
# %%
# These are the most common amounts
# %%
# Now, let's do a histogram to visualize it, but we will limit it to 2,500 since that was the biggest donation in the top 10.
# %%
com_don = top_donor[top_donor < 2500]
sns.set()
com_don.hist(bins=100)
plt.gcf().set_size_inches(15,8)
# %%
# It seems people are inclined to donate rounded number values
# %%
# We'll dive deeper and try to separate donations by party.
# %%
candidates = donor_df.cand_nm.unique()
candidates
# %%
# Dictionary of party affiliation
party_map = {'Bachmann, Michelle': 'Republican',
           'Cain, Herman': 'Republican',
           'Gingrich, Newt': 'Republican',
           'Huntsman, Jon': 'Republican',
           'Johnson, Gary Earl': 'Republican',
           'McCotter, Thaddeus G': 'Republican',
           'Obama, Barack': 'Democrat',
           'Paul, Ron': 'Republican',
           'Pawlenty, Timothy': 'Republican',
           'Perry, Rick': 'Republican',
           "Roemer, Charles E. 'Buddy' III": 'Republican',
           'Romney, Mitt': 'Republican',
           'Santorum, Rick': 'Republican'}

# Now map the party with candidate
donor_df['Party'] = donor_df.cand_nm.map(party_map)
# %%
donor_df = donor_df[donor_df.contb_receipt_amt > 0]
# %%
donor_df.head()
# %%
donor_df.groupby('cand_nm')['contb_receipt_amt'].count()
# %%
# As we can see, Obama had the highest number of donations. Now let's take a look at those values in dollars
# %%
donor_df.groupby('cand_nm')['contb_receipt_amt'].sum()
# %%
# The way it's presented is a little bit hard to read. Let's make it more readable
# %%
cand_amount = donor_df.groupby('cand_nm')['contb_receipt_amt'].sum()

i=0

for don in cand_amount:
    print('The candidate %s raise %.0f dollars' %(cand_amount.index[i], don))
    print('\n')
    i += 1
# %%
# Now it's better to read but kinda hard to compare. Let's put it into a graph
# %%
cand_amount.plot(kind='bar')
plt.gcf().set_size_inches(15,8)
# %%
# Since Obama is the only Democrat, let's compare it with all the other Republicans
# %%
donor_df.groupby('Party')['contb_receipt_amt'].sum().plot(kind='bar')
plt.gcf().set_size_inches(15,8)
# %%
# Looks like Obama couldn't compete against all the republicans, but he certainly has the advantage of their funding
# being splintered across multiple candidates.
# %%
# Let's look at donations and who they came from (as far as occupation is concerned)
# %%
occupation_df = donor_df.pivot_table('contb_receipt_amt', index = 'contbr_occupation',
                                    columns = 'Party', aggfunc = 'sum')
# %%
occupation_df.head()
# %%
occupation_df.tail()
# %%
occupation_df.shape
# %%
# Let's see what occupations, as a group, contributed more than a million dollars total.
# %%
occupation_df = occupation_df[occupation_df.sum(1) > 1000000]
# %%
occupation_df.shape
# %%
occupation_df.plot(kind='bar')
plt.gcf().set_size_inches(15,8)
# %%
occupation_df.plot(kind='barh', cmap='seismic')
plt.gcf().set_size_inches(15,12)
# %%
# We have a few issues on this graph. We have 'Information requested per best efforts' and 'Information requested'
# which are not actually an occupation, and we have 2 CEO occupations, which are actually the same thing.
# %%
occupation_df.drop(['INFORMATION REQUESTED PER BEST EFFORTS', 'INFORMATION REQUESTED'], axis=0, inplace=True)
# %%
occupation_df.loc['CEO'] = occupation_df.loc['CEO'] + occupation_df.loc['C.E.O.']

occupation_df.drop('C.E.O.', inplace=True)
# %%
occupation_df.plot(kind='barh', cmap='seismic')
plt.gcf().set_size_inches(15,12)
