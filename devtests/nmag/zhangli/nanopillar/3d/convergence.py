import sys

class Derivative:
  """Class to numerically calculate the derivative of a function.
  """
  def __init__(self, dt=None, dstep=None, save=True):
    """The derivative is calculated as dx/dt with dt greater or equal
    to the value provided here. If dt=None then there won't be restrictions
    on the magnitude of dt: the derivative will be computed every dstep
    calls to the function report_x. If save=True the values of the derivative
    are saved into the internal list self.derivatives.
    Otherwise the values are ignored.
    """
    if dt == None and dstep == None:
      raise ("At least one among the arguments dt and dstep "
             "has to be specified!")
    self.dt = dt
    self.dstep = dstep
    self.step = 0
    self.old = None
    self.save = save
    self.derivatives = []
    self.derivative2 = None

  def report_x(self, time, x):
    """Give the next value of the function of which we want to calculate
    the derivative.
    """
    if self.old == None:
      self.old = (time, x)
      return

    old_time, old_x = self.old
    take_derivative = False
    if self.dstep != None:
      take_derivative = (self.step % self.dstep == 0)
    self.step += 1
    if self.dt != None:
      take_derivative = take_derivative or (time >= old_time + self.dt)
    if take_derivative:
      derivative = (x - old_x)/(time - old_time)
      self.old = (time, x)
      if self.save:
        self.derivatives.append( (time, derivative) )
      if self.derivative2 != None:
        self.derivative2.report_x(time, derivative)

  def report_xs(self, time_x_list):
    for time, x in time_x_list:
      self.report_x(time, x)

  def derivative(self, dt=None, dstep=None, save=True):
    """Create a second derivative object."""
    if self.derivative2 != None:
      raise "This object has already a derivative!"
    second_derivative = Derivative(dt=dt, dstep=dstep, save=save)
    self.derivative2 = second_derivative
    return second_derivative

if len(sys.argv) < 2:
  print "USAGE: python convergence.py freqs.dat"
  sys.exit(1)

f = open(sys.argv[1], "r")
lines = f.readlines()
f.close()

data = []
for line in lines:
  cols = line.split()
  time = float(cols[0])
  freq = abs(float(cols[1]))
  mx = float(cols[3])
  data.append( (time, freq, mx) )

# Find the angle by integrating the frequency over time
old_time, old_freq, old_mx = data[0]
angle = 0.0
angles = []
for d in data[1:]:
  time, freq, mx = d
  angle += (time - old_time)*freq
  angles.append( (time, angle) )
  old_time, old_freq, old_mx = d

freq = Derivative(dt=1.0)
dfreq_dt = Derivative(dt=100.0)
d2freq_dt2 = dfreq_dt.derivative(dt=100.0)

freq.report_xs(angles)

_, max_dx_dt = freq.derivatives[0]
selected = []
for t, dx_dt in freq.derivatives[1:]:
  if dx_dt >= max_dx_dt:
    selected.append( (t, dx_dt) )
    max_dx_dt = dx_dt

dfreq_dt.report_xs(selected)

for time, value in dfreq_dt.derivatives:
  print time, value

