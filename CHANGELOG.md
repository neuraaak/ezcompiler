# Changelog

## [4.0.0]

### BREAKING

- Replace flat `installer_*` fields with the nested
  `[tool.ezcompiler.installer]` section and `CompilerConfig.installer` / `InstallerConfig`.
  Legacy configuration keys raise `ConfigurationError`; removed Python constructor
  keywords raise `TypeError`.
- Replace placeholder rendering with Jinja2 script generation using custom
  delimiters. Adopted/custom `.iss` files are now compiled directly and are not
  re-rendered or rewritten; the file takes precedence over generation options.
- Remove substitution of `#TOKEN#` placeholders in custom installer scripts.
  Generate replacements with `ezcompiler generate iss`, port manual edits, and
  adopt the new file through `installer.iss_path`.

### Fixed

- Keep `AppId` stable across versions, deriving its GUID from company and project
  names or honoring an explicit GUID so installers retain product identity.
- Supply all five volatile build values through ISCC `/D` defines:
  `MyAppVersion`, `VersionInfo`, `BundleDir`, `OutputDir`, and `MainExe`.
  Committed generated scripts no longer bake in stale release values.
- Write ephemeral and generated installer scripts as UTF-8 with a BOM to preserve
  accented names when ISCC reads them.
- Escape literal opening braces without duplicating closing braces, and emit the
  literal GUID syntax required by Inno Setup's `AppId`. Keep the setup filename
  literal so names containing braces produce the expected executable on disk.
- Make installer script behavior explicit: default scripts are ephemeral, failed
  ISCC invocations retain diagnostic scripts, generated scripts can be adopted,
  and file-mode builds warn about ignored non-default generation options.
