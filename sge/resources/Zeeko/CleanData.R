rm(list=ls())

setwd("/home/aidan/sge3/sge/resources/Zeeko/")

mydf = read.csv(file = "AusCreditFuzzy", sep = ",", stringsAsFactors = FALSE, strip.white = TRUE, colClasses=c('numeric'))
mydf = as.numeric(mydf)


mydf_Zeeko = mydf.xgboost

table(mydf_Zeeko$mydf...c.n_cols...1..)


N1 = nrow(mydf_Zeeko[mydf_Zeeko$mydf...c.n_cols...1.. == 0,])
N2 = nrow(mydf_Zeeko[mydf_Zeeko$mydf...c.n_cols...1.. == 1,])

Train_index1 <- sample(1:nrow(mydf_Zeeko[mydf_Zeeko$mydf...c.n_cols...1.. == 0,]),size=round(N1*0.75),replace=FALSE)
Train_index1 <- sort(Train_index1)
Train_index2 <- sample(1:nrow(mydf_Zeeko[mydf_Zeeko$mydf...c.n_cols...1.. == 1,]),size=round(N2*0.75),replace=FALSE)
Train_index2 <- sort(Train_index2)




write.table(mydf_Zeeko, "CyberFinal", append = FALSE, sep = " ", dec = ".",
            row.names = FALSE, col.names = FALSE)
