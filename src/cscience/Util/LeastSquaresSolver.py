"""
LeastSquaresSolver.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import math

class LeastSquaresSolver(object):
    """A dense matrix linear least squares solver.
    
    The problem is to find an x which minimizes the Euclidean norm || A * x - b
    ||, where A is an m by n matrix and b is a vector in R<sup>m</sup>.

    Author Marek Rychlik (rychlik@u.arizona.edu)

    Translated into Python by Ken Anderson (kena@cs.colorado.edu)
    """

    #  param a: a number.
    #  param b: the number determining the sign of the result.
    #  returns a number equal in magnitude to the first argument, whose sign is that of the second argument.
    def copySign(self, a, b):
        if b >= 0.0:
            return abs(a)
        else:
            return -abs(a)

    #  Square a number carefully.
    #
    #  param a: a number
    #  returns the value of a squared.
    def square(self, a):
        # This is most likely not needed in correctly implemented Java
        # Note: not sure if this is needed in python...
        #     : going to leave it in for now
        if a == 0.0:
            return 0.0
        else:
            return a * a

    #  The qrdcmp method finds the QR decomposition of a matrix A, which is not
    #  assumed to be square, but m x n. We do it by a slight modification of the algorithm of
    #  Numerical Recipes in C. Thus 
    #
    #                R = Q_n-1 * Q_n-2 * Q_n-2 * ... * Q_0 * A
    #
    #  where:
    #
    #                Q_j are Housholder matrices Q_j = I - u_j * u_j T c_j.
    #
    #  The vectors u_j are stored in columns of A on and below the main diagonal.
    #  
    #  The diagonal entries of R are stored in d[n].
    #
    #  This code is an adaptation of the code in Numerical Recipes, but the
    #  "optimization" was removed which prevents the code from working when the number of equations
    #  exceeds the number of unknowns.
    # 
    #  param a: Array holding the matrix A
    #  param c: Array holding the coefficients c_j
    #  param d: Array to hold the diagonal of R
    #  return true if the columns of a are linearly dependent, false otherwise
    def qrdcmp(self, m, n, a, c, d):
        sing = False
        
        for k in range(n):
            scale = 0.0
            for i in range(k, n):
                scale = max(scale, abs(a[i][k]))
            if scale == 0.0:
                sing = True
                c[k] = 0.0
                d[k] = 0.0
            else:
                for i in range(k, m):
                    a[i][k] /= scale
                total = 0.0
                for i in range(k, m):
                    total += self.square(a[i][k])
                sigma = self.copySign(math.sqrt(total), a[k][k])
                a[k][k] += sigma
                # Norm of the k-th column magically appears to be this:
                c[k] = sigma * a[k][k]
                d[k] = -scale * sigma
                # Find (I - 2 * a[k] * a[k]^T) * a[j]
                for j in range(k + 1, n):
                    total = 0.0
                    for i in range(k, m):
                        total += a[i][k] * a[i][j]
                    tau = total / c[k]
                    for i in range(k, m):
                        a[i][j] -= tau * a[i][k]
        return sing

    #  The qrsolv method solves the equation A * x = b by least squares. The matrix a
    #  is assumed to be transformed by qrdcmp and c and d are returned by that
    #  algorithm.
    #  
    #  param a: array holding A
    #  param c: array holding C
    #  param d: array holding d, the diagonal of R - the upper-triangular part of A
    #  param b: array holding B
    
    def qrsolv(self, m, n, a, c, d, b):
        # set b to Q^t*b
        for j in range(n):
            # Apply the j-th Housholder transformation I - 2 * a[j] * a[j]^T to b
            total = 0.0
            for i in range(j, m):
                total += a[i][j] * b[i]
            # Now total = a[j]^T * b, which is a number
            tau = total / c[j]
            for i in range(j, m):
                b[i] -= tau * a[i][j]
        # Solve R * x = b and set b := x
        self.rsolv(n, a, d, b);
        
    # The rsolv method solves R * x = b, where R is upper-triangular. R is stored in
    # the upper-triangular part of a matrix a, with the exception of the diagonal
    # entries, which are stored in d
    #
    # param a: The coefficient matrix preprocessed with qrdcmp
    # param d: The diagonal of R returned by qrdcmp
    # param b: The vector b returned by qrsolv, equal
    # to Q^T * b, where b is the original vector of right-hand sides.
    def rsolv(self, n, a, d, b):
        b[n - 1] /= d[n - 1]
        for i in range(n - 2, -1, -1):
            total = b[i]
            for j in range(i + 1, n):
                total -= a[i][j] * b[j]
            b[i] = total / d[i]

    #  Solves least squares problem: Give x which minimizes || A * x - b ||. In the process, the
    #  matrix A is replaced with the QR decomposition of A, (the Hessenberg version). The solution
    #  is deposited in the first n entries of b. It is assumed that A has at least as many rows and
    #  columns.
    # 
    #  param m: The number of equations
    #  param n: The number of unknowns
    #  param a: The coefficient matrix
    #  param b: The right-hand side
    #  returns true if singular, false otherwise
    def solve(self, m, n, a, b):
        c = []
        d = []
        for i in range(n):
            c.append(0.0)
            d.append(0.0)
        
        if self.qrdcmp(m, n, a, c, d):
            return True
        self.qrsolv(m, n, a, c, d, b)
        return False

# vim: ts=4:sw=4:et
