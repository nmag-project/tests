
#include "basic.h"
#include "bem3d.h"
#include "cluster.h"
#include "clusterbasis.h"
#include "h2virtual.h"
#include "laplacebem.h"
#include "surfacebem.h"
#include "supermatrix.h"
#include "hcoarsening.h"
#include "aca.h"
#include "krylov.h"

#include <assert.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/times.h>
#include <time.h>

/* ------------------------------------------------------------
    Demonstrate the direct boundary element method on surfaces
   ------------------------------------------------------------ */

/* Solution: u(x,y,z) = x+y+z, du/dn(x,y,z) = nx+ny+nz */

static double
rhs_dirichlet_linear(const double *x, const double *n)
{
  (void) n;
  return x[0] + x[1] + x[2];
}

static double
rhs_neumann_linear(const double *x, const double *n)
{
  (void) x;
  return n[0] + n[1] + n[2];
}

/* Solution: u(x,y,z) = x^2-z^2, du/dn(x,y,z) = 2*nx*x-2*nz*z */

static double
rhs_dirichlet_quadratic(const double *x, const double *n)
{
  (void) n;
  return x[0] * x[0] - x[2] * x[2];
}

static double
rhs_neumann_quadratic(const double *x, const double *n)
{
  return 2.0 * (n[0] * x[0] - n[2] * x[2]);
}

/* ------------------------------------------------------------
   Main program
   ------------------------------------------------------------ */

int
main()
{
  pbemgrid3d gr;
  pmacrogrid3d mg;
  pclustertree dct, nct;
  pcluster droot, nroot;
  pblockcluster blkV, blkK;
  psurfacebemfactory bfactoryK, bfactoryV;
  psupermatrix V, Vc, K;
  char buf[80];
  double *diri, *neum, *rhs;
  double error, norm;
  double eps, eta;
  int kmax;
  struct tms buffer;
  clock_t t1, t2;
  time_t t;
  int split, p, nfdeg, nmin, nmax;

  (void) time(&t);
  srand(t);

  split = 16;
  nfdeg = 2;
  p = 3;
  eps = 5e-3;

  (void) printf("==============================================\n");
  (void) printf("#   Solve direct boundary integral method    #\n");
  (void) printf("==============================================\n");

  (void) printf("# Split edges into how many parts? [%d]\n", split);
  (void) fgets(buf, 80, stdin);
  (void) sscanf(buf, "%d", &split);

  nfdeg = 2;
  (void) printf("# Order of the quadrature? [%d]\n", nfdeg);
  (void) fgets(buf, 80, stdin);
  (void) sscanf(buf, "%d", &nfdeg);

  p = 1 +  (int) (1.7 * log((double)split)/log(10.0));
  (void) printf("# Order of the interpolation? [%d]\n",	p);
  (void) fgets(buf, 80, stdin);
  (void) sscanf(buf, "%d", &p);

  eps = pow(10,-1.5*log(5.0*split)/log(10.0));
  (void) printf("# Desired precision? [%.1g]\n", eps);
  (void) fgets(buf, 80, stdin);
  (void) sscanf(buf, "%lf", &eps);

  nmin = 16;
  kmax = p*p*p;
  eta = 2.0;

  /* --- Create the surface grid */

  (void) printf("# Creating approximation of the unit sphere\n");
  mg = ellipsoid_macrogrid3d(1.0, 1.0, 1.0);
  gr = macro2_bemgrid3d(mg, split, 1);
  prepare_bemgrid3d(gr);
  (void) printf("  %d vertices, %d triangles\n",
		gr->vertices, gr->triangles);

  /* --- Create cluster trees */

  (void) printf("# Creating Dirichlet cluster tree\n");
  dct = buildvertexcluster_bemgrid3d(gr, HLIB_REGULAR, nmin, 0);
  droot = dct->root;
  (void) printf("  %d clusters, %d degrees of freedom\n",
		count_cluster(droot), droot->size);

  (void) printf("# Creating Neumann cluster tree\n");
  nct = NULL;
  /*
  nct = buildcluster_bemgrid3d(gr, HLIB_REGULAR, nmin, 0);
  */

  nct = buildvertexcluster_bemgrid3d(gr, HLIB_REGULAR, nmin, 0);


  nroot = nct->root;
  (void) printf("  %d clusters, %d degrees of freedom\n",
		count_cluster(nroot), nroot->size);

  nmax = (droot->size > nroot->size ? droot->size : nroot->size);

  /* --- Create BEM factories */

  (void) printf("# Creating BEM factory for single layer potential\n");
  /*bfactoryV = new_surfacebemfactory_slp(gr,
					HLIB_CONSTANT_BASIS, nct,
					HLIB_CONSTANT_BASIS, nct,
					nfdeg, nfdeg+2, p);
  bfactoryV->disp = (stdout_is_terminal() ? eta_progressbar : 0);
  bfactoryV->dist_adaptive=1;
  /*

  /*
  (void) printf("# Creating BEM factory for double layer potential\n");
  bfactoryK = new_surfacebemfactory_dlp(gr,
					HLIB_CONSTANT_BASIS, nct,
					HLIB_LINEAR_BASIS, dct,
					nfdeg, nfdeg+2, p, 0.5);

  */
  (void) printf("# Creating BEM factory for double layer potential\n");
  bfactoryK = new_surfacebemfactory_dlp(gr,
					HLIB_LINEAR_BASIS, nct,
					HLIB_LINEAR_BASIS, dct,
					nfdeg, nfdeg+2, p, 0.5);


  bfactoryK->disp = (stdout_is_terminal() ? eta_progressbar : 0);
  bfactoryK->disp = 0;
  bfactoryK->dist_adaptive=1;



  /* --- Create approximation of double layer potential */
    
  (void) printf("# Creating double layer potential matrix K\n");
  t1 = times(&buffer);
  blkK = build_blockcluster(nroot, droot,
			    HLIB_MAXADMISSIBILITY, HLIB_BLOCK_INHOMOGENEOUS,
			    eta, 0);
  K = build_supermatrix_from_blockcluster(blkK, 0, 0.0);
  t2 = times(&buffer);
  (void) printf("  %.1f seconds\n",
		(double) (t2-t1) / CLK_TCK);

  (void) printf("# Filling double layer potential matrix\n");
  t1 = times(&buffer);
  hcafill_surfacebem_supermatrix(K, nroot, droot, bfactoryK, eps/33.0, kmax);
  (void) printf("Got to here 1\n");
  t2 = times(&buffer);
  (void) printf("Got to here 2\n");
  (void) printf("  %.1f seconds\n"
		"  %d blocks\n"
		"  Storage requirements: %.1f MB (%.1f KB/DoF)\n"
		"  Nearfield storage requirements: %.1f MB\n",
		(double) (t2-t1) / CLK_TCK,
		getnrnodes_supermatrix(K),
		getsize_supermatrix(K) / 1048576.0,
		getsize_supermatrix(K) / 1024.0 / nmax,
		getsizefull_supermatrix(K) / 1048576.0);
  
  (void) printf("Got to here 3\n");

  /* --- Test double layer potential */

  (void) printf("Stastitical data on K\n");
  (void) printf(" K->rows =%d\n", K->rows);
  (void) printf(" K->cols =%d\n", K->cols);


  diri = allocate_vector(K->cols);
  

  (void) printf("Got to here 4\n");
  /*
  neum = allocate_vector(V->cols);

  assert(V->rows == V->cols);
  assert(K->rows == V->cols);
  */

  rhs = allocate_vector(K->rows);

  (void) printf("# Checking double layer potential\n");
  fill_vector(K->cols, diri, 1.0);
  (void) printf("Got to here 5\n");
  eval_supermatrix(K, diri, rhs);
  (void) printf("Got to here 6\n");
  norm = norm2_lapack(K->rows, rhs);
  (void) printf("Got to here 7\n");
  (void) printf("  |K'*1| = %g\n", norm);
  (void) printf("Got to here 8\n");
  /* --- Prepare preconditioner */




  /* --- Linear test example */

  (void) printf("# Testing u(x,y,z)=x+y+z\n");

  t1 = times(&buffer);
  fillprojection_surfacebem(diri, 1, rhs_dirichlet_linear, bfactoryK);
  error = l2norm_surfacebem(diri, rhs_dirichlet_linear, 1, bfactoryK);
  norm = l2norm_surfacebem(NULL, rhs_dirichlet_linear, 1, bfactoryK);
  t2 = times(&buffer);
  (void) printf("  %.1f seconds for the projection of Dirichlet values\n"
		"  L^2-norm error: %g (%g)\n",
		(double) (t2-t1) / CLK_TCK,
		error, error/norm);

  t1 = times(&buffer);
  eval_supermatrix(K, diri, rhs);
  t2 = times(&buffer);
  (void) printf("  %.1f seconds for applying the double layer potential\n",
		(double) (t2-t1) / CLK_TCK);

  /* --- Quadratic test example */

  (void) printf("# Testing u(x,y,z)=x^2-z^2\n");

  t1 = times(&buffer);
  fillprojection_surfacebem(diri, 1, rhs_dirichlet_quadratic, bfactoryK);
  error = l2norm_surfacebem(diri, rhs_dirichlet_quadratic, 1, bfactoryK);
  norm = l2norm_surfacebem(NULL, rhs_dirichlet_quadratic, 1, bfactoryK);
  t2 = times(&buffer);
  (void) printf("  %.1f seconds for the projection of Dirichlet values\n"
		"  L^2-norm error: %g (%g)\n",
		(double) (t2-t1) / CLK_TCK,
		error, error/norm);

  t1 = times(&buffer);
  eval_supermatrix(K, diri, rhs);
  t2 = times(&buffer);
  (void) printf("  %.1f seconds for applying the double layer potential\n",
		(double) (t2-t1) / CLK_TCK);

 /* 

  Matrix multiplication:

  w = s*v 
  void 
  eval_supermatrix(pcsupermatrix s, const double* v, double* w);

  From the size of the matrix, we conclude that this works out the
  dl-potential for each triangle surface, given the potential at all surface points.


  What we are interested in is the dl potential at all surface points,
  given the potential at the surface points.

  How to do that? (fangohr 10/05/2007) 
   -> maybe there is extra function for this or we can 
   -> modify the new_surfacebemfactory_dlp command suitably


 */




  outputsvd_supermatrix(K, "K.ps");


  return 0;}
