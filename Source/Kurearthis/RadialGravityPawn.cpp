#include "RadialGravityPawn.h"

#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"

ARadialGravityPawn::ARadialGravityPawn()
{
	PrimaryActorTick.bCanEverTick = true;
	// After the floating origin's TG_PrePhysics rebase for this frame.
	PrimaryActorTick.TickGroup = TG_DuringPhysics;
	AutoPossessPlayer = EAutoReceiveInput::Disabled;

	Capsule = CreateDefaultSubobject<UCapsuleComponent>(TEXT("Capsule"));
	Capsule->InitCapsuleSize(50.0f, 100.0f);   // r=50 cm, half-height=1 m
	Capsule->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Capsule->SetCollisionObjectType(ECC_Pawn);
	Capsule->SetCollisionResponseToAllChannels(ECR_Block);
	RootComponent = Capsule;

	VisMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VisMesh"));
	VisMesh->SetupAttachment(Capsule);
	VisMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CapsuleMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CapsuleMesh.Succeeded())
	{
		VisMesh->SetStaticMesh(CapsuleMesh.Object);
		// Engine cylinder is 100 cm tall, 50 cm radius; scale to ~2 m tall capsule body.
		VisMesh->SetRelativeScale3D(FVector(1.0f, 1.0f, 2.0f));
	}
}

FVector ARadialGravityPawn::GravityCenter() const
{
	return PlanetActor ? PlanetActor->GetActorLocation() : FallbackCenter;
}

void ARadialGravityPawn::BeginPlay()
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

	StartLocation = GetActorLocation();
	const FVector C = GravityCenter();
	StartRadialUp = (StartLocation - C).GetSafeNormal();

	IFileManager::Get().Delete(*JsonPath, false, true, true);
	FFileHelper::SaveStringToFile(
		FString::Printf(TEXT("# RadialGravityPawn  planet=%s  center=%s  moveSpeed=%.1f  surface=%.1f\n"),
			*GetNameSafe(PlanetActor), *C.ToString(), MoveSpeed, SurfaceRadius),
		*LogPath);
}

void ARadialGravityPawn::MoveForwardInput(float Value) { PendingForward += Value; }
void ARadialGravityPawn::MoveRightInput(float Value) { PendingRight += Value; }

void ARadialGravityPawn::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (DeltaSeconds <= 0.0f)
	{
		return;
	}
	Elapsed += DeltaSeconds;

	const FVector Center = GravityCenter();
	FVector Loc = GetActorLocation();
	const FVector RadialUp = (Loc - Center).GetSafeNormal();

	// --- Desired tangential move direction (world space) --------------------
	FVector DesiredDir = DebugDriveWorldDir;
	if (DesiredDir.IsNearlyZero())
	{
		// Build from input + current heading would need a camera; for now map
		// forward/right to two fixed tangent basis directions.
		const FVector Ref = FMath::Abs(RadialUp.Z) < 0.99 ? FVector::UpVector : FVector::ForwardVector;
		const FVector East = FVector::CrossProduct(Ref, RadialUp).GetSafeNormal();
		const FVector North = FVector::CrossProduct(RadialUp, East).GetSafeNormal();
		DesiredDir = North * PendingForward + East * PendingRight;
	}
	PendingForward = 0.0f;
	PendingRight = 0.0f;

	// Project the desired direction onto the local tangent plane.
	FVector TangentDir = DesiredDir - FVector::DotProduct(DesiredDir, RadialUp) * RadialUp;
	TangentDir = TangentDir.GetSafeNormal();

	// --- 1) Tangential (horizontal) move ------------------------------------
	// Non-swept: a grounded capsule grazes the flat floor on a horizontal sweep and
	// stops dead. The local patch is flat and obstacle-free, so we move directly;
	// the real collision work (radial gravity grounding) stays swept below.
	// Horizontal obstacle collision / surface sliding is a follow-up for when the
	// terrain has relief.
	if (!TangentDir.IsNearlyZero())
	{
		const FVector HDelta = TangentDir * (MoveSpeed * DeltaSeconds);
		AddActorWorldOffset(HDelta, /*bSweep=*/false);
		const FVector MovedH = GetActorLocation() - Loc;
		TangentialTraveled += (MovedH - FVector::DotProduct(MovedH, RadialUp) * RadialUp).Size();
		Loc = GetActorLocation();
	}

	// --- 2) Radial gravity + grounding (vertical) swept move ----------------
	VerticalVel -= GravityStrength * DeltaSeconds;          // accelerate toward center
	const FVector VDelta = RadialUp * (VerticalVel * DeltaSeconds);
	FHitResult VHit;
	AddActorWorldOffset(VDelta, /*bSweep=*/true, &VHit);
	bGrounded = false;
	if (VHit.bBlockingHit && FVector::DotProduct(VHit.ImpactNormal, RadialUp) > 0.5)
	{
		bGrounded = true;
		if (VerticalVel < 0.0)
		{
			VerticalVel = 0.0;   // landed: stop falling
		}
	}

	// --- 3) Orient the capsule so its up tracks the radial direction --------
	const FVector NewLoc = GetActorLocation();
	const FVector UpNow = (NewLoc - Center).GetSafeNormal();
	const FQuat Orient = FQuat::FindBetweenNormals(FVector::UpVector, UpNow);
	SetActorRotation(Orient);

	const double Dist = (NewLoc - Center).Size();
	const double UpDot = FVector::DotProduct(UpNow, RadialUp);   // ~1 across a tick

	LogAccum += DeltaSeconds;
	if (LogAccum >= 0.25)
	{
		LogAccum = 0.0;
		FFileHelper::SaveStringToFile(
			FString::Printf(TEXT("t=%.2f worldLoc=(%.1f,%.1f,%.1f) dist=%.1f grounded=%d vVel=%.1f traveled=%.1f up=(%.4f,%.4f,%.4f)\n"),
				Elapsed, NewLoc.X, NewLoc.Y, NewLoc.Z, Dist, bGrounded ? 1 : 0, VerticalVel,
				TangentialTraveled, UpNow.X, UpNow.Y, UpNow.Z),
			*LogPath, FFileHelper::EEncodingOptions::AutoDetect, &IFileManager::Get(),
			EFileWrite::FILEWRITE_Append);
	}

	// Refresh the result file periodically so the harness reads the latest state.
	ResultAccum += DeltaSeconds;
	if (ResultAccum >= 0.5)
	{
		ResultAccum = 0.0;
		WriteResult(NewLoc, Dist, UpNow, UpDot);
	}
}

void ARadialGravityPawn::WriteResult(const FVector& Loc, double Dist, const FVector& RadialUp, double UpDot)
{
	const FVector Center = GravityCenter();
	const double CapsuleHalf = Capsule ? Capsule->GetScaledCapsuleHalfHeight() : 100.0;
	const double HeightAboveSurface = Dist - SurfaceRadius - CapsuleHalf;
	// up alignment of the capsule's actual up vs radial (proves re-orientation).
	const FVector CapsuleUp = GetActorQuat().GetUpVector();
	const double CapsuleUpDot = FVector::DotProduct(CapsuleUp, RadialUp);

	const FString Json = FString::Printf(TEXT(
		"{\n"
		"  \"rested\": %s,\n"
		"  \"grounded\": %s,\n"
		"  \"time_s\": %.3f,\n"
		"  \"distance_from_center_cm\": %.3f,\n"
		"  \"surface_radius_cm\": %.3f,\n"
		"  \"height_above_surface_cm\": %.3f,\n"
		"  \"capsule_half_height_cm\": %.3f,\n"
		"  \"tangential_traveled_cm\": %.3f,\n"
		"  \"vertical_vel_cm_s\": %.4f,\n"
		"  \"local_up\": [%.6f, %.6f, %.6f],\n"
		"  \"capsule_up_dot_radial\": %.6f,\n"
		"  \"move_speed_cm_s\": %.3f\n"
		"}\n"),
		bGrounded ? TEXT("true") : TEXT("false"),
		bGrounded ? TEXT("true") : TEXT("false"),
		Elapsed, Dist, SurfaceRadius, HeightAboveSurface, CapsuleHalf,
		TangentialTraveled, VerticalVel,
		RadialUp.X, RadialUp.Y, RadialUp.Z, CapsuleUpDot, MoveSpeed);

	FFileHelper::SaveStringToFile(Json, *JsonPath);
}

void ARadialGravityPawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	if (PlayerInputComponent)
	{
		PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &ARadialGravityPawn::MoveForwardInput);
		PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &ARadialGravityPawn::MoveRightInput);
	}
}
