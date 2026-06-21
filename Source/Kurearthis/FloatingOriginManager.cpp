#include "FloatingOriginManager.h"

#include "RadialGravityTestBody.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "GameFramework/WorldSettings.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"

AFloatingOriginManager::AFloatingOriginManager()
{
	PrimaryActorTick.bCanEverTick = true;
	// Rebase before physics so the simulation step runs in the recentered frame.
	PrimaryActorTick.TickGroup = TG_PrePhysics;
}

void AFloatingOriginManager::BeginPlay()
{
	Super::BeginPlay();

	LogPath = FPaths::ProjectSavedDir() / TEXT("FloatingOrigin.log");
	FFileHelper::SaveStringToFile(
		FString::Printf(TEXT("# floating origin manager  threshold=%.1f cm  initial origin=%s\n"),
			RebaseThresholdCm, *GetWorld()->OriginLocation.ToString()),
		*LogPath);

	if (!Focus)
	{
		Focus = UGameplayStatics::GetActorOfClass(GetWorld(), ARadialGravityTestBody::StaticClass());
	}

	// Allow large coordinates without the engine culling actors during rebasing.
	if (AWorldSettings* WS = GetWorldSettings())
	{
		WS->bEnableWorldBoundsChecks = false;
	}
}

void AFloatingOriginManager::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!Focus)
	{
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	const FVector Loc = Focus->GetActorLocation();
	if (Loc.Size() <= RebaseThresholdCm)
	{
		return;
	}

	const FIntVector OldOrigin = World->OriginLocation;
	const FIntVector NewOrigin = OldOrigin + FIntVector(
		FMath::RoundToInt(Loc.X), FMath::RoundToInt(Loc.Y), FMath::RoundToInt(Loc.Z));

	World->SetNewWorldOrigin(NewOrigin);

	const FIntVector AfterOrigin = World->OriginLocation;
	const FVector FocusAfter = Focus->GetActorLocation();
	const bool bMoved = (AfterOrigin != OldOrigin);
	if (bMoved)
	{
		bRebasingConfirmedWorking = true;
	}
	RebaseCount++;

	FFileHelper::SaveStringToFile(
		FString::Printf(
			TEXT("rebase #%d worked=%d focusWas=(%.1f,%.1f,%.1f) |%.1f| origin %s -> %s focusNow=(%.1f,%.1f,%.1f) |%.1f|\n"),
			RebaseCount, bMoved ? 1 : 0, Loc.X, Loc.Y, Loc.Z, Loc.Size(),
			*OldOrigin.ToString(), *AfterOrigin.ToString(),
			FocusAfter.X, FocusAfter.Y, FocusAfter.Z, FocusAfter.Size()),
		*LogPath, FFileHelper::EEncodingOptions::AutoDetect, &IFileManager::Get(),
		EFileWrite::FILEWRITE_Append);
}
