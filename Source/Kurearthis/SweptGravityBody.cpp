#include "SweptGravityBody.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"

ASweptGravityBody::ASweptGravityBody()
{
	PrimaryActorTick.bCanEverTick = true;
	// Tick during physics (default) so the floating origin's TG_PrePhysics rebase
	// for this frame has already run before we read our location and move.
	PrimaryActorTick.TickGroup = TG_DuringPhysics;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	RootComponent = Mesh;

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (SphereMesh.Succeeded())
	{
		Mesh->SetStaticMesh(SphereMesh.Object);
	}

	// ~50 m radius ball. Kinematic: we move it ourselves and sweep against the
	// world; it must BLOCK static collision (the LocalSurfacePatch) but never
	// run Chaos simulation.
	Mesh->SetWorldScale3D(FVector(100.0));
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetSimulatePhysics(false);
	Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Mesh->SetCollisionObjectType(ECC_Pawn);
	Mesh->SetCollisionResponseToAllChannels(ECR_Block);
}

FVector ASweptGravityBody::GravityCenter() const
{
	return PlanetActor ? PlanetActor->GetActorLocation() : FallbackCenter;
}

void ASweptGravityBody::BeginPlay()
{
	Super::BeginPlay();

	LogPath = FPaths::ProjectSavedDir() / TEXT("RadialGravityProof.log");
	JsonPath = FPaths::ProjectSavedDir() / TEXT("RadialGravityProof.json");

	if (!PlanetActor)
	{
		TArray<AActor*> Found;
		UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Planet"), Found);
		if (Found.Num() > 0)
		{
			PlanetActor = Found[0];
		}
	}

	Velocity = FVector::ZeroVector;
	IFileManager::Get().Delete(*JsonPath, false, true, true);
	FFileHelper::SaveStringToFile(
		FString::Printf(TEXT("# SweptGravity (direct integration + sweep)  planet=%s  center=%s  strength=%.1f cm/s^2  surface=%.1f cm\n"),
			*GetNameSafe(PlanetActor), *GravityCenter().ToString(), GravityStrength, SurfaceRadius),
		*LogPath);
}

void ASweptGravityBody::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (bResultWritten || DeltaSeconds <= 0.0f)
	{
		return;
	}

	Elapsed += DeltaSeconds;

	const FVector Center = GravityCenter();
	const FVector Loc = GetActorLocation();
	const FVector ToCenter = Center - Loc;
	const double Dist = ToCenter.Size();
	const FVector Dir = (Dist > 0.0) ? (ToCenter / Dist) : FVector::ZeroVector;

	// Direct radial-gravity integration (double precision via FVector).
	Velocity += Dir * (GravityStrength * DeltaSeconds);
	const FVector Delta = Velocity * DeltaSeconds;

	// Swept move against the local surface collision.
	FHitResult Hit;
	AddActorWorldOffset(Delta, /*bSweep=*/true, &Hit);

	if (Hit.bBlockingHit)
	{
		// Remove the velocity component going into the surface so the body rests
		// instead of accelerating through it; keep any tangential component.
		const FVector N = Hit.ImpactNormal;
		const double IntoSurface = FVector::DotProduct(Velocity, N);
		if (IntoSurface < 0.0)
		{
			Velocity -= IntoSurface * N;
		}
		// Light tangential damping so a glancing landing settles rather than skating.
		Velocity *= 0.5;
	}

	const FVector NewLoc = GetActorLocation();
	const double NewDist = (Center - NewLoc).Size();
	const double Speed = Velocity.Size();
	const FVector Up = (NewDist > 0.0) ? ((NewLoc - Center) / NewDist) : FVector::UpVector;

	LogAccum += DeltaSeconds;
	if (LogAccum >= 0.2)
	{
		LogAccum = 0.0;
		const FString HitName = Hit.bBlockingHit ? GetNameSafe(Hit.GetActor()) : TEXT("-");
		FFileHelper::SaveStringToFile(
			FString::Printf(TEXT("t=%.2f worldLoc=(%.1f,%.1f,%.1f) |%.1f| dist=%.1f speed=%.1f up=(%.4f,%.4f,%.4f) hit=%d startPen=%d hitActor=%s impact=(%.1f,%.1f,%.1f) depth=%.1f\n"),
				Elapsed, NewLoc.X, NewLoc.Y, NewLoc.Z, NewLoc.Size(), NewDist, Speed,
				Up.X, Up.Y, Up.Z, Hit.bBlockingHit ? 1 : 0, Hit.bStartPenetrating ? 1 : 0,
				*HitName, Hit.ImpactPoint.X, Hit.ImpactPoint.Y, Hit.ImpactPoint.Z, Hit.PenetrationDepth),
			*LogPath, FFileHelper::EEncodingOptions::AutoDetect, &IFileManager::Get(),
			EFileWrite::FILEWRITE_Append);
	}

	const bool bNearSurface = FMath::Abs(NewDist - SurfaceRadius) < SurfaceBandCm;
	if (bNearSurface && Speed < RestSpeedThreshold)
	{
		RestTimer += DeltaSeconds;
	}
	else
	{
		RestTimer = 0.0;
	}

	if (RestTimer > 1.0)
	{
		bResultWritten = true;
		WriteResultJson(/*bRested=*/true, NewLoc, NewDist);
	}
	else if (Elapsed > 30.0)
	{
		bResultWritten = true;
		WriteResultJson(/*bRested=*/bNearSurface && Speed < RestSpeedThreshold, NewLoc, NewDist);
	}
}

void ASweptGravityBody::WriteResultJson(bool bRested, const FVector& Loc, double DistFromCenter)
{
	const FVector Center = GravityCenter();
	const FVector Up = (DistFromCenter > 0.0) ? ((Loc - Center) / DistFromCenter) : FVector::UpVector;

	const FString Json = FString::Printf(TEXT(
		"{\n"
		"  \"rested\": %s,\n"
		"  \"time_s\": %.3f,\n"
		"  \"world_location_cm\": [%.3f, %.3f, %.3f],\n"
		"  \"world_location_magnitude_cm\": %.3f,\n"
		"  \"planet_center_cm\": [%.3f, %.3f, %.3f],\n"
		"  \"distance_from_center_cm\": %.3f,\n"
		"  \"surface_radius_cm\": %.3f,\n"
		"  \"rest_minus_surface_cm\": %.3f,\n"
		"  \"speed_cm_s\": %.4f,\n"
		"  \"local_up\": [%.6f, %.6f, %.6f],\n"
		"  \"gravity_strength_cm_s2\": %.3f,\n"
		"  \"integrator\": \"swept-direct\"\n"
		"}\n"),
		bRested ? TEXT("true") : TEXT("false"),
		Elapsed, Loc.X, Loc.Y, Loc.Z, Loc.Size(),
		Center.X, Center.Y, Center.Z,
		DistFromCenter, SurfaceRadius, DistFromCenter - SurfaceRadius,
		Velocity.Size(), Up.X, Up.Y, Up.Z, GravityStrength);

	FFileHelper::SaveStringToFile(Json, *JsonPath);

	UE_LOG(LogTemp, Display,
		TEXT("KUREARTHIS_SWEPT_GRAVITY_REST rested=%d t=%.2f dist=%.1f worldMag=%.1f up=(%.3f,%.3f,%.3f) speed=%.2f"),
		bRested ? 1 : 0, Elapsed, DistFromCenter, Loc.Size(), Up.X, Up.Y, Up.Z, Velocity.Size());
}
