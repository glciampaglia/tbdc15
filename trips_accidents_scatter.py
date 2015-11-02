from pylab import *
import os
import pandas
import tarfile
scale = 1000.0

trips_path = os.path.expanduser('~/data/tbdc2015/infoblu/palermo.tar.gz')
accidents_path = os.path.expanduser('~/data/tbdc2015/unipol/BDC2015_UnipolsaiClaims2014_PA.csv')
boxes_path = os.path.expanduser('~/data/tbdc2015/city_boxes.csv')
city_code = 'p'

# ## Read data

# ### Bounding boxes data
df_box = pandas.read_csv(boxes_path, index_col='city')
df_box.ix[city_code]
box = df_box.ix[city_code].to_dict()

# ### Trips data
index_columns = ['i', 'j', 'weekday', 'hour']
with tarfile.open(trips_path, mode='r:gz') as tf:
    # open tar file in random access mode with on-the-fly gzip decompression
    frames = []
    for member in tf:
        print member.name
        f = tf.extractfile(member)
        df = pandas.read_csv(f, names=['trip_id','timestamp','lat','lon','type','speed'], sep=';', parse_dates=['timestamp'])
        df.rename(columns={'trip_id': 'trips'}, inplace=True)
        df['i'] = ((df['lat'] - box['lat_min']) * scale).round()
        df['j'] = ((df['lon'] - box['lon_min']) * scale).round()
        df['weekday'] = df['timestamp'].map(pandas.Timestamp.weekday)
        df['hour'] = df['timestamp'].map(lambda k: k.hour)
        frames.append(df)

df = pandas.concat(frames)
trips = df.groupby(['i', 'j', 'weekday', 'hour'], as_index=False).count().filter(index_columns + ['trips'])

# ### Accidents data
accidents = pandas.read_csv(accidents_path)
accidents.rename(columns={'day_type': 'weekday', 'time_range': 'hour'}, inplace=True)
accidents['i'] = ((accidents['latitude'] - box['lat_min']) * scale).round()
accidents['j'] = ((accidents['longitude'] - box['lon_min']) * scale).round()
accidents['accidents'] = 1
accidents_grouped = accidents.groupby(['i', 'j', 'weekday', 'hour'], as_index=False).count().filter(index_columns + ['accidents'])

# ## Join data
joined_df = trips.set_index(index_columns).join(accidents_grouped.set_index(index_columns)).fillna(0)
joined_df.to_hdf("trip_accidents_store.hdf", 'palermo')
print "Data saved to HDF."

# ## Plot
#
# ### Scatter plot of each cell
joined_df.plot(x='trips', y='accidents', linestyle='none', marker='x', alpha=.2, color='k')
#
# ### Bin by traffic density level and average
joined_df.groupby(joined_df.trips // 10).mean().plot(x='trips', y='accidents',
                                                     color='r', linestyle='solid',
                                                     ax=gca(), alpha=.5, linewidth=2)
xlim(joined_df['trips'].min(), joined_df['trips'].max() / 2)
ylim(joined_df['accidents'].min(), joined_df['accidents'].max())
grid('off')
title('Palermo')
xlabel('Traffic (Trip starts)')
ylabel('Insurance claims')
tight_layout()
savefig('trips_accidents_scatter_PA.pdf')
show()
