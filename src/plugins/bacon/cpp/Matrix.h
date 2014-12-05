/* Original simple matrix class taken from http://www.algarcia.org/nummeth/Cpp/Matrix.h */

#ifndef MATRIX_H
#define MATRIX_H

#include <assert.h>  // Defines the assert function.
//#define assert(x) {} //to avoid bound checking
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_blas.h>
#include <gsl/gsl_linalg.h>
#include <gsl/gsl_errno.h>

#include <string.h>
#include <stdio.h>

#define BUFF_SIZE 4096

class Matrix {

public:

// Default Constructor. Creates a 1 by 1 matrix; sets value to zero. 
Matrix () {
  ma = gsl_matrix_alloc( 1, 1);// Allocate memory
  ve.owner = 0;
  ve.block = ma->block;
  set(0.0);                // Set value of data_[0] to 0.0
  
  header = NULL;
}

// Regular Constructor. Creates an nR by nC matrix; sets values to zero.
// If number of columns is not specified, it is set to 1.
Matrix(int nR, int nC = 1, char *head=NULL) {
  assert(nR > 0 && nC > 0);    // Check that nC and nR both > 0.
  ma = gsl_matrix_alloc( nR, nC);// Allocate memory
  ve.owner = 0;
  ve.block = ma->block;
  set(0.0);                    // Set values of data_[] to 0.0

  if (head != NULL)
	header = strdup(head);
  else
	header = NULL;
}


//copy constructor
Matrix(Matrix &mat)  {
printf("Matrix::Matrix 2 ...\n");
  ma = gsl_matrix_alloc( mat.nRow(), mat.nCol());// Allocate memory
  ve.owner = 0;
  ve.block = ma->block;
  copy(mat);
  
  if (mat.Header() != NULL)
	header = strdup(mat.Header());
  else
	header = NULL;
  
}

//Identity (preferably square) matrix
void Iden() {
  //assert(nRow() == nCol());    // Check that square matrix.
  set(0.0);                    // Set values of data_[] to 0.0
  for (int i=0; i<nRow(); i++)
	ma->data[ (ma->tda)*i + i] = 1.0;
}



// Destructor. Called when a Matrix object goes out of scope or deleted.
~Matrix() {
	//printf("Matrix::~Matrix\n");
	if (ma != NULL)
		  gsl_matrix_free(ma);   // Release allocated memory
	if (header != NULL) {
		free(header);
	}
}



// Assignment operator function.
// Overloads the equal sign operator to work with
// Matrix objects.
Matrix& operator=(const Matrix& mat) {
  if( this == &mat ) return *this;  // If two sides equal, do nothing.
  this->copy(mat);                  // Copy right hand side to l.h.s.
  return *this;
}

// += operator function.
// Overloads the += sign operator to work with
// Matrix objects.
Matrix& operator+=(const Matrix& mat) {
  gsl_matrix_add( this->ma, mat.ma);        
  return *this;
}

// -= operator function.
// Overloads the -= sign operator to work with
// Matrix objects.
Matrix& operator-=(const Matrix& mat) {
  gsl_matrix_sub( this->ma, mat.ma);        
  return *this;
}

// *= operator function.
// Overloads the *= sign operator to work with
// Matrix objects.
Matrix& operator*=(const double a) {
  gsl_matrix_scale( this->ma, a);        
  return *this;
}





// Set function. Sets all elements of a matrix to a given value.
void set(double value) {
   gsl_matrix_set_all( ma, value);
}

/*// Set function. Sets all elements of a matrix to a given value.
void eval(double value, double (*fct)(double x)) {
   to be done
}*/


//info
// Simple "get" functions. Return number of rows or columns.
int nRow() const { return ma->size1; }
int nCol() const { return ma->size2; }

//min and max
double Max() { gsl_matrix_max(ma); }
double Min() { gsl_matrix_min(ma); }


// Parenthesis operator function.
// Allows access to values of Matrix via (i,j) pair.
// Example: a(1,1) = 2*b(2,3); 
// If column is unspecified, take as 1.
double& operator() (int i, int j = 0) {
  assert(i >= 0 && i < ma->size1);          // Bounds checking for rows
  assert(j >= 0 && j < ma->size2);          // Bounds checking for columns
  return ma->data[ (ma->tda)*i + j];  // Access appropriate value
}

// Parenthesis operator function (const version).
const double& operator() (int i, int j = 0) const{
  assert(i >= 0 && i < ma->size1);          // Bounds checking for rows
  assert(j >= 0 && j < ma->size2);          // Bounds checking for columns
  return ma->data[(ma->tda)*i + j];  // Access appropriate value
}

// Allows access to values of Matrix via ele(i,j) pair.
// If column is unspecified, take as 1.
double ele(int i, int j = 0) {
  assert(i >= 0 && i < ma->size1);          // Bounds checking for rows
  assert(j >= 0 && j < ma->size2);          // Bounds checking for columns
  return ma->data[ (ma->tda)*i + j];  // Access appropriate value
}




//i/o
//Print function
void print( FILE *F, char *name=NULL, int fw=11, int pres=4, char *sep=" ", int rownums=0, int colnums=0)
{
	if (name == NULL)
		if (header == NULL)
			fprintf( F, "\n");
		else
			fprintf( F, "%s\n", header);
	else
		fprintf( F, "%s", name);
	for (int i=0; i<ma->size1; i++)
	{
		if ((i == 0) && (colnums)) {
			fprintf( F, "%*s%s", fw, "", sep);
			for (int j=0; j<ma->size2; j++)
				fprintf( F, "%*d%s", fw, j, sep);
			fprintf(F, "\n");
		}
		for (int j=0; j<ma->size2; j++) {
			if ((j == 0) && (rownums))
				fprintf( F, "%3d%s", i, sep);
			fprintf( F, "%*.*g%s", fw, pres, ele(i,j), sep);
		}
		fprintf( F, "\n");
	}
}
void print(char *name=NULL) { print( stdout, name, 11, 4, " ", 0, 0); }
void printnums(char *name=NULL) { print( stdout, name, 11, 4, " ", 1, 1); }

void fileprint(char *fnam) {
	FILE *F;
	
	if ((F = fopen( fnam, "w+")) == NULL)
	{
		printf( "Could not open file %s for writing\n", fnam);

		assert(F == NULL);
	}
	else
	{
		print( F, NULL, 11, 4, " ");
	
		fclose(F);
	}
}

void printrow(int i) {
	assert(i < nRow());
	
	for (int j=0; j<ma->size2; j++) {
		printf( "%*.*g%s", 11, 4, ele(i,j), " ");
	}
	printf( "\n");
}

int filescan(char *fnam, int file_header=0) {
	FILE *F;
	
	if ((F = fopen( fnam, "r")) == NULL)
	{
		printf( "File %s not found\n", fnam);

		return 0;
	}
	else
	{
		if (file_header == 1) {
			header = (char *) malloc((size_t) BUFF_SIZE);

			header = fgets( header, (size_t) BUFF_SIZE, F);
			header[strlen(header)-1] = '\0'; //remove the \n
		}
		
		gsl_matrix_fscanf( F, ma);
	
		fclose(F);
		return 1;
	}
}

/*********************** Views *********************/
//Get the gsl matrix
gsl_matrix *Ma() { return ma; }


//Column gsl Vector
gsl_vector *AsColVec(int Col)   {
	assert(Col >= 0 && Col < ma->size2);          // Bounds checking for columns
	ve.size = ma->size1;
	ve.stride = ma->tda;
	ve.data = ma->data + Col;
	
	return &ve;
}
//First column is the defalut
gsl_vector *Ve()   { 
	ve.size = ma->size1;
	ve.stride = ma->tda;
	ve.data = ma->data;
	
	return &ve;
}


//Row Vector
gsl_vector *AsRowVec(int Row, int ChopOff=0)   {
	assert(Row >= 0 && Row < ma->size1);          // Bounds checking for rows
	ve.size = ma->size2-ChopOff;
	ve.stride = 1;
	ve.data = ma->data + (ma->tda)*Row;
	
	return &ve;
}



// Copy function.
// Copies values from one Matrix object to another.
void Copy(const Matrix *mat) {

	assert((nRow() == mat->nRow()) && (nCol() == mat->nCol()));
    gsl_matrix_memcpy( ma, mat->ma);
}

// Copy function.
// Copies values from one Matrix object to another.
void copy(const Matrix& mat) {
    gsl_matrix_memcpy( ma, mat.ma);	
}


const char *Header() { return header; }

//*********************************************************************
protected:

// Matrix data.
gsl_matrix *ma;
gsl_vector ve;

char *header;


}; // Class Matrix








class SubMatrix : public Matrix {

private:
	gsl_matrix_view view;
	Matrix *Parent;
	
public:
	SubMatrix(Matrix &mat, size_t k1, size_t k2, size_t n1, size_t n2) {
		view = gsl_matrix_submatrix ( mat.Ma(), k1, k2, n1, n2);
		ma = &view.matrix;
		Parent = &mat;
		if (mat.Header() != NULL)
			header = strdup(mat.Header());
		else
			header = NULL;
	}
	
	SubMatrix( Matrix& mat, size_t n1, size_t n2) {
		view = gsl_matrix_submatrix ( mat.Ma(), (size_t) 0, (size_t) 0, n1, n2);
		ma = &view.matrix;
		Parent = &mat;
		if (mat.Header() != NULL)
			header = strdup(mat.Header());
		else
			header = NULL;
	}

	SubMatrix() {
	//delay the opening of this submatrix
		ma = NULL;
		Parent = NULL;
		header = NULL;
	}
	
	~SubMatrix() { 
		ma = NULL; //we avoid the base class call to free with this
		if (header != NULL) {
			free(header);
			header=NULL;
		}

	}
	
	void Set(Matrix *mat, size_t k1, size_t k2, size_t n1, size_t n2) {
		view = gsl_matrix_submatrix ( mat->Ma(), k1, k2, n1, n2);
		ma = &view.matrix;
		Parent = mat;
		if (mat->Header() == NULL)
			header = NULL;
		else
			header = strdup(mat->Header());
	}
	
	const char *SetHeader(char *head) {
		if (header != NULL)
			free(header);
		header == NULL;
		if (head != NULL)
			header = strdup(head);
		return header;
	}
	

// Assignment operator function.
// Overloads the equal sign operator to work with
// Matrix objects.
SubMatrix& operator=(const SubMatrix& mat) {
  if( this == &mat ) return *this;  // If two sides equal, do nothing.
  this->copy(mat);                  // Copy right hand side to l.h.s.
  return *this;
}

// += operator function.
// Overloads the += sign operator to work with
// Matrix objects.
SubMatrix& operator+=(const SubMatrix& mat) {
  gsl_matrix_add( this->ma, mat.ma);        
  return *this;
}

// -= operator function.
// Overloads the -= sign operator to work with
// Matrix objects.
SubMatrix& operator-=(const SubMatrix& mat) {
  gsl_matrix_sub( this->ma, mat.ma);        
  return *this;
}

// *= operator function.
// Overloads the *= sign operator to work with
// Matrix objects.
SubMatrix& operator*=(const double a) {
  gsl_matrix_scale( this->ma, a);        
  return *this;
}



	void Set( Matrix *mat, size_t n1, size_t n2) {
		view = gsl_matrix_submatrix ( mat->Ma(), (size_t) 0, (size_t) 0, n1, n2);
		ma = &view.matrix;
		Parent = mat;
	}

	
	void ReSize(size_t k1, size_t k2, size_t n1, size_t n2) {
		view = gsl_matrix_submatrix( Parent->Ma(), k1, k2, n1, n2);
		ma = &view.matrix;
	}
	
	void ReSize(size_t n1, size_t n2) {
		view = gsl_matrix_submatrix ( Parent->Ma(), (size_t) 0, (size_t) 0, n1, n2);
		ma = &view.matrix;
	}
	
};



/*Auxiliary functions*/
//C = A^trA B^trB 
int MatMul(Matrix &C, int trA, Matrix &A, int trB, Matrix &B);
int MatMul(Matrix &C, Matrix &A, Matrix &B);
double CuadForm(Matrix &A, Matrix &b);
int MatMulSym(Matrix &C, Matrix &A, Matrix &B);
//inverse of real (symetric) positive defined matrix
//as a by product we may obtain the square root of the determinat of A
int InvRPD(Matrix &R, Matrix &A, double *LogDetSqrt=NULL, Matrix *ExternChol=NULL);
//I have seen problems with this when dest and src are rows or cls of the same matrix
int VecCopy(gsl_vector * dest, const gsl_vector * src);



#endif

