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

#define MAXNUMOFCURVES 100
#define MAXNUMOFDETS  1000

#define BUFFSIZE 4000


//the "every" thinning subsampling parameter is EVERY_MULT*All.Dim()
#define EVERY_MULT 5
//The burn in is BURN_IN_MULT*All.Dim()
#define BURN_IN_MULT 200

//Every how many iterations we expect and acceptance: inverse of the acceptance rate
#define ACCEP_EV 20


int main(int argc, char *argv[]) {// Command line: bacon inputfile outputfile  

/*

  - Falta hacer Mov, no funciona por el momento:  May 2009. 
  
  - Hacer hist, command line para un solo rango de profundidades:
		hist 10 10.5 1 MSB2K.out 
	         d1  d2  bin size
			 
 - 
*/

	if (argc < 4) {
		printf("Usage: bacon inputfile outputfile ssize\n");
		
		exit(0);
	}
	
	char  ax[BUFFSIZE];
	
	//Program file
	//sprintf( ax, "Cores/%s/%s.bacon", argv[1], argv[2]);
	sprintf( ax, "%s", argv[1]);
	//Read everything from the program file
	Input All( ax, MAXNUMOFCURVES, MAXNUMOFDETS); 
	
	

	//File to save the twalk output
	sprintf( ax, "%s", argv[2]);
	
	int ssize;
	sscanf( argv[3], " %d", &ssize);
	
	//ssize is the final sample size needed
	//ssize = it/(ACCEP_EV * All.Dim() * EVERY_MULT) - BURN_IN_MULT
	//Then we let
	
	int it = ACCEP_EV * All.Dim() * EVERY_MULT * (ssize + BURN_IN_MULT);
	
	int every=  -1*EVERY_MULT*All.Dim(); // only accepted iterations
	
	//Run the twalk
	All.RunTwalk( ax, it, every);
	
	
	All.PrintNumWarnings();

/*
	char  ax2[BUFFSIZE];
	//File to save the thinned twalk output
	sprintf( ax2, "%s", argv[2]);

	
	FILE *F, *G;
	if ((F = fopen( ax, "r")) == NULL) {
		printf("Could not open %s for reading.\n", ax);
		
		exit(0);
	}
	if ((G = fopen( ax2, "w+")) == NULL) {
		printf("Could not open %s for writing.\n", ax2);
		
		exit(0);
	}

	
	char ln[CHARBUFFER];
	int burnin= BURN_IN_MULT*All.Dim(), j=0;
	every = 1;
	//subsample the twalk output:
	printf("\nSubsampling %s, burnin= %d, every= %d and store results in %s ...\n", ax, burnin, every, ax2);
	while (!feof(F)) {
		fgets( ln, CHARBUFFER, F);
		if (j == burnin) break;
		j++;
	}
	
	j=0;
	int ss=0;	
	while (!feof(F)) {

		fgets( ln, CHARBUFFER, F);
		if ((j % every) == 0) {
			
			fputs( ln, G);
			ss++;			
		}		
		j++;
	}
	printf("out.all size= %d\n", j);
		
	fclose(F);
	fclose(G);
	
	printf("Removing %s\n", ax);
	remove(ax);
		
	printf("Final sample size %d\n", ss);
*/
	
	printf("bacon: suggested burn in= %d\n", All.Dim() * EVERY_MULT * BURN_IN_MULT);
	printf(FAREWELL);
	
	
	return All.Dim() * EVERY_MULT * BURN_IN_MULT;

	
}

