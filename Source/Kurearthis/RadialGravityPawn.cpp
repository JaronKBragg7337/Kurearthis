#include "RadialGravityPawn.h"

#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Engine/World.h"
#include "CollisionShape.h"
#include "CollisionQueryParams.h"

ARadialGravityPawn::ARadialGravityPawn()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_DuringPhysics;   // after the floating-origin rebase
	AutoPossessPlayer = EAutoReceiveInput::Player0;   // PIE possesses the placed pawn

	Capsule = CreateDefaultSubobject<UCapsuleComponent>(TEXT("Capsule"));
	Capsule->InitCapsuleSize(50.0f, 100.0f);
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
		VisMesh->SetRelativeScale3D(FVector(1.0f, 1.0f, 2.0f));
	}

	SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
	SpringArm->SetupAttachment(Capsule);
	SpringArm->SetRelativeLocation(FVector(0.0f, 0.0f, 80.0f));
	SpringArm->TargetArmLength = 600.0f;
	SpringArm->bUsePawnControlRotation = false;       // we orient everything manually
	SpringArm->bDoCollisionTest = false;              // no probing the giant planet mesh
	// Fully follow the pawn's orientation (its up = radial, which is NOT world +Z),
	// then add the mouse look-pitch as a relative rotation on top.
	SpringArm->bInheritPitch = true;
	SpringArm->bInheritYaw = true;
	SpringArm->bInheritRoll = true;
	SpringArm->SetRelativeRotation(FRotator(CameraPitch, 0.0f, 0.0f));

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
	Camera->bUsePawnControlRotation = false;
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
	const FVector RadialUp = (StartLocation - C).GetSafeNormal();

	// Initial heading: project world +Y onto the tangent plane (fallback +Z).
	FVector Seed = FVector::RightVector;
	if (FMath::Abs(FVector::DotProduct(Seed, RadialUp)) > 0.95)
	{
		Seed = FVector::UpVector;
	}
	ForwardDir = (Seed - FVector::DotProduct(Seed, RadialUp) * RadialUp).GetSafeNormal();

	IFileManager::Get().Delete(*JsonPath, false, true, true);
	FFileHelper::SaveStringToFile(
		FString::Printf(TEXT("# RadialGravityPawn  planet=%s  center=%s  moveSpeed=%.1f  surface=%.1f\n"),
			*GetNameSafe(PlanetActor), *C.ToString(), MoveSpeed, SurfaceRadius),
		*LogPath);
}

void ARadialGravityPawn::MoveForwardInput(float Value) { PendingForward += Value; }
void ARadialGravityPawn::MoveRightInput(float Value) { PendingRight += Value; }
void ARadialGravityPawn::TurnInput(float Value) { PendingTurn += Value; }
void ARadialGravityPawn::LookUpInput(float Value) { PendingLookUp += Value; }

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

	// Keep the heading in the tangent plane, then steer it with the mouse.
	ForwardDir = (ForwardDir - FVector::DotProduct(ForwardDir, RadialUp) * RadialUp).GetSafeNormal();
	if (!FMath::IsNearlyZero(PendingTurn))
	{
		ForwardDir = ForwardDir.RotateAngleAxis(PendingTurn * LookSensitivity, RadialUp).GetSafeNormal();
	}
	const FVector RightDir = FVector::CrossProduct(RadialUp, ForwardDir).GetSafeNormal();

	// Desired tangential move from input (or the head-less debug drive).
	FVector MoveDir = ForwardDir * PendingForward + RightDir * PendingRight;
	if (!DebugDriveWorldDir.IsNearlyZero())
	{
		MoveDir = DebugDriveWorldDir;
	}
	MoveDir = MoveDir - FVector::DotProduct(MoveDir, RadialUp) * RadialUp;
	PendingForward = PendingRight = PendingTurn = 0.0f;

	// --- 1) Tangential move (non-swept on the flat patch) -------------------
	const FVector TangentDir = MoveDir.GetSafeNormal();
	if (!TangentDir.IsNearlyZero())
	{
		AddActorWorldOffset(TangentDir * (MoveSpeed * DeltaSeconds), /*bSweep=*/false);
		const FVector MovedH = GetActorLocation() - Loc;
		TangentialTraveled += (MovedH - FVector::DotProduct(MovedH, RadialUp) * RadialUp).Size();
		Loc = GetActorLocation();
	}

	// --- 2) Ground-follow (snap up/down) + gravity for real falls -----------
	// A downward-only sweep cannot climb hills (it would sink into uphill terrain). So
	// probe a capsule from StepUp ABOVE the pawn downward: if it finds ground within reach,
	// snap the capsule to rest on it (handles uphill, flat, and small downhill); otherwise
	// the pawn is genuinely airborne, so integrate radial gravity and sweep down to land.
	const float CapHalf = Capsule ? Capsule->GetScaledCapsuleHalfHeight() : 100.0f;
	const float CapRadius = Capsule ? Capsule->GetScaledCapsuleRadius() : 50.0f;
	const float StepUp = 8000.0f;     // detect ground up to 80 m above (max uphill reach)
	const float SnapDown = 13000.0f;  // snap to ground up to ~50 m below; bigger drops fall
	const FVector ProbeStart = Loc + RadialUp * StepUp;
	const FVector ProbeEnd = Loc - RadialUp * SnapDown;
	const FCollisionShape CapShape = FCollisionShape::MakeCapsule(CapRadius, CapHalf);
	FCollisionQueryParams Params(SCENE_QUERY_STAT(TerrainGround), false, this);
	FHitResult GHit;
	const bool bGroundHit = GetWorld()->SweepSingleByChannel(
		GHit, ProbeStart, ProbeEnd, GetActorQuat(), ECC_WorldStatic, CapShape, Params);

	if (bGroundHit && !GHit.bStartPenetrating)
	{
		// GHit.Location = capsule center at the moment it rests on the ground.
		SetActorLocation(GHit.Location);
		bGrounded = true;
		VerticalVel = 0.0;
	}
	else
	{
		bGrounded = false;
		VerticalVel -= GravityStrength * DeltaSeconds;
		FHitResult VHit;
		AddActorWorldOffset(RadialUp * (VerticalVel * DeltaSeconds), /*bSweep=*/true, &VHit);
		if (VHit.bBlockingHit && FVector::DotProduct(VHit.ImpactNormal, RadialUp) > 0.3)
		{
			bGrounded = true;
			if (VerticalVel < 0.0)
			{
				VerticalVel = 0.0;
			}
		}
	}

	// --- 3) Orient capsule: up = radial, forward = heading ------------------
	const FVector NewLoc = GetActorLocation();
	const FVector UpNow = (NewLoc - Center).GetSafeNormal();
	const FVector FwdTangent = (ForwardDir - FVector::DotProduct(ForwardDir, UpNow) * UpNow).GetSafeNormal();
	SetActorRotation(FRotationMatrix::MakeFromZX(UpNow, FwdTangent).Rotator());

	// --- 4) Camera pitch (mouse) --------------------------------------------
	CameraPitch = FMath::Clamp(CameraPitch + PendingLookUp * LookSensitivity, -80.0f, 30.0f);
	PendingLookUp = 0.0f;
	if (SpringArm)
	{
		SpringArm->SetRelativeRotation(FRotator(CameraPitch, 0.0f, 0.0f));
	}

	const double Dist = (NewLoc - Center).Size();
	const double UpDot = FVector::DotProduct(UpNow, RadialUp);

	LogAccum += DeltaSeconds;
	if (LogAccum >= 0.25)
	{
		LogAccum = 0.0;
		FFileHelper::SaveStringToFile(
			FString::Printf(TEXT("t=%.2f dist=%.1f grounded=%d vVel=%.1f traveled=%.1f up=(%.4f,%.4f,%.4f)\n"),
				Elapsed, Dist, bGrounded ? 1 : 0, VerticalVel, TangentialTraveled, UpNow.X, UpNow.Y, UpNow.Z),
			*LogPath, FFileHelper::EEncodingOptions::AutoDetect, &IFileManager::Get(),
			EFileWrite::FILEWRITE_Append);
	}

	ResultAccum += DeltaSeconds;
	if (ResultAccum >= 0.5)
	{
		ResultAccum = 0.0;
		WriteResult(NewLoc, Dist, UpNow, UpDot);
	}
}

void ARadialGravityPawn::WriteResult(const FVector& Loc, double Dist, const FVector& RadialUp, double UpDot)
{
	const double CapsuleHalf = Capsule ? Capsule->GetScaledCapsuleHalfHeight() : 100.0;
	const double HeightAboveSurface = Dist - SurfaceRadius - CapsuleHalf;
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
		PlayerInputComponent->BindAxis(TEXT("Turn"), this, &ARadialGravityPawn::TurnInput);
		PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &ARadialGravityPawn::LookUpInput);
	}
}
