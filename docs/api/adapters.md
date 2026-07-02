# Adapters layer

Compiler and uploader adapter implementations for **EzCompiler**.

The adapters layer defines abstract base classes and concrete implementations for compilation and upload operations.

!!! note "Internal modules"
    Concrete compiler/uploader implementations live in private modules
    (prefixed with `_`) and are instantiated through the factories rather than
    imported directly. Public consumers should use
    [`CompilerFactory`](#compilerfactory) and [`UploaderFactory`](#uploaderfactory),
    or the high-level [`EzCompiler`](interfaces.md) facade.

---

## Compiler adapters

### BaseCompiler

Abstract base class defining the compiler interface.

::: ezcompiler.adapters.base_compiler.BaseCompiler

---

### CxFreezeCompiler

Cx_Freeze compiler implementation for directory-based builds.

::: ezcompiler.adapters._cx_freeze_compiler.CxFreezeCompiler

---

### PyInstallerCompiler

PyInstaller compiler implementation for single-file executables.

::: ezcompiler.adapters._pyinstaller_compiler.PyInstallerCompiler

---

### NuitkaCompiler

Nuitka compiler implementation for optimized native compilation.

::: ezcompiler.adapters._nuitka_compiler.NuitkaCompiler

---

### CompilerFactory

Factory class for creating compiler instances based on name or configuration.

::: ezcompiler.adapters.compiler_factory.CompilerFactory

---

## Installer adapters

### BaseInstaller

Abstract base class defining the first-deployment installer interface.

::: ezcompiler.adapters.base_installer.BaseInstaller

---

### InnoSetupInstaller

Inno Setup installer implementation, building a `setup.exe` via the external `ISCC.exe` binary.

::: ezcompiler.adapters._innosetup_installer.InnoSetupInstaller

---

### InstallerFactory

Factory class for creating installer instances based on backend name.

::: ezcompiler.adapters.installer_factory.InstallerFactory

---

## Releaser adapters

### BaseReleaser

Abstract base class defining the secure-release packager interface.

::: ezcompiler.adapters.base_releaser.BaseReleaser

---

### TufupReleaser

tufup (TUF) releaser implementation, packaging a compiled bundle into a signed TUF repository.

::: ezcompiler.adapters._tufup_releaser.TufupReleaser

---

### ReleaserFactory

Factory class for creating releaser instances based on backend name.

::: ezcompiler.adapters.releaser_factory.ReleaserFactory

---

## File writer adapters

### BaseFileWriter

Abstract base class defining the file writer interface.

::: ezcompiler.adapters.base_file_writer.BaseFileWriter

---

### DiskFileWriter

Concrete file writer implementation for local disk operations.

::: ezcompiler.adapters._disk_file_writer.DiskFileWriter

---

## Uploader adapters

### BaseUploader

Abstract base class defining the uploader interface.

::: ezcompiler.adapters.base_uploader.BaseUploader

---

### DiskUploader

Local disk uploader for saving compiled projects to the file system.

::: ezcompiler.adapters._disk_uploader.DiskUploader

---

### ServerUploader

HTTP/HTTPS server uploader for remote distribution.

::: ezcompiler.adapters._server_uploader.ServerUploader

---

## Factory

### UploaderFactory

Factory class for creating uploader instances based on configuration.

::: ezcompiler.adapters.uploader_factory.UploaderFactory
