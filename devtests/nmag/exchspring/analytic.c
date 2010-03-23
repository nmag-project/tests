#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_sf.h>
#include <gsl/gsl_roots.h>

double pi = 3.14159265358979323844, mu0 = 1.256637061435917295376e-6;

typedef struct {
  double msat, a;
  double L, x0, ha;
  double c, lambda, hb, tol;
} Params;

static void init(Params *p) {
  p->msat = 0.86e6;
  p->a = 13.0e-12;
  p->L = 20.0e-9;
  p->x0 = 0.0;
  p->ha = 1e6;
  p->tol = 1e-9;

  p->c = 2*p->a/(mu0*p->msat);
  p->lambda = sqrt(p->ha/p->c);
  p->hb = p->c*(pi/p->L)*(pi/p->L);
}

double func(double k, void *params) {
  Params *p = (Params *) params;
  double result;
  printf("calculating K(%g) = ", k);
  result = gsl_sf_ellint_Kcomp(k, GSL_PREC_DOUBLE) - 0.5*p->lambda*p->L;
  printf("%g\n", result);
  return result;
}

double find_k(Params *p) {
  int bisect = 1, status;
  gsl_function f;
  f.function = & func;
  f.params = p;

  if (bisect) {
    const gsl_root_fsolver_type *T = gsl_root_fsolver_bisection;
    double k, x_lo, x_hi;
    int iter = 0, max_iter = 100;

    gsl_root_fsolver *s = gsl_root_fsolver_alloc(T);
    gsl_root_fsolver_set(s, & f, 1e-5, 1.0 - 1e-5);
    do {
      ++iter;
      status = gsl_root_fsolver_iterate(s);
      k = gsl_root_fsolver_root(s);
      x_lo = gsl_root_fsolver_x_lower(s);
      x_hi = gsl_root_fsolver_x_upper(s);
      status = gsl_root_test_interval(x_lo, x_hi, 0, p->tol);
      if (status == GSL_SUCCESS)
        printf("Converged:\n");

      printf("%5d [%.7f, %.7f] %.7f %.7f\n", iter, x_lo, x_hi, k, x_hi - x_lo);
    } while (status == GSL_CONTINUE && iter < max_iter);
    gsl_root_fsolver_free(s);
    return k;

  } else {
    const gsl_root_fdfsolver_type *T = gsl_root_fdfsolver_newton;
    /*gsl_root_fdfsolver *s = gsl_root_fdfsolver_alloc(T);
    gsl_root_fdfsolver_set(s, func, 0.5);*/
    return 0.0;
  }
}

int main(void) {
  Params p;
  int status;
  double u, m, sn, cn, dn, x, dx, k, y;
  int i, n = 100;
  FILE *file;

  init(& p);

  /* First find k */
  k = find_k(& p);

  file = fopen("analytic.dat", "w");
  x = p.x0;
  dx = p.L/n;
  for(i = 0; i< n; i++) {
    u = p.lambda * x;
    m = k*k;
    status = gsl_sf_elljac_e(u, m, & sn, & cn, & dn);
    y = 2.0*asin(k*sn);
    fprintf(file, "%g %g\n", x, y);
    x += dx;
  }
  fclose(file);
  return 0;
}
