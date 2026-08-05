import dataclasses
from strata import blender_io

@dataclasses.dataclass
class SkyConfig:
    world_name: str = "Strata World"
    hdri_path: str = ""
    hdri_rotation: tuple = (0.0, 0.0, 0.0)
    zenith_color: tuple = (0.28, 0.46, 0.76, 1.0)
    horizon_color: tuple = (0.85, 0.9, 0.95, 1.0)
    environment_strength: float = 1.0
    use_camera_sky: bool = True

def build_sky(config: SkyConfig = None) -> dict:
    if config is None:
        config = SkyConfig()
    return blender_io.call("build_sky", **dataclasses.asdict(config))
