#!/usr/bin/env/ python3
"""vortex detection tool, by Guilherme Lindner, 2017-04\n
This program load NetCDF files from DNS simulations  or PIV experiments
and detect the vortices and apply a fitting to them.
"""
import sys
import argparse
import time
import numpy as np

from classes import VelocityField
import tools
import fitting
import plot
import schemes
import detection

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Optional app description',
                                     formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('-i', '--input', dest='infilename',
                        default='../data/test_data.nc',
                        help='input NetCDF file', metavar='FILE')
                        
    parser.add_argument('-o', '--output', dest='outfilename',
                        help='output NetCDF file', metavar='FILE')
    
    parser.add_argument('-s', '--scheme', dest='scheme', type=int, default=2,
                        help='Scheme for differencing\n'
                             '2 = second order\n'
                             '22 = least-square filter'
                             '4 = fourth order')
    
    parser.add_argument('-T', '--time', dest='timestep', type=int,
                        default=0,
                        help='Timestep/Sample desired')
                        
    parser.add_argument('-d', '--detect', dest='detect',
                        default='swirling',
                        help='Detection method:\n'
                             'Q = Q criterion\n'
                             'delta = delta criterion\n'
                             'swirling = 2D Swirling Strength')
    
    parser.add_argument('-t', '--threshold', dest='threshold',
                        default=0.0, type=float,
                        help='Threshold for detection, integer')

    parser.add_argument('-b', '--boxsize', dest='boxsize',
                        default=6, type=int,
                        help='Box size for the detection')
    
    parser.add_argument('-f', '--flip', dest='flip',
                        default=True, type=bool,
                        help='Flip X and Y axis for plotting, 0 = False, 1 = True')
                        
    parser.add_argument('-n', '--nofit', dest='nofit',
                        default=False, type=bool,
                        help='Disables fitting procedure')
    
    parser.add_argument('-p', '--plot', dest='plot_x',
                        default='',
                        help='Plot on screen:\n'
                             'detect = Vortices position\n'
                             'fields = Velocity fields\n'
                             'quiver = Vector on specific position')
    
    args = parser.parse_args()
    
    start = time.time()
    #---- LOAD DATA ----#
    print("Opening file:",args.infilename)

    #print("Sample target: (todo)", args.timestep)
    
    a = VelocityField(args.infilename,args.timestep)
    print("Samples:", a.samples)

    #---- DIFFERENCE APPROXIMATION ----# 
    lap = time.time()
    if args.scheme == 4:
        a.derivative = schemes.fourth_order_diff(a)
    elif args.scheme == 2:
        a.derivative = schemes.second_order_diff(a)
    elif args.scheme == 22:
        a.derivative = schemes.least_square_diff(a)
    else:
        print('No scheme', args.scheme, 'found. Exitting!')
        sys.exit()
    #print(round(time.time() - lap,3), 'seconds') 
    
    #---- VORTICITY ----#

    vorticity = a.derivative['dvdx'] - a.derivative['dudy']

    #---- METHOD FOR DETECTION OF VORTICES ----#
    lap = time.time()
    if args.detect == 'Q':
        swirling = detection.q_criterion(a)
    elif args.detect == 'swirling':
        swirling = detection.calc_swirling(a)
    elif args.detect == 'delta':
        swirling = detection.delta_criterion(a)
    #print(round(time.time() - lap,3), 'seconds')

    if a.norm == True:
        swirling = swirling/(np.std(swirling))
        #vorticity = vorticity/(np.std(vorticity))
        #swirling = tools.normalize(swirling,a.normdir) #normalization
        #vorticity = tools.normalize(vorticity,a.normdir)
    print(vorticity[1,1])
    
    #---- PEAK DETECTION ----#
    print("threshold=",args.threshold,"box size=",args.boxsize)

    peaks = tools.find_peaks(swirling, args.threshold, args.boxsize)

    print("Vortices found:",len(peaks[0]))

    #---- PEAKS DIRECTION OF ROTATION ----#
    dirL, dirR = tools.direction_rotation(vorticity,peaks)

    #---- MODEL FITTING ----# SEE IN PLOT
    vortices = list()
    if (args.nofit == True):
        print("No fitting")
    else:
        vortices = fitting.get_vortices(a,peaks,vorticity)
        print('---- Accepted vortices ----')
        print(len(vortices))
        print(vortices)
    #print('xCenter, yCenter, gamma, core Radius, correlation, mesh distance')
    #for vortex in vortices:
    #    print(vortex)

    #---- SAVING OUTPUT FILE ----#
    if args.outfilename == None:
        pass
    else:
        print("saving file",args.outfilename)
    
  
    #---- PLOTTING OPTIONS ----#
    if args.plot_x == 'detect':
        plot.plot_detection(dirL,dirR,swirling,args.flip)
    elif args.plot_x == 'fields':
        plot.plot_fields(a,vorticity)
    elif args.plot_x == 'fields2':
        plot.plot_fields2(a,vorticity,args.flip)
    elif args.plot_x == 'quiverRuim':
        dist = 10
        for i in range(len(peaks[0])):
            xCenter = peaks[0][i]
            yCenter = peaks[1][i]
            X, Y, Uw, Vw = tools.window(a,xCenter,yCenter,dist)
            swirlingw = swirling[xCenter-dist:xCenter+dist,yCenter-dist:yCenter+dist] #reuse window function?
            if (xCenter > dist) and (yCenter > dist):
                print('x1:',xCenter,'x2:',yCenter, 'swirl:',peaks[2][i])
                plot.plot_quiver(X, Y, Uw, Vw, swirlingw)
    elif args.plot_x == 'quiver':
        #for i in range(len(vortices)):
        #    swirlingw = swirling[vortices[i][0]-vortices[i][5]:vortices[i][0]+vortices[i][5],
        #      vortices[i][1]-vortices[i][5]:vortices[i][1]+vortices[i][5]]
        #    X, Y, Uw, Vw = tools.window(a,vortices[i][0],vortices[i][1],vortices[i][5])
        #    uMod, vMod = fitting.velocity_model(vortices[i][3], vortices[i][2],
        #     vortices[i][6], vortices[i][7], vortices[i][8], vortices[i][9], X, Y)
            X, Y, Uw, Vw = tools.window(a,235,58,15)
            plot.plot_quiver(X, Y, Uw, Vw, swirling)
                
    elif args.plot_x == 'fit':
        outfile = open('../results/vortices.dat','w')
        outfile.write('X Y gamma radius corr mesh x y u_c v_c \n')
        for line in vortices:
            outfile.write("%s %s %s %s %s %s %s %s %s %s \n" % line)
        for i in range(len(vortices)):
            print('xC:',vortices[i][0],'yC:',vortices[i][1], 'vort:',vortices[i][2],
             'mesh',vortices[i][5], 'corr',vortices[i][4], 'coreR',vortices[i][3],
             'u_conv',vortices[i][8],'v_conv',vortices[i][9])
            X, Y, Uw, Vw = tools.window(a,vortices[i][0],vortices[i][1],vortices[i][5]*2)
            uMod, vMod = fitting.velocity_model(vortices[i][3], vortices[i][2],
             vortices[i][6], vortices[i][7], vortices[i][8], vortices[i][9], X, Y)
            corr = fitting.correlation_coef(Uw,Vw,uMod,vMod)
            #Uw = Uw / np.sqrt(Uw**2 + Vw**2);
            #Vw = Vw / np.sqrt(Uw**2 + Vw**2);
            plot.plot_corr(X, Y, Uw, Vw, uMod, vMod, vortices[i][6],
                          vortices[i][7], vortices[i][3], vortices[i][4],i)
            dx = a.dx[2]-a.dx[1]
            dy = a.dy[2]-a.dx[1]
            temp_x = int(round(vortices[i][6]/dx,0))

            temp_y = int(round(vortices[i][7]/dy,0))
            temp_y = temp_y + 1
            print(vortices[i][0],'->',temp_x,vortices[i][1],'->',temp_y)
            
    elif args.plot_x == 'radius':
        plot.plot_radius(vortices)
    
    else:
        print('no plot')
