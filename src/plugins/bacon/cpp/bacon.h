/*
*********

Andres christen, May 2009.

Bacon
 
 BaconFix to be used with large K, number of sections 
 
 BaconMov with moving borders, to be used with small K (<10)
*
 */



#ifndef BACON_H
#define BACON_H 

//This is my traditional farewell, may be changed to something more "serious"
#define FAREWELL "Eso es to...eso es to...eso es to...eso es toooodo amigos!\n"

#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <string.h>

#include "cal.h"
#include "ranfun.h"
#include "Matrix.h"
#include "twalk.h"              // twalk simulator class



#define CHARBUFFER 8000


class Bacon: public obj_fcn {

	public:
		Bacon(int dim) : obj_fcn(dim) { /*nothing, template class*/}
		
		void show_descrip() const { printf("Bacon:\n"); }
		
		virtual double *Getx0() = 0;
		virtual double *Getxp0() = 0;
		
		virtual double Getc0() = 0;
		virtual double GetcK() = 0;
		virtual void ShowDescrip() = 0;
		virtual void PrintNumWarnings() = 0;

};


//Fixed number of sections
class BaconFix: public Bacon {
       protected:

			//Object that holds all determinations
			Dets *dets;

			int m, K; //m number of dets, K number of sections
			int H; //number of hiatuses
			double *h; //location of the hiatuses
			
			int useT; //=1 to use the t model, =0 to use the noermal model
			
			double w, w0, wp0;			
			
			double *x0, *xp0, *theta;
			
			double MinYr, MaxYr;
			
			//Based depth and increment between depths
			double c0, Dc;
			virtual double c(int i) { return c0 + i*Dc; }
			
			double U, Uprior, Uli;
			void AccPars(int prime) { /*fprintf( F, "%f  %f  %f\n", Uprior, Uli, U);*/ }
			
			double *alpha, *beta; //prior pars for the acc gamma prior in each inter hiatus section
			double prioracU(int i, const double al) { return (1.0-alpha[i])*log(al) + beta[i]*al; }

			double a, b; //a priori pars for the w beta prior
			double priorwU(const double w) {
			    double ds=1.0, logw=log(w);
			    return (ds/Dc)*(1.0-a)*logw + (1.0-b)*log(1.0-exp((ds/Dc)*logw));
			}
			//here ds = 1.0 (cm), it could be changed to a parameter


			double *ha, *hb; //a priori pars for the gamma prior on hiatus jumps in each inter hiatus
			double priorHU(int i, const double x) { return (1.0-ha[i])*log(x) + hb[i]*Dc*x; }
			
			int WarnBeyondLimits;
			//Sets the thetas and verifies correct limits
			int SetThetas(double *x) {
				double S=x[0]; //th0
				int rt = 1;

				theta[0] = x[0];
				if (fcmp( theta[0], MinYr) == -1) {// < MinYr
					WarnBeyondLimits++;
					//beyond established limits
					rt = 0;
				}
				for (int k=1; k<K; k++) {
					S += x[k]*(c(k)-c(k-1)); //For fixed c's, Dc = c(k)-c(k-1)
					theta[k] = S;  
				}
				//Last theta
				theta[K] = theta[K-1] + x[K]*(c(K)-c(K-1));
				if (fcmp( theta[K], MaxYr) == 1) 
					WarnBeyondLimits++;
					//beyond established limits
				
				return rt;
			}
			

       public:
	         BaconFix( Dets *detsdets, int KK, int HH, double **hiatus_pars, double aa, double bb,
				double MMinYr, double MMaxYr, double th0, double thp0, double cc0, double cm, int uuseT,
				unsigned long int seed, int more_pars=0)
				: Bacon((KK+1) + 1 + more_pars) {
				
			 
				//Use the student t model, 1, or the traditional normal model, 0
				useT = uuseT;
				
				dets = detsdets; 

				m = dets->Size();
				//Minimum and maximum years
				MinYr = MMinYr;
				MaxYr = MMaxYr;
				
				WarnBeyondLimits = 0;
				
				K = KK; // Number of sections
				H = HH; // Number of hiatuses
				//   reg.   w
				
				a = aa;
				b = bb;
				
				//hiatus_pars is a pointer to 5 arrays of doubles of size H+1
				//containing:
				h     = hiatus_pars[0];		
						
				alpha = hiatus_pars[1];
				beta  = hiatus_pars[2];
				
				ha    = hiatus_pars[3]; 
				hb    = hiatus_pars[4]; 


				//Open memory for the two points in the parameter space
				//x[0] is theta[0], then x[1] ... x[K], and x[K+1]=w
				x0  = new double[get_dim()];
				xp0 = new double[get_dim()];

				//These will hold the cal. years at each node
				//The translation from x's to thetas's is done in method insupport
				theta = new double[K+1];

				//Set the sections, locations for the c's
				c0 = cc0;
				Dc = (cm-c0)/(double) K;
				
				

				//Verify the ordering in the h's
				//The h's must be an array of size H+1!!! although there are only H hiatuses
				for (int k=0; k<H; k++) {
					if (fcmp( h[k], ((k == 0) ? c(K) :  h[k-1]) - Dc) != -1) { //we need only one per section
						printf("Bacon: ERROR: The hiatuses are not in descending order and/or less than %f\n", c(K));
						
						exit(0); //h[k] not in the correct order ... we need to have h[H-1] < ... < h[0] < c(K)
					}
				}
				if (H > 0)
					if (fcmp( h[H-1], c0) == -1) {
						printf("Bacon: ERROR: The last hiatus location is not greater than %f\n", c0);
						
						exit(0); //we need to have  c0 < h[H-1] 
					}
				h[H] = c0 - 2*Dc; //fix h[H] lower than the low limit for depths	
				
				
				//Initial values for x0
				x0[0]  = th0;
				xp0[0] = thp0;
				
				Seed(seed); //Set the Seed for random number generation

				//and for w, from its prior
				x0[K+1]  = BetaSim( a, b);
				xp0[K+1] = BetaSim( a, b);
				w0 = x0[K+1];
				wp0 = xp0[K+1]; //short names for the initial values

				//******************* NB ************************
				//the prior is scale=1/beta[0] ... however, to avoid models growing out of bounds
				//we prefer higher accumulation rates: scale=mult/beta[0]
				double mult=1.0;
				
				//initial values for the acc. rates
				x0[K]  = GammaSim( alpha[H], 1.0/beta[H]);
				xp0[K] = GammaSim( alpha[H], 1.0/beta[H]);
				if (H == 0) {  //with no hiatus
					for (int k=K-1; k>0; k--) { 
						x0[k]  = w0*x0[k+1] + (1.0-w0)*GammaSim( alpha[0], mult/beta[0]);		
						xp0[k] = wp0*xp0[k+1] + (1.0-wp0)*GammaSim( alpha[0], mult/beta[0]);

					}
				}
				else {//initial values for the acc. rates, with hiatus

					//we go backwards until we find the hiatus
					int l=0;	
					for (int k=K-1; k>0; k--) { 
						if ((fcmp( c(k-1), h[l]) == -1) && (fcmp( h[l], c(k)) != 1)) { //forgets
							x0[k]  = GammaSim( ha[l], 1.0/(hb[l]*Dc) );
							//printf("Hiatus %d: %f %f %f\n", l, ha[l], hb[l], x0[k]);
							l++; //jump to next hiatus, but max one hiatus in each section.
						}
						else //continue with  memory
							x0[k]  = w0*x0[k+1] + (1.0-w0)*GammaSim( alpha[l], mult/beta[l]);
					}
					
					l = 0; //do it again
					for (int k=K-1; k>0; k--) { 
						if ((fcmp( c(k-1), h[l]) == -1) && (fcmp( h[l], c(k)) != 1)) { //forgets
							xp0[k]  = GammaSim( ha[l], 1.0/(hb[l]*Dc) );
							//printf("Hiatus %d: %f %f %f\n", l, ha[l], hb[l], xp0[k]);
							l++; //jump to next hiatus, but max one hiatus in each section.
						}
						else //continue with the memory
							xp0[k]  = wp0*xp0[k+1] + (1.0-wp0)*GammaSim( alpha[l], mult/beta[l]);
					}
					
				}
				
				
			 }
			 

			//x[0] is theta[0], then x[1] ... x[K], x[K+1]=w
	         int insupport(double *x) {
			 
				//printf("insupport, ");
				//for (int i=0; i<get_dim(); i++) printf("x[%2d] = %f\n", i, x[i]);
				
				w = x[K+1];
				if   ((fcmp( w, 0.0) != 1) || (fcmp( w, 1.0) != -1))  //w out of support
					return 0;


				if (fcmp( x[K], 0.0) != 1) //acc. rate alpha_{K} <= 0, out of support
					return 0;

				if (H == 0) {
					//printf("A: %d  %f  %d\n", 0, x[0], K); 
					for (int k=1; k<K; k++) {
					
				
						//printf("B: %d  %f  %f\n", k, x[k], (x[k]-w*x[k+1])/(1.0-w)); 
						if (fcmp( (x[k]-w*x[k+1])/(1.0-w), 0.0) != 1) { //e_k <= 0
							return 0;
						}

					}
				}
				else {
					//printf("A: %d  %f  %d\n", 0, x[0], K); 

					//we go backwards until we find the hiatus
					int l=0;	
					
					for (int k=K-1; k>0; k--) { 
						//printf("B: %d  %f  %f\n", k, x[k], (x[k]-w*x[k+1])/(1.0-w)); 
						if ((fcmp( c(k-1), h[l]) == -1) && (fcmp( h[l], c(k)) != 1)) { //forgets
							if (fcmp( x[k], 0.0) != 1) //we only require x[k] greater than 0
								return 0;
							l++; //jump to next hiatus, but max one hiatus in each section.
						}
						else if (fcmp( (x[k]-w*x[k+1])/(1.0-w), 0.0) != 1) { //e_k <= 0
								return 0;
						}
					}

				}


				//Set the thetas and return
				int rt = SetThetas(x);

				//printf("%d\n", rt);

				return rt;
			 }
			 

			//we assume the correct thetas are in theta
			//G is only called right after insupport
			 virtual double G( const double d, const double *x) {
			 
				int i = (int) floor((d-c0)/Dc);

				return theta[i] + x[i+1]*(d-c(i));
				
			 }

			//This is a polymorphic version of the above age-depth model
			//where only the theta at the nearest node is returned.  
			//we assume the correct thetas are in theta!!!!
			virtual double G(const double d) {
		
				int i = (int) floor((d-c0)/Dc);
		
				return theta[i] + (d-c(i))*(theta[i+1]-theta[i])/Dc;
		
			}

			 
			 
	         ~BaconFix(){
				delete x0;
				delete xp0;
				delete theta;
				delete dets;				
			 }


			double Getc0() { return c(0); }
			double GetcK() { return c(K); }

			virtual void ShowDescrip() {
				printf("BaconFixed: Bacon jumps model with fixed c's.\n");
				printf("            K= %d, H= %d, dim= %d, Seed= %ld, Dc=%f, c(0)= %f, c(K)= %f\n",
					K, H, get_dim(), GetSeed(), Dc, c(0), c(K));
			}
			 
			void PrintNumWarnings() { 
				if (WarnBeyondLimits != 0) {
					printf("bacon: %d WarnBeyondLimits warnings:\n", WarnBeyondLimits);
					printf("bacon: WARNING: calibration attempted beyond MinYr= %f or MaxYr= %f\n", MinYr, MaxYr);
				}
			}
			
			 double *Getx0() { return x0; }
			 double *Getxp0() { return xp0; }
			 
			virtual double eval(double *x, int prime) {

				Uprior = 0.0;
				Uli = 0.0;

				//printf(" Init=%f", U);
		
				//assuming insupport is called right before eval


				if (useT) { //uses t model
					for (int j=0; j<(m-1); j++) {
		
						Uli += dets->Ut( j, G( dets->d(j), x)); //likelihood
		  
					//printf("%d  %f  %f  %f\n", j, dets->d(j), G( dets->d(j), x), Uli);
					}
					Uli += dets->Ut( m-1, G( dets->d(m-1), x));
				}
				else { //uses standard normal model
					for (int j=0; j<(m-1); j++) {
		
						Uli += dets->U( j, G( dets->d(j), x)); //likelihood
		  
					//printf("%d  %f  %f  %f\n", j, dets->d(j), G( dets->d(j), x), Uli);
					}
					Uli += dets->U( m-1, G( dets->d(m-1), x));
				}
				  
				//printf(" Uli=%f", Uli);
		
				Uprior += priorwU(w); //prior for w
		
				//printf(" priorw=%f", Uprior);


				//Set the prior for all accumulation rates
				Uprior += prioracU( 0, x[K]); //prior for alpha_K
				if (H == 0) {
					//printf("A: %d  %f  %d\n", 0, x[0], K); 
					for (int k=1; k<K; k++) {
						Uprior += prioracU( 0, (x[k]-w*x[k+1])/(1.0-w)); //prior for e_k
						//printf("%f %f\n", (x[k]-w*x[k+1])/(1.0-w), U);
					}
				}
				else {

					//we go backwards until we find the hiatus
					int l=0;	
					
					for (int k=K-1; k>0; k--) { 
						if ((fcmp( c(k-1), h[l]) == -1) && (fcmp( h[l], c(k)) != 1)) { //forgets
							Uprior += priorHU( l, x[k]); //prior for the hiatus jump in hiatus l
							l++; //jump to next hiatus, but max one hiatuas in each section.
						}
						else
							Uprior += prioracU( l, (x[k]-w*x[k+1])/(1.0-w)); //prior for e_k in section l
					}

				}
		
				//printf(" Uprior=%f, U=%f\n", Uprior, Uprior+Uli);
				/*if (!prime) {
					for (int i=0; i<n; i++) 
						printf("%f  ", x[i]);
					printf("%f\n", U);
				}*/

				return (U = Uprior + Uli);
			}
};


#endif
