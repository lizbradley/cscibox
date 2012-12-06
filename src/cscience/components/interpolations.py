from cscience import components

class Cubic(components.BaseComponent):
    def __call__(self, samples):
        samples['interpolation curve'] = None

components.library['Cubic blah blah blah (user)'] = Cubic

#The following Method taken from Burden's book 
#cubic interpolation notes:
# eqn: 
# ith piece of the spline is Yi(t)=a_i + b_i*t + c_i*t^2 +d_i*t^3, t in [0,1], i in(0,n-1) = natural
# then
# Y_i(0) = y_i = a_i 
# Y_i(1) = y_i+1 = a_i + b_i + c_i + d_i
# Take the derivative
# Y_i'(0) = D_i = b_i
# Y_i'(1) = D_i+1 = b_i + 2*c_i + + 3*d_i
# Solve all of these for a,b,c,d to get a matrix form
# a_i = y_i
# b_i = D_i
# c_i = 3*(y_i+1 - y_i) - 2*D_i - D_i+1
# d_i = 2*(y_i - y_i+1) + D_i + D_i+1
# Require the 2nd derivs match at the x's
# Y_i-1(1) = y_i
# Y_i+1'(1) = Y_i'(0)
# Y_i(0) = y_i
# Y_i-1''(1) = Y_i''(0)
# Endpoints satisfy:
# Y_o(0) = y_o
# Y_n-1(1) =y_n
# We now have 4*n-2 eqns, for 4n unks., so require:
# Y_o''(0) = 0
# Y_n-1''(1) = 0

# We can now arrange all of this into a nice tridiagonal-sparse matrix
# [1 2, 1 4 1, 1 4 1, ... , 2 1][D_o, D_1, .. , D_n] = [3*(y_1 - y_o), .. , 3*(y_n - y_n-1)]

#PLOT THIS!

# TO-DO:
# Read in data, assign to vectors
# Determine the a,b,c,d parameters

# Function vars: n = len of the data set - 1, x = is the vector of x-values from the data,
# 
#def CubicSpline(n,x,a,xd):
    # initiate the vectors for c, d & k using python zeros
    
    # k_i-1(x_i-1 - x_i) + (2*k_i(x_i-1 - x_i+1) + k_i(x_i - x_i+1) =
    # 6*(fraction)
    # c = (x_i-1 - x_i)
    # d = (x_i-1 - x_i+1)*2
    # k = fraction
    
    # need some zero vectors...
def zeroVector(m):
    z = [0]*m
    return(z)

 #INPUT: n = number of intervals; xn = x-vars; a = y-vals at x-vals.
def cubic_spline(n, xn, a, xd):      

# initiate the h vector
    h = zeroVector(n-1)

    # alpha will be values in a system of eq's that will allow us to solve for c
    # and then from there we can find b, d through substitution.
    alpha = zeroVector(n-1)

    # l, u, z are used in the method for solving the linear system
    l = zeroVector(n+1)
    u = zeroVector(n)
    z = zeroVector(n+1)

    # b, c, d will be the coefficients along with a.
    b = zeroVector(n)     
    c = zeroVector(n+1)
    d = zeroVector(n)    

# style from book
for i in range(n-1):
    # h[i] is used to satisfy the condition that 
    # Si+1(xi+l) = Si(xi+l) for each i = 0,..,n-1
    # i.e., the values at the knots are "doubled up"
    h[i] = xn[i+1]-xn[i]  

for i in range(1, n-1):
    # Sets up the linear system and allows us to find c.  Once we have 
    # c then b and d follow in terms of it.
    alpha[i] = (3./h[i])*(a[i+1]-a[i])-(3./h[i-1])*(a[i] - a[i-1])

# the l,u &z vectors give us our tridiagonal matrix 
l[0] = 1      
u[0] = 0      
z[0] = 0

for i in range(1, n-1):
    l[i] = 2*(xn[i+1] - xn[i-1]) - h[i-1]*u[i-1]
    u[i] = h[i]/l[i]
    z[i] = (alpha[i] - h[i-1]*z[i-1])/l[i]

l[n] = 1
z[n] = 0
c[n] = 0

# finds b, d in terms of c.
for j in range(n-2, -1, -1):      
    c[j] = z[j] - u[j]*c[j+1]
    b[j] = (a[j+1] - a[j])/h[j] - h[j]*(c[j+1] + 2*c[j])/3.
    d[j] = (c[j+1] - c[j])/(3*h[j])   

#return the coeficients

#stuff