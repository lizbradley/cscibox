/*
 *  events1.c
 *  
 *  runs a test using the Matrix Class
*
 */

#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <string.h>

#include "ranfun.h"
#include "Matrix.h"


//    c0    thr1   alpha1      c1  m1   thr2   alpha2      c2  m2   thr3   alpha3      c3  m3    LogPost

class Events {

protected:

	Matrix *OutB;
	SubMatrix Out;

	Matrix *XB;
	SubMatrix X;
	
	int it, K, cols;
	
	double d; //depth
	double th0, th1, Dth;
	
	
	//Based depth and increment between depths
	double c0, Dc;
	double c(int i) { return c0 + i*Dc; }

	

public:

	Events( char *fnam, int itt, int KK, double cc0, double DDc, char *fnam_events, int n) {
	
		//printf("Events( %s , %d , %d , %f , %f , %s , %d )\n",  fnam, itt, KK, cc0, DDc, fnam_events, n);

		it = itt;
		K = KK;
		c0 = cc0;
		Dc = DDc;
		
		//    th0  x's w   U
		cols = 1 + K + 1 + 1;
		
		OutB = new Matrix( it, cols);
		
		Out.Set( OutB, it, cols);
		Out.filescan(fnam);       //read the MCMC sample
		
		//SubMatrix A;
		//A.Set( OutB, 20, cols);
		//A.print( stdout, NULL, 8, 2, " ", 0, 0);
		
		XB = new Matrix( n, 2);
		X.Set( XB, n, 2);
		
	 	X.filescan(fnam_events); //load the proxie probabilities
		
		//X.print();
	}
	
	~Events() {
		X.~SubMatrix();
		//A.~SubMatrix();
		Out.~SubMatrix();
		delete OutB;
	}
	
	
	double Model( int i, double d) {
		
		//c0
		if (fcmp( d, c0) == -1) { //d < c0
			printf("Events: ERROR: d = %6.4f < c0= %6.4f!!\n", d, c0);
			exit(0);
		}
		
		double S=Out( i, 0); //th0
		
		for (int k=1; k<K; k++) {
			S += Out( i, k)*Dc;
			if (fcmp( d, c(k+1)) == -1)
				return S + Out( i, k+1)*(d-c(k));
		}
		printf("Events: WARNING: extrapolation, depth d = %f above cK = %f\n", d, c(K));
		return S + Out( i, K)*(d-c(K));
		
	}

	
	double Prob(int i, double th1, double th2) {
	
		int op=0; //below the interval
		double th, prob=1.0;
	
		for (int l=0; l<X.nRow(); l++) {
		
			th = Model( i, X(l,0));
			switch (op) {
		
				case 0:
					if ((fcmp( th1, th) == -1))  //th1 <= th   (fcmp( th1, th) == 0) &&
					//if (th1 <= th)  //th1 <= th
						op = 1; //within the interval
					else
						break;
				case 1:
					if (fcmp( th2, th) == -1) { //th > th2
						op = 2; //above the interval
						break;
					}
					prob *= 1.0-X(l,1);
					break;
				case 2:
					return 1.0-prob;
			}
			//printf("l= %d, d= %f, th1= %f, th= %f, th2= %f, op= %d, prob= %f\n",
			//	l, X(l,0), th1, th, th2, op, prob);
		}
	}
	
	double Prob(double th1, double th2) {
	
		double S = 0.0;
		for (int i=0; i<it; i++) 
			S += Prob( i, th1, th2);

		return S/(double) it;			
	}
	
	
};
	


main(int argc, char *argv[]) {

	if (argc != 13) {
		printf("Usage: events th1 th2 th_shift window\n");
		printf("        outputfname MCMCsamplesfname samplesize K c0 Dc eventprobsfname depths_size\n");
		
		exit(0);
	}

	double th1;
	sscanf( argv[1], "%lf", &th1); //2000.0;

	double th2;
	sscanf( argv[2], "%lf", &th2); //3800.0;

	double th_shift;
	sscanf( argv[3], "%lf", &th_shift); //10.0;

	double window;
	sscanf( argv[4], "%lf", &window); //50.0;

	char *outputfname = strdup(argv[5]); //"probs10.50.dat";

	char *MCMCsamplesfname = strdup(argv[6]); //"EngXV_3sec.out";

	int  samplesize = 10000; 
	sscanf( argv[7], "%d", &samplesize); //10000;

	int  K = 70;
	sscanf( argv[8], "%d", &K); //3;
	
	double c0=0.0;
	sscanf( argv[9], "%lf", &c0); 

	double Dc=0.0;
	sscanf( argv[10], "%lf", &Dc); 
	
	char *eventprobsfname = strdup(argv[11]); //"EngXV.events";

	int  depths_size;
	sscanf( argv[12], "%d", &depths_size); //101;
	
	
	//char *fnam, int itt, int KK, double cc0, double DDc, char *fnam_events, int n
	Events Ev( MCMCsamplesfname, samplesize, K, c0, Dc, eventprobsfname, depths_size);



	//printf("G(i= 10, d= 60)= %f\n", Ev.Model( 10, 78.0));
	//printf("Prob(2600, 2700)= %f \n", Ev.Prob( 2600.0, 2700.0));

	FILE *F;
	if ((F = fopen( outputfname, "w+")) == NULL) {
		printf("Could not open file %s for writing.\n", outputfname);
		
		exit(0);
	}

	double prob;
	double adv=0.1;
	printf("Calculating probabilities ...\n");
	for (double th=th1; th<=th2; th+=th_shift) {
		
		prob = Ev.Prob( th-window/2.0, th+window/2.0);
		
		fprintf( F, "%f %f\n", th, prob);
		
		if ((th-th1)/(th2-th1) > adv) {
			printf("%c%5.1f advance ...\n", '%', 100*(th-th1)/(th2-th1));
			adv += 0.1;
		}
	}
	
	fclose(F);
	
	printf("Es totototoooodo amigos!\n");
	
}





