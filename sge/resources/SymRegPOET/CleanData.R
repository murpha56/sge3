rm(list=ls())
library(openxlsx)
setwd("/home/aidan/sge3/sge/resources/SymRegPOET/")


mydf = read.xlsx("TestEpoch1a_GD_Reduced.xlsx")
#mydf = read.xlsx("Gd_Peptides_Features.xlsx")
mydf = as.numeric(mydf)

#table(mydf$as.numeric.pima.diabetes....1)
#N1 = nrow(mydf[mydf$as.numeric.pima.diabetes....1 == 0,])
#N2 = nrow(mydf[mydflibrary(openxlsx)$as.numeric.pima.diabetes....1 == 1,])

#Train_index1 <- sample(1:nrow(mydf[mydf$as.numeric.AusCredit.y....1 == 0,]),size=round(N1*0.75),replace=FALSE)
#Train_index1 <- sort(Train_index1)
#Train_index2 <- sample(1:nrow(mydf[mydf$as.numeric.AusCredit.y....1 == 1,]),size=round(N2*0.75),replace=FALSE)
#Train_index2 <- sort(Train_index2)



#mydf2 = mydf[,c(3:78,2)]


write.table(mydf, "Gd_Epoch1_Test_Motif_Reduced", append = FALSE, sep = " ", dec = ".",
            row.names = FALSE, col.names = FALSE)
