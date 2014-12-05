/*
 *  hist1.c
 *
*
 */

#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <string.h>

#include "ranfun.h"
#include "Matrix.h"


//    c0    thr1   alpha1      c1  m1   thr2   alpha2      c2  m2   thr3   alpha3      c3  m3    LogPost

class Hist {

protected:

	Matrix *OutB;
	SubMatrix Out;
	SubMatrix A;

	int it, K, cols, extrapol_warning;

	double d; //depth
	double th0, th1, Dth;

	//Based depth and increment between depths
	double c0, Dc;
	double c(int i) { return c0 + i*Dc; }

	double Model(double d, double thr, double alpha, double dr)
	{
		return thr + alpha*(d-dr);
	}

	double dr1(int i, int sec)  { return Out( i, 1 + sec*4 - (sec == 0 ? 1 : 2));}
	double thr(int i, int sec)   { return Out( i, 1 + sec*4); }
	double alpha(int i, int sec) { return Out( i, 1 + sec*4 + 1); }
	double dr(int i, int sec)     { return Out( i, 1 + sec*4 + 2); }

public:

	//read all data, # of simulations # of sections
	Hist( char *fnam, int itt, int KK, double cc0, double DDc) {

		it = itt;
		K = KK;
		c0 = cc0;
		Dc = DDc;
//		printf("Dc = %f  DDc= %f\n", Dc, DDc); // tmp MB

		extrapol_warning = 0;

		//    th0  x's w   U
		cols = 1 + K + 1 + 1;

		OutB = new Matrix( it, cols);

		Out.Set( OutB, it, cols);
		Out.filescan(fnam);

		//A.Set( OutB, 20, cols);
		//A.print();
	}

	~Hist() {
		A.~SubMatrix();
		Out.~SubMatrix();
		delete OutB;
	}


	double Model(int i) {

						//c0
		if (fcmp( d, c0) == -1) { //d < c0
			printf("hist: ERROR: d = %6.4f < c0= %6.4f!!\n", d, c0);
			exit(0);
		}

		double S=Out( i, 0); //th0
		if (fcmp(d, c(1)) == -1) // tmp MB to try and correct th0 bug
			return S + Out(i, 1)*(d-c(0)); // tmp MB to try and correct th0 bug

		for (int k=1; k<K; k++) {
			S += Out( i, k)*Dc;
			if (fcmp( d, c(k+1)) == -1)
				return S + Out( i, k+1)*(d-c(k));
		}

		if (extrapol_warning <= 0) {
			printf("hist: WARNING: extrapolation, depth d = %f above cK = %f\n", d, c(K));
		}
		return S + Out( i, K)*(d-c(K));

	}


	// calculate the counts at depth d, n=number of divisions, buffer
	void GetHist( double dd, double n, int *hi) {

		th0=1e300, th1=-1e300;
		double th;

		d = dd;

		int j;
		for (j=0; j<n; j++)
			hi[j] = 0;

		for (int i=0; i<it; i++) {

			th = Model(i);

			th0 = min( th, th0);
			th1 = max( th, th1);
		}

		// Use the above and below integers
		th0 = floor(th0);
		th1 = ceil(th1);

		Dth = (th1-th0)/(double) n;

		for (int i=0; i<it; i++) {

			th = Model(i);

			j = (int) floor((th-th0)/Dth);

			if ((j < 0) || (n <= j))
				printf("i= %3d, d= %6.4f, th= %6.4f, j= %d\n", i, d, th, j);

			hi[j]++;
		}

	}

	double GetTh0() { return th0; }
	double GetTh1() { return th1; }
	double GetDth() { return Dth; }
	int Get_extrapol_warnings() { return extrapol_warning; }
};



main(int argc, char *argv[]) {

	if (argc < 10) {
		printf("Usage: hist MCMCsamplesfname samplesize c0 Dc K num_breaks outfile numberofdepths depthsfile\n");
		printf("if outfile = -, the standard output is used and you can catch the output in R with:\n");
		printf("eval(parse( text= system(\"hist pars\", inter=TRUE), srcfile=NULL))\n");
		printf("You can then retrieve each histogram with hist[[i]] (pairlist).\n\n");

		exit(0);
	}



	char *MCMCsamplesfname = strdup(argv[1]); //"EngXV_3sec.out";

	int  samplesize;
	sscanf( argv[2], "%d", &samplesize);

	int  c0;
	sscanf( argv[3], "%d", &c0);

	double  Dc;
	sscanf( argv[4], "%lf", &Dc);

	int  K;
	sscanf( argv[5], "%d", &K);

	int n;
	sscanf( argv[6], "%d", &n);

	char fout[1000];
	FILE *F;
	sscanf( argv[7], "%s", fout);
	if (strcmp( fout, "-") == 0)
		 F = stdout;
	else
		if ((F = fopen( fout, "w+")) == NULL) {

			printf("Could not open file %s for writing.\n", fout);

			exit(0);
		}

   	int n_depths; // number of depths to be found within depthsfile
   	sscanf( argv[8], "%d", &n_depths);

 	char dfin[1000]; // read that file
 	FILE *fr;
 	sscanf( argv[9], "%s", dfin);
 	if ((fr = fopen(dfin, "r")) == NULL) {
 		printf("hist: ERROR, depths file %s not found.", dfin);

 		exit(0);
 	}

   	double *depth = new double[n_depths];
   	int rtn;
	for(int i=0; i<n_depths; i++) { // extract the depths
  	  rtn = fscanf(fr, " %lf", &depth[i]);
   	}
	fclose(fr);

	Hist Hi( MCMCsamplesfname, samplesize, K, c0, Dc);

	int *hi = new int[n];

	fprintf( F, "### file: %s, it= %d\n\nhists <- NULL;\n\n", MCMCsamplesfname, samplesize);
	for (int i=0;  i<n_depths; i++) {
		Hi.GetHist( depth[i], n, hi);

		fprintf( F, "hists <- append( hists, pairlist(");
		fprintf( F, "list( d=%f, th0=%6.0f, th1=%6.0f, n=%d, Dh=%f, ss=%d, counts=c( ",
			depth[i], Hi.GetTh0(), Hi.GetTh1(), n, Hi.GetDth(), samplesize);

		for (int i=0; i<n-1; i++)
			fprintf( F, " %d,", hi[i]);
		fprintf( F, " %d))))\n", hi[n-1]);
	}

	if (0 < Hi.Get_extrapol_warnings())
		printf("hist: WARNING: %d extrapolation warnings.\n", Hi.Get_extrapol_warnings());

	delete hi;
	delete depth;
}

