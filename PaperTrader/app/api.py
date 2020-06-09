# pip install datareader
import pandas as pd
import matplotlib.pyplot as plt
import quandl
from datetime import datetime, timedelta
import base64
from io import BytesIO

fig = plt.figure()


pd.core.common.is_list_like = pd.api.types.is_list_like

quandl.ApiConfig.api_key = "ytVQuTa78YZWSMYobhks"
end = datetime.now()
start = end - timedelta(days=365)

mydata2 = quandl.get('FSE/VOW3_X', start_date=start, end_date=end)
f = mydata2.reset_index()
# timeseries
plt.figure(1)
f = pd.Series(f.Close.values, f.Date)
f.plot()
plt.show()


tmpfile = BytesIO()
fig.savefig(tmpfile, format='png')


encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

html = '' + '<img src=\'data:image/png;base64,{}\'>'.format(encoded) + ''

with open('chart.html','w') as f:
    f.write(html)