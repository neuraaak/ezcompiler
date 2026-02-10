# Protocols Layer

Compiler and uploader protocol implementations for **EzCompiler**.

The protocols layer defines abstract base classes and concrete implementations for compilation and upload operations.

---

## Compiler Protocols

### BaseCompiler

Abstract base class defining the compiler protocol interface.

::: ezcompiler.protocols.base_compiler.BaseCompiler

---

### CxFreezeCompiler

Cx_Freeze compiler implementation for directory-based builds.

::: ezcompiler.protocols.cx_freeze_compiler.CxFreezeCompiler

---

### PyInstallerCompiler

PyInstaller compiler implementation for single-file executables.

::: ezcompiler.protocols.pyinstaller_compiler.PyInstallerCompiler

---

### NuitkaCompiler

Nuitka compiler implementation for optimized native compilation.

::: ezcompiler.protocols.nuitka_compiler.NuitkaCompiler

---

## Uploader Protocols

### BaseUploader

Abstract base class defining the uploader protocol interface.

::: ezcompiler.protocols.base_uploader.BaseUploader

---

### DiskUploader

Local disk uploader for saving compiled projects to the file system.

::: ezcompiler.protocols.disk_uploader.DiskUploader

---

### ServerUploader

HTTP/HTTPS server uploader for remote distribution.

::: ezcompiler.protocols.server_uploader.ServerUploader

---

## Factory

### UploaderFactory

Factory class for creating uploader instances based on configuration.

::: ezcompiler.protocols.uploader_factory.UploaderFactory
