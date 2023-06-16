rm(list=ls())

setwd("/home/aidan/sge3/sge/resources/Census/")

mydf = read.csv(file = "IncomeFuzzy", sep = ",", stringsAsFactors = FALSE, strip.white = TRUE, colClasses=c('numeric'))
mydf = read.csv(file = "IncomeTestFuzzy", sep = ",", stringsAsFactors = FALSE, strip.white = TRUE, colClasses=c('numeric'))
mydf = as.numeric(mydf)

table(mydf$IncomeDep)


N1 = nrow(mydf[mydf$as.numeric.pima.diabetes....1 == 0,])
N2 = nrow(mydf[mydf$as.numeric.pima.diabetes....1 == 1,])

#Train_index1 <- sample(1:nrow(mydf[mydf$as.numeric.AusCredit.y....1 == 0,]),size=round(N1*0.75),replace=FALSE)
#Train_index1 <- sort(Train_index1)
#Train_index2 <- sample(1:nrow(mydf[mydf$as.numeric.AusCredit.y....1 == 1,]),size=round(N2*0.75),replace=FALSE)
#Train_index2 <- sort(Train_index2)




write.table(mydf, "IncomeTestFinal", append = FALSE, sep = " ", dec = ".",
            row.names = FALSE, col.names = FALSE)
