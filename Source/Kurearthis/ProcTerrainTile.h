#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ProcTerrainTile.generated.h"

class UProceduralMeshComponent;

/**
 * A procedural displaced-mesh terrain tile (terrain chunk T2a; WORLD_MODEL.md terrain).
 *
 * Replaces the flat collision slab (ASurfacePatch) with REAL relief: a subdivided tangent
 * patch whose vertices are projected onto the sphere and displaced radially by a height
 * SOURCE, then given collision so the pawn grounds on the hills. The height source is
 * pluggable (T2 direction): the default is deterministic fBm Perlin noise (continuous
 * globally, so it is seamless across tiles for T2b), but a real-world DEM/OSM source
 * (T2d) plugs into SampleHeight() later without touching the mesh generation.
 *
 * Generate() builds the mesh + collision; call it after the actor transform + properties
 * are set (it reads the planet center by the "Planet" tag, surviving floating-origin
 * rebasing). Collision uses complex-as-simple so the pawn's capsule SWEEP grounds on it.
 */
UCLASS()
class KUREARTHIS_API AProcTerrainTile : public AActor
{
	GENERATED_BODY()

public:
	AProcTerrainTile();

	virtual void BeginPlay() override;

	/** Build (or rebuild) the displaced mesh + collision. Safe to call from editor Python. */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "ProcTerrain")
	void Generate();

	/** Height (cm) above the nominal surface radius at a world point on the sphere. */
	UFUNCTION(BlueprintCallable, Category = "ProcTerrain")
	double SampleHeight(const FVector& WorldSurfacePoint) const;

	UPROPERTY(VisibleAnywhere, Category = "ProcTerrain")
	UProceduralMeshComponent* Mesh;

	/** Planet whose center defines radial up. Found by the "Planet" tag if unset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	AActor* PlanetActor = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	FVector FallbackCenter = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	double SurfaceRadius = 637100000.0;

	/** Tile edge length along the surface (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	double TileSizeCm = 2000000.0;   // 20 km

	/** Grid subdivisions per side (vertices = Resolution+1 squared). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	int32 Resolution = 96;

	/** Peak radial displacement of the height source (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	double HeightAmplitudeCm = 40000.0;   // 400 m

	/** Wavelength of the largest noise octave (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	double NoiseBaseWavelengthCm = 400000.0;   // 4 km features

	/** fBm octaves. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	int32 Octaves = 4;

	/**
	 * If true, generate over a fixed longitude/latitude cell (for ASurfaceTileManager
	 * streaming) instead of the local tangent square. Adjacent cells then share EXACT edge
	 * vertices (same lon/lat → same world point → same height) so the grid has no cracks.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	bool bUseLonLatCell = false;

	/** Lon/lat cell corner + angular size (radians). Used when bUseLonLatCell. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	double CellLon0 = 0.0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	double CellLat0 = 0.0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ProcTerrain")
	double CellAngularSize = 0.0;

private:
	FVector GravityCenter() const;
};
