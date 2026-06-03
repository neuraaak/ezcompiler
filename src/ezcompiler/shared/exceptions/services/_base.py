# ///////////////////////////////////////////////////////////////
# BASE - Base exception for EzCompiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base exception - Core exception class for all EzCompiler errors.

This module defines the base exception class that all other exceptions inherit from.
"""

from __future__ import annotations

from ..utils._base import EzCompilerError


# TODO [AUDIT P2]: fusionner les deux hiérarchies d'exceptions (utils/ et services/)
# UploadError existe dans les deux arbres avec des parents différents — ambiguïté pour les consommateurs.
# Objectif : un seul arbre sous EzCompilerError (utils/base.py), supprimer EzCompilerServiceError
# ou en faire un alias transparent. Voir shared/exceptions/utils/ pour la hiérarchie cible.
class EzCompilerServiceError(EzCompilerError):
    """Base exception for all EzCompiler services errors."""
