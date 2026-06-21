# AUTHORIZATION — standing permissions for AI builders

This file records what Jaron has authorized Claude and Codex to do without
re-asking each session. It is project law (see `CHARTER.md`). Only Jaron may
amend it.

## Why this exists
Earlier sessions stalled by stopping to ask, or by taking shortcuts to avoid a
setup step, when Jaron had already authorized the real action. This file makes
the standing authorization explicit so builders implement instead of explaining.

## Build the real thing, not a shortcut
Authorized and expected: when the correct implementation needs a real foundation
(an SDK, a build system, an engine subsystem, a C++ module, an editor restart),
**do the necessary thing**. Do not substitute a smaller hack that pushes the real
problem downstream — that pattern is why this is the third attempt at this
project. "Necessary" is not the same as "big/over-scoped"; build the necessary
foundation for the current proof, and no more (the Growth law in `CHARTER.md`
still applies — don't build the whole solar system to prove one fall).

## Installing software / dependencies
- Builders MAY install tools, SDKs, runtimes, packages, and engine dependencies
  that the work genuinely needs (e.g. via `winget`, an official installer, or a
  package manager).
- Some installs require a Windows UAC / "Do you want to allow this app to make
  changes?" / firewall prompt. **The AI cannot see or click these prompts —
  Jaron approves them.** When an install needs elevation, the builder should:
  1. start the install via the strongest automated path,
  2. tell Jaron in plain text that a prompt may appear and to press **Yes /
     Allow / Install**,
  3. then continue and verify the result.
  (Confirmed 2026-06-20: the .NET Framework 4.8.1 SDK was installed this way;
  Jaron approved the prompt that the AI could not see.)
- Prefer per-user / silent installs where possible, but elevation is allowed
  when required. Do not install unrelated software, and say what is being
  installed and why.

## Unreal Engine operations
Authorized without re-asking:
- Drive the live editor primarily via localhost Python remote execution
  (`_authoring/ue_remote.py`); use the Python console and GUI automation only as
  fallbacks when needed.
- Close, reopen, and rebuild the editor (kill `UnrealEditor` /
  `CrashReportClientEditor`, run `Build.bat`, relaunch) when a C++ module change
  requires it. Always re-verify the live scene on reopen (Crash/Restart law).
- Add/modify C++ modules, Blueprints, assets, and config as the proof requires.
- Generate and run authoring/test scripts and harnesses.

## Strongest-automation-path policy (from Jaron, 2026-06-20)
"Use the strongest available automation path: Unreal Python, editor console,
Blueprint asset generation, GUI automation, native computer control, scripts,
test harnesses, and commits. Do not hand manual work back to Jaron unless every
automatable route fails — and if it does, document exactly what failed and why."
If an approach looks blocked, try an alternate automated path before asking.

## What still requires Jaron
- Approving the UAC / install / firewall prompts described above (a single click).
- Human-judgment verification: movement feel, visual read, whether surface +
  atmosphere + space read as one world, whether it actually plays well.
- Decisions that change project law or the product direction (amending the
  charter, picking between genuinely different architectures with long-term
  consequences) — surface a recommendation, don't silently commit the project
  to one.

## Still binding regardless of this file
- Honest builder attribution; share state only through committed files.
- No secrets/personal/private data in the repo (it is PUBLIC; the name must not
  hint at the space arc).
- The proof order and Growth/Reality/Assumption laws in `CHARTER.md`.
