import math, numpy
from pylab import *

class Range:
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def value(self, v):
        if self.min == None or v < self.min: self.min = v
        if self.max == None or v > self.max: self.max = v

    def length(self):
        if self.min != None and self.max != None: return self.max - self.min
        return 0.0

    def __str__(self):
        return "Range(min=%s, max=%s)" % (self.min, self.max)

def read_file(filename, x_col=0, y_col=1, f_col=2):
  # Read the content of the file in memory
  f = open(filename, "r")
  lines = f.read().splitlines()
  f.close()

  # Find the size of the file
  num_cols = None
  num_rows = 0
  nc = 0
  xrange = Range()
  yrange = Range()
  frange = Range()
  for line in lines:
    cs = line.split()
    n = len(cs)
    if n == 0:
      if num_cols == None:
        num_cols = nc

      elif nc != num_cols:
        print "Row %d has number of entries different to the max" % nc
        num_cols = max(num_cols, nc)

      nc = 0
      num_rows += 1

    else:
      x, y, f = [float(cs[i]) for i in [x_col, y_col, f_col]]
      xrange.value(x)
      yrange.value(y)
      frange.value(f)

      nc += 1

  # Now we allocate space in memory to hold the data
  data = numpy.ndarray(shape=(num_rows, num_cols), dtype=float)

  lx = xrange.length()
  ly = yrange.length()
  x0 = xrange.min
  y0 = yrange.min

  # Now we really get the data
  for line in lines:
    cs = line.split()
    if len(cs) > 0:
      x, y, f = [float(cs[i]) for i in [x_col, y_col, f_col]]
      ix = int(round((num_rows-1)*(x - x0)/lx))
      iy = int(round((num_cols-1)*(y - y0)/ly))
      data[ix, iy] = f

  x_delta = lx/num_cols
  y_delta = ly/num_rows
  return ((xrange, yrange, frange), data)

def fwd(r, x, n):
  return r.min + ((r.max - r.min)/n) * x

def bwd(r, x, n):
  return (x - r.min)/(r.max - r.min)*n

# Plot the data
cmap = cm.get_cmap('jet', 500)    # 10 discrete colors
((yrange, xrange, frange), data) = read_file("rec-space2.dat", f_col=4)
im = imshow(data, cmap=cmap, interpolation='bilinear', aspect='auto',
            extent=(xrange.min, xrange.max, yrange.min, yrange.max))

# Define the analytical solutions
gamma = 2.210173e5 # m/A s
exch_coupling = 13.0e-12 # J/m
Msat = 0.86e6 # in A/m
mu0 = 4.0e-7*math.pi # N/A^2 = J/m A^2
C = 2*exch_coupling/(mu0*Msat) # A m
def func2(x): return gamma*C*x**2 # 1/s
def func1(x): return 0.5*gamma*Msat + func2(x)

# Plot first solution
x = arange(0, data.shape[1], 1.0)
k = 1e9*fwd(xrange, x, data.shape[1])
omega1 = func1(k)
plot(1e-9*k, omega1, 'r', lw=2)

# Plot second solution
x = arange(0, data.shape[1], 1.0)
k = 1e9*fwd(xrange, x, data.shape[1])
omega1 = func2(k)
plot(1e-9*k, omega1, 'k', lw=2)

title("Dispersion for cylinder VS analytical curves")
#axis('off')
colorbar()

show()

