#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurfacePatch.generated.h"

class UStaticMeshComponent;

/**
 * Local surface-collision patch that FOLLOWS a focus actor around the sphere.
 *
 * The planet cannot be one giant collision mesh (PLANETARY_PROOF.md, 2c/2d), so the
 * walkable surface is a small local patch near the player. This actor re-centers and
 * re-orients that patch under the focus (the pawn) every tick: it sits tangent to the
 * sphere directly beneath the focus, its top face at the surface radius, its up = the
 * local radial direction. So the focus is always over solid ground and can roam the
 * whole planet without reaching the patch edge. This is the first step of the terrain
 * streaming described in WORLD_MODEL.md (here: one follower tile; later: a streamed
 * grid).
 *
 * Ticks in TG_PrePhysics so the patch is in place before the pawn's grounding sweep
 * (TG_DuringPhysics). Reads the planet center by the "Planet" tag, so it stays correct
 * under floating-origin rebasing.
 */
UCLASS()
class KUREARTHIS_API ASurfacePatch : public AActor
{
	GENERATED_BODY()

public:
	ASurfacePatch();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(VisibleAnywhere, Category = "SurfacePatch")
	UStaticMeshComponent* Mesh;

	/** Actor the patch stays beneath. Found by the "Focus" tag if unset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SurfacePatch")
	AActor* Focus = nullptr;

	/** Planet whose center defines the radial up. Found by the "Planet" tag if unset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SurfacePatch")
	AActor* PlanetActor = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SurfacePatch")
	FVector FallbackCenter = FVector::ZeroVector;

	/** Surface radius (cm); the patch top face is kept at this distance from center. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SurfacePatch")
	double SurfaceRadius = 637100000.0;

private:
	FVector GravityCenter() const;
};
