#include "ProcTerrainTile.h"

#include "ProceduralMeshComponent.h"
#include "KismetProceduralMeshLibrary.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"

// ---- Real-world DEM (T2d) -------------------------------------------------------------
// A single shared elevation grid baked by _authoring/fetch_dem.py, loaded once from
// Content/RealDEM/dem_active.bin. Where a sample's (lon,lat) falls inside the grid bbox,
// the terrain uses REAL elevation; elsewhere it falls back to procedural noise.
namespace
{
	struct FRealDEM
	{
		bool bTried = false;
		bool bValid = false;
		int32 Zoom = 0;
		int32 Width = 0;
		int32 Height = 0;
		double OriginPxX = 0.0;
		double OriginPxY = 0.0;
		TArray<float> Data;   // row-major, row 0 = north
		// OSM water (T2d-3): same grid; 255 = water. Water cells flatten to WaterLevelCm.
		bool bWater = false;
		double WaterLevelCm = 0.0;
		TArray<uint8> WaterMask;
	};

	const FRealDEM& GetRealDEM()
	{
		static FRealDEM Dem;
		if (!Dem.bTried)
		{
			Dem.bTried = true;
			const FString Path = FPaths::ProjectContentDir() / TEXT("RealDEM/dem_active.bin");
			TArray<uint8> Bytes;
			if (FFileHelper::LoadFileToArray(Bytes, *Path) && Bytes.Num() >= 36)
			{
				int32 Magic = 0;
				FMemory::Memcpy(&Magic, &Bytes[0], 4);
				if (Magic == 0x4B44454D)   // 'KDEM'
				{
					FMemory::Memcpy(&Dem.Zoom, &Bytes[8], 4);
					FMemory::Memcpy(&Dem.Width, &Bytes[12], 4);
					FMemory::Memcpy(&Dem.Height, &Bytes[16], 4);
					FMemory::Memcpy(&Dem.OriginPxX, &Bytes[20], 8);
					FMemory::Memcpy(&Dem.OriginPxY, &Bytes[28], 8);
					const int64 N = (int64)Dem.Width * (int64)Dem.Height;
					if (N > 0 && Bytes.Num() >= 36 + N * 4)
					{
						Dem.Data.SetNumUninitialized(N);
						FMemory::Memcpy(Dem.Data.GetData(), &Bytes[36], N * 4);
						Dem.bValid = true;
					}
				}
			}

			// Optional OSM water mask aligned to the same grid (T2d-3).
			if (Dem.bValid)
			{
				const FString WPath = FPaths::ProjectContentDir() / TEXT("RealDEM/water_active.bin");
				TArray<uint8> WB;
				if (FFileHelper::LoadFileToArray(WB, *WPath) && WB.Num() >= 44)
				{
					int32 WMagic = 0, WW = 0, WH = 0;
					FMemory::Memcpy(&WMagic, &WB[0], 4);
					FMemory::Memcpy(&WW, &WB[12], 4);
					FMemory::Memcpy(&WH, &WB[16], 4);
					double WLevelM = 0.0;
					FMemory::Memcpy(&WLevelM, &WB[36], 8);
					const int64 WN = (int64)WW * (int64)WH;
					if (WMagic == 0x4B574154 && WW == Dem.Width && WH == Dem.Height
						&& WN > 0 && WB.Num() >= 44 + WN)
					{
						Dem.WaterMask.SetNumUninitialized(WN);
						FMemory::Memcpy(Dem.WaterMask.GetData(), &WB[44], WN);
						Dem.WaterLevelCm = WLevelM * 100.0;
						Dem.bWater = true;
					}
				}
			}
		}
		return Dem;
	}

	// True if (lonDeg,latDeg) falls inside the loaded DEM grid bbox.
	bool DEMContainsLonLat(double LonDeg, double LatDeg)
	{
		const FRealDEM& Dem = GetRealDEM();
		if (!Dem.bValid)
		{
			return false;
		}
		const double Pi = 3.14159265358979323846;
		const double LatR = FMath::DegreesToRadians(LatDeg);
		const double TanLat = FMath::Tan(LatR);
		const double AsinhLat = FMath::Loge(TanLat + FMath::Sqrt(TanLat * TanLat + 1.0));
		const double Nn = (double)((int64)256 << Dem.Zoom);
		const double Col = (LonDeg + 180.0) / 360.0 * Nn - Dem.OriginPxX;
		const double Row = (1.0 - AsinhLat / Pi) / 2.0 * Nn - Dem.OriginPxY;
		return (Col >= 0.0 && Col <= Dem.Width - 1 && Row >= 0.0 && Row <= Dem.Height - 1);
	}
}

AProcTerrainTile::AProcTerrainTile()
{
	PrimaryActorTick.bCanEverTick = false;

	Mesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("Mesh"));
	RootComponent = Mesh;
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->bUseAsyncCooking = false;                 // collision ready synchronously for the harness
	Mesh->bUseComplexAsSimpleCollision = true;      // so the capsule SWEEP grounds on the triangles
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
	Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
}

FVector AProcTerrainTile::GravityCenter() const
{
	if (PlanetActor)
	{
		return PlanetActor->GetActorLocation();
	}
	return FallbackCenter;
}

// Deterministic fBm Perlin noise -> radial height (cm). Continuous in world space, so it
// is identical at shared points between neighbouring tiles (seamless, for T2b). This is the
// DEFAULT height source; a real DEM/OSM source (T2d) replaces the body of this function.
double AProcTerrainTile::SampleHeight(const FVector& WorldSurfacePoint) const
{
	// --- Real DEM where available (T2d) ---------------------------------------------
	const FRealDEM& Dem = GetRealDEM();
	if (Dem.bValid)
	{
		const FVector Dir = (WorldSurfacePoint - GravityCenter()).GetSafeNormal();
		if (!Dir.IsNearlyZero())
		{
			const double Pi = 3.14159265358979323846;
			const double LonDeg = FMath::RadiansToDegrees(FMath::Atan2(Dir.Y, Dir.X));
			const double LatR = FMath::Asin(FMath::Clamp((double)Dir.Z, -1.0, 1.0));
			const double TanLat = FMath::Tan(LatR);
			const double AsinhLat = FMath::Loge(TanLat + FMath::Sqrt(TanLat * TanLat + 1.0)); // asinh
			const double N = (double)((int64)256 << Dem.Zoom);
			const double Gx = (LonDeg + 180.0) / 360.0 * N;
			const double Gy = (1.0 - AsinhLat / Pi) / 2.0 * N;
			const double Col = Gx - Dem.OriginPxX;
			const double Row = Gy - Dem.OriginPxY;
			if (Col >= 0.0 && Col <= Dem.Width - 1 && Row >= 0.0 && Row <= Dem.Height - 1)
			{
				// OSM water cells read as a flat water surface (T2d-3).
				if (Dem.bWater)
				{
					const int32 Wc = FMath::Clamp((int32)FMath::RoundToDouble(Col), 0, Dem.Width - 1);
					const int32 Wr = FMath::Clamp((int32)FMath::RoundToDouble(Row), 0, Dem.Height - 1);
					if (Dem.WaterMask[(int64)Wr * Dem.Width + Wc] > 127)
					{
						return Dem.WaterLevelCm;
					}
				}
				const int32 c0 = (int32)FMath::FloorToDouble(Col);
				const int32 r0 = (int32)FMath::FloorToDouble(Row);
				const int32 c1 = FMath::Min(c0 + 1, Dem.Width - 1);
				const int32 r1 = FMath::Min(r0 + 1, Dem.Height - 1);
				const double Fc = Col - c0;
				const double Fr = Row - r0;
				auto At = [&](int32 R, int32 C) { return (double)Dem.Data[(int64)R * Dem.Width + C]; };
				const double Top = At(r0, c0) * (1.0 - Fc) + At(r0, c1) * Fc;
				const double Bot = At(r1, c0) * (1.0 - Fc) + At(r1, c1) * Fc;
				const double Meters = Top * (1.0 - Fr) + Bot * Fr;
				return Meters * 100.0;   // m -> cm
			}
		}
	}

	// --- Procedural fallback (fBm Perlin) -------------------------------------------
	const double BaseFreq = (NoiseBaseWavelengthCm > 0.0) ? (1.0 / NoiseBaseWavelengthCm) : 1e-6;
	double Sum = 0.0;
	double Amp = 1.0;
	double Freq = BaseFreq;
	double NormSum = 0.0;
	for (int32 o = 0; o < FMath::Max(1, Octaves); ++o)
	{
		const FVector P = WorldSurfacePoint * Freq;
		Sum += Amp * (double)FMath::PerlinNoise3D(FVector(P));   // [-1, 1]
		NormSum += Amp;
		Amp *= 0.5;
		Freq *= 2.0;
	}
	const double N = (NormSum > 0.0) ? (Sum / NormSum) : 0.0;     // [-1, 1]
	// Bias upward so terrain mostly rises above the nominal surface (no deep pits at spawn).
	return (N * 0.5 + 0.5) * HeightAmplitudeCm;
}

void AProcTerrainTile::Generate()
{
	if (!PlanetActor)
	{
		TArray<AActor*> Found;
		UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Planet"), Found);
		if (Found.Num() > 0)
		{
			PlanetActor = Found[0];
		}
	}

	const FVector Center = GravityCenter();
	const FTransform X = GetActorTransform();
	const FVector Ax = X.GetUnitAxis(EAxis::X);   // tile tangent basis
	const FVector Ay = X.GetUnitAxis(EAxis::Y);
	const FVector ActorLoc = X.GetLocation();

	// Use a finer grid where real DEM data is active so fine terrain + narrow rivers show.
	int32 EffRes = FMath::Max(2, Resolution);
	{
		const FVector CenterDir = (ActorLoc - Center).GetSafeNormal();
		if (!CenterDir.IsNearlyZero())
		{
			const double LonD = FMath::RadiansToDegrees(FMath::Atan2(CenterDir.Y, CenterDir.X));
			const double LatD = FMath::RadiansToDegrees(FMath::Asin(FMath::Clamp((double)CenterDir.Z, -1.0, 1.0)));
			if (DEMContainsLonLat(LonD, LatD))
			{
				EffRes = FMath::Max(EffRes, DemResolution);
			}
		}
	}
	const int32 N = EffRes;
	const int32 Side = N + 1;

	TArray<FVector> Verts;
	TArray<int32> Tris;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<FProcMeshTangent> Tangents;
	TArray<FLinearColor> Colors;
	Verts.Reserve(Side * Side);
	UVs.Reserve(Side * Side);

	for (int32 i = 0; i <= N; ++i)
	{
		for (int32 j = 0; j <= N; ++j)
		{
			FVector Dir;
			if (bUseLonLatCell)
			{
				// Fixed lon/lat grid: adjacent cells share exact edge vertices (no cracks).
				const double Lon = CellLon0 + ((double)i / (double)N) * CellAngularSize;
				const double Lat = CellLat0 + ((double)j / (double)N) * CellAngularSize;
				const double CosLat = FMath::Cos(Lat);
				Dir = FVector(CosLat * FMath::Cos(Lon), CosLat * FMath::Sin(Lon), FMath::Sin(Lat)).GetSafeNormal();
			}
			else
			{
				// Local tangent square (single-tile T2a mode).
				const double u = ((double)i / (double)N - 0.5) * TileSizeCm;
				const double v = ((double)j / (double)N - 0.5) * TileSizeCm;
				const FVector TangentPt = ActorLoc + Ax * u + Ay * v;
				Dir = (TangentPt - Center).GetSafeNormal();
			}
			const FVector SurfacePt = Center + Dir * SurfaceRadius;
			const double H = SampleHeight(SurfacePt);
			const FVector WorldP = Center + Dir * (SurfaceRadius + H);
			Verts.Add(X.InverseTransformPosition(WorldP));
			UVs.Add(FVector2D((double)i, (double)j));
		}
	}

	for (int32 i = 0; i < N; ++i)
	{
		for (int32 j = 0; j < N; ++j)
		{
			const int32 a = i * Side + j;
			const int32 b = a + 1;
			const int32 c = a + Side;
			const int32 d = c + 1;
			// Wind so the surface normal points outward (+local Z = radial up).
			Tris.Add(a); Tris.Add(c); Tris.Add(b);
			Tris.Add(b); Tris.Add(c); Tris.Add(d);
		}
	}

	UKismetProceduralMeshLibrary::CalculateTangentsForMesh(Verts, Tris, UVs, Normals, Tangents);

	Mesh->ClearAllMeshSections();
	Mesh->CreateMeshSection_LinearColor(0, Verts, Tris, Normals, UVs, Colors, Tangents, /*bCreateCollision=*/true);
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
	Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
}

void AProcTerrainTile::BeginPlay()
{
	Super::BeginPlay();
	Generate();
}
