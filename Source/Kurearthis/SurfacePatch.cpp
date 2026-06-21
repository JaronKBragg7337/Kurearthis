#include "SurfacePatch.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

ASurfacePatch::ASurfacePatch()
{
	PrimaryActorTick.bCanEverTick = true;
	// Place the patch before the pawn's grounding sweep (TG_DuringPhysics) runs.
	PrimaryActorTick.TickGroup = TG_PrePhysics;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	RootComponent = Mesh;

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeMesh.Succeeded())
	{
		Mesh->SetStaticMesh(CubeMesh.Object);
	}

	// A slab: thin in local X (the top face), wide in Y/Z (the tangent plane). The
	// actor scale is set by the spawner; default to a 5 km x 200 m tile.
	Mesh->SetWorldScale3D(FVector(200.0, 5000.0, 5000.0));
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetSimulatePhysics(false);
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
}

FVector ASurfacePatch::GravityCenter() const
{
	return PlanetActor ? PlanetActor->GetActorLocation() : FallbackCenter;
}

void ASurfacePatch::BeginPlay()
{
	Super::BeginPlay();

	if (!PlanetActor)
	{
		TArray<AActor*> Found;
		UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Planet"), Found);
		if (Found.Num() > 0)
		{
			PlanetActor = Found[0];
		}
	}
	// A fixed tile (managed by ASurfaceTileManager) must NOT grab the focus, or it would
	// start following the pawn and the ground would glue to the player again.
	if (!bFixed && !Focus)
	{
		TArray<AActor*> Found;
		UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Focus"), Found);
		if (Found.Num() > 0)
		{
			Focus = Found[0];
		}
	}
}

void ASurfacePatch::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (bFixed || !Focus)
	{
		return;
	}

	const FVector Center = GravityCenter();
	const FVector Up = (Focus->GetActorLocation() - Center).GetSafeNormal();
	if (Up.IsNearlyZero())
	{
		return;
	}

	// Half the slab thickness (local X half-extent: cube is 100 cm, so 50 * scale.X).
	const double HalfThick = GetActorScale3D().X * 50.0;

	// Sit tangent under the focus, top face (+local X) at the surface radius, up=radial.
	const FVector NewLoc = Center + Up * (SurfaceRadius - HalfThick);
	SetActorLocationAndRotation(NewLoc, FRotationMatrix::MakeFromX(Up).Rotator());
}
