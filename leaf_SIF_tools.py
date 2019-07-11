#
# Copyright 2019 University of Virginia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Author: Xi Yang, xiyang@virginia.edu

# the first function is to read a spectrum txt file with standard output,
# and return the digital numbers, wavelengths, and the integration time

import numpy as np
import pandas as pd
import glob
from scipy.optimize import curve_fit
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def read_rawspec(path):
    
    files           = glob.glob(path)
    spectrum        = pd.DataFrame(columns=['wavelength'])
    IT              = pd.DataFrame(columns=['IT'])
    file_i          = 0
    IT['IT']        = [0.0]
    
    for file in files:
        
        # First read the IT
        text_file                   = open(file,'r')
        lines                       = text_file.readlines()
        
        IT.insert(file_i+1,'IT'+str(file_i),float(lines[6][24:-1]))
        
        # Read the spectrum and wavelength
        raw                         = np.loadtxt(file,delimiter='\t',skiprows =14)
        spectrum.insert(file_i+1,'DN'+str(file_i), raw[:,1])
        spectrum['wavelength']      = raw[:,0]
        
        file_i                      = file_i + 1 

        
    return spectrum, IT

def SIF_SFM(leaf_radiance,panel_radiance,wavelength):
    # For simplicity, we just use a simple version of SIF retrieval based on SFM
    o2a_index = (wavelength > 759.00) & (wavelength < 767.76)
    plot_index= (wavelength > 730.00) & (wavelength < 780.00)
    b755_index= (wavelength > 754.00) & (wavelength < 756.00)
    s_bands = wavelength[o2a_index]
    p_value = panel_radiance[o2a_index]
    xdata = np.zeros((2, len(s_bands)))
    xdata[0, :], xdata[1, :] = s_bands, p_value
    ydata = leaf_radiance[o2a_index]
    x0 = [0.1, 0.1, 0.1, 0.1]
    popt, pcov = curve_fit(fit_o2a, xdata, ydata, p0=x0, method='lm',
                           xtol=1e-10, ftol=1e-10)
    wl = 760.0
    sif_o2a = popt[2] + wl * popt[3]
    # assuming that the panel radiance values have already been multiplied by Pi
    refl    = leaf_radiance/panel_radiance
    irra755 = np.mean(panel_radiance[b755_index])
    rad755  = np.mean(leaf_radiance[b755_index])
    
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax0 = fig.add_subplot(211)

    ax0.plot(wavelength[plot_index], refl[plot_index], color='r')
    ax0.set_ylabel('reflectance, PI*VEG/SKY')
    ax0.set_title("SIF760=%5.2f; Rad755=%.2f"% (sif_o2a, rad755), fontsize=9)
    ax0.locator_params(nbins=5, axis='y')

    ax1 = fig.add_subplot(212, sharex=ax0)
    ax2 = ax1.twinx()
    lns1 = ax1.plot(wavelength[plot_index], leaf_radiance[plot_index],
                    label='leaf', color='m')
    lns2 = ax2.plot(wavelength[plot_index], panel_radiance[plot_index],
                    label='panel', color='k')

    ax1.locator_params(nbins=5, axis='y')
    ax2.locator_params(nbins=5, axis='y')
    ax1.set_xlabel('Wavelength(nm)')
    ax1.set_ylabel('leaf, W/m2/nm/sr', color='m')
    ax2.set_ylabel('panel, W/m2/nm', color='k')
    ax1.tick_params('y', colors='m')
    ax2.tick_params('y', colors='k')
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0)

    frame = ax1.get_legend().get_frame()
    frame.set_linewidth(0.5)

#    fig.text(0.5, 0.95, dt, horizontalalignment='center', transform=ax0.transAxes)

    fig.subplots_adjust()
    
    return (sif_o2a,fig)

def DNtoRad(light,dark,intTime,calib_factor,calib_intTime):
    
    int_conv     = np.divide(calib_intTime,intTime)
    cal_spec     = np.array(calib_factor * int_conv[0])
    radiance     = (light - dark) * cal_spec
    
    return radiance

def fit_o2a(xdata, a, b, c, d):
    ''' LL-fit

    L(w) = r(w)*E(w)/pi + F(w)
    w     :  wavelength
    r     :  reflectance, don't include the emission component
    E     :  total solar irradiance incident on the target
    F     :  fluorescence

    L(w) = r_mod(w)*E(w)/pi + F_mod(w) + error(w)
    r_mod :  r_mod(w) = a + b*w ; linear
    F_mod :  F_mod(w) = c + d*w ; linear

    L(w) = (a + b*w)*E(w) / pi + c + d*w

    '''

    # O2A we use linear for Fmod, linear for rmod
    L = (a + b * xdata[0, :]) * xdata[1, :] / np.pi + c + xdata[0, :] * d

    # incoming radiance measured by reflectance panel
    # f = (x(1)+xdata(1,:).*x(2)).*xdata(2,:) + (x(3)+xdata(1,:).*x(4));

    return L

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    