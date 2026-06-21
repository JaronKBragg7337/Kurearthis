#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RadialGravityTestBody.generated.h"

class UStaticMeshComponent;

/**
 * Proof-stage test body for the planetary architecture.
 *
 * Simulates physics with the engine's default (flat -Z) gravity DISABLED and
 * instead applies a constant acceleration toward GravityCenter every tick. This
 * proves the foundational "planetary truth": gravity is radial toward a body
 * center and a falling object's local up is the radial direction, not world +Z.
 *
 * It is intentionally minimal and data-driven (center / strength / surface are
 * exposed) so the same radial-gravity math can graduate into the real movement
 * system later. It logs its full trajectory and rest state to Saved/ for
 * automated verification.
 */
UCLASS()
class KUREARTHIS_API ARadialGravityTestBody : public AActor
{
	GENERATED_BODY()

public:
	ARadialGravityTestBody();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(VisibleAnywhere, Category = "RadialGravity")
	UStaticMeshComponent* Mesh;

	/** Planet center in world space (cm). Default = world origin. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	FVector GravityCenter = FVector::ZeroVector;

	/** Gravitational acceleration magnitude (cm/s^2). 980 = 9.8 m/s^2. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	double GravityStrength = 980.0;

	/** Planet surface radius (cm), used only for rest detection / logging. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	double SurfaceRadius = 637100000.0;

	/** Speed below which the body is considered at rest (cm/s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	double RestSpeedThreshold = 250.0;

	/** Distance band around the surface that counts as "on the surface" (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	double SurfaceBandCm = 50000.0;

private:
	double Elapsed = 0.0;
	double LogAccum = 0.0;
	double RestTimer = 0.0;
	bool bResultWritten = false;
	FString LogPath;
	FString JsonPath;

	void WriteResultJson(bool bRested, const FVector& Loc, const FVector& Vel, double DistFromCenter);
};
