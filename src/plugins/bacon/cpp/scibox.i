

%module bacon_scibox
%{
#define SWIG_FILE_WITH_INIT
#include "scibox.h"
%}

%include "numpy.i"

%init %{
import_array();
%}

%apply(double* IN_ARRAY1, int DIM1) {(double* years, int ydim),
                                     (double* probs, int pdim)};
%apply(int DIM1, int DIM2, double* IN_ARRAY2) {(int hdim, int numhiatus, double* hdata)};

%typemap(in) PreCalDet** {
  $1 = NULL;
  if (PyList_Check($input)) {
    const size_t size = PyList_Size($input);
    $1 = (PreCalDet**)malloc((size+1) * sizeof(PreCalDet*));
    for (int i = 0; i < size; ++i) {
      void *argp = 0 ;
      const int res = SWIG_ConvertPtr(PyList_GetItem($input, i), &argp, $*1_descriptor, 0);
      if (!SWIG_IsOK(res)) {
        SWIG_exception_fail(SWIG_ArgError(res), "in method '" "$symname" "', argument " "$argnum" " of type '" "$1_type" "'");
      }
      $1[i] = reinterpret_cast<PreCalDet*>(argp);
    }
    $1[size] = NULL;
  }
  else {
    // Raise exception
    SWIG_exception_fail(SWIG_TypeError, "Expected list in $symname");
  }
}

%typemap(freearg) PreCalDet ** {
  free($1);
}

%ignore FuncInput;
%include "scibox.h"

%exception tempsim {
    $action
    if (PyErr_Occurred()) SWIG_fail;
}

%inline %{
int run_simulation(int numdets, PreCalDet** dets, int hdim, int numhiatus, double* hdata,
            int sections, double memorya, double memoryb, double minyr, double maxyr,
            double firstguess, double secondguess, double mindepth, double maxdepth,
            char* outfile, int numsamples) 
{
    if (numhiatus > 0 && hdim != 5) {
        PyErr_Format(PyExc_ValueError,
                     "Badly formed hiatus data");
        return 0;
    }

    return runSimulation(numdets, dets, numhiatus, hdata,
                         sections, memorya, memoryb, minyr, maxyr, 
                         firstguess, secondguess, mindepth, maxdepth,
                         outfile, numsamples);
}
%}




