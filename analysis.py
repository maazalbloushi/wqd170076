import json
import pandas as pd
import time
import datetime
import matplotlib.pyplot as plt
from pylab import get_current_fig_manager


from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

from sklearn.preprocessing import MinMaxScaler

# ────────────────────────────────────────────────────────────────────────────────

with open('20190927-TM.json', 'r') as handle:
    TMdump = json.loads(handle.read())
TMdf = pd.DataFrame(TMdump)
TMdf['t']= TMdf['t'].astype(str)
for idx, row in TMdf.iterrows():
    TMdf.iat[idx, TMdf.columns.get_loc('t')] = str(time.strftime('%Y-%m-%d', time.localtime(int(row['t']))))

# TMtrend = pd.read_csv('TM_searchFreq.csv')

# for idx, row in TMtrend.iterrows():
#     TMtrend.iat[idx, TMtrend.columns.get_loc('Month')] = datetime.datetime.date(datetime.datetime.strptime(row['Month'], "%Y-%m"))

TMdf['t'] = pd.to_datetime(TMdf['t'])
TMdf = TMdf.set_index('t')
TMdf2 = TMdf.resample('M').mean()
TMdf2['Trend'] = TMtrend['Telekom Malaysia: (Malaysia)'].tolist()
TMmms = MinMaxScaler()
TMXn = TMmms.fit_transform(TMdf2[['o','Trend']].values)

# ────────────────────────────────────────────────────────────────────────────────

l0 = plt.plot(TMdf2.index, TMXn[:,0], label='o')
# l0 = plt.plot(TMdf.index, TMdf.index, label='o')

l1 = plt.plot(TMdf2.index, TMXn[:,1], label='Trend')
plt.title('TM')
plt.legend([l0, l0],     # The line objects
           labels=['Stock', 'Trend'],   # The labels for each line
           loc="center right",   # Position of legend
           borderaxespad=0.1,    # Small spacing around legend box
           )
plt.tight_layout()

plt.show()


# l0 = plt.plot(TMdf2.index[-40:], TMXn[-40:,0], label='o')
# l1 = plt.plot(TMdf2.index[-40:], TMXn[-40:,1], label='Trend')
# plt.title('TM')
# plt.legend([l0, l1],     # The line objects
#            labels=['Stock', 'Trend'],   # The labels for each line
#            loc="center right",   # Position of legend
#            borderaxespad=0.1,    # Small spacing around legend box
#            )
# plt.tight_layout()

# plt.show()