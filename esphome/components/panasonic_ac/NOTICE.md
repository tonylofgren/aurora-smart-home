# Vendored from DomiStyle/esphome-panasonic-ac

This directory contains a verbatim copy of the `panasonic_ac` ESPHome
external component originally published at
[github.com/DomiStyle/esphome-panasonic-ac](https://github.com/DomiStyle/esphome-panasonic-ac).
The code is redistributed here under its original MIT license so Aurora
users can build Panasonic AC firmware without fetching a third-party
GitHub repository at compile time.

## Upstream snapshot

| Field | Value |
|-------|-------|
| Repository | `DomiStyle/esphome-panasonic-ac` |
| Branch | `master` |
| Commit | `6fce2556ce5264304c72236e7dcb7032bfdfcd4b` |
| Date | 2026-01-31 |

## License

MIT License, Copyright (c) 2020 Dominik. See [`LICENSE`](LICENSE) in this
directory for the full text.

The MIT license is preserved verbatim. No conditions are added.

## Aurora-side modifications

**None.** The files in this directory are byte-for-byte identical to the
upstream copy at the commit above. If a fix or local modification lands
here in the future, an Aurora-authored header comment will be added to
the affected file describing what changed and why, and this NOTICE will
be updated.

## File integrity (SHA-256)

If you want to verify that this vendor copy has not been tampered with,
the following hashes correspond to the files as fetched from the
upstream raw URL at the commit above:

| File | Bytes | SHA-256 |
|------|------:|---------|
| `__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `climate.py` | 5245 | `7973a2cd7d2488304d16ea213c7d9b35ba749a6c52f80ed68b9463753d94536b` |
| `esppac.h` | 5578 | `284e7b048a7f7ddd0f18e46ddb4d1284952892ba0361935263f15e27310e2dee` |
| `esppac.cpp` | 10280 | `a899e27da0ec42477c971e5eb65442cdd19767fa006e28ec6a7e83b2ae443f3b` |
| `esppac_cnt.h` | 1818 | `710df6be507a116c7207fae2f70fec7fb5735308d92101269b2f39a96545518a` |
| `esppac_cnt.cpp` | 16756 | `8368082de538617b5ed845ddd37275f4571456aa20352b4a6d2c2270e78062b1` |
| `esppac_wlan.h` | 2942 | `5b6fc854509f91191d8bc946ccf2e601b056863a9827a653d4c3fd88de8bc647` |
| `esppac_wlan.cpp` | 27919 | `9ec40039b9657f26b4af8b40cbec1ec134ecf506b4007ab2cd94c5c5df0a8773` |
| `esppac_commands_cnt.h` | 1013 | `1e203ba76e55d7f59beea48a5c6550d1d7ceec3628e65082905df284918a1734` |
| `esppac_commands_wlan.h` | 2471 | `9a91936686360c05ba6516a5e9770797fd3ccd57cdc89a8e2ec03286109f5334` |
| `panasonic_ac_select.h` | 362 | `0dd02dda60932c0b45b22b6e2d034998da48ddd8aee2d71cf304d05a667c2f6f` |
| `panasonic_ac_switch.h` | 353 | `aee65ea8f8075b877205a210bcbd9561223fbeb4b02dddda04fe093c8bb7b654` |
| `LICENSE` | 1064 | `4d80443925e00941c602416b912316665a4894fc9d29cf32f888f4b40394e0d2` |

Reproduce locally with:

```powershell
Get-FileHash -Algorithm SHA256 *
```

## How Aurora users load this component

Place a copy of this directory next to your ESPHome YAML config under a
folder named `components/panasonic_ac/`. Then in your YAML:

```yaml
external_components:
  - source:
      type: local
      path: components
    components: [panasonic_ac]
```

No GitHub fetch happens at compile time.

## Upstream protocol documentation

DomiStyle published the reverse-engineered protocol documentation under
the same MIT license at
[github.com/DomiStyle/esphome-panasonic-ac/tree/master/protocol](https://github.com/DomiStyle/esphome-panasonic-ac/tree/master/protocol).
The `.ods` spreadsheets describe the CN-CNT and CN-WLAN wire formats,
and the `logic_analyzer/` captures show real commands. Useful reading
if you need to extend the component for an AC model that does not yet
work.

## Maintenance commitment

Aurora is now responsible for keeping this vendor copy current with
upstream fixes. The expected cadence is a quarterly check against
upstream `master`; pull in protocol fixes and new AC model support as
they land. Update this NOTICE.md with the new commit SHA and refreshed
hash table after each sync.

## Bug reports

Bugs in the Panasonic protocol implementation or AC compatibility
issues are best filed upstream first
([DomiStyle issue tracker](https://github.com/DomiStyle/esphome-panasonic-ac/issues))
so other ESPHome users benefit. If a fix lands upstream and Aurora has
not yet synced, file a separate Aurora issue asking for the bump.
