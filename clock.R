plot.clock <- function(filename, tit=NA, norm=T)
{
  require(plotrix)
  data <- read.table(filename, head=F)
  
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
  
  days <- unique(data$V3)
  days <- days[order(days)]
  
  for(day in days)
  {
    one.day <- data[data$V3==day, ]
    if(norm)
    {
      one.day$V2 <- one.day$V2/sum(one.day$V2)
    }
    
    o <- order(one.day$V1)
    one.day <- one.day[o,]
    
    data[data$V3==day, ] <- one.day
  }
    
  max.day<- data$V3[data$V2 == max(data$V2)]  
  one.day <- data[data$V3==max.day, ]

  polar.plot(one.day$V2, one.day$V1*15, rp.type='l', clockwise=T, start=270, 
             labels=seq(0,23), label.pos=seq(0,23)*15-180, 
             line.col=NA)

  for(day in days)
  {
    one.day <- data[data$V3==day, ]
    
    polar.plot(one.day$V2, one.day$V1*15, rp.type='p', clockwise=T, start=270, 
               line.col=cores[day], add=T, lwd=3)
    print(paste(day, max(one.day$V2), one.day$V1[one.day$V2==max(one.day$V2)], sep=' '))
  }
  
  legend('bottom', legend=c('M','T','W','Th','F','Sa','Su'), text.col=cores[seq(1,7)], fill=cores[seq(1,7)])
  title(main=tit)
  return(one.day)
}

plot.all <- function()
{
  width=500
  height=500
  
#   png('Rome.png', width=width, height=height)
#   bla <- plot.clock('accidents_RM.dat', 'Rome')
#   dev.off()
# 
#   png('Bari.png', width=width, height=height)
#   bla <- plot.clock('accidents_BA.dat', 'Bari')
#   dev.off()
# 
#   png('Napoli.png', width=width, height=height)
#   bla <- plot.clock('accidents_NA.dat', 'Napoli')
#   dev.off()
# 
#   png('Venezia.png', width=width, height=height)  
#   bla <- plot.clock('accidents_VE.dat', 'Venezia')
#   dev.off()
# 
#   png('Torino.png', width=width, height=height)
#   bla <- plot.clock('accidents_TO.dat', 'Torino')
#   dev.off()
# 
#   png('Palermo.png', width=width, height=height)
#   plot.clock('accidents_PA.dat', 'Palermo')
#   dev.off()
# 
#   png('Milano.png', width=width, height=height)
#   bla <- plot.clock('accidents_MI.dat', 'Milano')
#   dev.off()
#   


  png('trips_Rome.png', width=width, height=height)
  bla <- plot.clock('infoblu/starts_rome.dat', 'Rome trips')
  dev.off()
  
  png('trips_Bari.png', width=width, height=height)
  bla <- plot.clock('infoblu/starts_bari.dat', 'Bari trips')
  dev.off()
  
  png('trips_Napoli.png', width=width, height=height)
  bla <- plot.clock('infoblu/starts_napoli.dat', 'Napoli trips')
  dev.off()
  
  png('trips_Venezia.png', width=width, height=height)  
  bla <- plot.clock('infoblu/starts_venezia.dat', 'Venezia trips')
  dev.off()
  
  png('trips_Torino.png', width=width, height=height)
  bla <- plot.clock('infoblu/starts_torino.dat', 'Torino trips')
  dev.off()
  
  png('trips_Palermo.png', width=width, height=height)
  bla <- plot.clock('infoblu/starts_palermo.dat', 'Palermo trips')
  dev.off()
  
  png('trips_Milano.png', width=width, height=height)
  bla <- plot.clock('infoblu/starts_milano.dat', 'Milano trips')
  dev.off()
}

scatter <- function(trips, accidents)
{
  accidents <- read.table(accidents, head=F)
  trips <- read.table(trips, head=F)
  
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
  
  days <- unique(accidents$V3)
  days <- days[order(days)]
  
  plot(1, xlim=c(0,1),ylim=c(0,1), type='n', xlab='trips', ylab='accidents', pch=15, col=day, las=1)
  
  for(day in days)
  {
    accidents.day <- accidents[accidents$V3==day,]
    trips.day <- trips[trips$V3==day,]
    
    merged <- merge(trips.day, accidents.day, by=1, all=T)
    merged$V2.y[is.na(merged$V2.y)] <- 0
    
    data <- merged[,c("V2.x","V2.y")]
    colnames(data) <- c("x","y")
    o <- order(data$x)
    points(x=data$x[o]/max(data$x), y=data$y[o]/max(data$y), pch=15+day, col=day)
  }
}
