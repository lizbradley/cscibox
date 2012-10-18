"""
GammaStats.py

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

def gammq(a, x):
    """Incomplete gamma function."""
    if (x < 0. or a <= 0.):
        raise ValueError, repr((a, x))
    if (x < a + 1.):
        return 1. - gser(a, x)[0]
    else:
        return gcf(a, x)[0]

def gser(a, x, itmax=700, eps=3.e-7):
    """Series approx'n to the incomplete gamma function."""
    gln = gammln(a)
    if (x < 0.):
            raise bad_arg, x
    if (x == 0.):
            return(0.)
    ap = a
    sum = 1. / a
    delta = sum
    n = 1
    while n <= itmax:
            ap = ap + 1.
            delta = delta * x / ap
            sum = sum + delta
            if (abs(delta) < abs(sum) * eps):
                    return (sum * math.exp(-x + a * math.log(x) - gln), gln)
            n = n + 1
    raise max_iters, str((abs(delta), abs(sum) * eps))

def gammln(xx):
    """Logarithm of the gamma function."""
    global gammln_cof, gammln_stp
    gammln_cof = [76.18009173, -86.50532033, 24.01409822, -1.231739516e0, 0.120858003e-2, -0.536382e-5]
    gammln_stp = 2.50662827465
    x = xx - 1.
    tmp = x + 5.5
    tmp = (x + 0.5) * math.log(tmp) - tmp
    ser = 1.
    for j in range(6):
            x = x + 1.
            ser = ser + gammln_cof[j] / x
    return tmp + math.log(gammln_stp * ser)

def gcf(a, x, itmax=200, eps=3.e-7):
    """Continued fraction approx'n of the incomplete gamma function."""
    gln = gammln(a)
    gold = 0.
    a0 = 1.
    a1 = x
    b0 = 0.
    b1 = 1.
    fac = 1.
    n = 1
    while n <= itmax:
            an = n
            ana = an - a
            a0 = (a1 + a0 * ana) * fac
            b0 = (b1 + b0 * ana) * fac
            anf = an * fac
            a1 = x * a0 + anf * a1
            b1 = x * b0 + anf * b1
            if (a1 != 0.):
                    fac = 1. / a1
                    g = b1 * fac
                    if (abs((g - gold) / g) < eps):
                            return (g * math.exp(-x + a * math.log(x) - gln), gln)
                    gold = g
            n = n + 1
    raise max_iters, str(abs((g - gold) / g))

# vim: ts=4:sw=4:et
