#include "ProcTerrainTile.h"

#include "ProceduralMeshComponent.h"
#include "KismetProceduralMeshLibrary.h"
#include "Kismet/GameplayStatics.h"

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

	const int32 N = FMath::Max(2, Resolution);
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
			const double u = ((double)i / (double)N - 0.5) * TileSizeCm;
			const double v = ((double)j / (double)N - 0.5) * TileSizeCm;
			// Point in the tile's tangent plane, projected onto the sphere, displaced radially.
			const FVector TangentPt = ActorLoc + Ax * u + Ay * v;
			const FVector Dir = (TangentPt - Center).GetSafeNormal();
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
