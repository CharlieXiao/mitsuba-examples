import drjit as dr
import matplotlib.pyplot as plt
import mitsuba as mi
import numpy as np

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
    "type": "roughdielectric",
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
theta_i = 85
phi_i = 0
# value must be longitude x latitude
wo, value = calculate_bsdf(rough_dielectric_bsdf, np.radians(theta_i), np.radians(phi_i), res, False)

# height * width?
# the desire shape is res,2*res
data = np.array(value)[:, 0].reshape(2 * res, res)

theta_out, phi_out = np.meshgrid(
    np.linspace(0, np.pi, res),
    np.linspace(0, 2 * np.pi, 2 * res)
)

fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

ax.contourf(phi_out, theta_out, data, extend="both", cmap='jet')
ax.plot(np.radians(phi_i), np.radians(theta_i), 'x', color='w', ms='10', mew=3)
plt.title("Light angle: {} degrees".format(theta_i))

plt.show()
