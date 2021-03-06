#############################################################################
# Simple example of objective function w/ and w/o warping

from imports import *

#############################################################################

# Time sampling
dt = 0.01*PI
nt = 1+int(30.0*PI/dt)
ft = -0.5*nt*dt
st = Sampling(nt,dt,ft)

pngdatDir = None
pngdatDir = '/Users/sluo/Desktop/png/'

#widthPoints = None # slides
#widthPoints = 240.0 # single column
widthPoints = 260.0 # half page column
#widthPoints = 175.0 # half of 4/3 column

#############################################################################

def main(args):
  goAmplitudeAndTraveltime() # amplitude and traveltime misfit (nonlinear)
  #goAmplitudeAndScale() # amplitude and index scale misfit (linear?)
  #goAmplitudeAndAmplitude() # amplitude and amplitude misfit (linear?)

def goAmplitudeAndAmplitude():

  showGlobalMinimum = True

  # Amplitude scale sampling
  fa = 0.0
  la = 2.0
  da = 0.05
  na = 1+int((la-fa)/da)
  sa = Sampling(na,da,fa)

  # Amplitude scale sampling
  fb = -2.75
  lb = 2.75
  db = 0.05
  nb = 1+int((lb-fb)/db)
  sb = Sampling(nb,db,fb)

  # Simulated data
  ds = zerofloat(nt)
  for it in range(nt):
    t = ft+it*dt
    ds[it] = cos(t)
  w = zerofloat(nt); w[nt/2] = 1.0
  RecursiveGaussianFilter(3.0*PI/dt).apply0(w,w)
  mul(w,ds,ds)
  div(ds,max(abs(ds)),ds)

  # Observed data
  amplitudeScaleA = 1.5
  amplitudeScaleB = 0.5
  do = mul(amplitudeScaleA+amplitudeScaleB,ds)

  # Objective function
  def makeObjectiveFunction(ds,do):
    ob = zerofloat(nb,na)
    class Loop(Parallel.LoopInt):
      def compute(self,ia):
        a = fa+ia*da
        for ib in range(nb):
          b = fb+ib*db
          dss = mul(a+b,ds)
          ob[ia][ib] = sum(mul(sub(dss,do),sub(dss,do)))
    Parallel.loop(na,Loop())
    div(ob,max(abs(ob)),ob)
    return ob

  ob = makeObjectiveFunction(ds,do)
  plot(ob,sb,sa,jet,cmin=0.0,cmax=1.0,title='obj')

  if showGlobalMinimum:
    copy(do,ds)

  cmax = la; cmin = -cmax
  points(Sampling(nt,0.1*dt,0.1*ft),ds,cmin=cmin,cmax=cmax,title='ds')
  points(Sampling(nt,0.1*dt,0.1*ft),do,cmin=cmin,cmax=cmax,title='do')
  points(Sampling(nt,0.1*dt,0.1*ft),ds,do,cmin=cmin,cmax=cmax,title='ds_do')
  #points(Sampling(nt,0.1*dt,0.1*ft),do,ds,cmin=cmin,cmax=cmax,title='do_ds')

def goAmplitudeAndScale():

  showGlobalMinimum = True

  # Amplitude scale sampling
  fa = 0.0
  la = 2.0
  da = 0.05
  na = 1+int((la-fa)/da)
  sa = Sampling(na,da,fa)

  # Index scale sampling
  fb = 0.5
  lb = 1.5
  #db = 0.001*PI
  db = 0.05
  nb = 1+int((lb-fb)/db)
  sb = Sampling(nb,db,fb)

  # Simulated data
  ds = zerofloat(nt)
  for it in range(nt):
    t = ft+it*dt
    ds[it] = cos(t)
  w = zerofloat(nt); w[nt/2] = 1.0
  RecursiveGaussianFilter(3.0*PI/dt).apply0(w,w)
  mul(w,ds,ds)
  div(ds,max(abs(ds)),ds)

  # Observed data
  amplitudeScale = 1.5
  indexScale = 1.2
  do = zerofloat(nt)
  si = SincInterp()
  for it in range(nt):
    t = st.getValue(it)
    do[it] = si.interpolate(st,ds,indexScale*t)
  mul(amplitudeScale,do,do) # scale

  # Objective function
  def makeObjectiveFunction(ds,do):
    ob = zerofloat(nb,na)
    class Loop(Parallel.LoopInt):
      def compute(self,ia):
        a = fa+ia*da
        for ib in range(nb):
          b = fb+ib*db
          dss = zerofloat(nt)
          for it in range(nt):
            t = st.getValue(it)
            dss[it] = si.interpolate(st,ds,b*t)
          mul(a,dss,dss)
          #ob[ia][ib] = sum(abs(sub(dss,do)))
          ob[ia][ib] = sum(mul(sub(dss,do),sub(dss,do)))
    Parallel.loop(na,Loop())
    div(ob,max(abs(ob)),ob)
    return ob

  ob = makeObjectiveFunction(ds,do)
  plot(ob,sb,sa,jet,cmin=0.0,cmax=1.0,title='obj')

  if showGlobalMinimum:
    copy(do,ds)

  cmax = la; cmin = -cmax
  points(Sampling(nt,0.1*dt,0.1*ft),ds,cmin=cmin,cmax=cmax,title='ds')
  points(Sampling(nt,0.1*dt,0.1*ft),do,cmin=cmin,cmax=cmax,title='do')
  points(Sampling(nt,0.1*dt,0.1*ft),ds,do,cmin=cmin,cmax=cmax,title='ds_do')
  #points(Sampling(nt,0.1*dt,0.1*ft),do,ds,cmin=cmin,cmax=cmax,title='do_ds')



def goAmplitudeAndTraveltime():

  useAmplitudeResidual = False
  showGlobalMinimum = False
  showLocalMinimum = False

  # Time lag sampling
  #nl = nt/4 # number of time lags
  nl = 650
  fl = -nl/2 # first lag
  dl = dt
  sl = Sampling(nl,dl,fl*dl)

  # Amplitude scale sampling
  fa = 0.0
  la = 2.0
  da = 0.05
  na = 1+int((la-fa)/da)
  sa = Sampling(na,da,fa)

  # Simulated data
  ds = zerofloat(nt)
  for it in range(nt):
    t = ft+it*dt
    ds[it] = cos(t)
  w = zerofloat(nt); w[nt/2] = 1.0
  RecursiveGaussianFilter(3.0*PI/dt).apply0(w,w)
  mul(w,ds,ds)
  div(ds,max(abs(ds)),ds)

  # Observed data
  amplitudeScale = 1.5
  timeShift = 1.5*PI
  if (not useAmplitudeResidual) and (not showGlobalMinimum):
    do = shift(ds,timeShift)
  else:
    do = copy(ds)
  mul(amplitudeScale,do,do) # scale

  # Objective function
  #corr = Correlation(Correlation.Measure.ABSOLUTE_DIFFERENCE)
  corr = Correlation(Correlation.Measure.SQUARED_DIFFERENCE)
  def makeObjectiveFunction(ds,do):
    ob = zerofloat(nl,na)
    class Loop(Parallel.LoopInt):
      def compute(self,ia):
        #a = fa+ia*da+1.0
        a = fa+ia*da
        dsa = mul(ds,a)
        corr.correlate(
          nt,-nt/2,dsa,
          nt,-nt/2,do,
          nl,-nl/2,ob[ia]
        )
    Parallel.loop(na,Loop())
    div(ob,max(abs(ob)),ob)
    return ob

  ob = makeObjectiveFunction(ds,do)
  #plot(ob,sl,sa,,cmin=0.0,cmax=1.0,title='obj')
  plot(ob,Sampling(nl,0.1*dl,0.1*fl*dl),sa,jet,cmin=0.0,cmax=1.0,title='obj')

  if showGlobalMinimum:
    mul(1.5,ds,ds)
  if showLocalMinimum:
    ds = shift(ds,-0.5*PI)
    #points(st,ds,do,title='ds_do')
    #plot(obj,sl,sa,cmin=0.0,cmax=1.0,title='obj')
    obj = makeObjectiveFunction(ds,do)
    lmin = 1.0e6
    aopt = 0.0
    for ia in range(na):
      obji = obj[ia][nl/2]
      if obji<lmin:
        lmin = obji
        aopt = fa+ia*da
    print "a =",aopt
    mul(aopt,ds,ds)

  #points(st,ds,title='ds')
  #points(st,do,title='do')
  #points(st,ds,do,title='ds_do')
  #cmax = 1.25*max(do); cmin = -cmax
  cmax = la; cmin = -cmax
  points(Sampling(nt,0.1*dt,0.1*ft),ds,cmin=cmin,cmax=cmax,title='ds')
  points(Sampling(nt,0.1*dt,0.1*ft),do,cmin=cmin,cmax=cmax,title='do')
  points(Sampling(nt,0.1*dt,0.1*ft),ds,do,cmin=cmin,cmax=cmax,title='ds_do')
  #points(Sampling(nt,0.1*dt,0.1*ft),do,ds,cmin=cmin,cmax=cmax,title='do_ds')
  points(Sampling(nt,0.1*dt,0.1*ft),shift(do,-timeShift),ds,
    cmin=cmin,cmax=cmax,title='do_shift')
  points(Sampling(nt,0.1*dt,0.1*ft),do,ds,shift(do,-timeShift),
    cmin=cmin,cmax=cmax,title='do_ds_shift')

def shift(f,tau):
  g = like(f)
  for it in range(nt):
    jt = it+int(tau/dt)
    if jt>=0 and jt<nt:
      g[jt] = f[it]
  return g

def timeDerivative(f):
  #odt = 0.5
  odt = 0.5/dt
  g = zerofloat(nt)
  for it in range(1,nt-1):
    g[it] = odt*(f[it+1]-f[it-1])
  return g

#############################################################################

gray = ColorMap.GRAY
jet = ColorMap.JET
rwb = ColorMap.RED_WHITE_BLUE
gyr = ColorMap.GRAY_YELLOW_RED
def plot(f,s1=None,s2=None,cmap=jet,
         cmin=0,cmax=0,perc=100,sperc=None,cbar=None,title=None):
  #panel = PlotPanel(PlotPanel.Orientation.X1DOWN_X2RIGHT)
  panel = PlotPanel()
  panel.setHLimits(s1.first,s1.last)
  panel.setVLimits(s2.first,s2.last)
  panel.setHLabel('Traveltime shift (s)')
  #panel.setHLabel('Traveltime shift')
  panel.setVLabel('Amplitude scale')
  cb = panel.addColorBar()
  cb.setLabel('Normalized misfit')
  #cb.setLabel('Misfit')
  cb.setInterval(1.0)
  if widthPoints is None:
    cb.setWidthMinimum(160)
  elif widthPoints==240.0:
    #cb.setWidthMinimum(130)
    cb.setWidthMinimum(120)
  elif widthPoints==260.0:
    cb.setWidthMinimum(110)
  elif widthPoints==175.0:
    cb.setWidthMinimum(120)
  if s1 is not None and s2 is not None:
    pixel = panel.addPixels(s1,s2,f)
    contour = panel.addContours(s1,s2,f)
    contour.setLineColor(Color.BLACK)
    contour.setLineWidth(3.0)
  else:
    pixel = panel.addPixels(f)
  pixel.setColorModel(cmap)
  if cmin<cmax:
    pixel.setClips(cmin,cmax)
  if perc<100:
    pixel.setPercentiles(100-perc,perc)
  if sperc is not None: # symmetric percentile clip (for plotting gradients)
    clips = Clips(100-sperc,sperc,f)
    clip = max(abs(clips.getClipMin()),abs(clips.getClipMax()))
    pixel.setClips(-clip,clip)
  pixel.setInterpolation(PixelsView.Interpolation.LINEAR)
  frame = PlotFrame(panel)
  if widthPoints is None:
    frame.setFontSizeForSlide(1.0,1.0)
    frame.setSize(1200,500)
  elif widthPoints==240.0:
    frame.setFontSizeForPrint(8,widthPoints)
    #frame.setSize(1200,500)
    frame.setSize(1200,450)
  elif widthPoints==260.0:
    frame.setFontSizeForPrint(8,widthPoints)
    frame.setSize(1200,450)
  elif widthPoints==175.0:
    frame.setFontSizeForPrint(8,widthPoints)
    frame.setSize(1200,600)
  if title:
    frame.setTitle(title)
  frame.setVisible(True)
  if title and pngdatDir:
    if widthPoints is not None:
      frame.paintToPng(720,widthPoints/72.0,pngdatDir+title+'.png')
    else:
      #frame.paintToPng(360,3.0,pngdatDir+title+'.png')
      frame.paintToPng(720,3.08,pngdatDir+title+'.png')
      #write(pngdatDir+title+'.dat',f)
  return panel

def points(s,x1,x2=None,x3=None,cmin=0.0,cmax=0.0,title=None):
  panel = PlotPanel()
  panel.setHLabel('Time (s)')
  panel.setVLabel('Amplitude')
  #panel.setHInterval(2.0)
  panel.setHInterval(1.0)
  panel.setHLimits(-3.0,3.0)
  grid = True
  if grid:
    gv = panel.addGrid("H0Vk--")
    gv.setColor(Color.BLACK)
    gv.setStyle(GridView.Style.DASH)
  if widthPoints is None:
    lineWidth = 3.0
  else:
    lineWidth = 4.0
  point1 = panel.addPoints(s,x1)
  point1.setLineColor(Color.BLACK)
  point1.setLineWidth(lineWidth)
  #max1 = 1.1*max(abs(x1))
  #panel.setVLimits(-max1,max1)
  if x2 is not None:
    #max2 = 1.1*max(abs(x2))
    point2 = panel.addPoints(s,x2)
    #point2.setLineColor(Color.BLUE)
    point2.setLineColor(Color.RED)
    #point2.setLineColor(Color.GRAY)
    #point2.setLineStyle(PointsView.Line.DASH)
    point2.setLineWidth(lineWidth)
    #panel.setVLimits(-max(max1,max2),max(max1,max2))
  if x3 is not None:
    point3 = panel.addPoints(s,x3)
    point3.setLineColor(Color.BLUE)
    #point3.setLineStyle(PointsView.Line.DOT)
    point3.setLineWidth(lineWidth)
  if cmin<cmax:
    panel.setVLimits(cmin,cmax)
  frame = PlotFrame(panel)
  if widthPoints is None:
    frame.setFontSizeForSlide(0.86,0.86)
    frame.setSize(1200,500)
  elif widthPoints==240.0:
    #frame.setFontSizeForPrint(8,widthPoints)
    #frame.setSize(1200,500)
    frame.setFontSizeForPrint(9,widthPoints)
    #frame.setSize(1067,500)
    frame.setSize(1067,450)
  elif widthPoints==260.0:
    frame.setFontSizeForPrint(9,widthPoints)
    frame.setSize(1078,450)
  elif widthPoints==175.0:
    #frame.setFontSizeForPrint(8,widthPoints)
    #frame.setSize(1200,500)
    frame.setFontSizeForPrint(9,widthPoints)
    frame.setSize(1067,600)
  if title:
    frame.setTitle(title)
  frame.setVisible(True)
  if title and pngdatDir:
    if widthPoints is not None:
      frame.paintToPng(720,widthPoints/72.0,pngdatDir+title+'.png')
    else:
      #frame.paintToPng(360,3.0,pngdatDir+title+'.png')
      frame.paintToPng(720,3.08,pngdatDir+title+'.png')
      #write(pngdatDir+title+'.dat',f)

def read(name,image=None):
  if not image:
    image = zerofloat(nz,nx)
  fileName = name
  ais = ArrayInputStream(fileName)
  ais.readFloats(image)
  ais.close()
  return image

def write(fname,image):
  aos = ArrayOutputStream(fname)
  aos.writeFloats(image)
  aos.close()

def report(str,stopwatch):
  s = stopwatch.time()
  h = int(s/3600); s -= h*3600
  m = int(s/60); s -= m*60
  if h>0:
    print str+': %02d:%02d:%02d'%(h,m,s)
  else:
    print str+': %02d:%02d'%(m,s)

#############################################################################
# Do everything on Swing thread.
import sys,time
class RunMain(Runnable):
  def run(self):
    start = time.time()
    main(sys.argv)
    s = time.time()-start
    h = int(s/3600); s -= h*3600
    m = int(s/60); s -= m*60
    print '%02d:%02d:%02d'%(h,m,s)
if __name__=='__main__':
  SwingUtilities.invokeLater(RunMain())
