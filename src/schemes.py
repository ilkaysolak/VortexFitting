"""Finite differences schemes
"""

import numpy as np

def second_order_diff(a):
    """Second order accurate finite difference scheme.
    
    Scheme 1:0:-1
    
    Args:
        a: 2D array of the velocity field, containing u and v
    
    Returns:
        All the spatial derivatives, dudx, dudy, dvdx and dvdy
        For example:
        a.derivative['dudx']
    """
    #x, y = np.meshgrid(a.dx,a.dy)
    dx = a.dx[1]-a.dx[0] #only for homogeneous mesh
    dy = a.dy[1]-a.dy[0] #only for homogeneous mesh
    #print('dx,dy',dx,dy)
    a.derivative['dudx'], a.derivative['dudy'] = np.gradient(a.u,dx)
    a.derivative['dvdx'], a.derivative['dvdy'] = np.gradient(a.v,dy)
    return a.derivative

def least_square_diff(a): #there is a problem on the boundary
    """Fourth order accurate finite difference scheme.
    Least-square filter (Raffel 1998)
    
    Scheme -2:-1:0:1:2
    
    Args:
        a: 2D array of the velocity field, containing u and v
    
    Returns:
        All the spatial derivatives, dudx, dudy, dvdx and dvdy
        For example:
        a.derivative['dudx']
    """
    print("Difference scheme: least-square filter")
    dx = a.dx[1]-a.dx[0] #only for homogeneous mesh
    dy = a.dy[1]-a.dy[0] #only for homogeneous mesh
    a.derivative['dudx'][2:-2,:] = (-2*a.u[0:-4,:] - a.u[1:-3,:] + a.u[3:-1,:] + 2*a.u[4:,:])/(10*dx)
    a.derivative['dudy'][:,2:-2] = (-2*a.u[:, 0:-4] - a.u[:,1:-3]+ a.u[:, 3:-1] + 2*a.u[:,4:])/(10*dy)
    a.derivative['dvdx'][2:-2,:] = (-2*a.v[0:-4,:] - a.v[1:-3,:] + a.v[3:-1,:] + 2*a.v[4:,:])/(10*dx)
    a.derivative['dvdy'][:,2:-2] = (-2*a.v[:, 0:-4] - a.v[:,1:-3]+ a.v[:, 3:-1] + 2*a.v[:,4:])/(10*dy)

    return a.derivative
    

def fourth_order_diff(a):
    """Fourth order accurate finite difference scheme.
    
    Scheme: 1:-8:0:8:-1
    
    Args:
        a: 2D array of the velocity field, containing u and v
    
    Returns:
        All the spatial derivatives, dudx, dudy, dvdx and dvdy
        For example:
        a.derivative['dudx']
    """
    print("Beginning differenciation with Fourth Order Scheme")
    dx = a.dx[1]-a.dx[0] #only for homogeneous mesh
    dy = a.dy[1]-a.dy[0] #only for homogeneous mesh
    a.derivative['dudx'][2:-2,:] = (a.u[0:-4,:] -8*a.u[1:-3,:] + 8*a.u[3:-1,:] - a.u[4:,:])/(12*dx)
    a.derivative['dudy'][:,2:-2] = (a.u[:, 0:-4] -8*a.u[:,1:-3]+ 8*a.u[:, 3:-1] - a.u[:,4:])/(12*dy)
    a.derivative['dvdx'][2:-2,:] = (a.v[0:-4,:] -8*a.v[1:-3,:] + 8*a.v[3:-1,:] - a.v[4:,:])/(12*dx)
    a.derivative['dvdy'][:,2:-2] = (a.v[:, 0:-4] -8*a.v[:,1:-3]+ 8*a.v[:, 3:-1] - a.v[:,4:])/(12*dy)

    return a.derivative
