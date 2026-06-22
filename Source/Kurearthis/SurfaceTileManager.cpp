#include "SurfaceTileManager.h"

#include "ProcTerrainTile.h"
#include "Kismet/GameplayStatics.h"
#include "Math/RotationMatrix.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"

ASurfaceTileManager::ASurfaceTileManager()
{
	PrimaryActorTick.bCanEverTick = true;
	// Place/stream tiles before the pawn's grounding sweep (TG_DuringPhysics) runs.
	PrimaryActorTick.TickGroup = TG_PrePhysics;
}

FVector ASurfaceTileManager::GravityCenter() const
{
	return PlanetActor ? PlanetActor->GetActorLocation() : FallbackCenter;
}

// Cell index of a world position: longitude/latitude bands of angular size TileSizeCm/R.
FIntPoint ASurfaceTileManager::CellOf(const FVector& WorldPos) const
{
	const FVector Up = (WorldPos - GravityCenter()).GetSafeNormal();
	if (Up.IsNearlyZero())
	{
		return FIntPoint::ZeroValue;
	}
	const double Theta = FMath::Atan2(Up.Y, Up.X);                       // longitude
	const double Phi = FMath::Asin(FMath::Clamp((double)Up.Z, -1.0, 1.0)); // latitude
	const double DAng = TileSizeCm / SurfaceRadius;
	return FIntPoint(FMath::FloorToInt(Theta / DAng), FMath::FloorToInt(Phi / DAng));
}

// Outward unit direction to the CENTER of a cell — deterministic, so a tile never moves.
FVector ASurfaceTileManager::CellDir(const FIntPoint& Cell) const
{
	const double DAng = TileSizeCm / SurfaceRadius;
	const double Theta = (Cell.X + 0.5) * DAng;
	const double Phi = (Cell.Y + 0.5) * DAng;
	const double CosPhi = FMath::Cos(Phi);
	return FVector(CosPhi * FMath::Cos(Theta), CosPhi * FMath::Sin(Theta), FMath::Sin(Phi)).GetSafeNormal();
}

void ASurfaceTileManager::BeginPlay()
{
	Super::BeginPlay();

	StatePath = FPaths::ProjectSavedDir() / TEXT("TileGrid.json");
	IFileManager::Get().Delete(*StatePath, false, true, true);

	if (!PlanetActor)
	{
		TArray<AActor*> Found;
		UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Planet"), Found);
		if (Found.Num() > 0)
		{
			PlanetActor = Found[0];
		}
	}
	if (!Focus)
	{
		TArray<AActor*> Found;
		UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Focus"), Found);
		if (Found.Num() > 0)
		{
			Focus = Found[0];
		}
	}
}

AProcTerrainTile* ASurfaceTileManager::SpawnTile(const FIntPoint& Cell)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}

	const double DAng = TileSizeCm / SurfaceRadius;
	const FVector Dir = CellDir(Cell);
	const FVector Center = GravityCenter();
	const FVector Loc = Center + Dir * SurfaceRadius;   // cell-center surface point
	const FTransform Xform(FRotationMatrix::MakeFromZ(Dir).Rotator(), Loc);

	// Deferred spawn so the lon/lat cell params are set BEFORE BeginPlay generates the
	// mesh. Adjacent cells share exact edge vertices (same lon/lat) → no cracks; the
	// world-space height source is continuous → no cliffs at borders.
	AProcTerrainTile* Tile = World->SpawnActorDeferred<AProcTerrainTile>(
		AProcTerrainTile::StaticClass(), Xform, this, nullptr,
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Tile)
	{
		return nullptr;
	}
	Tile->PlanetActor = PlanetActor;
	Tile->SurfaceRadius = SurfaceRadius;
	Tile->TileSizeCm = TileSizeCm;
	Tile->Resolution = TileResolution;
	Tile->HeightAmplitudeCm = HeightAmplitudeCm;
	Tile->NoiseBaseWavelengthCm = NoiseBaseWavelengthCm;
	Tile->bUseLonLatCell = true;
	Tile->CellLon0 = Cell.X * DAng;
	Tile->CellLat0 = Cell.Y * DAng;
	Tile->CellAngularSize = DAng;

	UGameplayStatics::FinishSpawningActor(Tile, Xform);   // BeginPlay -> Generate()

#if WITH_EDITOR
	Tile->SetActorLabel(FString::Printf(TEXT("Tile_%d_%d"), Cell.X, Cell.Y));
#endif

	++TotalSpawned;
	return Tile;
}

void ASurfaceTileManager::RebuildAround(const FIntPoint& Center)
{
	// Desired = the (2*GridRadius+1)^2 block centered on the focus cell.
	TSet<FIntPoint> Desired;
	for (int32 di = -GridRadius; di <= GridRadius; ++di)
	{
		for (int32 dj = -GridRadius; dj <= GridRadius; ++dj)
		{
			Desired.Add(FIntPoint(Center.X + di, Center.Y + dj));
		}
	}

	// Unload tiles now outside the block (behind the player).
	TArray<FIntPoint> ToRemove;
	for (const TPair<FIntPoint, AProcTerrainTile*>& Pair : ActiveTiles)
	{
		if (!Desired.Contains(Pair.Key))
		{
			ToRemove.Add(Pair.Key);
		}
	}
	for (const FIntPoint& Key : ToRemove)
	{
		AProcTerrainTile* Tile = ActiveTiles.FindRef(Key);
		if (IsValid(Tile))
		{
			Tile->Destroy();
		}
		ActiveTiles.Remove(Key);
		++TotalDestroyed;
	}

	// Load tiles ahead that are not present yet.
	for (const FIntPoint& Key : Desired)
	{
		if (!ActiveTiles.Contains(Key))
		{
			if (AProcTerrainTile* Tile = SpawnTile(Key))
			{
				ActiveTiles.Add(Key, Tile);
			}
		}
	}
}

void ASurfaceTileManager::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!Focus)
	{
		return;
	}

	const FIntPoint Cell = CellOf(Focus->GetActorLocation());
	if (!bHasCell || Cell != CurrentCell)
	{
		RebuildAround(Cell);
		CurrentCell = Cell;
		bHasCell = true;
		WriteState();
	}
}

void ASurfaceTileManager::EndPlay(const EEndPlayReason::Type Reason)
{
	WriteState();
	Super::EndPlay(Reason);
}

void ASurfaceTileManager::WriteState()
{
	const int32 Expected = (2 * GridRadius + 1) * (2 * GridRadius + 1);
	const FString Json = FString::Printf(TEXT(
		"{\n"
		"  \"active_tiles\": %d,\n"
		"  \"expected_active\": %d,\n"
		"  \"grid_radius\": %d,\n"
		"  \"total_spawned\": %d,\n"
		"  \"total_destroyed\": %d,\n"
		"  \"current_cell\": [%d, %d],\n"
		"  \"tile_size_cm\": %.1f,\n"
		"  \"height_amplitude_cm\": %.1f\n"
		"}\n"),
		ActiveTiles.Num(), Expected, GridRadius, TotalSpawned, TotalDestroyed,
		CurrentCell.X, CurrentCell.Y, TileSizeCm, HeightAmplitudeCm);
	FFileHelper::SaveStringToFile(Json, *StatePath);
}
