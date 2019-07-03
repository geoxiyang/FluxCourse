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

def read_rawspec(path):
    
    files           = glob.glob(path)
    spectrum        = pd.DataFrame(columns=['wavelength'])
    IT              = pd.DataFrame(columns=['IT'])
    file_i          = 0
    
    for file in files:
        
        # First read the IT
        text_file                   = open(file,'r')
        lines                       = text_file.readlines()
                
        IT.insert(file_i,'IT'+str(file_i),float(lines[6][24:-1]))
        
        # Read the spectrum and wavelength
        raw                         = np.loadtxt(file,delimiter='\t',skiprows =14)
        spectrum.insert(file_i+1,'DN'+str(file_i), raw[:,1])
        spectrum['wavelength']      = raw[:,0]
        
        file_i                      = file_i + 1 

        
    return spectrum, IT
