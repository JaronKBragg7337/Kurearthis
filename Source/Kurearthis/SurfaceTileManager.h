#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurfaceTileManager.generated.h"

class AProcTerrainTile;

/**
 * Streamed grid of FIXED surface tiles for seamless infinite roaming (PLANETARY_PROOF
 * 2i; WORLD_MODEL.md terrain streaming).
 *
 * The planet cannot be one giant collision mesh (2c/2d). A single follower tile keeps
 * the player grounded but glues the ground to the player, so there is no sense of
 * motion (Jaron hit this, 2h). The fix: a small grid (e.g. 3x3) of tiles FIXED in world
 * space that load ahead / unload behind as the player crosses tile boundaries — the
 * ground under the player is always solid AND never runs out, while each tile stays put
 * so walking feels right.
 *
 * Tiles are placed on a deterministic spherical lattice: each cell (i,j) maps to a fixed
 * longitude/latitude band, hence a fixed world position + orientation. So the same
 * physical region always maps to the same tile — tiles never shift once placed, only
 * spawn/despawn. (Lat/long has a pole singularity; the proof operates near the equator
 * where it is locally uniform — recorded, not hidden.)
 *
 * Ticks in TG_PrePhysics (before the pawn's grounding sweep in TG_DuringPhysics) so the
 * tiles around the pawn always exist before it tries to stand on them. Reads the planet
 * center by the "Planet" tag and the player by the "Focus" tag, so it survives
 * floating-origin rebasing.
 */
UCLASS()
class KUREARTHIS_API ASurfaceTileManager : public AActor
{
	GENERATED_BODY()

public:
	ASurfaceTileManager();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

	/** Player the grid stays centered on. Found by the "Focus" tag if unset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	AActor* Focus = nullptr;

	/** Planet whose center defines radial up. Found by the "Planet" tag if unset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	AActor* PlanetActor = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	FVector FallbackCenter = FVector::ZeroVector;

	/** Surface radius (cm); tile top faces are kept at this distance from center. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	double SurfaceRadius = 637100000.0;

	/** Edge length of one tile cell along the surface (cm). Default 5 km. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	double TileSizeCm = 500000.0;

	/** Rings of tiles kept around the focus cell. 1 -> 3x3, 2 -> 5x5. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	int32 GridRadius = 1;

	/** Grid subdivisions per streamed terrain tile. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	int32 TileResolution = 32;

	/** Peak radial terrain displacement (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	double HeightAmplitudeCm = 40000.0;

	/** Largest noise-octave wavelength (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	double NoiseBaseWavelengthCm = 400000.0;

	/** Max tiles to generate per tick — spreads high-res mesh gen so a crossing/startup does
	 *  not spike the frame (L1). Tiles cook collision async; the focus cell is generated first. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TileGrid")
	int32 MaxSpawnsPerTick = 1;

private:
	UPROPERTY()
	TMap<FIntPoint, AProcTerrainTile*> ActiveTiles;

	TArray<FIntPoint> PendingCells;   // cells queued to generate (closest-to-focus first)

	bool bHasCell = false;
	FIntPoint CurrentCell = FIntPoint::ZeroValue;
	int32 TotalSpawned = 0;
	int32 TotalDestroyed = 0;
	FString StatePath;

	FVector GravityCenter() const;
	FIntPoint CellOf(const FVector& WorldPos) const;
	FVector CellDir(const FIntPoint& Cell) const;
	void RebuildAround(const FIntPoint& Center);
	AProcTerrainTile* SpawnTile(const FIntPoint& Cell);
	void WriteState();
};
