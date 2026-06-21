#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "RadialGravityPawn.generated.h"

class UCapsuleComponent;
class UStaticMeshComponent;
class USpringArmComponent;
class UCameraComponent;

/**
 * Player pawn for the planetary surface (CHARTER proof #2: stand + move with
 * radial up), now playable.
 *
 * Custom movement, NOT UE's CharacterMovementComponent (which assumes flat +Z
 * up). Each tick it:
 *   - computes radial up = normalize(loc - planetCenter),
 *   - keeps a heading (forward) in the local tangent plane, steered by mouse,
 *   - moves from WASD along that tangent heading (non-swept on the flat patch),
 *   - applies radial gravity + a downward swept move that grounds the capsule on
 *     the LocalSurfacePatch,
 *   - orients the capsule so up = radial and forward = heading,
 *   - drives a third-person spring-arm camera (mouse pitch).
 * Reads the planet center by the "Planet" tag, so it survives floating-origin
 * rebasing (Proof 2e/2f).
 *
 * Driven by a possessing PlayerController (WASD + mouse) OR, for head-less harness
 * verification, by DebugDriveWorldDir.
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

	UPROPERTY(VisibleAnywhere, Category = "RadialPawn")
	USpringArmComponent* SpringArm;

	UPROPERTY(VisibleAnywhere, Category = "RadialPawn")
	UCameraComponent* Camera;

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
	double MoveSpeed = 1200.0;

	/** Mouse-look sensitivity (degrees per input unit). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	float LookSensitivity = 2.5f;

	/** Head-less verification drive: if non-zero, used as the world-space move direction. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialPawn")
	FVector DebugDriveWorldDir = FVector::ZeroVector;

private:
	double VerticalVel = 0.0;          // speed along radial up (cm/s); <0 = falling
	bool bGrounded = false;
	FVector ForwardDir = FVector::ZeroVector;   // heading in the tangent plane
	float CameraPitch = -15.0f;        // spring-arm pitch (deg)
	FVector StartLocation = FVector::ZeroVector;
	double TangentialTraveled = 0.0;
	double Elapsed = 0.0;
	double LogAccum = 0.0;
	double ResultAccum = 0.0;
	FString LogPath;
	FString JsonPath;

	float PendingForward = 0.0f;
	float PendingRight = 0.0f;
	float PendingTurn = 0.0f;
	float PendingLookUp = 0.0f;

	FVector GravityCenter() const;
	void MoveForwardInput(float Value);
	void MoveRightInput(float Value);
	void TurnInput(float Value);
	void LookUpInput(float Value);
	void WriteResult(const FVector& Loc, double Dist, const FVector& RadialUp, double UpDot);
};
