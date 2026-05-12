"""Custom exceptions E001-E008."""
from __future__ import annotations

class ApidocError(Exception):
    code: str = "E000"
    def __init__(self, message: str, detail: str = ""):
        self.message = message; self.detail = detail
        super().__init__(message)

class NetworkError(ApidocError):  code = "E001"
class AuthError(ApidocError):     code = "E002"
class ValidationError(ApidocError): code = "E003"
class ParseError(ApidocError):    code = "E004"
class NotFoundError(ApidocError): code = "E005"
class ServerError(ApidocError):   code = "E006"
class PluginError(ApidocError):   code = "E007"
class ConfigError(ApidocError):   code = "E008"
