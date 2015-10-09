map.city <- function(filename, city, city_file, accidents, week.day, scale=1000)
{
  jet.colors <- colorRampPalette(c("#00007F", "blue", "#007FFF", "cyan", "#7FFF7F", "yellow", "#FF7F00", "red"))
  
  cores <- c('#009EE0',
             '#FD0A0A',
             '#7D86C7',
             '#40E300',
             '#B8007C',
             '#F7E123',
             '#6A009C',
             '#000000',
             '#1B00A6',
             '#336868',
             '#7D86C7')
  
  cities <- read.table('boxes.dat', head=F, sep=',')
  coords <- unlist(cities[cities$V1==substr(tolower(city), 1, 1), 2:5])
  
  data <- read.table(filename, head=F)
  width <- as.integer((coords[1]-coords[2])*scale) 
  height <- as.integer((coords[3]-coords[4])*scale)
  mat <- matrix(0, ncol=width, nrow=height)
  mat.acc <- matrix(0, ncol=width, nrow=height)
  
  Max <- max(data$V3)+1
  
  for(i in seq(1,length(data$V1)))
  {
    if(data$V1[i] < height & data$V2[i] < width)
    {
      mat[data$V1[i], data$V2[i]] <- data$V3[i]
    }
  }
  
  city <- readShapeSpatial(city_file)
  plot(city, col='gray70', bg='white')

  x <- coords[2]+seq(1, width)*(coords[1]-coords[2])/width
  y <- coords[4]+seq(1, height)*(coords[3]-coords[4])/height                
    
  image(x, y, log10(t(mat[height:1,]))/log10(Max),
        col='white',#(gray.colors(256)), 
        add=T,
        useRaster=T,
  )
  
  accidents <- read.table(accidents, head=T, sep=',')
  day <- accidents #accidents[accidents$day_type==week.day,]
  
  points(x=day$longitude, y=day$latitude, pch=15, cex=0.3, col='red')
  
  Max <- max(data$V3)+1
  
  #image(x, y, t(mat.acc[height:1,]),
  #      col=jet.colors(256), 
  #      add=T,
  #      useRaster=T,
  #)
  
#   day$color <- 'red'
#   day$color[day$time_range >=6 & day$time_range <= 20] <- 'cyan'
#   day <- day[order(day$color),]
# 
#   points(x=day$longitude, y=day$latitude, type='p', pch=15, cex=0.6, col=day$color)
  
  day$color <- 'red'
#   day$color[day$time_range >=0 & day$time_range < 6] <- 'cyan'
#   day$color[day$time_range >=6 & day$time_range < 12] <- 'yellow'
#   day$color[day$time_range >=12 & day$time_range < 18] <- 'red'
#   day$color[day$time_range >=18 & day$time_range < 24] <- 'green'
  
day$color[day$time_range >=0 & day$time_range < 6] <- rgb(230, 97, 1, maxColorValue=255)
day$color[day$time_range >=6 & day$time_range < 12] <- rgb(253, 184, 99, maxColorValue=255)
day$color[day$time_range >=12 & day$time_range < 18] <- rgb(178, 171, 210, maxColorValue=255)
day$color[day$time_range >=18 & day$time_range < 24] <- rgb(94, 60, 153, maxColorValue=255)


  points(x=day$longitude, y=day$latitude, type='p', pch=15, cex=0.6, col=day$color)

  return(mat)
}


map.city.3d <- function(filename, city, shapefile, acc, scale=1000)
{
  require(maptools)
  require(lattice)
  jet.colors <- colorRampPalette(c("#00007F", "blue", "#007FFF", "cyan", "#7FFF7F", "yellow", "#FF7F00", "red"))
  
  cities <- read.table('boxes.dat', head=F, sep=',')
  coords <- unlist(cities[cities$V1==substr(tolower(city), 1, 1), 2:5])
  print(coords[2])
  
  
  data <- read.table(filename, head=F)
  width <- as.integer((coords[1]-coords[2])*scale) 
  height <- as.integer((coords[3]-coords[4])*scale)
  
  data$V1 <- coords[2]+data$V1*(coords[1]-coords[2])/width
  data$V2 <- coords[4]+data$V2*(coords[3]-coords[4])/height
  
  state.map <-  readShapeSpatial(shapefile)
  accidents <- read.table(acc, header=T, sep=',')
    
  #accidents <- accidents[accidents$day_type==1,]
  
  print(head(accidents))
  
  bla <- as.data.frame(state.map@polygons[1][[1]]@Polygons[1][[1]]@coords)
  colnames(bla) <- c("x", "y")
  state.map <- bla
  
  panel.3dmap <- function(..., rot.mat, distance, xlim, ylim, zlim, xlim.scaled, ylim.scaled, zlim.scaled)
  {
    scaled.val <- function(x, original, scaled)
    {
      scaled[1] + (x - original[1]) * diff(scaled) / diff(original)
    }
    
    
    m2 <- ltransform3dto3d(rbind(scaled.val(state.map$x, xlim, xlim.scaled),
                                scaled.val(state.map$y, ylim, ylim.scaled),
                                zlim.scaled[1]), 
                          rot.mat, distance)
    
    panel.xyplot(m2[1,],m2[2,], type='p', col=1, pch=15, cex=.1)
  }
  
  panel.3dmap2 <- function(..., rot.mat, distance, xlim, ylim, zlim, xlim.scaled, ylim.scaled, zlim.scaled)
  {
    scaled.val <- function(x, original, scaled)
    {
      scaled[1] + (x - original[1]) * diff(scaled) / diff(original)
    }
    
    
    m2 <- ltransform3dto3d(rbind(scaled.val(data$V1, xlim, xlim.scaled),
                                 scaled.val(data$V2, ylim, ylim.scaled),
                                 zlim.scaled[1]), 
                           rot.mat, distance)
    
    panel.xyplot(m2[1,], m2[2,], type='p', col=1, pch=15, cex=.1)
  }
  
  accidents$day_type2 <- accidents$day_type*0.002
  
  map <- cloud(day_type2 ~ longitude * latitude, accidents,
               panel.3d.cloud = function(...) {
                 panel.3dmap(...)
                 panel.3dmap2(...)
                 panel.3dscatter(...)
               }, 
               type = "h", 
               scales = list(draw = TRUE), zoom = 1.18,
               #xlim = x[1:2], ylim = x[3:4],
               xlim = range(data$V1), ylim=range(data$V2),
               xlab = NULL, ylab = NULL, zlab = NULL,
               #aspect = c(diff(x[3:4]) / diff(x[1:2]), 0.35),
               aspect = c(diff(range(data$V2))/diff(range(data$V1)), 0.35),
               panel.aspect = 0.50, lwd = 1.5, screen = list(z = 25, x = -50),
               par.settings = list(axis.line = list(col = "transparent"),
                                   box.3d = list(col = "transparent", alpha = 0)),
               col.line = accidents$day_type
  )
  
  print(map)
}