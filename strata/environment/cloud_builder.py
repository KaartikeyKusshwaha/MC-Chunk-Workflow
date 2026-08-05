import dataclasses
from strata import blender_io

@dataclasses.dataclass
class CloudConfig:
    height: float = 19.3
    dimensions: tuple = (2008.22, 2.07, 2008.22)
    rotation_euler: tuple = (1.5708, 0.0, 3.1416)  # 90°, 0°, 180°
    collection_name: str = "P1 Clouds"
    material_name: str = "Strata Cloud"
    principled_roughness: float = 0.38
    coat_weight: float = 0.22
    coat_roughness: float = 0.14
    emission_strength: float = 0.5
    mix_fac: float = 0.3
    bevel_radius: float = 0.05
    noise_scale: float = 120.0
    noise_detail: float = 2.0
    bump_strength: float = 0.018
    bump_distance: float = 0.006

def build_clouds(config: CloudConfig = None) -> dict:
    if config is None:
        config = CloudConfig()
    return blender_io.call("build_clouds", **dataclasses.asdict(config))
