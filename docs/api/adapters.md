# Adapters Layer

Compiler and uploader adapter implementations for **EzCompiler**.

The adapters layer defines abstract base classes and concrete implementations for compilation and upload operations.

---

## Compiler Adapters

### BaseCompiler

Abstract base class defining the compiler interface.

::: ezcompiler.adapters.base_compiler.BaseCompiler

---

### CxFreezeCompiler

Cx_Freeze compiler implementation for directory-based builds.

::: ezcompiler.adapters.cx_freeze_compiler.CxFreezeCompiler

---

### PyInstallerCompiler

PyInstaller compiler implementation for single-file executables.

::: ezcompiler.adapters.pyinstaller_compiler.PyInstallerCompiler

---

### NuitkaCompiler

Nuitka compiler implementation for optimized native compilation.

::: ezcompiler.adapters.nuitka_compiler.NuitkaCompiler

---

### CompilerFactory

Factory class for creating compiler instances based on name or configuration.

::: ezcompiler.adapters.compiler_factory.CompilerFactory

---

## File Writer Adapters

### BaseFileWriter

Abstract base class defining the file writer interface.

::: ezcompiler.adapters.base_file_writer.BaseFileWriter

---

### DiskFileWriter

Concrete file writer implementation for local disk operations.

::: ezcompiler.adapters.disk_file_writer.DiskFileWriter

---

## Uploader Adapters

### BaseUploader

Abstract base class defining the uploader interface.

::: ezcompiler.adapters.base_uploader.BaseUploader

---

### DiskUploader

Local disk uploader for saving compiled projects to the file system.

::: ezcompiler.adapters.disk_uploader.DiskUploader

---

### ServerUploader

HTTP/HTTPS server uploader for remote distribution.

::: ezcompiler.adapters.server_uploader.ServerUploader

---

## Factory

### UploaderFactory

Factory class for creating uploader instances based on configuration.

::: ezcompiler.adapters.uploader_factory.UploaderFactory
