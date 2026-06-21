"""Proof 3 — surface → atmosphere → dark space. Add a planetary-scale SkyAtmosphere.

Configures and SAVES PlanetaryProof with a `SkyAtmosphere` whose planet matches
`ProofEarth`: planet center at the component transform (world origin, where ProofEarth's
center sits), BottomRadius = 6371 km (= ProofEarth surface), atmosphere height 100 km. So
the scattering shell wraps the real planet and you see the sky thin into black as you
rise. Marks `SurfaceSun` as the atmosphere sun light and puts `SurfaceSky` into real-time
capture so ambient comes from the atmosphere.

NOTE (honest limitation, recorded not hidden): stock `ExponentialHeightFog` is keyed to
WORLD-Z height, not radial altitude, so on a sphere where "up" varies it is only correct
at one point — it is NOT added here. SkyAtmosphere's aerial perspective already gives the
radial haze/thinning. A radial fog (if wanted) is future custom work.

  python _authoring/ue_remote.py --file _authoring/setup_atmosphere_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
ATMO_LABEL = "SurfaceAtmosphere"
SURFACE_R_KM = 6371.0          # = ProofEarth surface (6,371,000 m)
ATMO_HEIGHT_KM = 100.0

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    les.load_level(MAP_ASSET)

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())
by_label = {a.get_actor_label(): a for a in actors}

# Idempotent: drop any prior atmosphere from earlier runs.
for a in actors:
    if a.get_actor_label() == ATMO_LABEL:
        actor_sub.destroy_actor(a)

# The sun drives the atmosphere scattering.
sun = by_label.get("SurfaceSun")
if sun is not None:
    try:
        sun.light_component.set_editor_property("atmosphere_sun_light", True)
    except Exception as e:
        print("sun atmosphere_sun_light note:", e)

atmo = actor_sub.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
atmo.set_actor_label(ATMO_LABEL)
comp = atmo.get_component_by_class(unreal.SkyAtmosphereComponent)
comp.set_editor_property("transform_mode", unreal.SkyAtmosphereTransformMode.PLANET_CENTER_AT_COMPONENT_TRANSFORM)
comp.set_editor_property("bottom_radius", SURFACE_R_KM)
comp.set_editor_property("atmosphere_height", ATMO_HEIGHT_KM)

# Ambient from the atmosphere itself.
sky = by_label.get("SurfaceSky")
if sky is not None:
    try:
        sky.light_component.set_editor_property("real_time_capture", True)
    except Exception as e:
        print("skylight real_time_capture note:", e)

les.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_ATMO_SETUP bottom_radius={SURFACE_R_KM}km height={ATMO_HEIGHT_KM}km actors={labels}")
