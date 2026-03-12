# Services Layer

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
