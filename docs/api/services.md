# Services layer

Business logic services and orchestration for **EzCompiler**.

The services layer implements the core business logic, handling compilation, configuration, template processing, and upload operations.

---

## CompilerService

Service for managing compiler selection and orchestrating the compilation process.

::: ezcompiler.services.compiler_service.CompilerService

---

## ConfigService

Service for loading, validating, and managing configuration.

::: ezcompiler.services.config_service.ConfigService

---

## TemplateService

Service for processing templates and generating dynamic files.

::: ezcompiler.services.template_service.TemplateService

---

## PipelineService

Service for orchestrating the full compile → zip → upload pipeline with injectable factory.

::: ezcompiler.services.pipeline_service.PipelineService

---

## UploaderService

Service for orchestrating upload operations to various backends.

::: ezcompiler.services.uploader_service.UploaderService

---

## UpdaterService

Service for generating client updater files (`update.py`, `settings.py`, `root.json`) for tufup-based auto-update workflows.

::: ezcompiler.services.updater_service.UpdaterService

---

## InstallerService

Service orchestrating first-deployment installer packaging via an installer adapter.

::: ezcompiler.services.installer_service.InstallerService

---

## ReleaseService

Service orchestrating secure-release packaging (TUF) and, optionally, publication.

::: ezcompiler.services.release_service.ReleaseService
