#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "RadialGravityPawn.generated.h"

class UCapsuleComponent;
class UStaticMeshComponent;

/**
 * Player pawn for the planetary surface (CHARTER proof #2: stand + move with
 * radial up).
 *
 * Custom movement, NOT UE's CharacterMovementComponent (which assumes flat +Z
 * up). Each tick it:
 *   - computes radial up = normalize(loc - planetCenter),
 *   - moves TANGENTIALLY from input (projected onto the local tangent plane) via
 *     a swept move,
 *   - applies radial gravity and a downward swept move that grounds the capsule
 *     on the LocalSurfacePatch,
 *   - re-orients the capsule so its local up tracks the radial direction.
 * It reads the planet center by the "Planet" tag, so it survives floating-origin
 * rebasing exactly like ASweptGravityBody (Proof 2e).
 *
 * Movement is driven by AddMovementInput (a possessing PlayerController) OR, for
 * head-less harness verification, by DebugDriveWorldDir.
 */
UCLASS()
class KUREARTHIS_API ARadialGravityPawn : public APawn
{
	GENERATED_BODY()

public:
	ARadialGravityPawn();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	UPROPERTY(VisibleAnywhere, Category = "RadialPawn")
	UCapsuleComponent* Capsule;

	UPROPERTY(VisibleAnywhere, Category = "RadialPawn")
	UStaticMeshComponent* VisMesh;

	/** Planet whose center is the gravity source. Found by the "Planet" tag if unset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	AActor* PlanetActor = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	FVector FallbackCenter = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	double GravityStrength = 980.0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	double SurfaceRadius = 637100000.0;

	/** Tangential move speed (cm/s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	double MoveSpeed = 10000.0;

	/** Head-less verification drive: if non-zero, used as the world-space move direction. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	FVector DebugDriveWorldDir = FVector::ZeroVector;

private:
	double VerticalVel = 0.0;          // speed along radial up (cm/s); <0 = falling
	bool bGrounded = false;
	FVector StartLocation = FVector::ZeroVector;
	FVector StartRadialUp = FVector::ZeroVector;
	double TangentialTraveled = 0.0;   // arc length walked along the surface (cm)
	double Elapsed = 0.0;
	double LogAccum = 0.0;
	double ResultAccum = 0.0;
	FString LogPath;
	FString JsonPath;

	float PendingForward = 0.0f;
	float PendingRight = 0.0f;

	FVector GravityCenter() const;
	void MoveForwardInput(float Value);
	void MoveRightInput(float Value);
	void WriteResult(const FVector& Loc, double Dist, const FVector& RadialUp, double UpDot);
};
