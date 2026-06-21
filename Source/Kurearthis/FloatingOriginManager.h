#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FloatingOriginManager.generated.h"

/**
 * Floating-origin foundation for the planetary world model.
 *
 * The planet is centered at the world origin with an Earth-scale radius, so
 * anything on its surface sits ~6,371 km from origin where single-precision
 * physics integration breaks down (proven in PLANETARY_PROOF.md, Proof 2b).
 *
 * This manager keeps a designated Focus actor (the player, or here the test
 * body) within RebaseThreshold of the world origin by calling
 * UWorld::SetNewWorldOrigin. The whole world (planet included) shifts so the
 * active region is always near (0,0,0), where Chaos is exact. Distances and
 * directions to the planet center are preserved because everything rebases
 * together. This is the real spine the surface gameplay, atmosphere exit, and
 * second body all build on, not a per-feature shortcut.
 */
UCLASS()
class KUREARTHIS_API AFloatingOriginManager : public AActor
{
	GENERATED_BODY()

public:
	AFloatingOriginManager();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	/** Actor to keep near the world origin. If null, the radial gravity test body is used. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "FloatingOrigin")
	AActor* Focus = nullptr;

	/** Rebase whenever Focus drifts this far (cm) from the world origin. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "FloatingOrigin")
	double RebaseThresholdCm = 50000.0; // 500 m

	/** Number of rebases performed (for verification). */
	UPROPERTY(VisibleAnywhere, Category = "FloatingOrigin")
	int32 RebaseCount = 0;

private:
	FString LogPath;
	bool bRebasingConfirmedWorking = false;
};
