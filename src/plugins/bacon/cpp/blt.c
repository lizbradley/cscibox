/*
 
 
 BACON:
 
Implements the semiparametric autoregressive model for 
radiocarbon chronologies, using the twalk.  See paper for mathematical details and
the files:

- bacon.h: This is the implementation, with the model definitions etc.

- cal.h: Reads and manages calibration curves and determinations 

- input.h, input.c: reads the input files and stores all data

- ranfun.h, twalk.h, Matrix.h: for some gsl interfaces for random number generation, the C++ twalk implementation and a simple Matrix class. 
 
 */

#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <string.h>

#include "bacon.h"
#include "input.h"
#include "ranfun.h"
#include "blt.h"




int main(int argc, char *argv[]) {
	
// Command line: blt inputfile outputfile ssize  


	if (argc < 4) {
		printf("Usage: blt inputfile outputfile ssize\n");
		
		exit(0);
	}
	
	printf("blt: THIS IS THE BLT\n\n");
	
	
	blt All(argv[1]);
	
	
	//Sample size for y ... each core is run for an effective sample size of 10*ssize
	//but is subsampled 10 times less often, to btain a similar sample size.
	int ssize;
	sscanf( argv[3], " %d", &ssize);
	
	//ssize is the final sample size needed
	//ssize = it/(ACCEP_EV * All.Dim() * EVERY_MULT) - BURN_IN_MULT
	//Then we let
	//	int it = (ACCEP_EV * All[0]->Dim() * EVERY_MULT * (ssize + BURN_IN_MULT));
	
	int it, every;

	//run in parallel using the -fopenmp compiler option
	#pragma omp parallel for
	for (int c=0; c<All.GetT(); c++) {
		//Run the twalk
		it = (ACCEP_EV * All.Dim(c) * EVERY_MULT * (0 + BURN_IN_MULT));
		every =  -1*EVERY_MULT*All.Dim(c);// only accepted iterations are saved

		printf("blt: %d iterations in core %s\n", abs(it), All.GetCoreName(c));

		All.RunTwalk( c, it, every, "w+", 0);
	}
	
	//Output file for the blt
	FILE *outy;
	if ((outy = fopen( argv[2], "w+")) == NULL)
	{
		printf("Could not open %s for writing\n", "ysamples.out");
		
		exit(-1);
	}
	//Header for tne blt output file
	for (int j=0; j<All.Getn(); j++)
		fprintf( outy, "%s ", All.GetMarkerName(j));
	fprintf( outy, "\n");
	
	printf("blt: Sampling from cores and y\n\n");	
	
	int N=ssize;
	double mean, tau, y;
	for (int k=0; k<N; k++) {

		#pragma omp parallel for
		for (int c=0; c<All.GetT(); c++) {

			it = (ACCEP_EV * All.Dim(c) * EVERY_MULT * ( 10 ));
			every=  -1*EVERY_MULT * 10 *All.Dim(c);// only accepted iterations are saved

			if ((k % 10) == 0)
				printf("blt: %d iterations in core %s\n", abs(it), All.GetCoreName(c));

			//Run the twalk, if no initial points are given,
			//then the previous last points are used.
			All.RunTwalk( c, it, every, "a", 1); //append the new samples
		}

		//Calculate the mean for each marker and update y
		for (int j=0; j<All.Getn(); j++) {
			
			mean = All.GetMeanTh(j);

			//Update the y
			tau = All.GetTau0(j) + All.GetSz(j)*All.GetTau1(j);
			y = NorSim( (All.GetTau0(j)*All.GetMu0(j) + All.GetSz(j)*All.GetTau1(j)*mean)/tau , sqrt(1.0/tau) );
		
			//set it in all cores
			//printf("Marker %d: %f %f %f %f %f %f ", j, mean, tau, All.GetTau0(j), All.GetSz(j), All.GetTau1(j), y);
			for (int c=0; c<All.GetT(); c++) {
				if (All.ExistsMarker( j, c)) {
					All.SetY( j, y);
					//printf("%f ", All.GetTh( j, c));
					//fprintf( outy, "%7.1f ", All.GetTh( j, c));
				}
			}
			//And save it
			//printf("\n");
			fprintf( outy, "%7.1f ", y);
		}
		fprintf( outy, "\n", y);

		if ((k % 10) == 0)
			printf("blt: %d iterations of %d done so far.\n\n", k+1  , N);
				
	}
	
	fclose(outy);
	printf("blt: y samples in %s\n", argv[2]);
	
	All.PrintNumWarnings();
	for (int c=0; c<All.GetT(); c++) {
		printf("blt: suggested burn in core %d = %d\n", c, All.Dim(c) * EVERY_MULT * BURN_IN_MULT);
	}
	printf(FAREWELL);
	
	
	return 1;
}

