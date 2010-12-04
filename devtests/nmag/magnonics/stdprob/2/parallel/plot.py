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

def read_file(filename, x_col=0, y_col=1, f_col=2, transform=None):
  if transform == None:
    transform = lambda v: v

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
      x, y, f = transform(tuple(float(cs[i]) for i in (x_col, y_col, f_col)))
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
      x, y, f = transform(tuple(float(cs[i]) for i in (x_col, y_col, f_col)))
      ix = int(round((num_rows-1)*(x - x0)/lx))
      iy = int(round((num_cols-1)*(y - y0)/ly))
      data[ix, iy] = f

  x_delta = lx/num_cols
  y_delta = ly/num_rows
  return ((xrange, yrange, frange), data)

def process_cell(s):
  try:
    value = float(s)
  except:
    value = str(s)
  return value

def read_file_cols(filename):
  f = open(filename, "r")
  ls = filter(lambda l: not l.startswith('#'), f.read().splitlines())
  data = [[process_cell(cell) for cell in l.split()]
          for l in ls]
  f.close()
  return data

def fwd(r, x, n):
  return r.min + ((r.max - r.min)/n) * x

def bwd(r, x, n):
  return (x - r.min)/(r.max - r.min)*n

# Plot the data
cmap = cm.get_cmap('jet', 500)    # 10 discrete colors

dk = 0.0182121313252
domega = 1.25663706144

def tsf(v):
  omega, k, f = v
  return (omega*1e-9/(2*math.pi) + 0.5*domega, k + 0.5*dk, f)

((yrange, xrange, frange), data) = \
  read_file("rec-space.dat", f_col=4, transform=tsf)

im = imshow(data, cmap=cmap, interpolation='bilinear', aspect='auto',
            extent=(xrange.min, xrange.max, yrange.min, yrange.max))

dynmx_data = numpy.array(read_file_cols("dynmatrix.dat"))

# Plot first solution
k = dynmx_data[:, 0]*1e-9
omega1 = dynmx_data[:, 1]
plot(-k, omega1, 'r', lw=2)

# Plot second solution
omega1 = dynmx_data[:, 2]
plot(k, omega1, 'r', lw=2)

title("Problem 2: Nmag VS dynamical matrix method")
xlabel("k (rad/ns)")
ylabel("omega (GHz)")

#axis('off')
colorbar()

show()

