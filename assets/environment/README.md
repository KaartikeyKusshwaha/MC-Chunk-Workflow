# Environment Assets

This directory contains assets and documentation for the environment pipeline (clouds, atmosphere, sky, sun).

## HDRI
The default HDRI for the world sky is `kloofendal_overcast_puresky_1k.exr`.
You can download it from [Polyhaven](https://polyhaven.com/a/kloofendal_overcast_puresky).

## Clouds
The cloud meshes are generated procedurally by the pipeline in Blender using the handlers in the bridge server. There is no pre-built mesh required! The cloud footprint and material setup is built on-the-fly.

## Configuration
You can customize the defaults for these environment elements by passing a configuration dictionary to the Strata SDK when calling the relevant pipeline functions.
