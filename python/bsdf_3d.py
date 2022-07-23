import drjit as dr
import matplotlib.pyplot as plt
import mitsuba as mi
import numpy as np

mi.set_variant('llvm_ad_rgb')

# bsdf
diffuse_reflectance_bsdf = mi.load_dict({
    'type': 'diffuse'
})

rough_conductor_bsdf = mi.load_dict({
    'type': 'roughconductor',
    'alpha': 0.2,
    'distribution': 'ggx'
})

rough_dielectric_bsdf = mi.load_dict({
    "type": "roughdielectric",
    "distribution": "ggx",
    "alpha": 0.2,
    "int_ior": "bk7",
    "ext_ior": "air"
})


def sph_to_dir(theta, phi):
    """Map spherical to Euclidean coordinates"""
    st, ct = dr.sincos(theta)
    sp, cp = dr.sincos(phi)
    return mi.Vector3f(cp * st, sp * st, ct)


# Create a (dummy) surface interaction to use for the evaluation of the BSDF
si = dr.zeros(mi.SurfaceInteraction3f)

theta_in = 89
phi_in = 0


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

# 1D array to 2D make it a mesh
wo, data = calculate_bsdf(rough_dielectric_bsdf, np.radians(theta_in), np.radians(phi_in), res, False)

points = wo * data

np_data = np.array(points).reshape((res,res*2,3))
# np_data = np.array(points).reshape((res,res*2,3))

print(np_data.shape)

fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], projection='3d')
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-2, 2)

# ax.scatter(np_data[:, 0], np_data[:, 1], np_data[:, 2], cmap='jet')

ax.plot_surface(np_data[:,:,0],np_data[:,:,1], np_data[:,:,2], cmap='jet'
#   # ,rstride=res, cstride=res*2
)

wi = np.array(sph_to_dir(np.radians(theta_in), np.radians(phi_in))).flatten()

print(wi)

ax.plot([wi[0], 0], [wi[1], 0], [wi[2], 0])

plt.title("$\\theta_i$ {} degrees".format(theta_in))

plt.show()
