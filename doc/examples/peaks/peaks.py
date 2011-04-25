from __future__ import division
import sys
from math import degrees, radians, sin, cos


import numpy as np

from refl1d.mystic.parameter import Parameter

def plot(X,Y,theory,data,err):
    import pylab

    #print "theory",theory[1:6,1:6]
    #print "data",data[1:6,1:6]
    #print "delta",(data-theory)[1:6,1:6]
    fig=pylab.gcf()
    ax=fig.add_subplot(3,1,2)
    pylab.pcolormesh(X,Y, theory)
    ax=fig.add_subplot(3,1,1)
    pylab.pcolormesh(X,Y, data)
    ax=fig.add_subplot(3,1,3)
    pylab.pcolormesh(X,Y, (data-theory))

class Gaussian(object):
    def __init__(self, A=1, xc=0, yc=0, s1=1, s2=1, theta=0, name=""):
        self.A = Parameter(A,name=name+"A")
        self.xc = Parameter(xc,name=name+"xc")
        self.yc = Parameter(yc,name=name+"yc")
        self.s1 = Parameter(s1,name=name+"s1")
        self.s2 = Parameter(s2,name=name+"s2")
        self.theta = Parameter(theta,name=name+"theta")

    def parameters(self):
        return dict(A=self.A,
                    xc=self.xc, yc=self.yc,
                    s1=self.s1, s2=self.s2,
                    theta=self.theta)

    def __call__(self, x, y):
        height = self.A.value
        s1 = self.s1.value
        s2 = self.s2.value
        t  = -radians(self.theta.value)
        xc = self.xc.value
        yc = self.yc.value
        if s1==0 or s2==0: return np.zeros_like(x)
        a =  cos(t)**2/s1**2 + sin(t)**2/s2**2
        b = sin(2*t)*(-1/s1**2 + 1/s2**2)
        c =  sin(t)**2/s1**2 + cos(t)**2/s2**2
        xbar,ybar = x-xc,y-yc
        Zf = np.exp( -0.5*(a*xbar**2 + b*xbar*ybar + c*ybar**2) )
        #normalization=1.0/(2*np.pi*s1*s2)
        #print "norm",np.sum(Zf)*normalization
        total = np.sum(Zf)
        if np.isnan(total) or total==0:
            print "G(A,s1,s2,t,xc,yc) ->",total,(height,s1,s2,t,xc,yc)
            print "a,b,c",a,b,c
        return Zf/total*abs(height) if total>0 else np.zeros_like(x)

class Background(object):
    def __init__(self, C=0, name=""):
        self.C = Parameter(C,name=name+"background")
    def parameters(self):
        return dict(C=self.C)
    def __call__(self, x, y):
        return self.C.value

class Peaks(object):
    def __init__(self, parts, X, Y, data, err):
        self.X,self.Y,self.data,self.err = X, Y, data, err
        self.parts = parts

    def numpoints(self):
        return np.prod(self.data.shape)

    def parameters(self):
        return [p.parameters() for p in self.parts]

    def theory(self):
        #return self.parts[0](self.X,self.Y)
        #parts = [M(self.X,self.Y) for M in self.parts]
        #for i,p in enumerate(parts):
        #    if np.any(np.isnan(p)): print "NaN in part",i
        return sum(M(self.X,self.Y) for M in self.parts)

    def residuals(self):
        #if np.any(self.err ==0): print "zeros in err"
        return (self.theory()-self.data)/self.err

    def nllf(self):
        R = self.residuals()
        #if np.any(np.isnan(R)): print "NaN in residuals"
        return 0.5*np.sum(R**2)

    def __call__(self):
        return 2*self.nllf()/self.dof

    def plot(self):
        plot(self.X, self.Y, self.theory(), self.data, self.err)

    def save(self, basename):
        pass

    def update(self):
        pass
