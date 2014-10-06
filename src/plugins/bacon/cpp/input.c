#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "input.h"

#define BUFFSZ 1024

//Set to point at the beginning of each parameter in buff
//Substitute commas or semicolon with \0
int Input::GetPars() {

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



Input::Input(char *datafile, int emaxnumofcurves, int maxm) {


	//Open the array to hold all c. curves
	maxnumofcurves = emaxnumofcurves;
	curves = new Cal * [maxnumofcurves];
	numofcurves = 0;

	//Open the object to hold all determinations
	dets = new Dets(maxm);
	Det *tmpdet;

	//Open the array of pointers to point at each parameter
	maxnumofpars = MAXNUMOFPARS;
	pars = new char * [maxnumofpars];
	numofpars = 0;
	rpars = new double[maxnumofpars];


	//Open a double array of doubles to hold the hiatuses locations, if any,
	//0=h's 1=alpha's 2=betas's 3=ha's and 4=hb's for each hiatus section
	hiatus_pars = new double * [5]; //pointers to rows
	for (int i=0; i<5; i++)
		hiatus_pars[i] = new double[MAXNUMOFHIATUS]; //open each row
	H = 0; //set to zero hiatuses at the begining


	FILE *F;

	if ((F = fopen( datafile, "r")) == NULL)
	{
		printf("Could not open %s for reading\n", datafile);

		exit(-1);
	}

	printf("Reading %s\n", datafile);
	char line[BUFFSZ];
	char key[10];
	int i=0, nm, j;


	do
	{
		if(fgets( line, BUFFSZ, F));
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

		//This is the calibration curve Key, we load a calibration curve here
		double th;
		if (strcmp( key, "Cal") == 0)
		{
			sscanf( pars[0], " %s", line); //c. curve name

			if (strcmp( "IntCal13", line) == 0) {   //int bomb
				curves[numofcurves++] = new IntCal13((int) rpars[1]);

				continue;
			}

			if (strcmp( "Marine13", line) == 0) {
				curves[numofcurves++] = new Marine13();

				continue;
			}

			if (strcmp( "SHCal13", line) == 0) {
				curves[numofcurves++] = new SHCal13((int) rpars[1]);

				continue;
			}

			if (strcmp( "GenericCal", line) == 0) {   //int bomb
				curves[numofcurves++] = new GenericCal(pars[1]+1); //a space after the comma

				continue;
			}

			if (strcmp( "ConstCal", line) == 0) {
				curves[numofcurves++] = new ConstCal();
				continue;
			}

			printf("Bacon: ERROR: Don't know how to handle curve %s, use GenericCal.\n", line, line);
			exit(0);
		}


		if (strcmp( key, "Det") == 0)
		{
			sscanf( pars[0], " %s", line);
					   //Det(char *enm, double ey, double estd, double x, double edeltaR, double edeltaSTD, double ea, double eb, Cal *ecc)
			tmpdet = new Det(  line   ,  rpars[1],    rpars[2], rpars[3],       rpars[4],         rpars[5],  rpars[6],  rpars[7], curves[(int) rpars[8]]);

			dets->AddDet(tmpdet);

			continue;
		}


		if (strcmp( key, "Hiatus") == 0)
		{
			hiatus_pars[0][H] = rpars[0]; //Hiatus position

			hiatus_pars[1][H] = rpars[1]; //alpha
			hiatus_pars[2][H] = rpars[2]; //beta

			hiatus_pars[3][H] = rpars[3]; //ha
			hiatus_pars[4][H] = rpars[4]; //hb

			printf("Hiatus at: %f\n", hiatus_pars[0][H]);

			H++;

			//If H==0 then hiatus_pars willl be ignored in the constructors BaconFix and BaconMov
			continue;
		}

		if (strcmp( key, "Bacon") == 0)
		{
			//Include the parameters for the last (first) section, or for the whole core if H == 0
			hiatus_pars[0][H] = -10.0; //Hiatus position, in this case, this one will be ignored

			hiatus_pars[1][H] = rpars[7+1]; //alpha
			hiatus_pars[2][H] = rpars[7+2]; //beta

			hiatus_pars[3][H] = 0.0; //ha, in this case, this one will be ignored
			hiatus_pars[4][H] = 0.0; //hb, in this case, this one will be ignored

			unsigned long int seed;
			if (numofpars == 11)
				seed = 0; //automatic seed set with time()
			else
				seed = (unsigned long int) rpars[11];


			//Open the Bacon object
			sscanf( pars[0], " %s", line); //type of object

			if (strcmp( line, "FixNor") == 0)
					                //dets                K   H  hiatus_pars         a         b
				bacon = new BaconFix( dets,  (int) rpars[1],  H, hiatus_pars, rpars[6], rpars[7],
					rpars[2], rpars[3], rpars[4], rpars[5], rpars[10], rpars[11], 0,      seed);
					//MinYr     MaxYr       th0      thp0         c0       cm   useNor

			if (strcmp( line, "FixT") == 0)
					                //dets                K   H  hiatus_pars         a         b
				bacon = new BaconFix( dets,  (int) rpars[1],  H, hiatus_pars, rpars[6], rpars[7],
					rpars[2], rpars[3], rpars[4], rpars[5], rpars[10], rpars[11], 1,      seed);
					//MinYr     MaxYr       th0      thp0         c0       cm  useT



			//Then open the twalk object
			BaconTwalk = new twalk( *bacon, bacon->Getx0(), bacon->Getxp0(), bacon->get_dim());

			break;  //this should be the last key in the program
		}

		printf("Unknown key: %s\n", key);

	} while (!feof(F));

	bacon->ShowDescrip();

	printf("\n");
}




