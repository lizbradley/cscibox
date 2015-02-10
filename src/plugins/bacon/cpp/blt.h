




//This class implements the input system 
//and data handling for the blt


#ifndef BLT_H
#define BLT_H



#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <assert.h>  // Defines the assert function.

#include "cal.h"
#include "bacon.h"
#include "input.h"
#include "ranfun.h"

#define MAXNUMOFCURVES 100
#define MAXNUMOFDETS  1000

#define BUFFSIZE 4000

//Maximum number of cores
#define MAXNUMOFCORES 20

//Maximum number of markers
#define MAXNUMOFMARKERS 10



//the "every" thinning subsampling parameter is EVERY_MULT*All.Dim()
#define EVERY_MULT 5
//The burn in is BURN_IN_MULT*All.Dim()
#define BURN_IN_MULT 200
//Every how many iterations we expect and acceptance: inverse of the acceptance rate
#define ACCEP_EV 20



class core {//Information for an individual core
	
private:
	
	char *datafile; //name of bacon file name
	char *outfile; //name of .out file name

	int n;
	//Array of int's with the Det number of each marker
	//if -1 that marker is missing. 
	int *det;
	
	Input *All; //bacon and all other information

public:
	
	core(char *dataf, char *outf, int nn=0, int *dt=NULL) {
		
		All = new Input( dataf, MAXNUMOFCURVES, MAXNUMOFDETS);
		
		datafile = new char[BUFFSIZE];
		strcpy( datafile, dataf);
		outfile = new char[BUFFSIZE];
		strcpy( outfile, outf);
		
		SetDets( nn, dt);
	}
	
	void SetDets( int nn, int *dt) {
		if ((n = nn) != 0) {
			det = new int[n];
			for (int j=0; j<n; j++) 
				det[j] = dt[j];
		}
		
	}
	
	char *GetName(void) { return datafile; }
	int GetNumAllDets(void) { return All->GetNumDets(); }

	const char *GetLabNum(int k) { return All->GetLabNum(k); }
	
	int ExistsMarker(int j) {  return (det[j] >= 0); }
	double GetDetY(int j) {
		assert(det[j] != -1); //Check if marker exist in this core
		return All->GetDetY(det[j]);
	}
	double GetDetSd(int j) {
		assert(det[j] != -1); //Check if marker exist in this core		
		return All->GetDetSd(det[j]);
	}
	double GetDetTh(int j) {
		assert(det[j] != -1); //Check if marker exist in this core
		return All->GetDetTh(det[j]);
	}
	double SetDetY( int j, double y) {
		assert(det[j] != -1); //Check if marker exist in this core
		return All->SetDetY( det[j], y);
	}
	double SetDetSd( int j, double sd) { 
		assert(det[j] != -1); //Check if marker exist in this core
		return All->SetDetSd( det[j], sd);
	}

	int Dim(void) { return All->Dim(); }
	int PrintNumWarnings(void) { All->PrintNumWarnings(); }
	int RunTwalk( int it, int every, char *mode, char silent) { All->RunTwalk( outfile, it, every, mode, silent); }
	
};


class blt {

private:

	core **Co; //all cores
	int T;  //number of cores
	
	int n; //number of markers
	int *m; //m[j] = number of cores with marker j
	double *mu0; //mu0[j] = a priori mean for marker j
	double *tau0; //tau0[j] = a priori precision for marker j	

	double *tau1; //tau1[j] = precision for marker j interval deposition
	
	char **MarkerNam; //MarkerNam[j] = Marker name
	
	//Used for the input file reader	
	char *buff;  //Buffer to hold the parameter line
	int maxnumofpars;
	int numofpars;
	char **pars; //Pointers to each parameter
	double *rpars; //array of double to read parameters
	int GetPars();
	

public:

	blt( char *datafile, int maxnumofcores=MAXNUMOFCORES, int maxnumofmarkers=MAXNUMOFMARKERS);
	
	int GetT() { return T; }
	int Getn() { return n; }

	//Run the twalk simulation for core c
	void RunTwalk( int c, int it, int every, char *mode= (char *) "w+", int silent=0) {
		
		/*In this case, only the accepted iterations are needed,
			include the DEFS = -DSAVEACCONLY line in the makefile*/
		
		Co[c]->RunTwalk( it, every, mode, silent);
		
	}
	
	int ExistsMarker(int j, int c) { return Co[c]->ExistsMarker(j); }
	
	//Set mu0 of marker j
	double SetMu0(int j) { 
		
		m[j] = 0;
		
		for (int c=0; c<T; c++)  {
			if (Co[c]->ExistsMarker(j)) {
				m[j]++;
				mu0[j] = Co[c]->GetDetY(j); //get any marker
			}
		}
		
		if (m[j] == 0) {
			printf("blt: ERROR, marker %d does not exist in all %d cores.\n", j, T);
			
			exit(-1);
			
		}
		
		for (int c=0; c<T; c++) 
			if (Co[c]->ExistsMarker(j))
				if (mu0[j] != Co[c]->GetDetY(j)) { //compare
					printf("blt: ERROR, two different mu0's given: %f %f\n", mu0[j], Co[c]->GetDetY(j));
					
					exit(-1);
				}

		return mu0[j];
	}
	
	double GetMu0(int j) { return mu0[j]; }


	double GetTau0(int j) { return tau0[j]; }
	double GetTau1(int j) { return tau1[j]; }
	double GetSz(int j) { return (double) m[j]; } //Get the number of cores with marker j
	
	
	//Set y of marker j
	double SetY( int j, double y) { 

		for (int c; c<T; c++) 
			if (Co[c]->ExistsMarker(j))
				Co[c]->SetDetY( j, y); //Set y of marker j, for all cores that has the marker
	
		return y;
	}
	
	double GetTh( int j, int c) { return Co[c]->GetDetTh(j); }

	//Get mean theta of marker j
	double GetMeanTh( int j) {
	
		double mean=0.0;
		
		for (int c=0; c<T; c++) 
			if (Co[c]->ExistsMarker(j))
				mean += Co[c]->GetDetTh(j); //Get theta of marker j, for all the cores that has the marker
		
		return (mean/(double) m[j]);
	}

	//Returns the dimension, total number of parameters, of core c
	int Dim(int c) { return Co[c]->Dim(); }
	
	//Print all warnings
	void PrintNumWarnings() {
		
		for (int c; c<T; c++) {
			printf("blt: WARNINGS, core %s ", Co[c]->GetName());
			Co[c]->PrintNumWarnings();
		}
	}
	
	char *GetMarkerName(int j) { return MarkerNam[j]; }
	char *GetCoreName(int c) { return Co[c]->GetName(); }
	
	
		
};

//Set to point at the beginning of each parameter in buff
//Substitute commas or semicolon with \0
int blt::GetPars() {
	
	int len = strlen(buff);
	numofpars = 0;
	pars[numofpars] = buff; //First par
	
	for (int i=0; i < len; i++) {
		
		if (buff[i] == ',') { //Middle par
			buff[i] = '\0';
			sscanf( pars[numofpars], " %lf", rpars+numofpars); //Try to read par. as double
			
			numofpars++;
			pars[numofpars] = buff+i+1; //Next par
			
			continue;
		}
		
		if (buff[i] == ';') { //end
			buff[i] = '\0';
			sscanf( pars[numofpars], " %lf", rpars+numofpars); //Try to read par. as double
			
			numofpars++;			
			return numofpars;
		}
	}
}



blt::blt( char *datafile, int maxnumofcores, int maxnumofmarkers) {
	
	
	//Open the array to hold all cores
	Co = new core * [maxnumofcores];
	T = 0; //zero cores so far
	
	n = 0; //zero markers so far
	
	m = new int[maxnumofmarkers]; //m[j] = number of cores with marker j
	mu0 = new double[maxnumofmarkers]; //mu0[j] = a priori mean for marker j
	tau0 = new double[maxnumofmarkers]; //tau0[j] = a priori precision for marker j	
	
	tau1 = new double[maxnumofmarkers]; //tau1[j] = precision for marker j interval deposition	
	
	MarkerNam = new char * [maxnumofmarkers];
	
	
	int dt[maxnumofmarkers]; 
	

	//Open the array of pointers to point at each parameter
	maxnumofpars = MAXNUMOFPARS;
	pars = new char * [maxnumofpars];
	numofpars = 0;
	rpars = new double[maxnumofpars];
	
	FILE *F;
	
	if ((F = fopen( datafile, "r")) == NULL)
	{
		printf("Could not open %s for reading\n", datafile);
		
		exit(-1);
	}
	
	printf("Reading %s\n", datafile);
	char line[BUFFSIZE];
	char key[10];
	int i=0, nm, j;
	
	
	do
	{
		if(fgets( line, BUFFSIZE, F));
		i++;
		
		//Remove leading blank spaces
		j = 0;
		while (line[j] == ' ')
			j++ ;
		
		
		if ((line[j] == '#') || (line[j] == '\n')) //Comment or blank line, ignore line
			continue;
		
		//This is the syntax, key number : parameters
		if (sscanf( line, " %s %d :", key, &nm) < 2)
		{
			printf("%s:%d Syntax error\n\n", datafile, i);
			
			break;
		}
		
		buff = strstr( line, ":") + 1;
		GetPars();
		
		/**** Debug ***
		 printf("%d: KEY: %s, n= %d, %d pars:", i, key, nm, numofpars);//Debug
		 for (int i=0; i<numofpars; i++)
		 printf("|%s:%g|", pars[i], rpars[i]);
		 printf("\n");
		 /****************/
		
		//This is the Marker key
		if (strcmp( key, "Marker") == 0)
		{
			MarkerNam[n] = new char[BUFFSIZE];
			sscanf( pars[0], " %s", MarkerNam[n]); //Marker name
			

			tau1[n] = 1.0/(sqr(rpars[1])); //Maker precision
			printf("%s %f\n", MarkerNam[n], tau1[n]);

			n++;
			continue;
		}
		
		//All markers should come first then all cores.  We already know the number of Markers here
		if (strcmp( key, "Core") == 0) {
			char ax1[BUFFSIZE], ax2[BUFFSIZE];

			sscanf( pars[0], " %s", ax1); //get bacon input file
			sscanf( pars[1], " %s", ax2); //get bacon output file

			Co[T] = new core( ax1, ax2);
			
			printf("%s , %s ", ax1, ax2);
			for (int j=0; j<n; j++) { //find the location of each marker, -1=does not exist in core
				dt[j] = -1;
				for (int k=0; k<Co[T]->GetNumAllDets(); k++) {
					if (strcmp( Co[T]->GetLabNum(k), MarkerNam[j]) == 0)
						dt[j] = k;
				}
				printf(", %d", dt[j]);
			}
			printf(";\n");
			
			Co[T]->SetDets( n, dt);
			
			for (int j=0; j<n; j++)
				if (Co[T]->ExistsMarker(j)) {
					tau0[j] = 1.0/sqr(Co[T]->GetDetSd(j));
					Co[T]->SetDetSd( j, sqr(1.0/tau1[j]));
				}

			T++;		
			continue;
		}
		
		printf("blt: Unknown key: %s\n", key);
		
	} while (!feof(F));
	
	fclose(F);

	for (int j=0; j<n; j++) {
		SetMu0(j); //This also sets m
	}

	printf("blt: %d markers and %d cores read.\n", n, T);
	
}



#endif


