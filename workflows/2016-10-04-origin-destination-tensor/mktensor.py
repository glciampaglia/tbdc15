#!/usr/bin/env python

"""Create a tensor from compressed infoblu archive."""

import numpy
import pandas
import argparse
import tarfile

column_names = ['trip', 'timestamp', 'lat', 'lon', 'vehicle', 'speed']
use_columns = ['trip', 'timestamp', 'lat', 'lon']


def digitize(lat, lon, box, scale):
    '''
    Transform one or more lat/lon pairs into 2D grid coordinates relative
    to a box and a given resolution (scale).
    '''
    i = numpy.floor(scale * (lat - box['lat_min'])).astype('int')
    j = numpy.floor(scale * (lon - box['lon_min'])).astype('int')
    return i, j


def gridshape(box, scale):
    '''
    Return the dimensions of the grid for the given resolution (scale).
    '''
    i_max, j_max = digitize(box['lat_max'], box['lon_max'], box, scale)
    shape = (i_max + 1, j_max + 1)
    return shape


def tocells(df, box, scale):
    '''
    Digitize latitude/longitude coordinates (see function digitize), and
    convert the resulting 2D grid coordinates into the corresponding ordinal
    cell numbers, relative to the box and given resolution (scale).

    Given an NxM matrix the ordinal number of cell (i, j)
    is:
        c = i + j * N

    Where indices start at 0 according to the Python convention. Returns a data
    frame where the lat and lon columns have been dropped and have been
    replaced with a column named 'c'.
    '''
    shape = gridshape(box, scale)
    i, j = digitize(df['lat'], df['lon'], box, scale)
    df['c'] =  i + j * shape[0]
    return df.drop(['lat', 'lon'], axis=1)


def makeparser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trips_file',
                        metavar='trips',
                        help='Tar archive with daily trip dumps',
                        type=argparse.FileType())
    parser.add_argument('box_file',
                        metavar='box_file',
                        help='Text file with coordinates of all city boxes',
                        type=argparse.FileType())
    parser.add_argument('output_file',
                        metavar='output',
                        help='Write data to HDF file')
    parser.add_argument('city_code',
                        metavar='city',
                        help='One-letter city code. Available: %(choices)s',
                        choices=list('bmnprtv'))
    parser.add_argument('-s',
                        '--scale',
                        help='spatial grid resolution (default: %(default)s per degree)',
                        type=int,
                        default=1000)
    parser.add_argument('--min-duration',
                        metavar='STRING',
                        help='Count only trips with minimum duration (%(metavar)s can be e.g. "1h", see pandas.Timedelta). Default: %(default)r',
                        type=pandas.Timedelta,
                        default=pandas.Timedelta('1m'))
    parser.add_argument('--max-duration',
                        metavar='STRING',
                        help='Count only trips with maximum duration (%(metavar)s can be e.g. "1h", see pandas.Timedelta). Default: %(default)r',
                        type=pandas.Timedelta,
                        default=pandas.Timedelta('1h'))
    parser.add_argument('--only',
                        metavar='NUM',
                        help='Read only %(metavar)s dumps from the Tar file.',
                        type=int)
    return parser


def main():
    parser = makeparser()
    args = parser.parse_args()
    df_box = pandas.read_csv(args.box_file, index_col='city')
    box = df_box.ix[args.city_code].to_dict()
    # open tar file in random access mode with on-the-fly gzip decompression
    with tarfile.open(fileobj=args.trips_file, mode='r:gz') as tf:
        frames = []
        cnt = 0
        for member in tf:
            if args.only is not None and cnt >= args.only:
                break
            print member.name
            f = tf.extractfile(member)
            df = processframe(f, box, args.scale, args.min_duration,
                              args.max_duration)
            frames.append(df)
            cnt += 1
    df = pandas.concat(frames)
    ts0 = df['timestamp'].min()
    vals = df['trips']
    df['timestamp_index'] = (df['timestamp'] - ts0).astype('m8[h]').astype(int)
    subs = df[['timestamp_index', 'origin', 'destination']]
    timestamps = df['timestamp']
    lat_dim, lon_dim = gridshape(box, args.scale)
    shape_df = pandas.DataFrame({0: {'lat': lat_dim, 'lon': lon_dim}}).T
    with pandas.HDFStore(args.output_file, mode='w',
                         complevel=9, complib='blosc') as store:
        store['/{}/vals'.format(args.city_code)] = vals
        store['/{}/subs'.format(args.city_code)] = subs
        store['/{}/shape'.format(args.city_code)] = shape_df
        store['/{}/timestamps'.format(args.city_code)] = timestamps
    print 'Data written to {}:/{}'.format(args.output_file, args.city_code)
    return df


def processframe(fileobj, box, scale, min_duration, max_duration):
    """
    Converts infoblu trips data into hour-origin-destination counts.

    Returns a data frame with the following columns:
        - timestamp
            with hourly frequencies
        - origin
            ordinal cell number
        - destination
            ordinal cell number
        - trips
            number of trips from origin to destination started within that hour
    """
    df = pandas.read_csv(fileobj,
                         sep=';',
                         names=column_names,
                         usecols=use_columns,
                         parse_dates=['timestamp'])
    # get the cell number of the trip origin
    df_orig = tocells(df.groupby('trip').first(), box, scale)
    # get the cell number of the trip destination
    df_dest = tocells(df.groupby('trip').last(), box, scale)
    # join origins to destinations and compute trip durations
    df_od = df_orig.join(df_dest, lsuffix='_orig', rsuffix='_dest')
    df_od['duration'] = df_od['timestamp_dest'] - df_od['timestamp_orig']
    # take only trips whose duration falls within requested min/max durations
    idx = (df_od['duration'] > min_duration) & (df_od['duration'] < max_duration)
    df_od = df_od[idx]
    # adjust column names, drop columns that are not needed anymore
    df_od.drop(['timestamp_dest', 'duration'], axis=1, inplace=True)
    df_od.rename(columns={'c_orig': 'origin',
                          'c_dest': 'destination',
                          'timestamp_orig': 'timestamp'},
                 inplace=True)
    # group trips by origin, destination, and hourly timestamp of departure
    df_od.reset_index(inplace=True)
    df_od.rename(columns={'trip': 'trips'}, inplace=True)
    tg = pandas.TimeGrouper(freq='H')
    groupby_cols = [tg, 'origin', 'destination']
    return df_od.set_index('timestamp').groupby(groupby_cols).count().reset_index()


if __name__ == '__main__':
    df = main()
