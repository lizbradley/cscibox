




//This class implements the input system for all parameters
//It reads the configuration file and hold all input needed for 
//the Bacon clasess.


#ifndef INPUT_H
#define INPUT_H



#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "cal.h"
#include "bacon.h"
#include "ranfun.h"

//Maximum number of parameters in a lines in the input program
#define MAXNUMOFPARS 20

//Maximum number of hiatuses
#define MAXNUMOFHIATUS 10

class Input {

private:

	Cal **curves;  //array with the determinations
	
	int numofcurves; //current number of c. curves
	int maxnumofcurves; //Maximum number of c. curves
	
	char *buff;  //Buffer to hold the parameter line
	
	int maxnumofpars;
	int numofpars;
	char **pars; //Pointers to each parameter

	double *rpars; //array of double to read parameters
	
	int GetPars();
	
	int K; //Number of sections
	
	int H; //Number of hiatuses
	double **hiatus_pars; //location for the hiatuses and prior parameters

	double th0; //Initial values for theta0
	double thp0;
			
	Dets *dets; //these are the determinations
	
	BaconFix *bacon;
	
	twalk *BaconTwalk;


public:

	Input(char *datafile, int maxnumofcurves, int maxm);

	//Run the twalk simulation, put the output in outputfnam
	void RunTwalk(char *outputfnam, int it, int save_every, char *mode= (char *) "w+", int silent=0) {
		
		/*In this case, only the accepted iterations are needed,
			include the DEFS = -DSAVEACCONLY line in the makefile*/

		BaconTwalk->simulation( it, outputfnam, mode, save_every, bacon->Getx0(), bacon->Getxp0(), silent=silent);
		
	}
	
	const char *GetLabNum(int j) { return dets->labnm(j); }
	int GetNumDets(void) { return dets->Size(); }

	double GetDetY( int j) { return dets->y(j); }
	double GetDetSd( int j) { return dets->sd(j); }
	double GetDetTh( int j) { return bacon->G(dets->d(j)); }

	double SetDetY( int j, double y) { return dets->SetY( j, y); }
	double SetDetSd( int j, double sd) { return dets->SetSd( j, sd); }
	
	//Returns the dimension, total number of parameters
	int Dim() { return bacon->get_dim(); }
	
	//Print number of warnings
	void PrintNumWarnings() { return bacon->PrintNumWarnings(); }
	
	
	double Getc0() { return bacon->Getc0(); }
	double GetcK() { return bacon->GetcK(); }
	int GetK() { return K; }

	/*void PrintCal( FILE *F, double c0, double cK, double by, const double *x) {

		bacon->SetThetas(x);
		for (double d=c0; d<=cK; d += by) 
			fprintf( F, "%6.1f ", bacon->G( d, x));
		fprintf( F, "\n");
		
	}*/
		
};



#endif


