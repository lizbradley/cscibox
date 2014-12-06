/*
 *  kernel.c
 *  
 *
 *  Created by jac on 29/04/2009.
 *
 */

#include "twalk.h"


/*OK <--- f_a(beta), a is a parameter */
double kernel::fbeta(double beta, double a) {
        double b = 0;

        if(0<=beta && beta<1.0)
                b = pow(beta, a);

        if(beta>1)
                b = pow(1.0/beta, a);

        return ((a-1.0)*(a+1.0)/(2.0*a)*b);
}

/* OK <--- -log f_a(beta). It is assumed that beta > 0*/
double Ufbeta(double beta, double a) {
        double b = 0;
        if(beta < 1)
                b = -a *log(beta);
        if(beta>=1)
                b = a * log(beta);

        return (-log(a-1.0)-log(a+1.0)+log(2.0*a)+b);
}

/* OK */
double kernel::Fbeta(double beta, double a) {
        double b1 = 0.0; double b2 = 0.0;
        if(0<=beta && beta <=1)
                b1 = (a-1.0)/(2.0*a)*pow(beta,a+1.0);

        if(beta>1) {
                b1 = (a-1.0)/(2.0*a);
                b2 = (a+1.0)/(2.0*a)*(1-pow(1.0/beta, a-1.0));
        }

        return b1 + b2;
}

double Simfbeta( double a) {

        if(  Un01()< (a-1.0)/(2.0*a) )
                return (exp(1.0/(a+1.0)*log(Un01())));
        else
                return (exp(1.0/(1.0-a)*log(Un01())));

}


//----------------------------------- K 0 --------------------------------------
double *kernel0::Simh(double *x, double *xp, int n,double  beta, int *phi) {

        return x;
}

double kernel0::GU(double *h, double *x, double *xp, int n) const {
        if(vector_cmp(h,x,n))
                return 1.0;
        else
                return 0.0;
}


//----------------------------------- K1 traverse----------------------------
double *kernel1::Simh(double *x, double *xp, int n, double  beta, int *phi) {

        //double *h = vector(n);

        for(int i=0; i<n; i++)
			if (phi[i] == 1)
                h[i] = xp[i] + beta * (xp[i]-x[i]);
			else
				h[i] = x[i];

        return h;
}

double kernel1::GU(double *h, double *x, double *xp, int n) const {
	
	return -2;
}


//----------------------------------- K 2 --------------------------------------
//This is parameter aw in the paper
double Phi2Sim(double aw) {
	
	double u = Un01();
	return ((aw/(1.0+aw))*(-1.0+2.0*u+aw*u*u));
}

double *kernel2::Simh(double *x, double *xp, int n,double  beta, int *phi) {
        
	//double *h = vector(n);

        for(int i=0; i<n; i++) {
                h[i] = x[i] + phi[i]*(x[i]-xp[i])*Phi2Sim(PARAMETER_aw);
        }
        
	return h;
}

double kernel2::GU(double *h, double *x, double *xp, int n) const {
	return 1.0;
}


//----------------------------------- K 3 --------------------------------------
double *kernel3::Simh(double *x, double *xp, int n,double  beta, int *phi)  {

		//double *h = vector(n);

        //double *rest = vector(n);

        int i;

        resta_vector(xp,x,n,rest);
        indice_max_vector(rest, n, i, phi);

        sigma = fabs(rest[i])/3.0;

        for(int j=0; j<n; j++)
                h[j] = x[j] + phi[j] * sigma * NorSim(0,1.0);

		//free_vector(rest);
        return h;
}

double kernel3::GU(double *h, double *x, double *xp, int n) const {

        if(!vector_cmp(x,xp,2)) {

				int i;


                double intProd = 0.0;

                for(int j=0; j<n; j++)
                        intProd += (h[j]-xp[j])*(h[j]-xp[j]);

				//it is assumed that Simh is just called and we have the correct sigma
                return ((n/2)*log(2.0*M_PI) + n*log(sigma) + 0.5*(1/(sigma*sigma))*intProd);
        }		
        else return -1;
}


//----------------------------------- K 4 --------------------------------------
double *kernel4::Simh(double *x, double *xp, int n,double  beta, int *phi)  {

        //double *rest = vector(n);
        //double *h = vector(n);
        int i;

        resta_vector(xp,x,n,rest);
        indice_max_vector(rest, n, i, phi);

        sigma = fabs(rest[i]);

        for(int j=0; j<n; j++)
			if (phi[j] == 1)
                h[j] = xp[j] + sigma * NorSim(0,1.0);
			else
				h[j] = x[j];

		//free_vector(rest);
        return h;
}

double kernel4::GU(double *h, double *x, double *xp, int n) const {

        int i;



        double intProd = 0.0;

        for(int j=0; j<n; j++)
                intProd += (h[j]-xp[j])*(h[j]-xp[j]);

		//it is assumed that Simh is just called and we have the correct sigma
        return ((n/2)*log(2.0*M_PI) + n*log(sigma) + 0.5*(1/(sigma*sigma))*intProd);
}
