#include "scibox.h"

#include <stdio.h>
#include <stdlib.h>

PreCalDet::PreCalDet(char *enm, double ey, double estd, double edpth, 
                     double ea, double eb, 
                     double* years, int ydim, double* probs, int pdim) :
  Det(enm, ey, estd, edpth, 0, 0, ea, eb, NULL) {
    ydist = new double[pdim];
    memcpy(ydist, years, pdim*sizeof(double));
    pdist = new double[pdim];
    memcpy(pdist, probs, pdim*sizeof(double));
    distlen = pdim;
    
    if (distlen > 0)
    {
        minage = ydist[0];
        maxage = ydist[distlen-1];
    }
    else
    {
        cc = new ConstCal();
    }
}

//exp(-U) should be the likelihood for this determination.
// -- probably needs conversion...?
double PreCalDet::U(double theta) { 
    if (distlen <= 0) {
        return cc->U(med, vr, theta);
    }
    
    
    //in bounds of passed dist...
    if (fcmp(theta, minage) > -1 && fcmp(theta, maxage) < 1) {
        int min = 0;
        int max = distlen-1;
        int mid = (min + max)/2;
        double interp = 0;
        
        //so! theta is a year, and ydist is a list of years.
        // we want year[mid] <= theta AND year[mid+1] > theta
        while (!( (fcmp(ydist[mid], theta) <= 0) && (fcmp(ydist[mid+1], theta) > 0) )) {

            if (fcmp(theta, ydist[mid]) > 0)
                min = mid + 1;
            else
                max = mid - 1;
            mid = (min + max)/2;
        }
        //linear interpolation
        interp = pdist[mid] + (theta-ydist[mid])*(pdist[mid+1]-pdist[mid])/(ydist[mid+1]-ydist[mid]);
        return -log(interp);
    }
    else {
        //a probability of 0 is returned from the likelihood function as +infinity
        //I'm just using a big (for this application) number here.
        return 500;
    } 
}
double PreCalDet::Ut(double theta) { 
    //TODO: figure out if there is a good way to use the t-dist when we already
    //have a probability curve...
    if (distlen <= 0)
        return cc->Ut(med, vr, theta);
    else
        return U(theta);
}


FuncInput::FuncInput(int numdets, PreCalDet** indets, int numhiatus, double* hdata,
                     int sections, double a, double b, double minyr, double maxyr,
                     double eth0, double ethp0, double c0, double cm) : Input() {
                     
    dets = new Dets(numdets);
    for (int i = 0; i < numdets; i++) {
        dets->AddDet(indets[i]);
    }
    
    H = numhiatus;
    hiatus_pars = new double* [5];
    for (int i = 0; i < 5; i++) {
        hiatus_pars[i] = new double[H+1]; //allocate memory
        std::memcpy(hiatus_pars[i], &hdata[i*numhiatus], sizeof(double) * numhiatus);
    }
    
    //last dummy hiatus is automatically passed in.
    
    K = sections; 
    th0 = eth0;
    thp0 = ethp0;
    
    bacon = new BaconFix(dets, K, H, hiatus_pars, a, b, minyr, maxyr,
                         th0, thp0, c0, cm, 0, 0); 
              
    //Then open the twalk object
    BaconTwalk = new twalk(*bacon, bacon->Getx0(), bacon->Getxp0(), bacon->get_dim());
    
    //sanity test...
    bacon->ShowDescrip();
}

//These should really be defined in one consistent header...
#define ACCEP_EV 20
#define EVERY_MULT 5
#define BURN_IN_MULT 200

int runSimulation(int numdets, PreCalDet** dets, int numhiatus, double* hdata,
                  int sections, double a, double b, double minyr, double maxyr,
                  double th0, double thp0, double c0, double cm,
                  char* outfile, int numsamples) {

    FuncInput indata(numdets, dets, numhiatus, hdata, sections, a, b,
                     minyr, maxyr, th0, thp0, c0, cm);
    
    int it = ACCEP_EV * indata.Dim() * EVERY_MULT * (numsamples + BURN_IN_MULT);
    int every = -1 * EVERY_MULT * indata.Dim(); // this is how many iterations are saved to file.
    
    //Run the twalk
    indata.RunTwalk(outfile, it, every, (char*)"w+", 0);
    indata.PrintNumWarnings();
    
    return indata.Dim() * EVERY_MULT * BURN_IN_MULT;
}



