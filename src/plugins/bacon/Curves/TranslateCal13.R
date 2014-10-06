
################################################################
### Program to translate the IntCal13 curves to the standard format:
### cal. BP   rc BP    std. error,
### in cal. BP increasing order, with no commas.
#################################################################


### Read the terrestrial and Marine curves files as distributed in
### http://www.radiocarbon.org/IntCal13.htm :

cc.terr <- read.csv( "intcal13.14c", header=FALSE, skip=11, sep=" ")
cc.marine <- read.csv( "marine13.14c", header=FALSE, skip=11)
cc.south <- read.csv( "shcal13.14c", header=FALSE, skip=11)

### Write them in the desired format:

write.table( cc.terr[nrow(cc.terr):1,1:3], file="3Col_intcal13.14C", row.names=FALSE, col.names=FALSE)
write.table( cc.marine[nrow(cc.marine):1,1:3], file="3Col_marine13.14C", row.names=FALSE, col.names=FALSE)
write.table( cc.south[nrow(cc.south):1,1:3], file="3Col_shcal13.14C", row.names=FALSE, col.names=FALSE)
