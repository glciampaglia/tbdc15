#!/usr/bin/env python

import sys
import gzip

if __name__ == "__main__":

    cities = {}

    for line in open("boxes.dat"):
        fields = line.strip().split(',')
        cities[fields[0]] = [float(field) for field in fields[1:]]

    scale = 1000.
    matrix = {}

    city = cities[sys.argv[1].lower()[0]]

    lat_min = city[3]
    lat_max = city[2]
    lon_min = city[1]
    lon_max = city[0]

    for filename in sys.argv[2:]:
        print >> sys.stderr, filename

        for line in gzip.open(filename):
            fields = line.strip().split(';')

            lat = float(fields[2])
            lon = float(fields[3])

            if lat > lat_max or lat < lat_min:
                continue

            if lon > lon_max or lon < lon_min:
                continue

            cell = (int(lat*scale)/scale, int(lon*scale)/scale)

            matrix[cell] = matrix.get(cell, 0) + 1

    for key, value in matrix.iteritems():
        print int((lat_max-key[0])*scale), int((key[1]-lon_min)*scale), value
