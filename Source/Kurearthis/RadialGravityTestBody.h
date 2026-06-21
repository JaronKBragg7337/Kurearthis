#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RadialGravityTestBody.generated.h"

class UStaticMeshComponent;

/**
 * Test body for the planetary architecture.
 *
 * Simulates real Chaos physics with the engine's default (flat -Z) gravity
 * DISABLED and instead applies a constant acceleration toward the planet
 * center every tick. Proves the foundational planetary truth: gravity is
 * radial toward a body center and a falling object's local up is the radial
 * direction, not world +Z.
 *
 * The planet center is read from the actual planet actor each tick (found by
 * the "Planet" tag), so the math stays correct under floating-origin rebasing
 * (see AFloatingOriginManager): when the world recenters, body and planet shift
 * together and the radial vector between them is preserved. All logging uses the
 * body-to-planet RELATIVE distance, which is frame-independent.
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

	/** Planet whose center is the gravity source. Found by the "Planet" tag if unset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	AActor* PlanetActor = nullptr;

	/** Fallback gravity center (cm) if no planet actor is found. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	FVector FallbackCenter = FVector::ZeroVector;

	/** Gravitational acceleration magnitude (cm/s^2). 980 = 9.8 m/s^2. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	double GravityStrength = 980.0;

	/** Planet surface radius (cm), used for rest detection / logging. */
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

	FVector GravityCenter() const;
	void WriteResultJson(bool bRested, const FVector& Loc, const FVector& Vel, double DistFromCenter);
};
