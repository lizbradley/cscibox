/******************************************************************************************

 *                      Definition of the twalk class

 *

 *                              cpptwalk-beta-1.1

 *                                Apr 2011

 *

 ********************************************************************************************/








//#include <iostream>

#include <stdlib.h>
#include <string>
#include <time.h>



#include "ranfun.h"


#ifndef TWALK_H
#define TWALK_H


/*These are the parameter settings a_w, a_t and n1, as defined in the paper*/
#define PARAMETER_aw 1.5
#define PARAMETER_at 6.0
/*** Expected number of coordinates to be moved, parameter n_1 ****/
#define EXP_MOV_COOR 4


#define min(x,y) ((x) < (y) ? (x) : (y))


/*Define SAVEACCONLY to save only accepted iterations, when the chain moves.
This is normally done at compile time and not here, see the makefile
#define SAVEACCONLY*/





/********* This part used to be vector.h ************************/


//---------------------------------------------------------------------------
// Creates a vector  
double *vector(int ncols);


//---------------------------------------------------------------------------
// Destroys a vector  
void free_vector(double *cabeza);

//---------------------------------------------------------------------------

void fver_vector(FILE *fptr, double *u, int m);

/*Returns 1 if v = u, component to component*/
int vector_cmp(double *v, double *u, int n);

//copia vector v1 en v2
void cp_vector(double *v1, double *v2, int n);

//---------------------------------------------------------------------------
void resta_vector(double *v1, double *v2, int n, double *res);

/*encuentra el  maximo  ai en valor abs de una vector y devuelve su indice*/
void indice_max_vector(double *v, int n, int &indice, int *phi);
	
int sum(int *v, int n);






/*********** This part used to be obj_fcn.h **********************/

/*Objective function abstract class*/
class obj_fcn {
        private:
                int dim;
        public:

		obj_fcn(int d) {dim  = d;};
		virtual ~obj_fcn() {};
		int get_dim() {return dim;};
		virtual void AccPars(int prime) {};
		virtual void NotAcc(int prime)  {};

		virtual void show_descrip() const = 0;
		virtual int insupport(double *x)  = 0;
		virtual double eval(double *x, int prime)  = 0;
};






/******************* This part used to be kernel.h ***********************/



/*Kernel abstract class*/
class kernel {
        public:
			double *h; //auxiliar vector
			void seth(double *hh) {  h = hh; }
			
			virtual ~kernel() {};

                virtual double *Simh(double *x, double *xp, int n, double  beta, int *phi) = 0;
                virtual double GU(double *h, double *x, double *xp, int n) const = 0;

                double fbeta(double beta, double a);
                double Fbeta(double beta, double a);

};

/* OK <--- -log f_a(beta). It is assumed beta > 0*/
double Ufbeta(double beta, double a);
double Simfbeta( double a);


//----------------------------------- K 0 --------------------------------------
class kernel0: public kernel {
        public:
                virtual double *Simh(double *x, double *xp, int n,double  beta, int *phi);
                virtual double GU(double *h, double *x, double *xp, int n) const;
		~kernel0() {};
};


//----------------------------------- K1 --------------------------------------
class kernel1: public kernel {

        public:
                virtual double *Simh(double *x, double *xp, int n,double  beta, int *phi) ;
                virtual double GU(double *h, double *x, double *xp, int n) const;
		~kernel1() {};
};

//----------------------------------- K 2 --------------------------------------
class kernel2: public kernel {

        public:
                virtual double *Simh(double *x, double *xp, int n,double  beta, int *phi);
                virtual double GU(double *h, double *x, double *xp, int n) const;
		~kernel2() {};
};


//----------------------------------- K 3 --------------------------------------
class kernel3: public kernel {

		private:
			double sigma;

        public:
			double *rest;
			void setrest(double *r) { rest = r; }

                virtual double *Simh(double *x, double *xp, int n,double  beta, int *phi);
                virtual double GU(double *h, double *x, double *xp, int n) const;
		~kernel3() {};
};



//----------------------------------- K 4 --------------------------------------
class kernel4: public kernel {

		private:
			double sigma;

        public:
			double *rest;
			void setrest(double *r) { rest = r; }

                virtual double *Simh(double *x, double *xp, int n,double  beta, int *phi);
                virtual double GU(double *h, double *x, double *xp, int n) const;
		~kernel4() {};
};




/****** This is the old twalk.h **************/


#define  WAIT 30

class twalk {

        private:

		/*Objective function*/

                obj_fcn *Obj;

		
		/*Initial values and the poll of points updated in each iteration*/

                double *x;
                double *xp;
				double U, Up;
				
				double *h;
				double *rest;


		/*Dimension of the objective function domain*/
                int n;                  //x, xp dimension
				
				//parameters needed by methos simulations and one_move
				double acc;            //acceptance counter
				int val;
				kernel *ker;
				double propU, propUp, *y, *yp, dir,  W1, W2, A, aux, beta;
				int *phi;
				double mapU, *mapx;
				

		/*Kernel probabilities, no longer used*/
                //double *krl_probs;     
				
		/* Saving scheme, < 0 only accepeted it., otherwise only it %% abs(save_every) == 0 (1 = all iterations) */
		/* if 0, save all iterations and save the file recacc with kernel acceptance rates etc.  For debugging info*/
		
				 int save_every;
				 int debugg;

		/*Transition kernels*/
		kernel1 k1; kernel2 k2; kernel3 k3; kernel4 k4; kernel0 k0;

				int nphi;
				double pphi;
				

		

		/*Selection between (y,h(x,xp)) and (h(xp,x),yp)*/
	double select_pivot()  {

		double aux = Un01();

        return aux;

	}

	/*Selection between (y,h(x,xp)) and (h(xp,x),yp)*/
	int *select_phi(int *phi)  {

		nphi=0;

		for (int i=0; i<n; i++) 
			if (Un01() < pphi) {
				phi[i] = 1;
				nphi++;
			}
			else
				phi[i] = 0;

		return phi;
	}


        public:
	                                                  /**** not used, for backward compatibility but it doesn't work! ****/
	twalk(obj_fcn &Obj1, double *x1, double *xp1, int n1, double *krl_probs1=NULL) {

        Obj = &Obj1;
        x = x1;
        xp = xp1;
        n = n1;
		
		//all this is not done correctly but it fixes for the moment the memory
		//loss,  I'd like to change it to using Matrix.h
		h = vector(n);
		rest = vector(n);
		 
		k1.seth(h);
		k2.seth(h);
		k3.seth(h);k3.setrest(rest);
		k4.seth(h);k4.setrest(rest);
		
		
		pphi = min( n, EXP_MOV_COOR)/(double) n;
		
		mapx = vector(n);
		y = vector(n);
		yp =vector(n);
		acc = 0.0;
		A = 0.0;
		phi = new int[n];
	}



	~twalk() {
		free_vector(h);
		free_vector(rest);
		free_vector(mapx);
		free_vector(y);
		free_vector(yp);
		delete phi;
	}

		/* select a kernel accordingly with krl_probs */

	kernel *select_kernel(int &val) {

		double aux = Un01();

        kernel *k;


        if(aux<0.0000 )                         //kernel K0, not in use
                { val = 0; return &k0; }

        else if(0.0000 <= aux && aux < 0.0082)    //Kernel K3, hop
                { val = 3; return &k3; }

        else if(0.0082 <= aux && aux < 0.0164)       //kernel K4, blow
                { val = 4; return &k4; }

        else if(0.0164 <= aux && aux <0.5082)        //kernel K1, traverse
                { val = 1; return &k1; }

        else if(0.5082 <= aux && aux < 1.0)       //kernel K2, walk
                { val = 2; return &k2; }

        return k;
	}



    // ----- --- Initialization --- -----
int init(double *xx, double *xxp) {

	if (xx != NULL) {
		cp_vector( xx, x, n);
	}
	
	if (xxp != NULL)
		cp_vector( xxp, xp, n);


	 //initialization

		if(Obj->insupport(x)) {
			U = Obj->eval( x, 0);
			Obj->AccPars(0);
		}
		else {
			printf("twalk: parameters x out of support:\n");
			for (int i=0; i<n; i++)
				printf("%11.6g ", x[i]);

			printf("\n");
			return 0;
		}

		if(Obj->insupport(xp)) {
			Up = Obj->eval( xp, 1);
			Obj->AccPars(1);
		}
		else {
			printf("twalk: parameters xp out of support.\n");
			for (int i=0; i<n; i++)
				printf("%11.6g ", xp[i]);

			printf("\n");
			return 0;
		}
	
		mapU = U;
		cp_vector(x, mapx, n);

		propU = U;
		propUp = Up;

		cp_vector(x,y,n);
		cp_vector(xp,yp,n);


//For backward compatibility
#ifdef SAVEACCONLY
		save_every = (int) -1;
#endif
	
		return 1;
}

int one_move() {


		/* Selection of the pivot and transition kernel*/	


                ker = select_kernel(val);
                dir = select_pivot();
				select_phi(phi);


				if(dir<0.5) {                   // x is the pivot

		

			/* Beta is a dummy parameter in the kernel 0, 1, 3, 4 and 5 cases*/	
					beta = Simfbeta(PARAMETER_at);

			/* yp is the proposal*/

					cp_vector( ker->Simh( xp, x, n, beta, phi), yp, n);
					cp_vector( x, y, n);
					propU = U;
					

			/* Verifying that the proposal is in the obj function domain */

					if(Obj->insupport(yp)) {

			
				/*Evaluating the obj function in the proposal */	

						propUp = Obj->eval( yp, 1);
						

				/*Computing the acceptance probability */

						W1 = ker->GU(yp,xp,x,n);
						W2 = ker->GU(xp,yp,x,n);

						if(W1==-1 || W2==-1)
							A = 0.0;
						else if(W1==-2 && W2==-2)
								A = exp((U-propU)+(Up-propUp)+(nphi-2)*log(beta));
							else
								A = exp((U-propU)+(Up-propUp)+(W1-W2));

					}
					else
						A = 0.0;

                }
				else {                           // xp is the pivot

		/* Repeating the procedure above  but using xp as pivot*/

			
					beta = Simfbeta(PARAMETER_at);
					cp_vector( ker->Simh( x, xp, n, beta, phi), y, n);
					cp_vector( xp, yp, n);
					propUp = Up;

					if(Obj->insupport(y)) {

						propU = Obj->eval( y, 0);


						W1 = ker->GU(y,x,xp,n);
						W2 = ker->GU(x,y,xp,n);

						if(W1==-1 || W2==-1)
							A = 0.0;
						else if(W1==-2 && W2==-2)
								A = exp((U-propU)+(Up-propUp)+(nphi-2)*log(beta));
							  else
								A = exp((U-propU)+(Up-propUp)+(W1-W2));
                        }
                        else
							A = 0.0;

                }

 

				aux = Un01();
                if( aux < A ) {            //Accepted

						acc += nphi/(double) n; //proportion of moved parameters
						
						cp_vector(y,x,n);
                        U = propU;

						cp_vector(yp,xp,n);
                        Up = propUp;

						

						if (dir >= 0.5) {
						 //y is accepted
							Obj->AccPars(0);

							if (fcmp( U, mapU) == -1) { //U < mapU
								mapU = U;
								cp_vector( x, mapx, n);
							}
							
							return 1; //y accepted
						}
						else {//yp is accepted

							Obj->AccPars(1);
							
							return -1; //yp accepted
						}
						
						

                }
				else {

					if (dir >= 0.5) //y is not accepted
						Obj->NotAcc(0);
					else //yp is not accepted
						Obj->NotAcc(1);
					
					return 0;
				}


}



/***  backwards compatibility !!!!!!!!!!! ***/
int simulation(int Tr1, char *filename, char *op="wt") {

	simulation( Tr1, filename, op="wt", (int) 0, NULL, NULL);
}

/* Here is the implementation of the central part of the algorithm */
int simulation(int Tr1, char *filename, char *op="wt", int save_every1=1, double *xx=NULL, double *xxp=NULL, int silent=0) {

	
	FILE *fptr;
	FILE *recacc;

		
	long sec=time(NULL); //beging of the twalk
	if (silent == 0)
		printf("twalk: %10d iterations to run, %s", Tr1, ctime(&sec));


    // ----- --- Initialization --- -----

	if (init( xx, xxp) == 0)
		exit(0);

	//send an estimation for the duration of the sampling if 
	//evaluating the ob. func. twice takes more than one second

	long sec2=time(NULL); //last time we sent a message
	if (silent == 0) {
		printf("       ");
		Remain( Tr1, 2, sec, sec2);
	}



	save_every = save_every1;
		
	if (save_every == 0) {
		save_every = 1;
		debugg = 1;
	}
	else
		debugg = 0;

	
	if (debugg) {
		if ((recacc = fopen("recacc.dat", "w")) == NULL) {
	
			fprintf( stderr, "Could not open file %s for writing\n", "recacc.dat");
		
			exit(0);
		}
		
		printf("twalk: Kernel acceptance rates information to be saved in file  recacc.dat\n");
	}



    // ----- --- -------------- --- -----
    if ((fptr = (fopen(filename, op)))) { 

		fver_vector(fptr, x, n);
        fprintf(fptr, "\t %lf", U);
		
		if (silent == 0)
			if (save_every < 0)
				printf("twalk thinning: 1 out of every %d accepted iterations will be saved in file %s\n", abs(save_every), filename);
			else
				printf("twalk: All %d iterations to be saved in file %s\n", save_every, filename);
		

    

		int j1=1, j=0, rt;
		long ax;
		int acc_it=0;
		

        for(int it=1; it<=Tr1; it++) {  
				
				rt = one_move();
				
				if ((rt == 1) || (rt == -1)) {
						acc_it++;
						if (save_every < 0) //Only accepted iterations are saved
							if ((acc_it % abs(save_every)) == 0) {
								fver_vector(fptr, x, n);
								fprintf(fptr, "\t %13.6g", U);
							}
						if (debugg)			
							fprintf( recacc, "%d %f\n", val, nphi/(double) n);
				}
				else //Propolsal not accepted
					if (debugg)
						fprintf( recacc, "%d %f\n", val, 0.0);
					

#ifdef FLUSHEVERYIT
				fflush(fptr);
#endif

				if (save_every > 0) //accepetd or not acc. iterations are saved
					if ((it % save_every) == 0) {
						fver_vector(fptr, x, n);
						fprintf(fptr, "\t %13.6g", U);
					}


				if ((it % (1 << j1)) == 0) {

					j1++;
					j1 = min( j1, 10); //check the time at least every 2^10=1024 iterations
					if (((ax=time(NULL)) - sec2) > (1 << j)*WAIT)
					{
						if (silent == 0) {
							printf("twalk: %10d iterations so far. ", it);
							Remain( Tr1, it, sec, ax);
						}
						sec2 = ax;
						j++;
						j1--; //check the time as often 
					}
				}

        }

		fclose(fptr);

#ifdef DEBUGG
		fclose(recacc);
#endif

	//leave the MAP	estimator: WARNING, it could be the same as x!

	/*cp_vector( mapx, xp, n);
	Obj->insupport(xp);
	Up = Obj->eval( xp, 1);	

	printf("maxU= %f, Up= %f, MAP:", mapU, Up);
	fver_vector( stdout, mapx, n);
	printf("\n");
	delete mapx;



		fver_vector(fptr, xp, n);

		fprintf(fptr, "\t %13.6g", Up);

        fclose(fptr);*/

		

		//return current points

		if (xx != NULL)
			cp_vector( x, xx, n);

		if (xxp != NULL)
			cp_vector( xp, xxp, n);


		sec = time(NULL);
		if (silent == 0)
			printf("twalk: Finished, %4.1f%% of moved pars per iteration, ratio (%f/%d). Output in file %s,\n      %s\n",
				 100.0*(acc/(double) Tr1), acc, Tr1, filename, ctime(&sec));
			
        return (int) rint(acc);

    }
    else
        return -1;

}


//Information messages
//total it, current it, start time, current time
void Remain(int Tr, int it, long sec1, long sec2) {

	long ax =  //how many seconds remaining

	(long) ( (Tr - it) *  ((sec2 - sec1)/(double) it) );


	if (ax == 0) {

		printf("\n");
		fflush(stdout);
		return;
	}

	if (ax < 60) {

		printf("Will finish in approx. %ld seconds.\n", ax);
		fflush(stdout);
		return;
	}

	if (ax <= 360) {

		printf("Will finish in approx. %ld minutes and %ld seconds.\n",
			ax/60, ax % 60);
		fflush(stdout);
		return;
	}

	if (ax > 360) {

		ax += sec2;  //current time plus seconds remaining=end time
		printf("Will finish in %s", ctime(&ax));
		fflush(stdout);
		return;
	}
}


		

};



#endif























