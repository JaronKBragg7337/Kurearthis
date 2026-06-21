#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SweptGravityBody.generated.h"

class UStaticMeshComponent;

/**
 * Custom radial-gravity body driven by DIRECT INTEGRATION + swept movement,
 * NOT Chaos forces.
 *
 * Proof 2b/2c/2d established that Chaos rigid-body physics is unusable here:
 * it fails at planetary absolute coordinates and, even near the origin under a
 * floating origin, an `AddForce(bAccelChange)` body falls ~100x too slowly
 * (see PLANETARY_PROOF.md). The proven-correct path is the double-precision
 * integrator of Proof 2a. This actor is that integrator made into a runtime
 * body: each tick it accumulates velocity toward the planet center (UE5 FVector
 * is double precision) and moves itself with `AddActorWorldOffset(sweep=true)`
 * so it collides against the LOCAL surface patch near the origin and RESTS on it
 * with local up = radial. It is kinematic (no SimulatePhysics).
 *
 * The planet center is read from the actor tagged "Planet" each tick, so the
 * math survives floating-origin rebasing (AFloatingOriginManager) exactly as the
 * Chaos test body did. All logging uses the frame-independent body-to-center
 * distance.
 */
UCLASS()
class KUREARTHIS_API ASweptGravityBody : public AActor
{
	GENERATED_BODY()

public:
	ASweptGravityBody();

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
	double RestSpeedThreshold = 50.0;

	/** Distance band around the surface that counts as "on the surface" (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RadialGravity")
	double SurfaceBandCm = 50000.0;

private:
	FVector Velocity = FVector::ZeroVector;
	double Elapsed = 0.0;
	double LogAccum = 0.0;
	double RestTimer = 0.0;
	bool bResultWritten = false;
	FString LogPath;
	FString JsonPath;

	FVector GravityCenter() const;
	void WriteResultJson(bool bRested, const FVector& Loc, double DistFromCenter);
};
