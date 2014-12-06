# Do: check how plot.accrate.age does dark since it allows for dark>1!, postbomb dates really taken into account (if MinYr=-1e3)?

# for future versions: slump, F14C, enhanced age calculations around hiatuses, if hiatus plot acc.posts of the individual sections?, consider option to allow for asymmetric cal BP errors (e.g. read from files)?

# Done: changed .hpd to _ages.txt since many users get tricked by the extension, Bacon.hist gives 95% ranges, mid and wmean, BCAD, settings file, removed calc.every (gave problems with long cores), warn if any date errors 0 change to 1, optional depths.file for age calculations, language check cpp files, killed hist bug that assumed integers for res, changed to .csv files as default with option to use .dat files, suggest to adapt prior for acc.mean if initial estimate much different from default (20), allowing for different separator (e.g. French/Scandinavian use ';' not ',', also check use decimal points), renamed 'res' to hopefully more intuitive 'thick', d.R/d.STD for mixed dates where cc=0, enhanced flexibility MaxYr/MinYr (e.g. now depends on dates if cc=0), updated bacon's hist function (now bin/hist2), now reads depths from a file, added option to change axes order in age-depth graphs, added cleanup function to remove prior files etc., updated calibration curves to IntCal13, option in agedepth to only plot the age-model (so not the upper panels),



### load data, run bacon and analyse outputs
Bacon <- function(core="MSB2K", thick=5, prob=0.95, d.min=NA, d.max=NA, d.by=1, unit="cm", maxcalc=500, depths.file=FALSE, acc.shape=1.5, acc.mean=20, mem.strength=4, mem.mean=0.7, hiatus.depths=NA, hiatus.shape=1, hiatus.mean=1000, after=.0001, cc=1, cc1="IntCal13", cc2="Marine13", cc3="SHCal13", cc4="ConstCal", postbomb=0, d.R=0, d.STD=0, t.a=3, t.b=4, normal=FALSE, suggest=TRUE, reswarn=c(10,200), remember=TRUE, cleanup=TRUE, ask=TRUE, run=TRUE, defaults="default_settings.txt", sep=",", dec=".", runname="", slump=NA, BCAD=FALSE, ssize=2000, rounded=1, th0=c(), burnin=min(200, ssize), MinYr=c(), MaxYr=c(), find.round=4, bins=c(), cutoff=.001, plot.pdf=TRUE, rotate.axes=FALSE, rev.yr=FALSE, rev.d=FALSE, yr.min=c(), yr.max=c(), normalise.dists=TRUE, plot.title=core, title.location="topleft", d.lab="Depth", yr.lab=c(), d.res=200, yr.res=200, date.res=100, grey.res=100, width=15, dark=1, greyscale=function(x) grey(1-x), C14.col=rgb(0,0,1,.35), C14.border=rgb(0,0,1,.5), cal.col=rgb(0,.5,.5,.35), cal.border=rgb(0,.5,.5,.5), range.col=grey(0.5), range.lty="12", hiatus.col=grey(0.5), hiatus.lty="12", wm.col="red", wm.lty="12", med.col=NA, med.lty="12", mar=c(3,3,1,1), mgp=c(1.5,.7,.0), bty="l")
  {
    ### read in the data, adapt settings from defaults if needed
    dets <- .read.dets(core, sep=sep, dec=dec, cc=cc)

    ### give feedback about calibration curves used
    if(ncol(dets) > 4 && length(cc) > 0)
      {
        cc.csv <- unique(dets[,5])
        if(length(cc.csv) == 1)
          {
            if(cc.csv != cc)
              cat(" Using calibration curve specified within the .csv file,", cc[cc.csv], "\n")
          } else
            if(min(cc.csv) == 0)
              cat(" Using a mix of cal BP and calibrated C-14 dates\n") else
                cat(" Using several C-14 calibration curves\n")
      }


    if(suggest)
      {
        # adapt prior for mean accumulation rate?
        sugg <- sapply(c(1,2,5), function(x) x*10^(-1:2)) # some suggested 'round' values
        ballpacc <- lm(dets[,2]*1.1 ~ dets[,4])$coefficients[2] # very rough acc.rate estimates, uncalibrated dates
        ballpacc <- abs(sugg - ballpacc) # get absolute differences between given acc.mean and suggested ones
        sugg <- sugg[order(ballpacc)[1]] # suggest rounded acc.rate with lowest absolute difference
        if(sugg != acc.mean) # suggest this rounded acc.rate
          {
            ans <- readline(cat(" Ballpark estimates suggest changing the prior for acc.mean to ", sugg, " yr/", unit, ". OK? (y/n)  ", sep=""))
            if(tolower(substr(ans,1,1)) == "y")
              acc.mean <- sugg else
                cat(" No problem, using prior acc.mean=", acc.mean, " yr/", unit, "\n", sep="")
          }
      }
    info <- .Bacon.settings(core=core, dets=dets, thick=thick, remember=remember, d.min=d.min, d.max=d.max, d.by=d.by, depths.file=depths.file, slump=slump, acc.mean=acc.mean, acc.shape=acc.shape, mem.mean=mem.mean, mem.strength=mem.strength, hiatus.depths=hiatus.depths, hiatus.mean=hiatus.mean, hiatus.shape=hiatus.shape, BCAD=BCAD, cc=cc, postbomb=postbomb, cc1=cc1, cc2=cc2, cc3=cc3, cc4=cc4, unit=unit, normal=normal, t.a=t.a, t.b=t.b, d.R=d.R, d.STD=d.STD, prob=prob, defaults=defaults, runname=runname, ssize=ssize, bins=bins, dark=dark, rounded=rounded, MinYr=MinYr, MaxYr=MaxYr, cutoff=cutoff, yr.res=yr.res, after=after, find.round=find.round)
    info <<- info

    ### check for initial mistakes
    if(any(info$acc.shape==info$acc.mean))
      stop("\n Warning! acc.shape cannot be equal to acc.mean", call.=FALSE)
    if(info$t.b - info$t.a != 1)
      stop("\n Warning! t.b - t.a should always be 1, check the manual")

    ### calibrate dates
    if(info$cc > 0) # confirm we're using radiocarbon dates
      if(info$postbomb == 0 && ((ncol(info$dets)==4 && min(info$dets[,2]) < 0) ||
        ncol(info$dets)>4 && max(info$dets[,5]) > 0 && min(info$dets[info$dets[,5] > 0,2]) < 0))
          stop("\nWarning, you have negative C14 ages so should select a postbomb curve")
    info$calib <- .bacon.calib(dets, info, date.res)

    ### find some relevant values
    info$rng <- c()
    for(i in 1:length(info$calib$probs))
      {
        tmp <- info$calib$probs[[i]]
        info$rng <- range(info$rng, tmp[which(tmp[,2]>cutoff),1])
      }
    if(length(th0)==0) # provide two ball-park initial age estimates
      info$th0 <- round(rnorm(2, max(MinYr, dets[1,2]), dets[1,3]))
    info$th0[info$th0 < info$MinYr] <- info$MinYr # otherwise twalk will not start

    ### assign depths, possibly suggest alternative value for thick
    info$d <- seq(floor(info$d.min), ceiling(info$d.max), by=thick)
    info$K <- length(info$d)
    ans <- "n"
    if(suggest)
      if(length(reswarn)==2)
        if(info$K < min(reswarn))
          {
           sugg <- min(pretty(thick*(info$K/min(reswarn))))
            ans <- readline(cat(" Warning, the current value for thick, ", thick, ", will result in very few age-model sections (", info$K, ", not very flexible). Suggested maximum value for thick: ", sugg, " OK? (y/n) ", sep=""))
          } else
            if(info$K > max(reswarn))
              {
                sugg <- max(pretty(thick*(info$K/max(reswarn))))
                ans <- readline(cat(" Warning, the current value for thick, ", thick, ", will result in very many age-model sections (", info$K, ", possibly hard to run). Suggested minimum value for thick: ", sugg, " OK? (y/n) ", sep=""))
              }
    if(tolower(substr(ans,1,1)) == "y")
      {
        cat(" OK, setting thick to ", sugg, "\n")
        thick <- sugg
        info$d <- seq(floor(info$d.min), ceiling(info$d.max), by=thick)
        info$K <- length(info$d)
      }

    ### produce files
    if(.Platform$OS == "windows")
      info$prefix <- paste("Cores\\", core, "\\", core, runname, "_", info$K, sep="") else
        info$prefix <- paste("Cores/", core, "/", core, runname, "_", info$K, sep="")
    info$bacon.file <- paste(info$prefix, ".bacon", sep="")
    if(!file.exists(outfile <- paste(info$prefix, ".out", sep="")))
      file.create(outfile)

    ### store values (again) for future manipulations
    info <<- info

    prepare <- function()
      {
        ### plot initial data and priors
        layout(matrix(if(is.na(info$hiatus.depths)[1]) c(1,2,3,3) else c(1,2,3,4,4,4),
          nrow=2, byrow=TRUE), heights=c(.3,.7))
        par(mar=mar, mgp=mgp, bty=bty)
        PlotAccPrior(info$acc.shape, info$acc.mean)
        PlotMemPrior(info$mem.strength, info$mem.mean, thick)
        if(!is.na(info$hiatus.depths)[1])
          PlotHiatusPrior(info$hiatus.shape, info$hiatus.mean, info$hiatus.depths)
        calib.plot(info, date.res=date.res, rotate.axes=rotate.axes, width=width, cutoff=cutoff, rev.d=rev.d, rev.yr=rev.yr, normalise.dists=normalise.dists, C14.col=C14.col, C14.border=C14.border, cal.col=cal.col, cal.border=cal.border)
        legend(title.location, core, bty="n", cex=1.5)
      }

    cook <- function()
      {
        txt <- paste("bin/bacon ", info$prefix, ".bacon ", outfile, " ", ssize, sep="")
        if(.Platform$OS == "windows")
          suppressWarnings(shell(txt, translate=TRUE)) else
            system(txt)
        scissors(burnin, info)
        serve()
        if(plot.pdf)
          dev.copy2pdf(file=paste(info$prefix, ".pdf", sep=""))
      }

    serve <- function(plot.pdf=FALSE)
      {
        if(length(bins) == 0) bins <- 100
        if(length(yr.lab) == 0) yr.lab <- ifelse(info$BCAD, "BC/AD", "cal yr BP")
        par(mar=mar, mgp=mgp, bty=bty)
        agedepth(info, bins=bins, d.res=d.res, yr.res=yr.res, rounded=rounded, rotate.axes=rotate.axes, width=width, normalise.dists=normalise.dists, greyscale=greyscale, maxcalc=maxcalc, C14.col=C14.col, C14.border=C14.border, cal.col=cal.col, cal.border=cal.border, plot.range=plot.range, range.col=range.col, wm.col=wm.col, med.col=med.col, range.lty=range.lty, wm.lty=wm.lty, med.lty=med.lty, hiatus.col=hiatus.col, hiatus.lty=hiatus.lty, yr.lab=yr.lab, d.lab=d.lab, yr.min=yr.min, yr.max=yr.max, rev.d=rev.d, rev.yr=rev.yr, plot.title=plot.title, grey.res=grey.res, date.res=date.res, plot.pdf=FALSE, cleanup=cleanup)
      }

    ### run bacon if initial graphs seem OK; run automatically, not at all, or only plot the age-model
    .write.Bacon.file(info)

    if(!run) serve() else
      if(!ask) cook() else
        {
          prepare()
          ans <- readline(cat("  Run", core, "with", info$K, "sections? (y/n) "))
          if(tolower(substr(ans,1,1))=="y")
            cook() else cat("  OK. Please adapt settings.\n\n")
        }
    closeAllConnections()
  }



# read the dets file, converting old formats to new ones if so required
.read.dets <- function(core, set=info, sep=",", dec=".", cc=1)
  {
    # if a .csv file exists, read it (checking that more recent than the dat file). Otherwise, read the .dat file, check the columns, report back if >4 (>5?) columns, and convert to .csv (report this also)
    if(.Platform$OS == "windows")
      {
        csv.file <- paste("Cores\\", core, "\\", core, ".csv", sep="")
        dat.file <- paste("Cores\\", core, "\\", core, ".dat", sep="")
      } else
      {
        csv.file <- paste("Cores/", core, "/", core, ".csv", sep="")
        dat.file <- paste("Cores/", core, "/", core, ".dat", sep="")
      }

    dR.names <- c("r", "d", "d.r", "dr", "deltar", "r.mn", "rm", "rmn", "res.mean", "res.mn")
    dSTD.names <- c("r", "d", "d.std", "std", "std.1", "dstd", "r.std", "rstd", "res.sd")
    ta.names <- c("t", "t.a", "ta", "sta")
    tb.names <- c("t", "t.b", "tb", "stb")
    cc.names <- c("c", "cc")
    suggested.names <- c("labID", "age", "error", "depth", "cc", "dR", "dSTD", "ta", "tb")
    changed <- 0

    if(file.exists(csv.file))
      {
        dets <- read.table(csv.file, header=TRUE, sep=sep)
        if(file.exists(dat.file)) # deal with old .dat files
          if(file.info(csv.file)$mtime < file.info(dat.file)$mtime)
            cat("Warning, the .dat file is newer than the .csv file! I will read the .csv file. From now on please modify ", csv.file, ", not ", dat.file, " \n", sep="") else
              cat("Reading", csv.file, "\n")
      } else # so we need to read in the .dat file and convert it to a .csv file if possible
        {
          cat("No .csv file found, reading", dat.file, "and converting it to .csv\n")
          dets <- read.table(dat.file, header=TRUE)
          changed <- 1
        }
    name <- tolower(names(dets))

    # check if 'classic' dets file, which has a different column order from the current default
    if(ncol(dets) > 4)
      if(ncol(dets) == 5) # then probably a 'new' dets file
        {
          if((name[5] %in% cc.names) && min(dets[,5]) >= 0 && max(dets[,5]) <= 4) {} else# extra check for correct values
            stop("Error! Unexpected name or values in fifth column (cc, should be between 0 and 4). Please check the manual for guidelines in producing a correct .csv file.\n")
        } else
          if(ncol(dets) == 6) # probably an 'old' file: dR, dSTD
            {
              if(name[5] %in% dR.names && name[6] %in% dSTD.names)
                {
                  dets <- cbind(dets[,1:4], rep(cc, nrow(dets)), dets[,5:6]) # some shuffling
                  cat(" Assumed order of columns in dets file: lab ID, Age, error, depth, dR, dSTD. \nAdding calibration curve column (fifth column, before dR and dSTD) and saving as", csv.file, "\n")
                  changed <- 1
                }
            } else
              if(ncol(dets) == 7) # probably a 'new' file: cc, dR, dSTD
                {
                  if(name[5] %in% cc.names && min(dets[,5]) >= 0 && max(dets[,5]) <= 4 &&
                    name[6] %in% dR.names && name[7] %in% dSTD.names) {} else
                      stop("Error! Unexpected column names, order or values in dets file. \nPlease check the manual for correct dets file formats.\n")
                } else
                  if(ncol(dets) == 8) # probably an 'old' file: dR, dSTD, ta, tb
                    {
                      if(name[5] %in% dR.names && name[6] %in% dSTD.names)
                        if(name[7] %in% ta.names && name[8] %in% tb.names)
                          if(range(dets[,8] - dets[,7]) == c(1,1)) # check that these set expected student-t values
                            {
                              dets <- cbind(dets[,1:4], rep(cc, nrow(dets)), dets[,5:6]) # some shuffling
                              cat(" Assumed order of columns in dets file: lab ID, Age, error, depth, dR, dSTD. \nAdding calibration curve column (fifth column, before dR and dSTD) and saving as", csv.file, "\n")
                              changed <- 1
                            } else
                              stop("Error! Unexpected column names, order or values in dets file. \nPlease check the manual for how to produce a correct .csv file")
                    } else
                      if(ncol(dets) == 9) # most complex case, many checks needed
                        {
                          if(name[9] %in% cc.names && # we're almost sure that this is a 'classic' dets file
                            min(dets[,9]) >= 0 && max(dets[,9]) <= 4 && # check that this sets calibration curves
                              range(dets[,8] - dets[,7]) == c(1,1) && # check that these set expected student-t values
                                name[5] %in% dR.names && name[6] %in% dSTD.names && # column names as expected?
                                  name[7] %in% ta.names && name[8] %in% tb.names) # column names as expected?
                                    {
                                      dets <- dets[,c(1:4,9,5:8)] # shuffle colums around
                                      cat(" Assumed order of columns in dets file: lab ID, Age, error, depth, dR, dSTD, t.a, t.b, cc. \nAdapting column order and saving as", csv.file, "\n")
                                      changed <- 1
                                    } else
                                    if(name[5] %in% cc.names && # oh, probably a 'new' file from more recent Bacon
                                      min(dets[,5]) >= 0 && max(dets[,5]) <= 4 && # check that this sets cal.curves
                                        range(dets[,9] - dets[,8]) == c(1,1) && # columns 8-9 set student-t correctly
                                          name[8] %in% ta.names && name[9] %in% tb.names && # and are correctly named
                                            name[6] %in% dR.names && name[7] %in% dSTD.names) # all lights are green
                                              {} else
                                                stop("Error! Unexpected column names, order or values in dets file. \nPlease check the manual for how to produce a correct .csv file")
                        } else
                          stop("Error! Unexpected column names, order or values in dets file. \nPlease check the manual for how to produce a correct dets file.\n")

    # more sanity checks
    if(!is.numeric(dets[,2]) || !is.numeric(dets[,3]) || !is.numeric(dets[,4]))
      stop("Error, unexpected values in dets file, I expected numbers. Check the manual.\n", call.=FALSE)
    if(min(dets[,3]) <= 0)
      {
        cat("Warning, zero year errors don't exist in Bacon's world. I will increase them to 1yr.\n")
        dets[dets[,3] <= 0,3] <- 1
        changed <- 1
      }
    if(min(diff(dets[,4]) < 0))
      {
        cat("\nWarning, the depths are not in ascending order, I will correct this")
        dets <- dets[order(set$dets[,4]),]
        changed <- 1
      }

    # if current dets differ from original .csv file, rewrite it
    if(changed > 0)
      write.table(dets, csv.file, sep=paste(sep, "\t", sep=""), dec=dec, row.names=FALSE, col.names=suggested.names[1:ncol(dets)], quote=FALSE)

    dets
  }



# read in default values, values from previous run, any specified values, and report the desired one
.Bacon.settings <- function(core, dets, thick, remember=TRUE, d.min, d.max, d.by, depths.file, slump, acc.mean, acc.shape, mem.mean, mem.strength, hiatus.depths, hiatus.mean, hiatus.shape, BCAD, cc, postbomb, cc1, cc2, cc3, cc4, unit, normal, t.a, t.b, d.R, d.STD, prob, defaults, runname, ssize, bins, dark, rounded, MinYr, MaxYr, cutoff, yr.res, after, find.round)
  {
    vals <- list(d.min, d.max, d.by, depths.file, slump, acc.mean, acc.shape, mem.mean, mem.strength, hiatus.depths, hiatus.mean, hiatus.shape, BCAD, cc, postbomb, cc1, cc2, cc3, cc4, unit, normal, t.a, t.b, d.R, d.STD, prob)
    valnames <- c("d.min", "d.max", "d.by", "depths.file", "slump", "acc.mean", "acc.shape", "mem.mean", "mem.strength", "hiatus.depths", "hiatus.mean", "hiatus.shape", "BCAD", "cc", "postbomb", "cc1", "cc2", "cc3", "cc4", "unit", "normal", "t.a", "t.b", "d.R", "d.STD", "prob")
    extr <- function(i, def=deffile, pre=prevfile, exists.pre=prevf, rem=remember, sep=" ", isnum=TRUE)
      {
        if(any(is.na(vals[[i]])))
          {
            ext.def <- strsplit(def[i], sep)[[1]]
            ext.def <- ext.def[-length(ext.def)] # remove description
            if(exists.pre)
              {
                ext.pre <- strsplit(pre[i], sep)[[1]]
                ext.pre <- ext.pre[-length(ext.pre)] # remove description
                if(def[i] == pre[i]) # values for dev and pre similar, no worries
                  ext <- ext.pre else
                if(rem)
                  {
                    if(i==13) ifelse(ext.pre, "using BC/AD", "using cal BP") else
                      if(i>2) cat(" using previous run's value for ", valnames[i], ", ", ext.pre, "\n", sep="")
                    ext <- ext.pre
                  } else
                    {
                      if(i==13) ifelse(ext.def, "using BC/AD", "using cal BP") else
                        if(i>2) cat(" using default value for ", valnames[i], ", ", ext.def, "\n", sep="")
                      ext <- ext.def
                    }
              } else ext <- ext.def

            if(any(ext=="NA") || any(is.na(ext))) NA else
              if(isnum) as.numeric(ext) else noquote(ext)
          } else
             if(isnum) as.numeric(vals[[i]]) else vals[[i]]
      }

    # read in default values and those of previous run if available
    deffile <- readLines(defaults, n=-1)
    if(.Platform$OS== "windows")
      prevfile <- paste("Cores\\", core, "\\", core, "_settings.txt", sep="") else
        prevfile <- paste("Cores/", core, "/", core, "_settings.txt", sep="")
    prevf <- FALSE
    if(file.exists(prevfile))
      {
        prevfile <- readLines(prevfile, n=-1)
        if(length(prevfile) > 0) prevf <- TRUE
      }

    d.min <- extr(1); d.max <- extr(2); d.by <- extr(3); depths.file <- extr(4)
    slump <- extr(5); acc.mean <- extr(6);
    if(length(acc.shape) == 1) acc.shape <- extr(7)
    mem.mean <- extr(8)
    mem.strength <- extr(9)
    hiatus.depths <- if(is.na(hiatus.depths)[1]) NA else extr(10)
    hiatus.mean <- extr(11); hiatus.shape <- extr(12)
    BCAD <- extr(13); cc <- extr(14); postbomb <- extr(15); cc1 <- extr(16, isnum=FALSE)
    cc2 <- extr(17, isnum=FALSE); cc3 <- extr(18, isnum=FALSE); cc4 <- extr(19, isnum=FALSE)
    unit <- extr(20, isnum=FALSE); normal <- extr(21); t.a <- extr(22); t.b <- extr(23)
    d.R <- extr(24); d.STD <- extr(25); prob <- extr(26)

    if(is.na(d.min) || d.min=="NA") d.min <- min(dets[,4])
    if(is.na(d.max) || d.max=="NA") d.max <- max(dets[,4])
    if(length(acc.shape) < length(acc.mean))
      acc.shape <- rep(acc.shape, length(acc.mean)) else
        if(length(acc.shape) > length(acc.mean))
          acc.mean <- rep(acc.mean, length(acc.shape))
     if(length(mem.strength) < length(mem.mean))
       mem.strength <- rep(mem.strength, length(mem.mean)) else
        if(length(mem.strength) > length(mem.mean))
          mem.mean <- rep(mem.mean, length(mem.strength))


    ### produce/update settings file, and return the values
    if(.Platform$OS == "windows")
      prevfile <- file(paste("Cores\\", core, "\\", core, "_settings.txt", sep=""), "w") else
        prevfile <- file(paste("Cores/", core, "/", core, "_settings.txt", sep=""), "w")
    scat <- function(m,n="") cat(m,n, sep="", file=prevfile)
    cat(d.min, " #d.min\n", d.max, " #d.max\n", d.by, " #d.by\n",
      depths.file, " #depths.file\n", slump, " #slump\n", sep="", file=prevfile)
    for(i in acc.mean) scat(i, " "); scat("#acc.mean\n")
    for(i in acc.shape) scat(i, " "); scat("#acc.shape\n", "")
    for(i in mem.mean) scat(i, " "); scat("#mem.mean\n", "")
    for(i in mem.strength) scat(i, " "); scat("#mem.strength\n", "")
    for(i in hiatus.depths) scat(i, " "); scat("#hiatus.depths\n", "")
    for(i in hiatus.mean) scat(i, " "); scat("#hiatus.mean\n", "")
    for(i in hiatus.shape) scat(i, " "); scat("#hiatus.shape\n", "")
    cat(BCAD, " #BCAD\n", cc, " #cc\n", postbomb, " #postbomb\n",
      cc1, " #cc1\n", cc2, " #cc2\n", cc3, " #cc3\n", cc4, " #cc4\n",
      unit, " #unit\n", normal, " #normal\n", t.a, " #t.a\n", t.b, " #t.b\n",
      d.R, " #d.R\n", d.STD, " #d.STD\n", prob, " #prob\n", sep="", file=prevfile)
    close(prevfile)

    if(length(MinYr) == 0)
      MinYr <- min(-1e3, round(dets[,2] - (5*dets[,3])))
    if(length(MaxYr) == 0)
      MaxYr <- max(1e6, round(dets[,2] + (5*dets[,3])))

    list(core=core, thick=thick, dets=dets, d.min=d.min, d.max=d.max,
      d.by=d.by, depths.file=depths.file, slump=slump,
      acc.mean=acc.mean, acc.shape=acc.shape, mem.mean=mem.mean,
      mem.strength=mem.strength, hiatus.depths=hiatus.depths, hiatus.mean=hiatus.mean,
      hiatus.shape=hiatus.shape, BCAD=BCAD, cc=cc, postbomb=postbomb,
      cc1=cc1, cc2=cc2, cc3=cc3, cc4=cc4, unit=noquote(unit), normal=normal,
      t.a=t.a, t.b=t.b, d.R=d.R, d.STD=d.STD, prob=prob, date=date(),
      runname=runname, ssize=ssize, bins=bins, dark=dark, rounded=rounded,
      MinYr=MinYr, MaxYr=MaxYr, cutoff=cutoff, yr.res=yr.res, after=after, find.round=find.round)
  }



.write.Bacon.file <- function(set=info)
  {
    if(set$d.min < min(set$dets[,4]))
      {
        extrap <- c(NA, min(set$dets[,2]), max(1e4, 100*set$dets[,3]), set$d.min, 0)
        dets <- rbind(extrap, set$dets, deparse.level=0)
      }
    if(set$d.max > max(set$dets[,4]))
      {
        extrap <- c(NA, max(set$dets[,2]), max(1e4, 100*set$dets[,3]), set$d.max, 0)
        dets <- rbind(set$dets, extrap, deparse.level=1)
      }

    fl <- file(set$bacon.file, "w")
    cat("## Ran on", set$date, "\n\n", file=fl)
    cat("Cal 0 : ConstCal;\nCal 1 : ",
      if(set$cc1=="IntCal13" || set$cc1=="\"IntCal13\"") "IntCal13" else noquote(set$cc1),
      ", ", set$postbomb, ";\nCal 2 : ",
      if(set$cc2=="Marine13" || set$cc2=="\"Marine13\"") "Marine13" else noquote(set$cc2),
      ";\nCal 3 : ",
      if(set$cc3=="SHCal13" || set$cc3=="\"SHCal13\"") "SHCal13" else noquote(set$cc3), ", ", set$postbomb, ";",
      if(set$cc4=="ConstCal" || set$cc4=="\"ConstCal\"") set$cc4 <- c() else
        if(.Platform$OS == "windows")
          paste("\nCal 4 : GenericCal, Curves\\", set$cc4, ";", sep="") else
          paste("\nCal 4 : GenericCal, Curves/", set$cc4, ";", sep=""),
      sep="", file=fl)
    cat("\n\n##   id.   yr    std   depth  d.R  d.STD     t.a   t.b   cc", file=fl)

    if(ncol(set$dets) == 4) # then we need to provide some constants once only
      {
        cat("\nDet 0 : ", as.character(set$dets[1,1]), " ,  ", set$dets[1,2], ",  ",
          set$dets[1,3], ",  ", set$dets[1,4], ",  ", set$d.R, ",  ", set$d.STD,
          ",  ", set$t.a, ",  ", set$t.b, ",  ", set$cc, ";", sep="", file=fl)
        if(nrow(set$dets)>1)
          for(i in 2:nrow(set$dets))
            cat("\nDet ", i-1, " : ",  as.character(set$dets[i,1]),
            " , ", set$dets[i,2], ", ", set$dets[i,3], ", ", set$dets[i,4],
            ";", sep="", file=fl)
      } else # use additional columns provided within the .dat file
      {
        cc <- set$dets[,5]
        d.R <- rep(set$d.R, nrow(set$dets))
        d.R[cc==0] <- 0 # only apply dR to C14 dates
        d.STD <- rep(set$d.STD, nrow(set$dets))
        d.STD[cc==0] <- 0 # only apply dR to C14 dates
        t.a <- rep(set$t.a, nrow(set$dets))
        t.b <- rep(set$t.b, nrow(set$dets))

        if(ncol(set$dets) >= 7)
          {
            d.R <- set$dets[,6]
            d.STD <- set$dets[,7]
          }
        if(ncol(set$dets) >= 9)
          {
            t.a <- set$dets[,8]
            t.b <- set$dets[,9]
          }

        for(i in 1:nrow(set$dets))
          cat("\nDet ", i-1, " : ",  as.character(set$dets[i,1]), " , ",
            set$dets[i,2], ", ", set$dets[i,3], ", ", set$dets[i,4],  ",  ",
            d.R[i], ",  ", d.STD[i], ",  ", t.a[i], ",  ", t.b[i], ",  ",
            cc[i], ";", sep="", file=fl)
       }

    if(!is.na(set$hiatus.depths)[1]) ### hiatus(es) inferred. Prior values should be provided starting from top section
      {
        cat("\n  Hiatus set at depth(s)", set$hiatus.depths, "\n")
        if(length(set$acc.shape)==1)
          set$acc.shape <- rep(set$acc.shape, length(set$hiatus.depths)+1)
        if(length(set$acc.mean)==1)
          set$acc.mean <- rep(set$acc.mean, length(set$hiatus.depths)+1)
        if(length(set$hiatus.mean)==1)
          set$hiatus.mean <- rep(set$hiatus.mean, length(set$hiatus.depths))
        if(length(set$hiatus.shape)==1)
          set$hiatus.shape <- rep(set$hiatus.shape, length(set$hiatus.depths))
        info <<- set
        cat("\n\n### Depths and priors for fixed hiatuses, in descending order",
          "\n##### cm  alpha beta      ha     hb", file=fl)
        for(i in length(set$hiatus.depths):1)
          cat("\nHiatus ", i-1, ":  ", set$hiatus.depth[i], ",  ", set$acc.shape[i+1],
            ",  ", set$acc.shape[i+1]/set$acc.mean[i+1], ",  ", set$hiatus.shape[i],
            ",  ", set$hiatus.shape[i]/set$hiatus.mean[i], ";", sep="", file=fl)
      }

   ### final parameters
    wrapup <- paste("\n\n##\t\t K   MinYr   MaxYr   th0   th0p   w.a   w.b   alpha  beta  dmin  dmax",
      "\nBacon 0: ", ifelse(set$normal, "FixNor", "FixT"), ", ", set$K,
      ",  ", set$MinYr, ",  ", set$MaxYr, ",  ", set$th0[1], ",  ", set$th0[2],
      ",  ", set$mem.strength*set$mem.mean, ",  ", set$mem.strength*(1-set$mem.mean),
      ",  ", set$acc.shape[1], ",  ", set$acc.shape[1]/set$acc.mean[1], ", ", set$d.min,
      ", ", set$d.max, ";\n", sep="")
    cat(wrapup, file=fl)
    close(fl)
  }



# if cores behave badly, you can try cleaning up previous runs and settings with the following function:
Bacon.cleanup <- function(set=info)
  {
    files <- c(paste(set$prefix, ".bacon", sep=""), paste(set$prefix, ".out", sep=""),
      paste(set$prefix, ".pdf", sep=""), paste(set$prefix, "_ages.txt", sep=""),
      paste("Cores/", set$core, "/", set$core, "_settings.txt", sep=""))
    for(i in files)
      if(file.exists(i))
        tmp <- file.remove(i)
    if(exists("tmp")) rm(tmp)
    cat("Previous Bacon runs of core", set$core, "with thick=", info$thick, "deleted. Now try running the core again\n")
  }



agedepth <- function(set=info, d.lab="Depth", yr.lab=ifelse(set$BCAD, "BC/AD", "cal yr BP"), d.min=set$d.min, d.max=set$d.max, d.by=set$d.by, yr.min=c(), yr.max=c(), bins=max(50, if(exists("set$output")) 2*ceiling(sqrt(nrow(set$output)))), dark=set$dark, prob=set$prob, rounded=0, d.res=200, yr.res=200, date.res=100, grey.res=100, rotate.axes=FALSE, rev.yr=FALSE, rev.d=FALSE, maxcalc=500, width=15, cutoff=.001, plot.range=TRUE, range.col=grey(0.5), range.lty="12", wm.col="red", wm.lty="12", med.col=NA, med.lty="12", C14.col=rgb(0,0,1,.35), C14.border=rgb(0,0,1,.5), cal.col=rgb(0,.5,.5,.35), cal.border=rgb(0,.5,.5,.5), hiatus.col=grey(0.5), hiatus.lty="12", greyscale=function(x) grey(1-x), normalise.dists=TRUE, cc=set$cc, plot.title=set$core, title.location="topleft", after=set$after, bty="l", mar=c(3,3,1,1), mgp=c(1.5,.7,.0), plot.pdf=FALSE, model.only=FALSE, cleanup=TRUE)
  {
    ### Load the output
    lngth <- length(readLines(paste(set$prefix, ".out", sep="")))
    if(!exists("set$output") || nrow(set$output) != lngth)
      set <- .Bacon.AnaOut(paste(set$prefix, ".out", sep=""), set)

    if(model.only)
      layout(1) else
        layout(matrix(if(is.na(set$hiatus.depths)[1]) c(1:3, rep(4,3)) else c(1:4, rep(5,4)), nrow=2, byrow=TRUE), heights=c(.3,.7))
    par(bty=bty, mar=mar, mgp=mgp, yaxs="i")
    if(!model.only)
      {
        PlotLogPost(set, 0, set$Tr) # convergence information
        PlotAccPost(set)
        PlotMemPost(set, set$core, set$K, "", set$mem.strength, set$mem.mean, ds=1, thick=set$thick)
        if(!is.na(set$hiatus.depths[1]))
          PlotHiatusPost(set, set$hiatus.shape, set$hiatus.mean)
      }

    ### first calculate calendar axis limits
    ranges <- Bacon.hist(range(set$d), set, Plot=FALSE, prob=prob, yr.res=yr.res)
    if(length(yr.min)==0) yr.min <- min(ranges)
    if(length(yr.max)==0) yr.max <- max(ranges)
    yr.lim <- c(yr.min, yr.max)
    if(rev.yr) yr.lim <- rev(yr.lim)
    if(set$BCAD) yr.lim <- 1950-yr.lim
    dlim=c(d.max, d.min)
    if(rev.d) dlim <- dlim[2:1]

    par(yaxs="r")
    if(rotate.axes)
      plot(0, type="n", ylim=dlim, xlim=yr.lim, ylab=d.lab, xlab=yr.lab, bty="n") else
        plot(0, type="n", xlim=dlim[2:1], ylim=yr.lim, xlab=d.lab, ylab=yr.lab, bty="n")

    .depth.ghost(set, rotate.axes=rotate.axes, d.res=d.res, yr.res=yr.res, grey.res=grey.res, dark=dark, greyscale=greyscale, d.min=d.min, d.max=d.max, cleanup=cleanup)
    calib.plot(set, rotate.axes=rotate.axes, width=width, date.res=date.res, cutoff=cutoff, C14.col=C14.col, C14.border=C14.border, cal.col=cal.col, cal.border=cal.border, new.plot=FALSE, normalise.dists=normalise.dists)
    legend(title.location, plot.title, bty="n", cex=1.5)
    box(bty=bty)

    # now calculate and plot the ranges and 'best' estimates for each required depth
    if(!(set$depths.file))
      d <- seq(d.min, d.max, by=d.by) else
        {
          if(.Platform$OS == "windows")
            dfile <- paste("Cores\\", set$core, "\\", set$core, "_depths.txt", sep="") else
              dfile <- paste("Cores/", set$core, "/", set$core, "_depths.txt", sep="")
          if(!file.exists(dfile))
            stop(" Warning! I cannot find the file ", paste("Cores/", set$core, "/", set$core, "_depths.txt", sep=""), "\n") else
             d <- as.numeric(read.table(dfile, header=FALSE)[,1])
        }

    if(length(d) > maxcalc)
      cat(" Warning, this will take quite some time to calculate. I suggest increasing d.by to, e.g.", 10*set$d.by, "\n")

    for(i in set$hiatus.depths)
      if(i %in% d) d <- sort(c(i-after, d)) else d <- sort(c(i-after, i, d)) ### tmp
    ranges <- Bacon.hist(d, set, prob=prob, yr.res=yr.res, cleanup=cleanup)
    if(set$BCAD) ranges <- 1950-ranges

    th <- rbind(1, nrow(ranges))
    if(!is.na(set$hiatus.depths[1]))
      {
        hi.d <- c()
        for(i in set$hiatus.depths) hi.d <- c(hi.d, max(which(d<=i)))
        th <- array(sort(c(1, nrow(ranges), hi.d-1, hi.d)), dim=c(2,length(hi.d)+1))
      }
    for(i in 1:ncol(th))
      {
        h <- th[1,i] : th[2,i]
        if(rotate.axes)
          {
            lines(ranges[h,1], d[h], col=range.col, lty=range.lty)
            lines(ranges[h,2], d[h], col=range.col, lty=range.lty)
            lines(ranges[h,3], d[h], col=med.col, lty=med.lty) # median
            lines(ranges[h,4], d[h], col=wm.col, lty=wm.lty) # weighted mean
          } else
          {
            lines(d[h], ranges[h,1], col=range.col, lty=range.lty)
            lines(d[h], ranges[h,2], col=range.col, lty=range.lty)
            lines(d[h], ranges[h,3], col=med.col, lty=med.lty) # median
            lines(d[h], ranges[h,4], col=wm.col, lty=wm.lty) # weighted mean
          }
        }
    abline(v=set$hiatus.depths, col=hiatus.col, lty=hiatus.lty)
    set$ranges <- cbind(d, round(ranges, rounded))
    colnames(set$ranges) <- c("depth", "min", "max", "median", "wmean")
    info <<- set

    if(plot.pdf)
      dev.copy2pdf(file=paste(set$prefix, ".pdf", sep=""))

    write.table(set$ranges, paste(set$prefix, "_ages.txt", sep=""), quote=FALSE, row.names=FALSE, sep="\t")
    rng <- abs(round(set$ranges[,3]-set$ranges[,2], rounded))
    min.rng <- d[which(rng==min(rng))]
    max.rng <- d[which(rng==max(rng))]
    if(length(min.rng)==1) min.rng <- paste(" yr at", min.rng, noquote(set$unit)) else
      min.rng <- paste(" yr between", min(min.rng), "and", max(min.rng), noquote(set$unit))
    if(length(max.rng)==1) max.rng <- paste(" yr at", max.rng, set$unit) else
      max.rng <- paste(" yr between", min(max.rng), "and", max(max.rng), noquote(set$unit))
    cat("Mean ", 100*prob, "% confidence ranges ", round(mean(rng), rounded), " yr, min. ",
      min(rng), min.rng, ", max. ", max(rng), max.rng, "\n\n", sep="")
  }



### for proxy.ghost
.DepthsOfScore <- function(value, dat)
 {
   d <- c()
   for(i in 1:(nrow(dat)-1))
    {
      valueRange <- dat[i:(i+1),2]
      if(min(valueRange) <= value && max(valueRange) >= value)
        {
          slope <- (dat[i,2] - dat[i+1,2]) / (dat[i,1] - dat[i+1,1])
          intercept <- dat[i,2] - (slope*dat[i,1])
          if(slope==0) d[i-1] <- dat[i,1]
          d <- sort(c(d, (value - intercept) / slope ))
        }
      }
    unique(d)
  }



Bacon.Age.d <- function(d, set=info, its=set$output, BCAD=set$BCAD)
 {
   elbows <- cbind(its[,1])
   accs <- its[,2:(ncol(its)-1)]
   for(i in 2:ncol(accs))
     elbows <- cbind(elbows, elbows[,ncol(elbows)] + (set$thick * accs[,i-1]))

   if(d %in% set$d)
     ages <- elbows[,which(set$d == d)] else
      {
        maxd <- max(which(set$d < d))
        ages <- elbows[,maxd] + ((d-set$d[maxd]) * accs[,maxd])
      }
   if(!is.na(set$hiatus.depths)[1])
     for(hi in set$hiatus.depths)
       {
         below <- min(which(set$d > hi), set$K-1)+1
         above <- max(which(set$d < hi))
         if(d > set$d[above] && d < set$d[below])
           {
             start.hiatus <- elbows[,below] - (its[,1+below] * (set$d[below] - hi))
             end.hiatus <- elbows[,above] + (its[,above] * (hi - set$d[above]))
             ok <- which(end.hiatus < start.hiatus)
             if(d < hi)
               ages[ok] <- elbows[ok,above] + (its[ok,above] * (d - set$d[above])) else
               ages[ok] <- elbows[ok,below] - (its[ok,1+below] * (set$d[below] - d))
           }
       }
   if(BCAD) ages <- 1950 - ages
   ages
 }



# calculate pre- and post ages of hiatus depths
### to plot greyscale/ghost graphs of age-depth model
.depth.ghost <- function(set=info, bins=max(50, if(exists("set$output")) 2*ceiling(sqrt(nrow(set$output)))), d.min=set$d.min, d.max=set$d.max, rotate.axes=FALSE, d.res=100, yr.res=200, grey.res=100, dark=set$dark, greyscale=function(x) grey(1-x), cleanup=TRUE)
  {
    d <- seq(d.min, d.max, length=d.res)
    Bacon.hist(d, set, bins, yr.res=yr.res, cleanup=cleanup)
    d.jumps <- diff(d)[1]

    peak <- 0
    for(i in 1:(length(d)))
      {
        yrs <- seq(hists[[i]]$th0, hists[[i]]$th1, length=hists[[i]]$n)
        hst <- approx(yrs, hists[[i]]$counts, seq(min(yrs), max(yrs), length=yr.res))
        if(length(hst$y>0) < 5) # for narrow distributions, go narrow
          hst <- approx(yrs, hists[[i]]$counts, seq(min(yrs), max(yrs), length=20))
        peak <- max(peak, max(hst$y))
      }

    for(i in 1:length(d))
      {
        yrs <- seq(hists[[i]]$th0, hists[[i]]$th1, length=hists[[i]]$n)
        hst <- approx(yrs, hists[[i]]$counts, seq(min(yrs), max(yrs), length=yr.res))
        if(length(hst$y>0) < 5) # for narrow distributions, go narrow
          hst <- approx(yrs, hists[[i]]$counts, seq(min(yrs), max(yrs), length=20))
        if(set$BCAD)
          {
            hst$x <- rev(1950-hst$x) # Christ...
            hst$y <- rev(hst$y)
          }
        hst$y <- hst$y/peak
        hst$y[hst$y>dark] <- max(hst$y)
        if(dark>1) stop(" Warning, the dark value should be <1")
        gr <- seq(0, dark, length=grey.res)
        if(rotate.axes)
          image(hst$x, c(d[i]-(d.jumps/2), d[i]+(d.jumps/2)), t(t(hst$y)), add=TRUE, col=greyscale(gr)) else
            image(c(d[i]-(d.jumps/2), d[i]+(d.jumps/2)), hst$x, t(hst$y), add=TRUE, col=greyscale(gr))
      }
  }



proxy.ghost <- function(proxy=1, proxy.lab=c(), proxy.res=200, yr.res=200, grey.res=100, set=info, bins=max(50, if(exists("set$output")) 2*ceiling(sqrt(nrow(set$output)))), dark=set$dark, rotate.axes=FALSE, rev.proxy=FALSE, rev.yr=FALSE, plot.wm=FALSE, wm.col="red", yr.lim=c(), proxy.lim=c(), sep=",", xaxs="i", draw.box="l", BCAD=set$BCAD, yr.lab=ifelse(BCAD, "BC/AD", "cal yr BP"), transpose=FALSE, cleanup=TRUE)
  {
    if(length(set$Tr)==0)
      stop("\nPlease first run agedepth()\n\n")
    if(.Platform$OS== "windows")
      proxies <- read.csv(paste("Cores\\", set$core, "\\", set$core, "_proxies.csv", sep=""), header=TRUE, sep=sep) else
        proxies <- read.csv(paste("Cores/", set$core, "/", set$core, "_proxies.csv", sep=""), header=TRUE, sep=sep)
    if(transpose) proxies <- t(proxies)
    if(length(proxy.lab)==0) proxy.lab <- names(proxies)[proxy+1]
    proxy <- cbind(as.numeric(proxies[,1]), as.numeric(proxies[,proxy+1]))
    proxy <- proxy[!is.na(proxy[,2]),]
    proxy <- proxy[which(proxy[,1] <= max(set$d)),]
    proxy <- proxy[which(proxy[,1] >= min(set$d)),]
    pr.wm.ages <- approx(set$ranges[,1], set$ranges[,5], proxies[,1])$y
    if(length(unique(proxy[,2]))==1)
      stop("\nThis proxy's values remain constant throughout the core, and cannot be proxy-ghosted!\n\n")
    proxyseq <- seq(min(proxy[,2]), max(proxy[,2]), length=proxy.res)
    out <- list(yrseq=c(), binned=c(), maxs=c())
    ds <- c()
    d.length <- array(1, dim=c(proxy.res, 2))

    for(i in 1:proxy.res)
      {
        tmp  <- .DepthsOfScore(proxyseq[i], proxy)
        ds <- c(ds, tmp)
        if(i > 1) d.length[i,1] <- d.length[(i-1),2]+1
        d.length[i,2] <- d.length[i,1]+length(tmp)-1
        if(length(tmp)==0) d.length[i,] <- d.length[i-1,]
      }
    cat("\nCalculating histograms... \n")

    Bacon.hist(ds, set, bins, Plot=FALSE, cleanup=cleanup)
    yr.min <- c()
    yr.max <- c()
    for(i in 1:length(hists))
      {
        yr.min <- min(yr.min, hists[[i]]$th0)
        yr.max <- max(yr.max, hists[[i]]$th1)
      }
    yr.seq <- seq(yr.min, yr.max, length=yr.res)

    all.counts <- array(0, dim=c(length(hists), length(yr.seq)))
    for(i in 1:length(hists))
      all.counts[i,] <- approx(seq(hists[[i]]$th0, hists[[i]]$th1, length=hists[[i]]$n), hists[[i]]$counts, yr.seq)$y
    all.counts[is.na(all.counts)] <- 0
    all.counts <- all.counts/max(all.counts)
    all.counts[all.counts > dark] <- dark
    max.counts <- array(0, dim=c(proxy.res, length(yr.seq)))
    for(i in 1:proxy.res)
      for(j in 1:length(yr.seq))
        max.counts[i,j] <- max(all.counts[d.length[i,1]:d.length[i,2],j])
    if(length(yr.lim)==0)
      if(xaxs=="r")
        yr.lim <- range(pretty(c(1.04*max(yr.seq), .96*min(yr.seq)))) else
          yr.lim <- range(yr.seq)[2:1]
    if(rev.yr) yr.lim <- yr.lim[2:1]
    if(BCAD)
      {
        yr.lim <- 1950-yr.lim
        max.counts <- max.counts[,ncol(max.counts):1]
        yr.seq <- 1950-rev(yr.seq)
      }
    if(length(proxy.lim)==0) proxy.lim <- range(proxyseq)
    if(rev.proxy) proxy.lim <- proxy.lim[2:1]
    if(rotate.axes)
      {
        image(proxyseq, yr.seq, max.counts, xlim=proxy.lim, ylim=yr.lim, col=grey(seq(1,0,length=grey.res)), ylab=yr.lab, xlab=proxy.lab, xaxs=xaxs)
        if(plot.wm) lines(proxy[,2], pr.wm.ages, col=wm.col)
      } else
      {
        image(yr.seq, proxyseq, t(max.counts), xlim=yr.lim, ylim=proxy.lim, col=grey(seq(1,0,length=grey.res)), xlab=yr.lab, ylab=proxy.lab, xaxs=xaxs)
        if(plot.wm) lines(pr.wm.ages, proxy[,2], col=wm.col)
      }
    box(bty=draw.box)
  }



### calculate age distributions of depth(s)
Bacon.hist <- function(d, set=info, bins=max(50, if(exists("set$output")) 2*ceiling(sqrt(nrow(set$output)))), tmpfile=tempfile(), depthfile=tempfile(), xlab=c(), xlim=c(), ylab="Frequency", ylim=c(), Plot=TRUE, yr.res=200, prob=set$prob, hist.col=grey(0.5), hist.border=grey(.2), range.col="blue", med.col="green", wmean.col="red", cleanup=TRUE)
  {
    write(d, depthfile, 1)
    outfile <- paste(set$prefix, ".out", sep="")
    txt <- paste("bin/hist2 ", outfile, set$Tr, set$d.min, set$thick, set$K, bins, tmpfile, length(d), depthfile)
    if(.Platform$OS == "windows")
      suppressWarnings(shell(txt, translate=TRUE)) else
        system(txt)
    source(tmpfile)
    if(cleanup) file.remove(tmpfile, depthfile)

    # here check for hiatuses and re-calculate any affected d. Should really be done in hist.c etc.
    if(!is.na(set$hiatus.depths)[1])
      {
        d.hists <- c()
        for(j in 1:length(hists))
          d.hists[j] <- hists[[j]]$d
        for(hi in set$hiatus.depths)
          for(i in d)
            {
              below <- min(which(set$d > hi), set$K-1)+1
              above <- max(which(set$d < hi))
              if(i < set$d[below] && i > set$d[above])
                {
                  this <- max(which(round(d.hists,set$find.round)==round(i,set$find.round))) # ugly
                  if(length(this[!is.na(this)]) > 0)
                    {
                      newdist <- hist(Bacon.Age.d(i, info), bins, plot=FALSE)
                      hists[[this]]$th0 <- round(min(newdist$mids))  # th0
                      hists[[this]]$th1 <- round(max(newdist$mids))  # th1
                      hists[[this]]$n <- length(newdist$mids)        # n
                      hists[[this]]$counts <- round(newdist$counts)
                      hists <<- hists
                    }
                }
            }
      }

    ranges.hst <- function(hst)
      {
        wm <- weighted.mean(hst[,1], hst[,2])
        hst <- cbind(hst[,1], cumsum(hst[,2])/sum(hst[,2]))
        qu <- approx(hst[,2], hst[,1], c((1-prob)/2, 1-((1-prob)/2), .5), rule=2)
        c(qu$y, wm)
      }
    rng <- array(NA, dim=c(length(d), 4))
    for(i in 1:length(d))
      {
        yrs <- seq(hists[[i]]$th0, hists[[i]]$th1, length=hists[[i]]$n)
        if(set$BCAD) yrs <- 1950 - yrs
        hst <- approx(yrs, hists[[i]]$counts, seq(min(yrs), max(yrs), length=yr.res))
        if(length(hst$y[hst$y>0]) < 2)
          hst <- approx(yrs, hists[[i]]$counts, seq(min(yrs), max(yrs), length=50)) # for very narrow ranges
        rng[i,] <- ranges.hst(cbind(hst$x, hst$y))
      }

    # now instead of hpd and MAP uses weighted mean and quantiles incl. median
    if(length(d)==1 && Plot==TRUE)
      {
        if(length(xlab) == 0) xlab <- ifelse(set$BCAD, "BC/AD", "cal yr BP")
        if(length(xlim) == 0) xlim <- range(hst$x)
        if(length(ylim) == 0) ylim <- c(0, max(hst$y))
        pol <- cbind(c(min(hst$x), hst$x, max(hst$x)), c(0, hst$y, 0))
        plot(0, type="n", xlim=xlim, ylim=ylim, xlab=xlab, ylab=ylab, yaxs="i")
        polygon(pol, col=hist.col, border=hist.border)
        segments(rng[1], 0, rng[2], 0, col=range.col, lwd=3)
        points(rng[3:4], c(0,0), col=c(wmean.col,med.col), pch=20)

        cat("  weighted mean (", wmean.col, "): ", round(rng[4],1), " ", xlab,
        ", median (", med.col, "): ",  round(rng[3],1), " ", xlab, "\n", sep="")
        cat(100*prob, "% range (", range.col, "): ", round(rng[1],1), " to ", round(rng[2],1), xlab, "\n", sep="")
      } else
    rng
  }


# for sake of simplicity we're removing the file Ana.R and the command source("Ana.R"):
# source("Ana.R")
# the only remaining required function from Ana.R is the following:
.Bacon.AnaOut <- function(fnam, set=info)
  {
    out <- read.table(fnam)
    n <- ncol(out)-1
    set$n <- n
    set$Tr <- nrow(out)
    set$Us <- out[,n+1]
    set$output <- out[,1:n]
    set
}



### Time series of the log of the posterior
PlotLogPost <- function(set, from=0, to=set$Tr)
  plot(from:(to-1), -set$Us[(from+1):to], type="l",
    ylab="Log of Objective", xlab="Iteration", main="")



### cut away first bunch of iterations if MCMC burnin still visible
### NB will adapt the original .out file!
scissors <- function(burnin, set=info)
  {
    output <- read.table(paste(set$prefix, ".out", sep=""))
    if(burnin>= nrow(output))
      stop("\nCannot remove that many iterations, there would be none left!\n\n", call.=FALSE)
    output <- output[burnin:nrow(output),]
    write.table(output, paste(set$prefix, ".out", sep=""), col.names=F, row.names=F)
    info$output <<- output # write to info, not to set
  }



### thin iterations by given proportion (if too much autocorrelation is visible in the MCMC series)
### NB will adapt the original .out file!
thinner <- function(ratio=.1, set=info)
  {
    output <- read.table(paste(set$prefix, ".out", sep=""))
    if(ratio >= 1)
      stop("\nCannot remove that many iterations, there would be none left!\n\n", call.=FALSE)
    ratio <- sample(nrow(output), ratio*nrow(output))
    output <- output[-ratio,]
    write.table(output, paste(set$prefix, ".out", sep=""), col.names=F, row.names=F)
    info$output <<- output # write to info, not to set
  }



### calibrate C14 dates and calculate distributions for any calendar dates
.bacon.calib <- function(dat, set=info, date.res=100, normal=set$normal, t.a=set$t.a, t.b=set$t.b, d.R=set$d.R, d.STD=set$d.STD)
  {
    # read in the curves
    if(set$cc1=="IntCal13" || set$cc1=="\"IntCal13\"")
      cc1 <- read.table("Curves/3Col_intcal13.14C") else
        cc1 <- read.csv(paste("Curves/", set$cc1, ".14C", sep=""), header=FALSE, skip=11)[,1:3]
    if(set$cc2=="Marine13" || set$cc2=="\"Marine13\"")
      cc2 <- read.table("Curves/3Col_marine13.14C") else
        cc2 <- read.csv(paste("Curves/", set$cc2, ".14C", sep=""), header=FALSE, skip=11)[,1:3]
    if(set$cc3=="SHCal13" || set$cc3=="\"SHCal13\"")
      cc3 <- read.table("Curves/3Col_shcal13.14C") else
        cc3 <- read.table(paste("Curves/", set$cc3, ".14C", sep=""))[,1:3]
    if(set$cc4=="ConstCal" || set$cc4=="\"ConstCal\"") cc4 <- NA else
      cc4 <- read.table(paste("Curves/", set$cc4, sep=""))[,1:3]

    if(set$postbomb != 0)
      {
        if(set$postbomb==1) bomb <- read.table("Curves/postbomb_NH1.14C")[,1:3] else
          if(set$postbomb==2) bomb <- read.table("Curves/postbomb_NH2.14C")[,1:3] else
            if(set$postbomb==3) bomb <- read.table("Curves/postbomb_NH3.14C")[,1:3] else
              if(set$postbomb==4) bomb <- read.table("Curves/postbomb_SH1-2.14C")[,1:3] else
                if(set$postbomb==5) bomb <- read.table("Curves/postbomb_SH3.14C")[,1:3] else
                  stop("Warning, cannot find postbomb curve #", set$postbomb, " (use values of 1 to 5 only)")
        bomb.x <- seq(max(bomb[,1]), min(bomb[,1]), by=-.1) # interpolate
        bomb.y <- approx(bomb[,1], bomb[,2], bomb.x)$y
        bomb.z <- approx(bomb[,1], bomb[,3], bomb.x)$y
        bomb <- cbind(bomb.x, bomb.y, bomb.z, deparse.level=0)
        if(set$postbomb < 4)
          cc1 <- rbind(bomb, cc1, deparse.level=0) else
            cc3 <- rbind(bomb, cc3, deparse.level=0)
      }

    ## use Gaussian or t (Christen and Perez Radiocarbon 2009) calibration
    if(round(set$t.b-set$t.a) !=1)
      stop("\n Warning! t.b - t.a should always be 1, check the manual")
    d.cal <- function(cc, rcmean, w2, t.a, t.b)
      {
        if(set$normal)
          cal <- cbind(cc[,1], dnorm(cc[,2], rcmean, sqrt(cc[,3]^2+w2))) else
          cal <- cbind(cc[,1], (t.b+ ((rcmean-cc[,2])^2) / (2*(cc[,3]^2 + w2))) ^ (-1*(t.a+0.5)))
        cal[,2] <- cal[,2]/sum(cal[,2])
        if(length(which(cal[,2]>set$cutoff)) > 5) # ensure that also very precise dates get a range of probabilities
          cal[which(cal[,2]>set$cutoff),] else
            {
              calx <- seq(min(cal[,1]), max(cal[,1]), length=50)
              caly <- approx(cal[,1], cal[,2], calx)$y
              cbind(calx, caly/sum(caly))
            }
      }

    # now calibrate all dates
    calib <- list(d=dat[,4])
    if(ncol(dat)==4) # only one type of dates (e.g., calBP, or all IntCal13 C14 dates)
      {
        if(set$cc==0)
          {
            d.R <- 0; d.STD <- 0 # only C14 dates should need correcting for age offsets
            x <- seq(min(dat[,2])-max(100,4*max(dat[,3])), max(dat[,2])+max(100,4*max(dat[,3])), length=date.res)
            ccurve <- cbind(x, x, rep(0,length(x))) # dummy 1:1 curve
          } else
            if(set$cc==1) ccurve <- cc1 else
              if(set$cc==2) ccurve <- cc2 else
                if(set$cc==3) ccurve <- cc3 else
                  ccurve <- cc4
        for(i in 1:nrow(dat))
          calib$probs[[i]] <- d.cal(ccurve, dat[i,2]-d.R, dat[i,3]^2+d.STD^2, set$t.a, set$t.b)
      } else
        for(i in 1:nrow(dat))
          {
            det <- as.numeric(dat[i,])
            if(det[5]==0)
              {
                x <- seq(det[2]-max(100,4*det[3]), det[2]+max(100,4*det[3]), length=date.res)
                ccurve <- cbind(x, x, rep(0,length(x))) # dummy 1:1 curve
              } else
                if(det[5]==1) ccurve <- cc1 else if(det[5]==2) ccurve <- cc2 else
                  if(det[5]==3) ccurve <- cc3 else ccurve <- cc4

            d.R <- set$d.R; d.STD <- set$d.STD; t.a <- set$t.a; t.b <- set$t.b
            if(length(det) >= 7 && det[5] > 0) # the user provided age offsets; only for C14 dates
              {
                d.R <- det[6]
                d.STD <- det[7]
              }

            if(length(det) >= 9) # the user provided t.a and t.b values for each date
              {
                t.a <- det[8]
                t.b <- det[9]
                if(round(t.b-t.a) !=1) stop("\n Warning! t.b - t.a should always be 1, check the manual")
              }

            calib$probs[[i]] <- d.cal(ccurve, det[2]-d.R, det[3]^2+d.STD^2, t.a, t.b)
          }
    calib
  }





### produce plots of the calibrated distributions
calib.plot <- function(set=info, rotate.axes=FALSE, rev.d=FALSE, rev.yr=FALSE, yr.lim=c(), date.res=100, d.lab="Depth", yr.lab=ifelse(set$BCAD, "BC/AD", "cal yr BP"), width=15, cutoff=.001, C14.col=rgb(0,0,1,.5), C14.border=rgb(0,0,1,.75), cal.col=rgb(0,.5,.5,.5), cal.border=rgb(0,.5,.5,.75), new.plot=TRUE, plot.dists=TRUE, normalise.dists=TRUE)
  {
    width <- length(set$d.min:set$d.max) * width/50
    if(length(yr.lim)==0)
      {
        lims <- c()
        for(i in 1:length(set$calib$probs))
          lims <- c(lims, set$calib$probs[[i]][,1])
          yr.lim <- range(lims)
          if(set$BCAD) yr.lim <- 1950-yr.lim
      }
    if(rev.yr) yr.lim <- yr.lim[2:1]
    dlim <- range(set$d)
    if(rev.d) dlim <- dlim[2:1]
    if(new.plot)
      if(rotate.axes)
        plot(0, type="n", xlim=yr.lim, ylim=dlim[2:1], xlab=yr.lab, ylab=d.lab, main="") else
          plot(0, type="n", xlim=dlim, ylim=yr.lim, xlab=d.lab, ylab=yr.lab, main="")

    if(plot.dists)
      for(i in 1:length(set$calib$probs))
        {
          cal <- set$calib$probs[[i]]
          if(set$BCAD) cal[,1] <- 1950-cal[,1]
          o <- order(cal[,1])
          if(normalise.dists)
            cal <- cbind(cal[o,1], width*cal[o,2]/sum(cal[,2])) else
              cal <- cbind(cal[o,1], width*cal[o,2]/max(cal[,2]))
          cal <- approx(cal[,1], cal[,2], seq(min(cal[,1]), max(cal[,1]), length=200)) # tmp
          pol <- cbind(c(set$calib$d[[i]]-cal$y, set$calib$d[[i]]+rev(cal$y)), c(cal$x, rev(cal$x)))
          if(rotate.axes) pol <- cbind(pol[,2], pol[,1])
          if(ncol(set$dets)==4 || (ncol(set$dets) > 4 && set$dets[i,5] > 0))
            {
              col <- C14.col
              border <- C14.border
            } else
            {
              col <- cal.col
              border <- cal.border
            }
         polygon(pol, col=col, border=border)
        }
  }



# mix calibration curves, e.g. for dates with marine and terrestrial components
mix.curves <- function(ratio=0.5, cc1="Curves/3Col_intcal13.14C", cc2="Curves/3Col_marine13.14C", name="Curves/mixed.14C", offset=c(0,0))
  {
    cc1 <- read.table(cc1)
    cc2 <- read.table(cc2)

    cc2.mu <- approx(cc2[,1], cc2[,2], cc1[,1], rule=2)$y + offset[1] # interpolate cc2 to the calendar years of cc1
    cc2.error <- approx(cc2[,1], cc2[,3], cc1[,1], rule=2)$y
    cc2.error <- sqrt(cc2.error^2 + offset[2]^2)
    mu <- ratio * cc1[,2] + (1-ratio) * cc2.mu
    error <- ratio * cc1[,3] + (1-ratio) * cc2.error
    write.table(cbind(cc1[,1], mu, error), name, row.names=FALSE, col.names=FALSE, sep="\t")
  }



# calculate C14 ages from pmC values
pMC.age <- function(mn, sdev, ratio=100, decimals=0)
  {
    y <- -8033*log(mn/ratio)
    sdev <- y - -8033*log((mn+sdev)/ratio)
    round(c(y, sdev), decimals)
  }



# calculate pMC values from C14 ages
age.pMC <- function(mn, sdev, ratio=100, decimals=3)
  {
    y <- exp(-mn/8033)
    sdev <- y - exp(-(mn+sdev)/8033)
    signif(ratio*c(y, sdev), decimals)
  }



### Functions to plot the prior distributions



### plot the prior for the accumulation rate
PlotAccPrior <- function(s, mn, set=info, main="", xlim=c(0, 3*max(mn)), xlab=paste("Acc. rate (yr/", noquote(set$unit), ")", sep=""), ylab="Density", add=FALSE, legend=TRUE, cex=.9)
  {
    o <- order(s, decreasing=TRUE)
    priors <- unique(cbind(s[o],mn[o])[,1:2])
    if(length(priors) == 2)
      {
        curve(dgamma(x, s, s/mn), col=3, lwd=2, xlim=xlim, xlab=xlab, ylab=ylab, add=add)
        txt <- paste("acc.shape: ", priors[1], "\nacc.mean: ", priors[2])
      } else
      {
        curve(dgamma(x, priors[1,1], priors[1,1]/priors[1,2]), col=3, lwd=2, xlim=xlim, xlab=xlab, ylab=ylab, add=add)
        for(i in 2:nrow(priors))
          curve(dgamma(x, priors[i,1], priors[i,1]/priors[i,2]), col=3, lwd=2, xlim=xlim, xlab=xlab, ylab=ylab, add=if(i==1) add else TRUE)
        txt <- paste("acc.shape: ", toString(priors[,1]), "\nacc.mean: ", toString(priors[,2]))
      }
    if(legend)
      legend("topright", txt, bty="n", cex=cex, text.col=2, adj=c(0,0))
  }



### plot the prior for the memory (= accumulation rate varibility between neighbouring depths)
PlotMemPrior <- function(s, mn, thick, ds=1, set=info, xlab="Memory (ratio)", ylab="Density", main="", add=FALSE, legend=TRUE, cex=.9)
  {
    o <- order(s, decreasing=TRUE)
    priors <- unique(cbind(s[o],mn[o])[,1:2])
    if(length(priors)==2)
      {
        curve(dbeta(x, s*mn, s*(1-mn)), 0, 1, col=3, lwd=2, xlab=xlab, ylab=ylab, add=add)
        txt <- paste("mem.strength: ", s, "\nmem.mean: ", mn, "\n", set$K, " ", thick, noquote(set$unit), " sections", sep="")
      } else
      {
        curve(dbeta(x, priors[1,1]*priors[1,2], priors[1,1]*(1-priors[1,2])), 0, 1, col=3, lwd=2, xlab=xlab, ylab=ylab, add=add)
        for(i in 2:nrow(priors))
          curve(dbeta(x, priors[i,1]*priors[i,2], priors[i,1]*(1-priors[i,2])), 0, 1, col=3, lwd=2, xlab="", ylab="", add=TRUE)
        txt <- paste("acc.shape: ", toString(priors[,1]), "\nacc.mean: ", toString(priors[,2]))
      }
    if(legend)
      legend("topright", txt, bty="n", cex=cex, text.col=2, adj=c(0,0))
    warn <- FALSE
    for(i in s)
      for(j in mn)
        if(i*(1-j) <= 1) warn <- 1
    if(warn) cat("\nWarning! Chosen memory prior might cause problems.\nmem.strength * (1 - mem.mean) should be smaller than 1\n ")
  }



### plot the prior for the hiatus length
PlotHiatusPrior <- function(s=set$hiatus.shape, mn=set$hiatus.mean, hiatus=set$hiatus.depths, set=info, xlab="Hiatus size (yr)", ylab="Density", main="", xlim=c(0, 3*max(mn)), add=FALSE, legend=TRUE)
  {
    o <- order(s, decreasing=TRUE)
    priors <- unique(cbind(s[o],mn[o])[,1:2])
    if(length(priors) == 2)
      {
        curve(dgamma(x, priors[1], priors[1]/priors[2]), col=3, lwd=2, xlim=xlim, xlab=xlab, ylab=ylab, add=add)
        txt <- paste("h.shape: ", toString(priors[1]), "\nh.mean: ", toString(priors[2]), "\nd: ", toString(hiatus))
      } else
      for(i in 2:nrow(priors))
        {
          curve(dgamma(x, priors[i,1], priors[i,1]/priors[i,2]), col=3, lwd=2, xlim=xlim, xlab=xlab, ylab=ylab, add=if(i==1) add else TRUE)
          txt <- paste("h.shape: ", toString(priors[,1]), "\nh.mean: ", toString(priors[,2]), "\nd: ", toString(hiatus))
        }
    if(legend)
      legend("topright", txt, bty="n", cex=.7, text.col=2, adj=c(0,0))
  }



### plot the posterior (and prior) of the accumulation rate
PlotAccPost <- function(set=info, s=set$acc.shape, mn=set$acc.mean, main="", xlab=paste("Acc. rate (yr/", set$unit, ")", sep=""), ylab="Frequency")
  {
    hi <- 2:(set$K-1)
    if(!is.na(set$hiatus.depths)[1])
      for(i in set$hiatus.depths) hi <- hi[-max(which(set$d < i))]
    post <- c()
    for(i in hi) post <- c(post, set$output[[i]])
    post <- density(post)
    maxprior <- dgamma((s-1)/(s/mn), s, s/mn)
    if(is.infinite(max(maxprior))) max.y <- max(post$y) else
      max.y <- max(maxprior, post$y)
    lim.x <- range(0, post$x, 2*mn)
    plot(0, type="n", xlim=lim.x, xlab=xlab, ylim=c(0, 1.1*max.y), ylab="")
    polygon(post, col=grey(.8), border=grey(.4))
    PlotAccPrior(s, mn, add=TRUE, xlim=range(post$x), xlab="", ylab=ylab, main=main)
  }



### plot the posterior (and prior) of the memory
PlotMemPost <- function(set=info, corenam, K, main="", s=set$mem.strength, mn=set$mem.mean, xlab=paste("Memory"), ylab="Density", ds=1, thick)
  {
    post <- density(set$output[,set$n]^(1/set$thick), from=0, to=1)
    post <- cbind(c(min(post$x), post$x, max(post$x)), c(0, post$y, 0))
    maxprior <- max(dbeta((0:100)/100, s*mn, s*(1-mn)))
    if(is.infinite(max(maxprior))) max.y <- max(post[,2]) else
      max.y <- max(maxprior, max(post[,2]))
    plot(0, type="n", xlab=xlab, xlim=c(0,1), ylim=c(0, 1.1*max.y), ylab="", main="")
    polygon(post, col=grey(.8), border=grey(.4))
    PlotMemPrior(s, mn, thick, add=TRUE, xlab="", ylab=ylab, main=main)
 }



### plot the posterior (and prior) of the hiatus
PlotHiatusPost <- function(set=info, shape=set$hiatus.shape, mn=set$hiatus.mean, main="", xlim=c(0, 3*max(set$acc.mean)), xlab=paste("Hiatus size (yr)", sep=""), ylab="Frequency", minbreaks=10, after=set$after)
  {
    gaps <- c()
    for(i in set$hiatus.depths)
      {
        below <- Bacon.Age.d(i+after, info)
        above <- Bacon.Age.d(i-after, info)
        gaps <- c(gaps, below - above)
      }
    gaps <- density(gaps, from=0)
    max.x <- max(gaps$x, xlim)
    max.prior <- dgamma((shape-1)/(shape/mn), shape, shape/mn)
    if(is.infinite(max(max.prior))) max.y <- max(gaps$y) else
      max.y <- max(max.prior, gaps$y)
    plot(0, type="n", main="", xlab=xlab, xlim=c(0, max.x), ylab=ylab, ylim=c(0, 1.1*max.y))
    polygon(cbind(c(min(gaps$x), gaps$x, max(gaps$x)), c(0,gaps$y,0)),
      col=grey(.8), border=grey(.4))
    PlotHiatusPrior(add=TRUE, xlim=c(0, max.x), xlab="", ylab=ylab, main=main)
  }



## Accumulation rate calculations



# should take into account hiatuses
accrate.depth <- function(d, set=info, cmyr=FALSE)
  {
    if(is.na(set$hiatus.depths))
      {
        if(min(set$d) <= d && max(set$d) >= d)
          accs <- set$output[,1+max(which(set$d <= d))] else accs <- NA
      } else
          for(hi in set$hiatus.depths)
            {
              whichbelow <- min(which(set$d > d))
              whichabove <- max(which(set$d < d))
              if(set$d[whichbelow] > hi && set$d[whichabove] < hi)
                if(d < hi)
                  accs <- set$output[,1+1+whichbelow] else
                    accs <- set$output[,0+whichabove]
            }
    if(cmyr) 1/accs else accs
  }

# should take into account hiatuses
accrate.age <- function(age, set=info, cmyr=FALSE)
  {
   ages <- cbind(set$output[,1])
   for(i in 1:set$K)
     ages <- cbind(ages, ages[,i] + (set$thick * (set$output[,i+1])))

   if(age < min(ages) || age > max(ages))
     cat(" Warning, age outside the core's age range!\n")
   accs <- c()
   for(i in 2:ncol(ages))
      {
        these <- (ages[,i-1] < age) * (ages[,i] > age)
        if(sum(these) > 0) # age lies within these age-model iterations
          accs <- c(accs, set$output[which(these>0),i+1])
      }
    if(cmyr) 1/accs else accs
  }



plot.accrate.depth <- function(set=info, d=set$d, d.lim=range(set$d), acc.lim=c(), d.lab="Depth", cmyr=FALSE, acc.lab=ifelse(cmyr, "accumulation rate (cm/yr)", "accumulation rate (yr/cm)"), dark=1, rotate.axes=FALSE, rev.d=FALSE, rev.acc=FALSE)
  {
    max.acc <- 0; max.dens <- 0
    acc <- list()
    for(i in 1:length(d))
      if(length(acc.lim) == 0)
        acc[[i]] <- density(accrate.depth(d[i], set, cmyr=cmyr), from=0) else
        acc[[i]] <- density(accrate.depth(d[i], set, cmyr=cmyr), from=0, to=max(acc.lim))
    for(i in 1:length(d))
      {
         max.acc <- max(max.acc, acc[[i]]$x)
         max.dens <- max(max.dens, acc[[i]]$y)
      }
    for(i in 1:length(d))
      {
        acc[[i]]$y <- acc[[i]]$y/max.dens
        acc[[i]]$y[acc[[i]]$y > dark] <- dark
      }

if(rev.d) d.lim <- rev(d.lim)
if(length(acc.lim) == 0) acc.lim <- c(0, max.acc)
if(rev.acc) acc.lim <- rev(acc.lim)

    if(rotate.axes)
      {
        plot(0, type="n", xlab=acc.lab, ylab=d.lab, ylim=d.lim, xlim=acc.lim)
        for(i in 2:length(d))
          image(acc[[i]]$x, d[c(i-1, i)], t(1-t(acc[[i]]$y)), add=TRUE, col=grey(seq(1-max(acc[[i]]$y), 1, length=50)))
      } else
      {
        plot(0, type="n", xlab=d.lab, ylab=acc.lab, xlim=d.lim, ylim=acc.lim)
        for(i in 2:length(d))
          image(d[c(i-1, i)], acc[[i]]$x, 1-t(acc[[i]]$y), add=TRUE, col=grey(seq(1-max(acc[[i]]$y), 1, length=50)))
      }
  }



# currently doesn't deal with hiatus
plot.accrate.age <- function(min.age=min(set$ranges[,2]), max.age=max(set$ranges[,3]), yr.res=200, set=info, yr.lim=c(), acc.lim=c(), upper=.99, dark=50, BCAD=set$BCAD, yr.lab=ifelse(BCAD, "BC/AD", "cal BP"), acc.lab="accumulation rate (yr/cm)", cmyr=FALSE, rotate.axes=FALSE, rev.yr=FALSE, rev.acc=FALSE)
 {
    yr.seq <- seq(min.age, max.age, length=yr.res)
    max.y <- 0; all.x <- c()
    hist.list <- list()
    for(i in 1:length(yr.seq))
      {
        if(!(i %% 50)) cat(".")
        acc <- accrate.age(yr.seq[i], set, cmyr=cmyr)
        if(cmyr) acc <- rev(acc)
        if(length(acc) > 2)
          if(length(acc.lim)==0)
            acc <- density(acc, from=0) else
            acc <- density(acc, from=0, to=max(acc.lim))
        hist.list$x[[i]] <- acc$x
        hist.list$y[[i]] <- acc$y/sum(acc$y)
        max.y <- max(max.y, hist.list$y[[i]])
        all.x <- c(all.x, acc$x)
      }

    if(BCAD) yr.seq <- 1950 - yr.seq
    if(length(yr.lim) == 0) yr.lim <- range(yr.seq)
    if(length(acc.lim) == 0) acc.lim <- c(0, 1.1*quantile(all.x, upper))

    if(rev.yr) yr.lim <- rev(yr.lim)
    if(rev.acc) acc.lim <- rev(acc.lim)

    if(rotate.axes)
      {
        plot(0, type="n", xlim=acc.lim, xlab=acc.lab, ylim=yr.lim, ylab=yr.lab)
        for(i in 2:length(yr.seq))
          image(sort(hist.list$x[[i]]), yr.seq[c(i-1,i)], t(t(matrix(hist.list$y[[i]]))),
            col=grey(seq(1, 1-min(1,max(hist.list$y[[i]])*dark/max.y), length=50)), add=TRUE)
      } else
      {
        plot(0, type="n", xlim=yr.lim, xlab=yr.lab, ylim=acc.lim, ylab=acc.lab)
        for(i in 2:length(yr.seq))
          image(sort(yr.seq[c(i-1,i)]), hist.list$x[[i]], t(matrix(hist.list$y[[i]])),
            col=grey(seq(1, 1-min(1,max(hist.list$y[[i]])*dark/max.y), length=50)), add=TRUE)
     }
    cat("\n")
  }


### doesn't deal with hiatus yet
flux.age <- function(proxy=1, min.age=min(set$ranges[,2]), max.age=max(set$ranges[,3]), age.res=200, set=info, flux=c(), flux.lim=c(), flux.lab="flux", upper=.95, dark=set$dark, yr.lim=c(), BCAD=set$BCAD, yr.lab=ifelse(BCAD, "BC/AD", "cal BP"), rotate.axes=FALSE, rev.flux=FALSE, rev.yr=FALSE)
  {
    if(length(flux) == 0) # then read a .csv file, expecting data in columns with headers
      {
        flux <- read.csv(paste("Cores/", set$core, "/", set$core, "_flux.csv", sep=""))
        flux <- cbind(flux[,1], flux[,1+proxy])
	    isNA <- is.na(flux[,2])
	    flux <- flux[!isNA,]
      }
    age.seq <- seq(min(min.age, max.age), max(min.age, max.age), length=age.res);
    fluxes <- array(NA, dim=c(nrow(set$output), length(age.seq)))
    for(i in 1:nrow(set$output))
      {
        if(!(i %% 100)) cat(".")
        ages <- as.numeric(set$output[i,1:(ncol(set$output)-1)]) # 1st step to calculate ages for each set$d
        ages <- c(ages[1], ages[1]+set$thick * cumsum(ages[2:length(ages)])) # now calculate the ages for each set$d
        ages.d <- approx(ages, c(set$d, max(set$d)+set$thick), age.seq, rule=1)$y # find the depth belonging to each age.seq, NA if none
        ages.i <- floor(approx(ages, (length(set$d):0)+1, age.seq, rule=2)$y) # find the column belonging to each age.seq
        flux.d <- approx(flux[,1], flux[,2], ages.d)$y # interpolate flux (in depth) to depths belonging to each age.seq
        fluxes[i,] <- flux.d / as.numeric(set$output[i,(1+ages.i)]) # (amount / cm^3) / (yr/cm) = amount * cm-2 * yr-1
      }
    cat("\n")
    fluxes[is.na(fluxes)] <- -99999
    if(length(flux.lim) == 0) flux.lim <- c(0, quantile(fluxes[fluxes>0], upper))
    max.dens <- 0
    for(i in 1:length(age.seq))
      {
        tmp <- fluxes[,i] # all fluxes that fall at the required age.seq age
        if(length(tmp) > 0)
          max.dens <- max(max.dens, density(tmp, from=0, to=max(flux.lim))$y)
      }

    if(length(yr.lim) == 0) yr.lim <- range(age.seq)

    if(rotate.axes)
      plot(0, type="n", ylim=yr.lim, ylab=yr.lab, xlim=flux.lim, xlab=flux.lab) else
        plot(0, type="n", xlim=yr.lim, xlab=yr.lab, ylim=flux.lim, ylab=flux.lab)
    for(i in 2:length(age.seq))
     {
       tmp <- fluxes[,i] # all fluxes that fall at the required age.seq age
       if(length(tmp[tmp>=0]) > 2)
         {
           flux.hist <- density(tmp, from=0, to=max(flux.lim))
           flux.hist$y <- flux.hist$y - min(flux.hist$y)
           if(rotate.axes)
             image(flux.hist$x, age.seq[c(i-1,i)], matrix(flux.hist$y/max.dens), add=TRUE,
               col=grey(seq(1,max(0, 1-dark*(max(flux.hist$y)/max.dens)), length=100))) else
                 image(age.seq[c(i-1,i)], flux.hist$x, t(matrix(flux.hist$y/max.dens)), add=TRUE,
                   col=grey(seq(1,max(0, 1-dark*(max(flux.hist$y)/max.dens)), length=100)))
         }
     }
  }



### plot chronological probability curves for events in the core
### does not yet deal correctly with hiatuses
AgesOfEvents <- function(window, move, min.age=min(set$ranges[,2]), max.age=max(set$ranges[,3]), set=info, plot.steps=FALSE, BCAD=info$BCAD, yr.lab=ifelse(BCAD, "BC/AD", "cal BP"), yr.lim=c(), prob.lab="prob", prob.lim=c(), rotate.axes=FALSE, rev.yr=TRUE, yaxs="i", bty="l")
  {
    outfile <- paste(set$prefix, "_", window, "_probs.txt", sep="")
    file.create(outfile)
    MCMCname <- paste(set$prefix, ".out", sep="")
    if(.Platform$OS == "windows")
      probfile <- paste("Cores\\", set$core, "\\", set$core, "_events.txt", sep="") else
        probfile <- paste("Cores/", set$core, "/", set$core, "_events.txt", sep="")
    if(!file.exists(probfile))
      stop("\nFile with probabilities for events per depth not found! Check the manual\n\n")
    probs <- read.table(probfile)
    if(!is.numeric(probs[1,1]))
      stop("\nFirst line of the _events.txt file should NOT contain titles; please remove them\n\n")
    if(min(probs[,1]) < min(set$d) || max(probs[,1]) > max(set$d))
      {
        cat("\nSome depths in the _events.txt file go beyond the age-model; I will remove them\n\n")
        file.rename(probfile, paste(probfile, "_backup", sep=""))
        probs <- probs[which(probs[,1] >= min(set$d)),]
        probs <- probs[which(probs[,1] <= max(set$d)),]
        write.table(probs, probfile, col.names=FALSE, row.names=FALSE, quote=FALSE)
      }

    txt <- paste("bin/events", min.age, max.age, move, window, outfile, MCMCname, nrow(set$output), set$K, set$d[1], set$thick, probfile, nrow(probs))
    if(.Platform$OS == "windows")
      suppressWarnings(shell(txt, translate=TRUE)) else
        system(txt)
    probs <- read.table(outfile)
    if(BCAD)
      {
        probs[,1] <- 1950 - probs[,1]
        o <- order(probs[,1])
        probs <- probs[o,]
      }

    if(plot.steps)
      {
        d.sort <- sort(rep(1:nrow(probs),2))
        d.sort <- cbind(d.sort[-length(d.sort)], d.sort[-1])
        probs <- cbind(c(min(probs[,1]), probs[d.sort[,1],1], max(probs[,1])), c(0,probs[d.sort[,2],2],0))
      } else
        probs <- cbind(c(min(probs[,1]), probs[,1], max(probs[,1])), c(0,probs[,2],0))
    par(yaxs=yaxs, bty=bty)

  if(length(yr.lim) == 0) yr.lim <- range(probs[,1])
  if(rev.yr) yr.lim <- rev(yr.lim)
  if(length(prob.lim) == 0) prob.lim <- c(0, 1.1*max(probs[,2]))

    if(rotate.axes)
      {
        plot(probs[,2], probs[,1], type="n", ylab=yr.lab, xlab=prob.lab, xlim=prob.lim, ylim=yr.lim)
       polygon(probs[,2:1], col="grey")
      } else
      {
        plot(probs, type="n", xlab=yr.lab, ylab=prob.lab, ylim=prob.lim, xlim=yr.lim)
       polygon(probs, col="grey")
      }
    if(move > window) cat("\nAre you sure you want the window widths to be smaller than the moves?\n\n")
  }



Cores <- function() list.files("Cores/")



if(!file.exists("default_settings.txt"))
  {
    fl <- "default_settings.txt"
    fl <- file(fl, "w")
    cat("NA #d.min\nNA #d.max\n1 #d.by\nFALSE #depths.file\nNA #slump\n",
      "20 #acc.mean\n1.5 #acc.shape\n0.7 #mem.mean\n4 #mem.strength\n",
      "NA #hiatus.depths\n1000 #hiatus.mean\n1 #hiatus.shape\n",
      "0 #BCAD\n1 #cc\n0 #postbomb\nIntCal13 #cc1\n",
      "Marine13 #cc2\nSHCal13 #cc3\nConstCal #cc4\n",
      "cm #unit\n0 #normal\n3 #t.a\n4 #t.b\n",
      "0 #d.R\n0 #d.STD\n0.95 #prob\n", sep="", file=fl)
    close(fl)
  }

cat("Hi there, welcome to Bacon for Bayesian age-depth modelling\n")

ifelse(.Platform$OS == "windows", hst <- "hist2.exe", hst <- "hist2")
if(!(hst %in% list.files("bin")))
  cat("\n Warning! It seems you haven't downloaded/installed the latest Bacon executable files. Check the manual.\n")
rm(hst)
