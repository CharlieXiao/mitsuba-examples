import numpy as np
import matplotlib.pyplot as plt

import sys
import os

MI_DIR="/Users/charliexiao/CLionProjects/mitsuba3/build/release"

sys.path.insert(0,os.path.join(MI_DIR,"python"))
os.environ['PATH'] = MI_DIR+":"+os.environ['PATH']

import mitsuba as mi
import drjit as dr

mi.set_variant('llvm_rgb')

# enable interactivate mode
# plt.ion()

# bsdf
diffuse_bsdf = mi.load_dict({
  'type':'diffuse',
  'reflectance':{
    'type':'rgb',
    'value':[0.5,0.5,0.5]
  }
})

roughconductor_bsdf = mi.load_dict({
    'type': 'roughconductor',
    'alpha': 0.2,
    'distribution': 'ggx'
})

roughdielectric_bsdf = mi.load_dict({
  'type':'roughdielectric',
  'alpha':0.05,
  'distribution':'ggx'
})

def sph_to_dir(theta, phi):
    """Map spherical to Euclidean coordinates"""
    st, ct = dr.sincos(theta)
    sp, cp = dr.sincos(phi)
    return mi.Vector3f(cp * st, sp * st, ct)

# Create a (dummy) surface interaction to use for the evaluation of the BSDF
si = dr.zeros(mi.SurfaceInteraction3f)

theta_in = np.radians(45.0)
phi_in = 0

# Specify an incident direction with 45 degrees elevation
si.wi = sph_to_dir(theta_in,phi_in)

def calculate_brdf_surface(si:mi.SurfaceInteraction3f,bsdf,res:int=50,remove_cos:bool=True):
    theta_o, phi_o = dr.meshgrid(
        dr.linspace(mi.Float, 0,     dr.pi,     res),
        dr.linspace(mi.Float, 0, 2 * dr.pi, 2 * res)
    )

    wo = sph_to_dir(theta_o, phi_o)
    
    if remove_cos:
      # 当 cos_theta < 1e3 || cos_theta > 1e-3 时直接返回0
      rcp_cos_theta_o = dr.rcp(mi.Frame3f.cos_theta(wo))
      res = (rcp_cos_theta_o > 1e3) & (rcp_cos_theta_o < -1e3)
      # print(help(res))
      # print(type(res),res)
      rcp_cos_theta_o[res] = 0

      value = bsdf.eval(mi.BSDFContext(), si, wo)
      sign = dr.sign(value)
      return wo * sign * dr.abs( value * rcp_cos_theta_o )
    else:
      return wo * bsdf.eval(mi.BSDFContext(), si, wo)

res = 20

# 1D array to 2D make it a mesh
points = calculate_brdf_surface(si,roughdielectric_bsdf,res)

np_data = np.array(points)
# np_data = np.array(points).reshape((res,res*2,3))

print(np_data.shape)

fig = plt.figure()
ax = fig.add_axes([0.1,0.1,0.8,0.8],projection='3d')
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-2, 2)


ax.scatter(np_data[:,0],np_data[:,1],np_data[:,2],cmap='viridis')

# ax.plot_surface(np_data[:,:,0],np_data[:,:,1], np_data[:,:,2], cmap='viridis'
#   # ,rstride=res, cstride=res*2
# )

wi = 3 * np.array(si.wi).flatten()

ax.plot([wi[0],0],[wi[1],0],[wi[2],0])

plt.title("Light angle {} degrees".format(np.rad2deg(theta_in)))

plt.show()