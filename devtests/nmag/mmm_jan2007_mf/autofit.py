#!/usr/bin/env python
import sys
import math
import commands

show_fits = True

l = len(sys.argv)
if l != 2:
  print "USAGE: autofit file"
  print "  file is the name of the file which contains the data."
  sys.exit(1)

f_name = sys.argv[1]

time_row = 0
m_rows = [4, 5, 6]
components_to_fit = [0, 1]
h_row = 3
time_mult_factor = 0.001
m_mult_factor = 1.0
tmp_file = "/tmp/tmp.gnp"
dec_file="/tmp/dec.dat"

# Read the data and parse it
f = open(f_name, "r")
lines = f.readlines()
f.close()

data = []
for l in lines:
  if l[0] == '#': continue

  r = l.split()
  time = float(r[time_row])*time_mult_factor
  m  = [float(r[m_row])*m_mult_factor for m_row in m_rows]
  data.append((time, m))

# Calculate some general parameters from the data

# Mean magnetisation values
mean_m = [0.0, 0.0, 0.0]
for row in data:
  time, m = row
  mean_m = [acc_i + m_i for acc_i, m_i in zip(mean_m, m)]
n = len(data)
mean_m = [float(acc_i)/n for acc_i in mean_m]

# Interval of variation for the magnetisations
def m_interval(data, component_idx):
  min_m = max_m = data[0][1][component_idx]
  for row in data:
    time, m = row
    mag = m[component_idx]
    if mag < min_m: min_m = mag
    if mag > max_m: max_m = mag
  return (min_m, max_m)

intervals = [m_interval(data, i) for i in range(3)]
amplitudes = [1.1*max(mx - mean, mean - mn)
              for (mean, (mn, mx)) in zip(mean_m, intervals)]

time_0 = data[0][0]
time_1 = data[-1][0]
delta_t = time_1 - time_0
half_t = time_0 + 0.8*delta_t

num_oscillations = 0
max_norm_dm = 0.0
direction = None
old_direction = None
old_m = None
half_max_m = [None, None, None]
half_min_m = [None, None, None]
i = 0
k = 0 # use first component of m to detect oscillations
for row in data:
  time, m = row
  dm = [m_i - mean_i for m_i, mean_i in zip(m, mean_m)]
  norm_dm = math.sqrt(dm[0]**2 + dm[1]**2 + dm[2]**2)
  if norm_dm > max_norm_dm: max_norm_dm = norm_dm

  if i % 5 == 0:
    if old_m:
      if m[k] > old_m[k]:
        direction = 1
      else:
        direction = -1
      if old_direction:
        if old_direction != direction:
          num_oscillations += 1
      old_direction = direction
    old_m = m
  i += 1

  if time > half_t:
    for j in range(3):
      if half_min_m[j]:
        if m[j] < half_min_m[j]: half_min_m[j] = m[j]
      else:
        half_min_m[j] = m[j]
      if half_max_m[j]:
        if m[j] > half_max_m[j]: half_max_m[j] = m[j]
      else:
        half_max_m[j] = m[j]

half_amplitude = [mx - mn for mn, mx in zip(half_min_m, half_max_m)]

ls = [-2.0*math.log(ha/a)/delta_t
      for ha, a in zip(half_amplitude, amplitudes)]
# for now we determine the period and the phase with a first fit,
# and then we fit all the others parameters
period = delta_t*2.0/num_oscillations 
w = 2.0*math.pi/period

fit_data = ["", "", ""]
for i in components_to_fit:
  c1 = time_row + 1
  c2 = m_rows[i] + 1
  h_ext = float((lines[0].split())[h_row])
  gnp_lines = []
  gnp_lines.append('set samples 1000')
  gnp_lines.append('dm = %g' % 0.0)
  gnp_lines.append('fit_t0 = %g' % (half_t))
  gnp_lines.append('ft = %g' % time_mult_factor)
  gnp_lines.append('fm = %g' % m_mult_factor)
  gnp_lines.append('h_ext = %g' % h_ext)
  gnp_lines.append('t0 = %g' % time_0)
  gnp_lines.append('p = %g' % 0.1)
  gnp_lines.append('x0 = %g' % mean_m[i])
  gnp_lines.append('A = %g' % amplitudes[i])
  gnp_lines.append('half_t = %g' % half_t)
  gnp_lines.append('lambda = %g' % ls[i])
  gnp_lines.append('w = %g' % w)
  gnp_lines.append('f(x)=A*exp(-lambda*(x - t0))*cos(w*(x - t0 + p)) + x0')
  gnp_lines.append('fit [fit_t0:] f(x) "%s" u ($%d*ft):($%d*fm) via p, w, A, lambda, x0' % (f_name, c1, c2))
  if show_fits:
    gnp_lines.append('plot [fit_t0:] "%s" u ($%d*ft):($%d*fm) w l t "data", f(x) t "fit"' % (f_name, c1, c2))
    gnp_lines.append('pause -1')
  gnp_lines.append('print "# h_ext, A, lambda, w, dm, p, x0"')
  gnp_lines.append('print h_ext, A, lambda, w, dm, p, x0')

  f = open(tmp_file, "w")
  f.write("\n".join(gnp_lines))
  f.close()

  out_lines = commands.getoutput("gnuplot %s" % tmp_file)
  fit_data[i] += (out_lines.splitlines())[-1] + "\n"

for i in components_to_fit:
  if len(fit_data[i]) > 0:
    f = open("fits%d.dat" % i, "a")
    f.write(fit_data[i])
    f.close()
