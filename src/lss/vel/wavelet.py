#############################################################################
# Wavelet estimation

from imports import *

#############################################################################

nt = 2001
dt = 0.0005
ft = -(nt/2)*dt
st = Sampling(nt,dt,ft)
fpeak = 10.0

def main(args):
  goZeroPhase()
  #goMinimumPhase()
  #rotateAndDifferentiate()

def rotateAndDifferentiate():
  rx = getTrace()
  fft = Fft(rx)
  sf = fft.getFrequencySampling1()
  nf = sf.count

  # Forward FFT
  cy = fft.applyForward(rx)

  # Phase rotation
  p = 0.25*FLT_PI
  t = like(cy)
  for i in range(nf):
    w = sf.getValue(i)
    t[2*i  ] = -cos(p)
    t[2*i+1] = -sin(p)
    #t[2*i  ] = -w*w*cos(p) # include 2nd time derivative
    #t[2*i+1] = -w*w*sin(p) # include 2nd time derivative
  cmul(t,cy,cy)

  # Differentiate
  sf = fft.getFrequencySampling1()
  s = like(cy)
  for i in range(nf):
    w = sf.getValue(i)
    s[2*i  ] = -w*w # for 2nd derivative
    #s[2*i+1] = w # for 1st derivative
  cmul(s,cy,cy)

  # Inverse FFT
  ry = fft.applyInverse(cy)

  points(rx)
  points(ry)

def goZeroPhase():
  x = getTrace()
  y = findZeroPhase(x)
  points(x)
  points(y)

def goMinimumPhase():
  x = getTrace()
  y = findMinimumPhase(x)
  points(x)
  points(y)

def findZeroPhase(rx):
  fft = Fft(rx)
  cx = fft.applyForward(rx)
  #points(cx)
  cx = cmplx(cabs(cx),like(cabs(cx))) # amplitude spectrum
  #points(cx)
  ry = fft.applyInverse(cx)
  #points(ry)
  return ry

def findMinimumPhase(rx):
  n = len(rx)
  fft = Fft(rx)
  cx = fft.applyForward(rx)
  cx = cabs(cx)
  points(cx)
  mul(cx,cx,cx) # spectrum
  #points(cx)
  add(1.0e-4*max(cx),cx,cx) # stabilize for logarithm
  cx = cmplx(cx,like(cx)) # spectrum
  cx = clog(cx)
  #points(cx)
  ry = fft.applyInverse(cx)
  #points(ry)
  for i in range(n/2,n):
    ry[i] = 0.0
  #points(ry)
  cz = fft.applyForward(ry)
  cz = cexp(cz)
  rz = fft.applyInverse(cz)
  #points(rz)
  points(cabs(fft.applyForward(rz)))
  return rz

def like(x):
  return zerofloat(len(x))

def points(x):
  SimplePlot.asPoints(x)

def acor(x):
  return xcor(x,x)
  
def xcor(x,y):
  z = zerofloat(nt)
  Conv.xcor(nt,-nt/2,x,nt,-nt/2,y,nt,-nt/2,z)
  return z

def getTrace():
  x = zerofloat(nt)
  for it in range(nt):
    t = ft+it*dt
    x[it] = ricker(t)
  return x

def ricker(t):
  x = FLT_PI*fpeak*t
  xx = x*x
  return (1.0-2.0*xx)*exp(-xx);

#############################################################################
# Do everything on Swing thread.

class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
