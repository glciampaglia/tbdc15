#!/usr/bin/env Rscript

get.box <- function(filename)
{
  require(maptools)
  city <- readShapeSpatial(filename)
  
  coords <- NULL
  
  for(polygon in city@polygons[1][[1]]@Polygons)
  {
    coords <- rbind(coords, polygon@coords)
  }
  
  print(paste(max(coords[,1]),
              min(coords[,1]),
              max(coords[,2]),
              min(coords[,2]), 
              sep=","))
  
  return(city)
}

argv <- commandArgs(trailingOnly = T)

if(length(argv) != 1)
{
  quit()
}

city <- get.box(argv[1])