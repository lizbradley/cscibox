


#include <gsl/gsl_math.h>
#include <gsl/gsl_rng.h>
#include <gsl/gsl_randist.h>
#include <gsl/gsl_sf_gamma.h>
#include <time.h>
#include <math.h>
#include <stdlib.h>

#ifndef RANFUN_H
#define RANFUN_H


#define min(x,y) ((x) < (y) ? (x) : (y))
#define max(x,y) ((x) > (y) ? (x) : (y))

inline double sqr( double x) { return (x*x);}

//interface for gsl_compare
// x==y, 0, x<y, -1, x>y, 1.
int fcmp (double x, double y, double epsilon = 0.00000000001); 

/*Interface with gsl*/

/*Available random number generators from gsl 
 gsl_rng_taus
       
       see http://sourceware.cygnus.com/gsl/ref/gsl-ref_5.html*/

#define GENERATOR gsl_rng_taus

/*to use inline functions in gsl (in c++)*/
/*define  DHAVE_INLINE at compile time*/
#ifdef DHAVE_INLINE
#define  INLINE inline
#endif

#ifndef  DHAVE_INLINE
#define  INLINE /*nothing*/
#endif


void Seed(unsigned long int s);

unsigned long int GetSeed();

double Un01();  /*Un01() */

double Unab(double a, double b);  /*U(a,b]*/

unsigned int Un0n(int n); /*Uniform integer in { 0, 1, ..., n-1 }*/

int Sign(); /*random -1 or 1*/

double NorSim(double m, double sigma); /*Normal*/

double ExpSim(double mu); /*p(x) dx = {1 \over \mu} \exp(-x/\mu) dx*/

double GammaSim(double a, double b); /*Gamma: p(x) dx = K x^{a-1} e^{-x/b} dx*/
double GammaDens(double x, double a, double b); /*density for beta, as above */

double BetaSim(double a, double b); /*Beta: p(x) dx = K x^{a-1} (1-x)^{b-1} dx */
double BetaDens(double x, double a, double b); /*density for beta, as above */

unsigned int BiSim( double p, int n); /*Binomial: p^k (1-p)^{n-k} */

/*Log of Special function Gamma*/

double LogGamma(double x);

#endif







 
