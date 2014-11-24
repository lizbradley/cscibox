
#ifndef SCIBOX_H
#define SCIBOX_H

#include <math.h>

#include "cal.h"
#include "input.h"

//Class to use for pre-calibrated dates that already have likelihoods.
class PreCalDet : public Det{
protected:
    double* ydist;
    double* pdist;
    int distlen;
    
    double minage, maxage;
    // -- initialize cal curve to a constant cal curve... 
public:
    PreCalDet(char *enm, double ey, double estd, double edpth, 
              double ea, double eb, 
              double* years, int ydim, double* probs, int pdim);
              
    void ShortOut() {
        printf("%s: %6.0f+-%-6.0f  d=%-g  minyr=%-g maxyr=%-g\n",
                nm, y, std, x, minage, maxage);
    }
              
    double U(double theta);
    double Ut(double theta);
};


class FuncInput : public Input {

public:
    
    FuncInput(int numdets, PreCalDet** indets, int numhiatus, double* hdata,
              int sections, double a, double b, double minyr, double maxyr,
              double eth0, double ethp0, double c0, double cm);

};

extern int runSimulation(int numdets, PreCalDet** dets, int numhiatus, double* hdata,
                         int sections, double a, double b, double minyr, double maxyr,
                         double th0, double thp0, double c0, double cm,
                         char* outfile, int numsamples);

#endif





