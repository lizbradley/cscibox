/*
 *  Matrix.c
 *  
 *
 *  Created by jac on 17/04/2007.
 *  Copyright 2007 __MyCompanyName__. All rights reserved.
 *
 */

#include <stdio.h>
#include <math.h>

#include "Matrix.h"


/*Auxiliary functions*/
//C = A^trA B^trB 
int MatMul(Matrix &C, int trA, Matrix &A, int trB, Matrix &B) {

	CBLAS_TRANSPOSE_t TransA = ((trA == 0) ? CblasNoTrans : CblasTrans); 
	CBLAS_TRANSPOSE_t TransB = ((trB == 0) ? CblasNoTrans : CblasTrans); 

	return gsl_blas_dgemm( TransA, TransB, 1.0, A.Ma(), B.Ma(), 0.0, C.Ma());
}


int MatMul(Matrix &C, Matrix &A, Matrix &B) {

	return gsl_blas_dgemm( CblasNoTrans, CblasNoTrans, 1.0, A.Ma(), B.Ma(), 0.0, C.Ma());
}


/*Cuad. Form C = b^T A b*/
double CuadForm(Matrix &A, Matrix &b) {

	//Make the auxiliar (vector) matrix
	Matrix Aux(A.nRow());
	Matrix res(1);
	
	gsl_blas_dgemm( CblasNoTrans, CblasNoTrans, 1.0, A.Ma(), b.Ma(), 0.0, Aux.Ma());
	gsl_blas_dgemm( CblasTrans,   CblasNoTrans, 1.0, b.Ma(), Aux.Ma(), 0.0, res.Ma());
		
	return res(0);
}
	


int MatMulSym(Matrix &C, Matrix &A, Matrix &B) {

	return gsl_blas_dsymm( CblasLeft, CblasUpper, 1.0, A.Ma(), B.Ma(), 0.0, C.Ma());
}

//inverse of real (symmetric) positive defined matrix
//as a by-product we may obtain the square root of the determinant of A
int InvRPD(Matrix &R, Matrix &A, double *LogDetSqrt, Matrix *ExternChol) {
	
	assert(A.nRow() == A.nCol());  
	assert(R.nRow() == R.nCol());  
	assert(A.nRow() == R.nCol());  

	Matrix *Chol;
	//Make the auxiliar matrix equal to A
	if (ExternChol == NULL)
		Chol = new Matrix( A.nRow(), A.nCol());
	else
		Chol = ExternChol;
	
	R.Iden(); //Make R the identity
	
	Chol->copy(A);

	//Chol->print("A=\n");

	gsl_error_handler_t *hand = gsl_set_error_handler_off ();
	int res = gsl_linalg_cholesky_decomp(Chol->Ma());
	gsl_set_error_handler(hand);
	
	if (res == GSL_EDOM) {
		//printf("Matrix::InvRPD: Warning: Non positive definite matrix.\n"); //exit(0);
		
		return 0;
	}
		
	assert(res != GSL_EDOM); //Check that everything went well
	
	
	//solve for the cannonical vectors to obtain the inverse in R
	for (int i=0; i<R.nRow(); i++)
	{
		//R.print("R=\n");
		gsl_linalg_cholesky_svx( Chol->Ma(), R.AsColVec(i));
	}
	
	if (LogDetSqrt != NULL) {
		*LogDetSqrt = 0.0;
		for (int i=0; i<Chol->nRow(); i++) {
			*LogDetSqrt += log(Chol->ele( i, i)); //multiply the diagonal elements
		}
	}
	
	if (ExternChol == NULL)
		delete Chol;

	return 1;
}


//I have seen problems with this when dest and src are rows or cls of the same matrix
int VecCopy(gsl_vector * dest, const gsl_vector * src) {

	assert(dest->size == src->size);
	
	return gsl_vector_memcpy( dest, src);
}

