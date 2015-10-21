from pylab import *
import pandas
scale = 1000.0
df = pandas.read_csv('/home/giovanni/data/telecom_big_data_challenge_2015/output_20150301_PALERMO.txt.gz', compression='gzip', names=['trip_id','timestamp','lat','lon','type','speed'], sep=';')
df_box = pandas.read_csv('/home/giovanni/data/telecom_big_data_challenge_2015/city_boxes.csv', index_col='city')
df_box.ix['p']
box = df_box.ix['p'].to_dict()
df['i'] = ((df['lat'] - box['lat_min']) * scale).round()
df['j'] = ((df['lon'] - box['lon_min']) * scale).round()
trips = df.groupby(['i', 'j'], as_index=False).count().filter(['i','j','trip_id']).rename(columns={'trip_id': 'trips'})
accidents = pandas.read_csv('/home/giovanni/data/telecom_big_data_challenge_2015/BDC2015_UnipolsaiClaims2014_PA.csv')
accidents['i'] = ((accidents['latitude'] - box['lat_min']) * scale).round()
accidents['j'] = ((accidents['longitude'] - box['lon_min']) * scale).round()
accidents_grouped = accidents.groupby(['i', 'j'], as_index=False).count().filter(['i','j','day_type']).rename(columns={'day_type': 'accidents'})
joined_df = trips.set_index(['i','j']).join(accidents_grouped.set_index(['i','j'])).fillna(0)
joined_df.plot(x='trips', y='accidents', linestyle='none', marker='x', alpha=.2, color='k')
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
