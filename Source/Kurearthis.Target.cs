using UnrealBuildTool;
using System.Collections.Generic;

public class KurearthisTarget : TargetRules
{
	public KurearthisTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V7;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("Kurearthis");
	}
}
