/******************************************************************************************
 *               Pseudo-random numbers routines (extracted from GSL ) 
 *
 *                              cpptwalk-beta-1.0
 *                                July 2006
 *
 ********************************************************************************************/


#include <time.h>
#include "ranfun.h"

/* interface for gsl_compare */
int fcmp (double x, double y, double epsilon) {

	return gsl_fcmp( x, y, epsilon);
}


static gsl_rng *r;  /*static reference to the generator*/
static unsigned long int sd=0; /*static reference to the seed*/


void Seed(unsigned long int s)
{
/*This chooses the generator to be used ("taus")
This is a maximally equidistributed combined Tausworthe generator by L'Ecuyer. The sequence is,

       x_n = (s1_n ^^ s2_n ^^ s3_n)

       where,

       s1_{n+1} = (((s1_n&4294967294)<<12)^^(((s1_n<<13)^^s1_n)>>19))
       s2_{n+1} = (((s2_n&4294967288)<< 4)^^(((s2_n<< 2)^^s2_n)>>25))
       s3_{n+1} = (((s3_n&4294967280)<<17)^^(((s3_n<< 3)^^s3_n)>>11))

       computed modulo 2^32. In the formulas above ^^ denotes "exclusive-or".
       Note that the algorithm relies on the properties of 32-bit unsigned integers and has
       been implemented using a bitmask of 0xFFFFFFFF to make it work on 64 bit machines.

       The period of this generator is 2^88 (about 10^26). It uses 3 words of state per generator.
       For more information see,
              P. L'Ecuyer, "Maximally Equidistributed Combined Tausworthe Generators",
              Mathematics of Computation, 65, 213 (1996), 203--213.*/

/*Allocates space for a generator and sets the seed*/


	r = gsl_rng_alloc(GENERATOR);

        if (s == 0) /*to use a seed taken from the calendar*/
        	sd = (unsigned long int) time(NULL);
	else
        	sd = s;

        gsl_rng_set(r, sd);
}

unsigned long int GetSeed()
{
	return sd;
}


double Un01()  /*Un01() */
{
	return gsl_rng_uniform(r);
}


INLINE double Unab(double a, double b)  /*U(a,b)*/
{
	return a+(b-a)*gsl_rng_uniform(r); /*gsl_rng_flat( r, a, b);*/
}

INLINE unsigned int Un0n(int n) /*Uniform integer [0,n-1]*/
{
	return gsl_rng_uniform_int(r, n);
}

INLINE int Sign() /*random -1 or 1*/
{
	return ((gsl_rng_uniform(r) < 0.5) ? -1 : 1);
}


INLINE double NorSim(double m, double sigma) /*Normal*/
{
	return (m + gsl_ran_gaussian(r, sigma));
}

INLINE double ExpSim(double mu)
{
	 return (gsl_ran_exponential(r, mu));
}

INLINE double GammaSim(double a, double b) /*Gamma: K x^{a-1} e^{-x/b}*/
{
	return gsl_ran_gamma(r, a, b);
}

INLINE double GammaDens(double x, double a, double b) /*Gamma: K x^{a-1} e^{-x/b}*/
{
	return gsl_ran_gamma_pdf(x, a, b);
}



INLINE double BetaSim(double a, double b) { /*Beta: p(x) dx = K x^{a-1} (1-x)^{b-1} dx */
	return gsl_ran_beta ( r, a, b);
}
INLINE double BetaDens(double x, double a, double b) { /*density for beta, as above */
	return gsl_ran_beta_pdf( x, a, b);
}



unsigned int BiSim( double p, int n)
{
	return gsl_ran_binomial ( r, p, n);
}

double LogGamma(double x) /*Logarithm of Gamma special function*/
{
        return gsl_sf_lngamma(x);

}











