---
description: Aurora - independent community smart home orchestrator. Routes any smart home request to the right specialist skill and recommends the correct Claude model. Use this as your starting point for Home Assistant, ESPHome, Node-RED, or any IoT automation task.
---

Read and follow the `aurora/SKILL.md` file that lives in this Aurora plugin's install directory - the same plugin directory that contains this `commands/aurora.md` file. Resolve the path relative to this command file's own location inside `~/.claude/plugins/<plugin>/aurora-smart-home/`, NOT relative to the user's current working directory. The user is almost always sitting in a different project (where they want a smart home thing built) and that project will not contain an `aurora/` folder. If you cannot find `aurora/SKILL.md` next to this command file, the Aurora plugin install is broken - say so directly rather than offering to create the file in the user's working project.

Once `aurora/SKILL.md` is loaded, start with the banner display and the opening question per the instructions in that file.
