import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import mitsuba as mi
import drjit as dr

mi.set_variant('llvm_ad_rgb')

diffuse_reflectance_bsdf = mi.load_dict({
    'type': 'diffuse'
})

rough_conductor_bsdf = mi.load_dict({
    'type': 'roughconductor',
    'alpha': 0.2,
    'distribution': 'ggx'
})

rough_dielectric_bsdf = mi.load_dict({
    "type":"roughdielectric",
    "distribution": "ggx",
    "alpha": 0.2,
    "int_ior": "bk7",
    "ext_ior": "air"
})


def sph_to_dir(theta, phi):
    sin_theta, cos_theta = dr.sincos(theta)
    sin_phi, cos_phi = dr.sincos(phi)
    return mi.Vector3f(cos_phi * sin_theta, sin_phi * sin_theta, cos_theta)


def calculate_bsdf(bsdf, theta_in: float, phi_in: float, res: int = 50, remove_cos: bool = True):
    si = dr.zeros(mi.SurfaceInteraction3f)
    si.wi = sph_to_dir(theta_in, phi_in)
    # ths shape is [2*res,res] ?
    theta_out, phi_out = dr.meshgrid(
        dr.linspace(mi.Float, 0, dr.pi, res),
        dr.linspace(mi.Float, 0, 2 * dr.pi, 2 * res)
    )

    wo = sph_to_dir(theta_out, phi_out)

    if remove_cos:
        # 当 cos_theta < 1e3 || cos_theta > 1e-3 时直接返回0
        rcp_cos_theta_o = dr.rcp(mi.Frame3f.cos_theta(wo))
        rcp_cos_theta_o[(rcp_cos_theta_o > 1e3) & (rcp_cos_theta_o < -1e3)] = 0

        value = bsdf.eval(mi.BSDFContext(), si, wo)
        sign = dr.sign(value)
        return wo, sign * dr.abs(value * rcp_cos_theta_o)
    else:
        return wo, bsdf.eval(mi.BSDFContext(), si, wo)


res = 300
theta_i = 45
phi_i = 0
# value must be longitude x latitude
wo, value = calculate_bsdf(rough_dielectric_bsdf, np.radians(theta_i), np.radians(phi_i), res, False)

# height * width?
# the desire shape is res,2*res
data = np.array(value)[:, 0].reshape(2 * res, res).T

# lat_long

# lat_long_data =
print(data.shape)

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"

colorbar = True
title = f"{'rough_dielectric[alpha=0.2,dis=ggx]'} BSDF Plot with $\\theta_i$ = {theta_i} $\\phi_i$ = {phi_i}"
# data = np.load("example_data/conductor_ggx_0.2_60.npy")

print(data.shape)

fig, ax = plt.subplots(figsize=(8, 4))

im = ax.imshow(data, extent=[0, 2 * np.pi, np.pi, 0], cmap='jet')

plt.xlabel(r'$\phi_o$', size=14, ha='center', va='top')
l = plt.ylabel(r'$\theta_o$', size=14, ha='right', va='center')
l.set_rotation(0)
ax.set_xticks([0, np.pi, 2 * np.pi])
ax.set_xticklabels(['0', '$\\pi$', '$2\\pi$'])
ax.set_yticks([0, np.pi / 2, np.pi])
ax.set_yticklabels(['0', '$\\pi/2$', '$\\pi$'])

if title:
    plt.title(title, size=10, weight='bold')

if colorbar:
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.1)
    plt.colorbar(im, cax=cax)

plt.show()
