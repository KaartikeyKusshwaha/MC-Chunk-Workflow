import dataclasses
from strata import blender_io

@dataclasses.dataclass
class AtmosphereConfig:
    location: tuple = (-150.0, 220.0, 700.0)
    dimensions: tuple = (9000.0, 9000.0, 2200.0)
    collection_name: str = "Strata Atmosphere"
    density: float = 0.02
    height_min: float = 0.0
    height_max: float = 1.0

def build_atmosphere(config: AtmosphereConfig = None) -> dict:
    if config is None:
        config = AtmosphereConfig()
    return blender_io.call("build_atmosphere", **dataclasses.asdict(config))
