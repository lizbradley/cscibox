
#ifndef CAL_H
#define CAL_H

#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <string.h>

#include "ranfun.h"
#include "Matrix.h"

#define IntCal13FNAM "Curves/3Col_intcal13.14C"
#define IntCal13ROWS 5142
#define IntCal13COLS 3

#define Marine13FNAM "Curves/3Col_marine13.14C"
#define Marine13ROWS 4801
#define Marine13COLS 3

#define SHCal13FNAM "Curves/3Col_shcal13.14C"
#define SHCal13ROWS 5142
#define SHCal13COLS 3

#define GENCCMAXLINLEN 255
#define GENCCCOLS 3

#define POSTBOMBFNAMS	"None", \
						"Curves/postbomb_NH1.14C", \
						"Curves/postbomb_NH2.14C", \
						"Curves/postbomb_NH3.14C", \
						"Curves/postbomb_SH1-2.14C", \
						"Curves/postbomb_SH3.14C"




/**** Template class to hold a calibration curve and perform all necessary calibrations. ****/
class Cal {

protected:

	int k;
	double mu, sig;

public:

	Cal(int kk) { k = kk; }

	double GetSig() { return sig; }
	double GetMu() { return mu; }

	virtual char *Name() = 0;

	virtual double cal(double theta) = 0;
	virtual double U( double y, double vr, double theta) = 0;
	virtual double Ut( double y, double vr, double theta, double a, double b) = 0;

	virtual double MinCal() = 0;
	virtual double MaxCal() = 0;

};


//Constant "calibration curve", no curve, basically
class ConstCal : public Cal {

public:

	ConstCal() : Cal(0) {
		printf("Constant calibration curve.\n");
	}

	double cal(double theta) {
		mu = theta;
		sig = 0.0;

		return theta;
	}

	char *Name() { return "Constant c. curve"; }

	double U( double y, double vr, double theta) { return 0.5*sqr(y - theta)/vr; }
	double Ut( double y, double vr, double theta, double a, double b) { return (a + 0.5)*log( b + 0.5*sqr(y - theta)/vr); }

	double MinCal() { return -1.0e300; }
	double MaxCal() { return 1.0e300; }
};




//Generic Cal. curve.  Three columns, no header, first col. ascending order BP
class GenericCal : public Cal {

protected:

	Matrix *CCB;
	SubMatrix CC;
	SubMatrix A;
	int numrows, min, max, mid;
	char name[1024];
	double mincal, maxcal, const2;

public:

	GenericCal(char *fnam) : Cal(0) {

		//Count the number of lines in the file
		FILE *F;
		if ((F = fopen( fnam, "r")) == NULL) {
			printf("Cal: ERROR: Could not find generic cal. curve, file not found: %s\n", fnam);

			exit(0);
		}

		numrows=0;
		char ln[GENCCMAXLINLEN];
		while (!feof(F)) {
			fgets( ln, GENCCMAXLINLEN, F);

			numrows++;
		}
		numrows--;
		fclose(F);

		//Read the file as usual:
		CCB = new Matrix( numrows, GENCCCOLS);

		CC.Set( CCB, CCB->nRow(), CCB->nCol());

		printf("GenericCal: Reading from file: %s, %d rows, 3 cols.\n", fnam, numrows);

		if (CC.filescan(fnam) == 0) {
			printf("Cal: ERROR: Could not find generic cal. curve, file not found: %s\n", fnam);

			exit(0);
		}

		//Set mincal and maxcal
		mincal = CC(0,0);
		maxcal = CC(numrows-1,0);

		const2 = 0.5*log(2.0 * M_PI); //M_PI defined in gsl library

		sprintf( name, "Generic cal. curve %s", fnam);
	}

	~GenericCal() {
		A.~SubMatrix();
		CC.~SubMatrix();
		delete CCB;
	}


	double cal(double theta) {


		//Find k, the correct knot.
		//We need k such that:  CC(k,0) <= theta < CC(k+1,0)


		if (fcmp(theta, mincal) == -1)
			//fprintf( stderr, "WARNING: Calibration attempted beyond Generic cal. curve %s limits, theta= %f\n", fnam, theta);
			k = 0; //extrapolation
		else
			if (fcmp(theta, maxcal) == -1) {
				//Binary search:

				min = 0;
				max = numrows-1;
				mid = (min + max)/2; //Integer division
				            //CC( mid, 0) <= theta < CC( mid+1, 0)
				while (!( (fcmp(CC( mid, 0), theta) <= 0) && (fcmp(theta, CC( mid+1, 0)) == -1) )) {

					if (fcmp(theta, CC( mid, 0)) == 1) //theta > CC( mid, 0)
						min = mid + 1;
					else
						max = mid - 1;
					mid = (min + max)/2;
				}
				k = mid;
			}
			else
			//fprintf( stderr, "WARNING: Calibration attempted beyond Generic cal. curve %s limits, theta= %f\n", fnam, theta);
				k = numrows-2; //extrapolation

		//printf(" %d: %6.3f %6.3f %6.3f\n", k, CC( k, 0), theta, CC( k+1, 0));

		mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/(CC(k+1,0)-CC(k,0));
		sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/(CC(k+1,0)-CC(k,0));

		return mu;
	}

	char *Name() { return name; }


	double U( double y, double vr, double theta)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return const2 - 0.5*log(tau)  + tau * 0.5 * sqr(y-mu);
	}


	//The new energy using the t distribution
	double Ut( double y, double vr, double theta, double a, double b)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return (a + 0.5)*log( b + tau * 0.5 * sqr(y-mu));
	}


	double MinCal() { return mincal; }
	double MaxCal() { return maxcal; }
};

/* draft curve for IntCal13 */
class IntCal13 : public Cal {

protected:

	Matrix *CCB;
	SubMatrix CC;
	SubMatrix A;
	int Bomb;
	Cal *bombcc;
	char name[255];
	double mincal, const2;

public:

	IntCal13(int bomb) : Cal(IntCal13ROWS) {

		CCB = new Matrix( IntCal13ROWS, IntCal13COLS);
		CC.Set( CCB, CCB->nRow(), CCB->nCol());

		printf("IntCal13: Reading from file: %s\n", IntCal13FNAM);

			if (CC.filescan(IntCal13FNAM) == 0) {
				printf("Cal: ERROR: Could not find IntCal13 cal. curve, file not found: %s\n", IntCal13FNAM);
			exit(0);
		}

		const2 = 0.5*log(2.0 * M_PI); //M_PI defined in gsl library

		char *postbombfnam[] = { POSTBOMBFNAMS };

		/** Read bomb **/
		Bomb = bomb;
		if (Bomb == 0) {
			mincal = -5.0; //no bomb
			sprintf( name, "IntCal13");
		}
		else
			if (Bomb < 5) {

			bombcc = new GenericCal(postbombfnam[Bomb]);
			mincal = bombcc->MinCal();
			sprintf( name, "IntCal13+%s", postbombfnam[Bomb]);
			}
			else {
				printf("Bacon: ERROR: Post bomb curve: 0 None, 1 NH1, 2 NH2, 3 NH3, 4 SH1-2, 5 SH3\n");
				exit(0);
			}


	}

	~IntCal13() {
		A.~SubMatrix();
		CC.~SubMatrix();
		delete CCB;
	}


	double MinCal() { return mincal; }
	double MaxCal() { return 50000.0; }

	virtual char *Name() { return name; }


//prototype for gsl_compare
// x==y, 0, x<y, -1, x>y, 1.
//int fcmp (double x, double y, double epsilon = 0.00000000001);
	double cal(double theta)
	{
        if (fcmp(theta, -5.0) == -1)
        {
			if (Bomb == 0) {
				//fprintf( stderr, "WARNING: Calibration attempted beyond IntCal13 cal. curve limits, theta= %f\n",theta);
				k = 0; //Extrapolation
				mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/5.0;
				sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/5.0;
			}
			else {
				bombcc->cal(theta);
				mu = bombcc->GetMu();
				sig = bombcc->GetSig();
			}

        }
        else
                if (fcmp(theta, 13900.0) != 1)
                {				//************** NB: In the official IntCal13 year 0 is node 1 (node 0 is -5)
                        k = 1 + (int) floor(theta/5.0);
                        mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/5.0;
                        sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/5.0;
                }
                else
                        if (fcmp(theta, 25000.0) != 1)
                        {
                                k = 2781 + (int) floor((theta-13900.0)/10.0);
                                mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/10.0;
                                sig = CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/10.0;
                        }
                        else
                                if (fcmp(theta, 50000.0) != 1)
                                {
                                        k = 3891 + (int) floor((theta-25000.0)/20.0);
                                        mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/20.0;
                                        sig = CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/20.0;
                                }
					else
						{
                        //fprintf( stderr, "WARNING: Calibration attempted beyond IntCal13 cal. curve limits, theta= %f\n",theta);
							k = IntCal13ROWS - 2;
							mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/100.0;
							sig = CC(k,2);
						}
		return mu;
	}

	double U( double y, double vr, double theta)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return const2 - 0.5*log(tau)  + tau * 0.5 * sqr(y-mu);
	}

	//The new energy using the t distribution
	double Ut( double y, double vr, double theta, double a, double b)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return (a + 0.5)*log( b + tau * 0.5 * sqr(y-mu));
	}
};





class Marine13 : public Cal {

protected:

	Matrix *CCB;
	SubMatrix CC;
	SubMatrix A;
	double const2;

public:

	Marine13() : Cal(Marine13ROWS) {

		CCB = new Matrix( Marine13ROWS, Marine13COLS);

		CC.Set( CCB, CCB->nRow(), CCB->nCol());

		printf("Marine13: Reading from file: %s\n", Marine13FNAM);

		if (CC.filescan(Marine13FNAM) == 0) {
			printf("Cal: ERROR: Could not find Marine13 cal. curve, file not found: %s\n", Marine13FNAM);

			exit(0);
		}

		const2 = 0.5*log(2.0 * M_PI); //M_PI defined in gsl library


	}

	~Marine13() {
		A.~SubMatrix();
		CC.~SubMatrix();
		delete CCB;
	}


	double MinCal() { return 0.0; }
	double MaxCal() { return 50000.0; }


	//char *Name() { return "IntCal09Marine"; }
	char *Name() { return "Marine13"; }


//prototype for gsl_compare
// x==y, 0, x<y, -1, x>y, 1.
//int fcmp (double x, double y, double epsilon = 0.00000000001);
	double cal(double theta)
	{
        if (fcmp(theta, 0.0) == -1)
        {
                //fprintf( stderr, "WARNING: Calibration attempted beyond marine09 cal. curve limits, theta= %f\n",theta);
                k = 0;
                mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/5;
                sig <- CC(k,2);
        }
        else
                if (fcmp(theta, 10500.0) != 1)
                {				//************** NB: 0 is the number of rows before cal year 0
                        k = 0 + (int) floor(theta/5.0);
                        mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/5.0;
                        sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/5.0;
                }
                else
                        if (fcmp(theta, 25000.0) != 1)
                        {
                                k = 2100 + (int) floor((theta-10500.0)/10.0);
                                mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/10.0;
                                sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/10.0;
                        }
                        else
                                if (fcmp(theta, 50000.0) != 1)
                                {
                                        k = 3550 + (int) floor((theta-25000.0)/20.0);
                                        mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/20.0;
                                        sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/20.0;
                                }
                                else
/*									if (fcmp(theta, 40000.0) != 1)
									{
                                        k = 3250 + (int) floor((theta-25000.0)/50.0);
                                        mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/50.0;
                                        sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/50.0;
									}
									else
										if (fcmp(theta, 50000.0) != 1)
										{
											k = 3550 + (int) floor((theta-40000.0)/100.0);
											mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/100.0;
											sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/100.0;
										}
										else */
										{
                        //fprintf( stderr, "WARNING: Calibration attempted beyond IntCal04 cal. curve limits, theta= %f\n",theta);
											k = Marine13ROWS - 2;
											mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/100.0;
											sig =CC(k,2);
										}

		return mu;
	}



	double U( double y, double vr, double theta)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return const2 - 0.5*log(tau)  + tau * 0.5 * sqr(y-mu);
	}


	//The new energy using the t distribution
	double Ut( double y, double vr, double theta, double a, double b)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return (a + 0.5)*log( b + tau * 0.5 * sqr(y-mu));
	}

};




class SHCal13 : public Cal {

protected:

	Matrix *CCB;
	SubMatrix CC;
	SubMatrix A;
	int Bomb;
	Cal *bombcc;
	char name[255];
	double mincal, const2;

public:

	SHCal13(int bomb) : Cal(SHCal13ROWS) {

		CCB = new Matrix( SHCal13ROWS, SHCal13COLS);
		CC.Set( CCB, CCB->nRow(), CCB->nCol());

		printf("SHCal13: Reading from file: %s\n", IntCal13FNAM);

			if (CC.filescan(SHCal13FNAM) == 0) {
				printf("Cal: ERROR: Could not find SHCal13 cal. curve, file not found: %s\n", SHCal13FNAM);
			exit(0);
		}

		const2 = 0.5*log(2.0 * M_PI); //M_PI defined in gsl library

		char *postbombfnam[] = { POSTBOMBFNAMS };

		/** Read bomb **/
		Bomb = bomb;
		if (Bomb == 0) {
			mincal = -5.0; //no bomb
			sprintf( name, "SHCal13");
		}
		else
			if (Bomb < 5) {

			bombcc = new GenericCal(postbombfnam[Bomb]);
			mincal = bombcc->MinCal();
			sprintf( name, "SHCal13+%s", postbombfnam[Bomb]);
			}
			else {
				printf("Bacon: ERROR: Post bomb curve: 0 None, 1 NH1, 2 NH2, 3 NH3, 4 SH1-2, 5 SH3\n");
				exit(0);
			}


	}

	~SHCal13() {
		A.~SubMatrix();
		CC.~SubMatrix();
		delete CCB;
	}


	double MinCal() { return mincal; }
	double MaxCal() { return 50000.0; }

	virtual char *Name() { return name; }


//prototype for gsl_compare
// x==y, 0, x<y, -1, x>y, 1.
//int fcmp (double x, double y, double epsilon = 0.00000000001);
	double cal(double theta)
	{
        if (fcmp(theta, -5.0) == -1)
        {
			if (Bomb == 0) {
				//fprintf( stderr, "WARNING: Calibration attempted beyond SHCal13 cal. curve limits, theta= %f\n",theta);
				k = 0; //Extrapolation
				mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/5.0;
				sig =CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/5.0;
			}
			else {
				bombcc->cal(theta);
				mu = bombcc->GetMu();
				sig = bombcc->GetSig();
			}

        }
        else
                if (fcmp(theta, 13900.0) != 1)
                {				//************** NB: In the official SHCal13 year 0 is node 1 (node 0 is -5)
                        k = 1 + (int) floor(theta/5.0);
                        mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/5.0;
                        sig = CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/5.0;
                }
                else
                        if (fcmp(theta, 25000.0) != 1)
                        {
                                k = 2781 + (int) floor((theta-13900.0)/10.0);
                                mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/10.0;
                                sig = CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/10.0;
                        }
                        else
                                if (fcmp(theta, 50000.0) != 1)
                                {
                                        k = 3891 + (int) floor((theta-25000.0)/20.0);
                                        mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/20.0;
                                        sig = CC(k,2) + (theta-CC(k,0))*(CC(k+1,2)-CC(k,2))/20.0;
                                }
					else
						{
                        //fprintf( stderr, "WARNING: Calibration attempted beyond SHCal13 cal. curve limits, theta= %f\n",theta);
							k = SHCal13ROWS - 2;
							mu = CC(k,1) + (theta-CC(k,0))*(CC(k+1,1)-CC(k,1))/100.0;
							sig = CC(k,2);
						}

		return mu;
	}

	double U( double y, double vr, double theta)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return const2 - 0.5*log(tau)  + tau * 0.5 * sqr(y-mu);
	}

	//The new energy using the t distribution
	double Ut( double y, double vr, double theta, double a, double b)
	{
        cal(theta);

        double tau = 1.0/(vr + sqr(sig));

        return (a + 0.5)*log( b + tau * 0.5 * sqr(y-mu));
	}
};





/******* Class Det *******/


//Definition for class Det, to hold a generic "determination", could be non-radiocarbon
class Det {
protected:
	char *nm;	// lab number
	double y;		// mean
	double std;	// std dev

	double x;  //depth or anything else

	double deltaR;	// delta-R (reservoir correction)
	double deltaSTD;	// delta-R std dev. (reservoir correction)

	double a, b; //prior parameters for the t distribution

	Cal *cc;	// calibration curve to use

	double med;	// mean and variance and std dev. after reservoir correction
	double vr;
	double corrstd;

public:
	Det(char *enm, double ey, double estd, double xx, double edeltaR, double edeltaSTD, double ea, double eb, Cal *ecc) {

		//Read members
		nm = strdup(enm);
		y = ey;
		std = estd;
		x = xx;
		deltaR = edeltaR;
		deltaSTD = edeltaSTD;

		a = ea;
		b = eb;

		cc = ecc;

		med = y - deltaR;
		vr = sqr(std) + sqr(deltaSTD);
		corrstd = sqrt(vr);

	}

	void ShortOut() {
		printf("%s: %6.0f+-%-6.0f  d=%-g  ResCorr= %6.1f+-%-6.1f  a=%-g b=%-g   cc=%s\n",
				nm, y, std, x, deltaR, deltaSTD, a, b, cc->Name());
	}

	double ChangeCorrMean(double y) { return (med = y); }
	double ChangeSd(double stdnew) {
		std = stdnew;
		vr = sqr(std) + sqr(deltaSTD);
		return std;
	}

	const char *labnm() { return nm; }
	double mean() { return y; }
	double sd() { return std; }
	double corr_mean() { return med; }
	double corr_vr() { return vr; }
	double res_mean() { return deltaR; }
	double res_std() { return deltaSTD; }
	double d() { return x; }

	//exp(-U) will be the likelihood for this determination.
	double U(double theta) { return cc->U( med, vr, theta); }
	double Ut(double theta) { return cc->Ut( med, vr, theta, a, b); }
};



//To hold a series of determinations
class Dets {

protected:

	Det **det;  //array with the determinations

	int m; //current number of determinations
	int max_m; //Maximum number of determinations

public:
	//The constructor only opens an array of pointers to Det structures
	Dets(int emax_m) {

		max_m = emax_m;

		m = 0;

		det = new Det * [max_m];
	}

	void AddDet(Det *de) {

		if (m == max_m) {

			printf("ERROR: Maximum number of determinations exceeded\n\n");

			exit(0);
		}

		m++;
		det[m-1] = de;

		printf("Added det: ");
		ShortOut(m-1);
	}

	int Size() { return m; }

	void ShortOut(int j) { det[j]->ShortOut(); }

	const char *labnm(int j) { return det[j]->labnm(); }
	double y(int j)  {  return det[j]->corr_mean(); }
	double sd(int j) {  return det[j]->sd(); }
	double vr(int j) {  return det[j]->corr_vr(); }
	double d(int j)  {  return det[j]->d(); }


	double SetY(int j, double y) {  return det[j]->ChangeCorrMean(y); }
	double SetSd(int j, double y) {  return det[j]->ChangeSd(y); }


	double U(int j, double theta)  { return det[j]->U(theta); }
	double Ut(int j, double theta) { return det[j]->Ut(theta); }
};

#endif
