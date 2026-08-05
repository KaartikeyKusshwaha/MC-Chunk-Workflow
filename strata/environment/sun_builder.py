import dataclasses
from strata import blender_io

@dataclasses.dataclass
class SunConfig:
    sun_mesh_scale: float = 35.7
    sun_mesh_location: tuple = (-695.4, -347.3, 280.2)
    sun_mesh_rotation: tuple = (1.672, 0.0, 2.172)
    emission_color: tuple = (1.0, 1.0, 1.0, 1.0)
    emission_strength: float = 3.0
    lamp_rotation: tuple = (0.908, 0.0, -2.601)
    lamp_strength: float = 3.0
    collection_name: str = "Strata Sun"

def build_sun(config: SunConfig = None) -> dict:
    if config is None:
        config = SunConfig()
    return blender_io.call("build_sun", **dataclasses.asdict(config))
