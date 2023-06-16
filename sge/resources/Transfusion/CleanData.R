rm(list=ls())

setwd("/home/aidan/sge3/sge/resources/Transfusion/")

mydf = read.csv(file = "TransfusionFuzzy", sep = ",", stringsAsFactors = FALSE, strip.white = TRUE, colClasses=c('numeric'))
mydf = as.numeric(mydf)

table(mydf$transf.y)


N1 = nrow(mydf[mydf$transf.y == 0,])
N2 = nrow(mydf[mydf$transf.y == 1,])

Train_index1 <- sample(1:nrow(mydf[mydf$transf.y == 0,]),size=round(N1*0.75),replace=FALSE)
Train_index1 <- sort(Train_index1)
Train_index2 <- sample(1:nrow(mydf[mydf$transf.y == 1,]),size=round(N2*0.75),replace=FALSE)
Train_index2 <- sort(Train_index2)




write.table(mydf, "TransfusionFinal", append = FALSE, sep = " ", dec = ".",
            row.names = FALSE, col.names = FALSE)
