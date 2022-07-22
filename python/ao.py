import time
from typing import Tuple, List

import drjit as dr
import matplotlib.pyplot as plt
import mitsuba as mi
import numpy as np

mi.set_variant('llvm_ad_rgb')
mi.set_log_level(mi.LogLevel.Info)


class AmbientIntegrator(mi.SamplingIntegrator):
    def __init__(self, props: mi.Properties):
        super(AmbientIntegrator, self).__init__(props)
        # add your parameters here
        self.m_alpha = props.get("alpha", np.Inf)
        self.m_kd = props.get("kd", 0.5)
        self.m_hide_emitter = props.get("hide_emitter", True)

    def sample(self, scene: mi.Scene, sampler: mi.Sampler, ray: mi.RayDifferential3f,
               medium: mi.Medium = None, active: mi.Mask = True) -> Tuple[mi.Spectrum, mi.Mask, List[mi.Float]]:
        # using PyReturn = std::tuple<Spectrum, Mask, std::vector<Float>>;
        # the result value must be like this
        si: mi.SurfaceInteraction3f = scene.ray_intersect(ray, active)
        valid_ray: mi.Mask = si.is_valid()
        active &= si.is_valid()
        result = dr.zeros(mi.Spectrum)

        result[~valid_ray] = dr.select(self.m_hide_emitter, 0.0, 1.0)

        wi: mi.Vector3f = mi.warp.square_to_cosine_hemisphere(sampler.next_2d(active))
        pdf: mi.Float = mi.warp.square_to_cosine_hemisphere_pdf(wi)

        active &= pdf > 0.0
        if self.m_alpha == np.Inf:
            active &= ~scene.ray_test(si.spawn_ray(si.to_world(wi)), active)
        else:
            active &= ~scene.ray_test(si.spawn_ray_to(si.p + self.m_alpha * si.to_world(wi)))

        if dr.any(active):
            result[active] = self.m_kd * mi.Frame3f.cos_theta(wi) * (1.0 / np.pi) * dr.rcp(pdf)

        return result, valid_ray, []


mi.register_integrator("ao", lambda props: AmbientIntegrator(props))


def main():
    # scene = mi.load_dict(mi.cornell_box())
    scene = mi.load_file("../dragon/dragon-ao.xml")

    ao_integrator = mi.load_dict({
        'type': 'ao',
        'kd': 0.7,
        'hide_emitter': False,
        # 'alpha':0.5
    })

    # print("begin rendering...")
    # # render
    start_time = time.perf_counter_ns()
    img = mi.render(scene, integrator=ao_integrator, spp=256)
    bitmap = mi.Bitmap(img).convert(srgb_gamma=True)
    end_time = time.perf_counter_ns()
    print("done, total time:", (end_time - start_time) * 1e-9, 's')
    print("write bitmap to disk")
    bitmap.write("../dragon/dragon-python-ao.exr")
    plt.imshow(bitmap)
    plt.show()


if __name__ == "__main__":
    main()
