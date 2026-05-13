# Unknown Component Validator

Defines what an agent does when the user names a community component (ESPHome `external_components`, HACS integration, AppDaemon app, Node-RED contrib package) that Aurora has no profile for. Without this contract, agents either fabricate plausible-but-wrong configuration or refuse to help at all. The protocol picks the third path: gather the minimum facts needed to be honest, record the gap in the snapshot, and proceed with explicit caution flags.

## When to Run

Any agent that is about to recommend, configure, or generate code involving a community-distributed component MUST run this protocol first when no matching profile exists in:

- `aurora/references/external_components/` (ESPHome modules)
- `aurora/references/hacs_integrations/` (HACS-distributed HA integrations)

In practice that covers: Volt (external ESPHome components), Atlas (HACS integrations and community API connectors), Ada (HACS-installed custom integrations the user references), Mira (HACS-installed LLM or voice integrations), River (community Node-RED contrib packages).

## The Contract

When Aurora has no profile, do NOT proceed by guessing. Ask the user three concrete questions, record their answers as a `notes[]` entry in the project snapshot, and continue with the answers as authoritative.

### The three questions

1. **Source URL** — "What is the exact GitHub URL (or other source) for this component? Aurora has no profile for it, so the source has to come from you."

2. **Hardware / HA version requirements** — for ESPHome components: "Which ESP chips does it support and what's the minimum ESPHome version?". For HACS integrations: "Which Home Assistant version is the minimum, and which HA entity domains does it provide?".

3. **Datasheet / docs link** — "Where is the component's documentation? Aurora will not generate configuration past what the documentation explicitly shows."

If the user cannot answer any of the three, the validator blocks: the agent MUST refuse to generate configuration until the user supplies the missing fact. Refusing is the correct outcome — the alternative is fabrication.

## Snapshot Recording

After the user answers, the invoking agent appends a `notes[]` entry to the project snapshot (`aurora-project.json`) with shape:

```json
{
  "author": "<agent_soul>",
  "added_at": "<ISO 8601 timestamp>",
  "text": "Unknown community component '<name>' used at user's request. Source: <url>. Min version: <version>. Docs: <url>. Aurora has no verified profile for this component; configuration is based on user-supplied facts and the linked documentation only."
}
```

This entry has three purposes:

- A future agent reviewing the snapshot sees the gap and treats the component cautiously.
- If a debugging session later discovers the component was the failure point, the audit trail is intact.
- When the maintainer (or a contributor) decides to add a verified profile to `aurora/references/external_components/` or `aurora/references/hacs_integrations/`, the snapshot entry is a starting point.

## Caution Flags

After the snapshot is updated, the agent's output MUST include a clearly visible caution block:

```
⚠️ Community component (no Aurora profile)
   Component: <name>
   Source: <url>
   Configuration here follows the documentation at <docs_url> and the
   facts you supplied. Aurora has not verified this component against
   any datasheet or against your current platform version.

   What this means in practice:
   - Test the component in isolation before relying on it.
   - If it breaks, check the upstream issue tracker before assuming
     Aurora's surrounding configuration is wrong.
   - Consider opening a PR to aurora/references/<dir>/<name>.json
     so the next user gets a verified profile.
```

The block is mandatory even when configuration is straightforward. It is the user's signal that the rest of the response is not as well-grounded as code that uses validated reference data.

## QUICK Mode Without a Snapshot

In QUICK mode (single-agent task, no snapshot on disk) the agent still asks the three questions and still emits the caution block, but the `notes[]` recording step is skipped. The caution block alone carries the warning.

## What This Validator Does NOT Do

- It does not rate or judge community components ("good" / "bad" / "recommended"). That requires verified data the catalog does not yet have.
- It does not validate that the source URL is reachable or that the component is licensed compatibly. Those are out of scope.
- It does not auto-add the component to the catalog. Profile entries require manual verification per `aurora/references/external_components/CONTRIBUTING.md`.

## Output

- Pass: empty failures list. The user supplied all three answers; the agent proceeds with the caution block.
- Warnings: none. The caution block in the user-facing output replaces the warning channel.
- Failures: list of failure strings — one per unanswered question. Agents MUST NOT generate configuration if non-empty.

Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional).

## Example: Volt encountering an unprofiled external_component

User: "Configure my ESP32-S3 with the `airgradient` external component."

Volt looks up `aurora/references/external_components/airgradient.json` — not present.

Volt invokes the unknown-component protocol and responds:

```
I do not have a verified profile for the `airgradient` external_components
module. To configure your board with it correctly I need three things:

1. The exact GitHub URL (or other source) for the airgradient component.
2. Which ESP chips it supports and the minimum ESPHome version.
3. A link to the component's documentation.

I will use your answers and the linked docs as the only sources for the
generated YAML, and will flag the configuration as unverified in your
project snapshot.
```

If the user supplies all three, Volt updates `aurora-project.json` with the notes entry and continues with the caution block in the YAML response.

If the user cannot supply one, Volt refuses to generate the config: the alternative is fabrication, which is worse than no answer.
