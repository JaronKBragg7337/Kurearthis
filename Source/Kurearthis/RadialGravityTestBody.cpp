#include "RadialGravityTestBody.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"

ARadialGravityTestBody::ARadialGravityTestBody()
{
	PrimaryActorTick.bCanEverTick = true;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	RootComponent = Mesh;

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (SphereMesh.Succeeded())
	{
		Mesh->SetStaticMesh(SphereMesh.Object);
	}

	// Engine sphere is 50 cm radius at scale 1; scale 100 => ~50 m radius ball,
	// large enough to avoid tunnelling against the planet at this scale.
	Mesh->SetWorldScale3D(FVector(100.0));
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetSimulatePhysics(false); // turned on in BeginPlay after registration
	Mesh->SetCollisionProfileName(TEXT("PhysicsActor"));
	Mesh->SetNotifyRigidBodyCollision(true);
}

void ARadialGravityTestBody::BeginPlay()
{
	Super::BeginPlay();

	LogPath = FPaths::ProjectSavedDir() / TEXT("RadialGravityProof.log");
	JsonPath = FPaths::ProjectSavedDir() / TEXT("RadialGravityProof.json");

	// Start clean.
	IFileManager::Get().Delete(*JsonPath, false, true, true);
	FFileHelper::SaveStringToFile(
		FString::Printf(TEXT("# RadialGravity proof  center=%s  strength=%.1f cm/s^2  surface=%.1f cm\n"),
			*GravityCenter.ToString(), GravityStrength, SurfaceRadius),
		*LogPath);

	// Disable the engine's flat -Z gravity, then simulate. From now on the only
	// gravity acting on this body is the radial force we apply each tick.
	Mesh->SetSimulatePhysics(true);
	Mesh->SetEnableGravity(false);
	Mesh->SetUseCCD(true);
	Mesh->WakeAllRigidBodies();
}

void ARadialGravityTestBody::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!Mesh || !Mesh->IsSimulatingPhysics())
	{
		return;
	}

	Elapsed += DeltaSeconds;

	const FVector Loc = Mesh->GetComponentLocation();
	const FVector ToCenter = GravityCenter - Loc;
	const double Dist = ToCenter.Size();
	const FVector Dir = (Dist > 0.0) ? (ToCenter / Dist) : FVector::ZeroVector;

	// Radial acceleration toward the planet center. bAccelChange=true makes this
	// a mass-independent acceleration in cm/s^2.
	Mesh->AddForce(Dir * GravityStrength, NAME_None, /*bAccelChange=*/true);

	const FVector Vel = Mesh->GetPhysicsLinearVelocity();
	const double Speed = Vel.Size();
	const FVector Up = (Dist > 0.0) ? ((Loc - GravityCenter) / Dist) : FVector::UpVector;

	LogAccum += DeltaSeconds;
	if (LogAccum >= 0.2)
	{
		LogAccum = 0.0;
		FFileHelper::SaveStringToFile(
			FString::Printf(TEXT("t=%.2f loc=(%.1f,%.1f,%.1f) dist=%.1f speed=%.1f up=(%.4f,%.4f,%.4f)\n"),
				Elapsed, Loc.X, Loc.Y, Loc.Z, Dist, Speed, Up.X, Up.Y, Up.Z),
			*LogPath, FFileHelper::EEncodingOptions::AutoDetect, &IFileManager::Get(),
			EFileWrite::FILEWRITE_Append);
	}

	const bool bNearSurface = FMath::Abs(Dist - SurfaceRadius) < SurfaceBandCm;
	if (bNearSurface && Speed < RestSpeedThreshold)
	{
		RestTimer += DeltaSeconds;
	}
	else
	{
		RestTimer = 0.0;
	}

	if (!bResultWritten && RestTimer > 1.0)
	{
		bResultWritten = true;
		WriteResultJson(/*bRested=*/true, Loc, Vel, Dist);
	}
	// Fallback so verification always has a final snapshot to read.
	else if (!bResultWritten && Elapsed > 25.0)
	{
		bResultWritten = true;
		WriteResultJson(/*bRested=*/bNearSurface && Speed < RestSpeedThreshold, Loc, Vel, Dist);
	}
}

void ARadialGravityTestBody::WriteResultJson(bool bRested, const FVector& Loc, const FVector& Vel, double DistFromCenter)
{
	const FVector Up = (DistFromCenter > 0.0) ? ((Loc - GravityCenter) / DistFromCenter) : FVector::UpVector;

	const FString Json = FString::Printf(TEXT(
		"{\n"
		"  \"rested\": %s,\n"
		"  \"time_s\": %.3f,\n"
		"  \"location_cm\": [%.3f, %.3f, %.3f],\n"
		"  \"distance_from_center_cm\": %.3f,\n"
		"  \"surface_radius_cm\": %.3f,\n"
		"  \"rest_minus_surface_cm\": %.3f,\n"
		"  \"speed_cm_s\": %.4f,\n"
		"  \"local_up\": [%.6f, %.6f, %.6f],\n"
		"  \"gravity_center_cm\": [%.1f, %.1f, %.1f],\n"
		"  \"gravity_strength_cm_s2\": %.3f\n"
		"}\n"),
		bRested ? TEXT("true") : TEXT("false"),
		Elapsed, Loc.X, Loc.Y, Loc.Z, DistFromCenter, SurfaceRadius, DistFromCenter - SurfaceRadius,
		Vel.Size(), Up.X, Up.Y, Up.Z, GravityCenter.X, GravityCenter.Y, GravityCenter.Z, GravityStrength);

	FFileHelper::SaveStringToFile(Json, *JsonPath);

	UE_LOG(LogTemp, Display,
		TEXT("KUREARTHIS_RADIAL_GRAVITY_REST rested=%d t=%.2f dist=%.1f up=(%.3f,%.3f,%.3f) speed=%.2f"),
		bRested ? 1 : 0, Elapsed, DistFromCenter, Up.X, Up.Y, Up.Z, Vel.Size());
}
