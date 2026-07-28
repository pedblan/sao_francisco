from __future__ import annotations

import ctypes
import hmac
import importlib
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from types import ModuleType
from typing import Any, cast


class CredentialError(RuntimeError):
    """Erro sanitizado ao acessar uma credencial."""


class SecureStoreUnavailable(CredentialError):
    """O cofre nativo não está disponível nesta plataforma."""


@dataclass(frozen=True, slots=True)
class CredentialSpec:
    provider: str
    account: str
    environment_name: str
    display_name: str


CREDENTIALS: dict[str, CredentialSpec] = {
    "openai": CredentialSpec(
        provider="openai",
        account="openai-api-key",
        environment_name="OPENAI_API_KEY",
        display_name="OpenAI",
    ),
    "gemini": CredentialSpec(
        provider="gemini",
        account="gemini-api-key",
        environment_name="GEMINI_API_KEY",
        display_name="Gemini",
    ),
}

SERVICE_NAME = "São Francisco"
ERR_SEC_SUCCESS = 0
ERR_SEC_DUPLICATE_ITEM = -25299
ERR_SEC_ITEM_NOT_FOUND = -25300
ERROR_NOT_FOUND = 1168
CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2


def secure_store_label() -> str:
    if sys.platform == "darwin":
        return "macOS Keychain"
    if sys.platform == "win32":
        return "Credenciais do Windows"
    return "cofre seguro do sistema"


def secure_store_available() -> bool:
    try:
        if sys.platform == "darwin":
            _security_framework()
        elif sys.platform == "win32":
            _windows_api()
        else:
            return False
    except SecureStoreUnavailable:
        return False
    return True


def credential_status(provider: str) -> dict[str, object]:
    spec = _spec(provider)
    native = _read_native(spec.account)
    environment = os.environ.get(spec.environment_name, "").strip()
    if native:
        source = secure_store_label()
    elif environment:
        source = "sessão atual"
    else:
        source = ""
    return {
        "provider": provider,
        "name": spec.display_name,
        "configured": bool(native or environment),
        "source": source,
        "storeAvailable": secure_store_available(),
        "storeLabel": secure_store_label(),
    }


def read_secret(provider: str) -> str | None:
    spec = _spec(provider)
    native = _read_native(spec.account)
    if native:
        return native
    environment = os.environ.get(spec.environment_name, "").strip()
    return environment or None


def save_secret(provider: str, value: str) -> None:
    spec = _spec(provider)
    secret = value.strip()
    if not secret:
        raise CredentialError("Cole uma chave antes de salvar.")
    _save_native_verified(spec.account, secret)


def delete_secret(provider: str) -> None:
    spec = _spec(provider)
    _delete_native(spec.account)


def _spec(provider: str) -> CredentialSpec:
    try:
        return CREDENTIALS[provider]
    except KeyError as exc:
        raise CredentialError("Provedor de credencial desconhecido.") from exc


@lru_cache(maxsize=1)
def _security_framework() -> Any:
    if sys.platform != "darwin":
        raise SecureStoreUnavailable("macOS Keychain indisponível.")
    try:
        module: ModuleType = importlib.import_module("Security")
    except ImportError as exc:
        raise SecureStoreUnavailable(
            "A integração nativa com o macOS Keychain não foi instalada."
        ) from exc
    return cast(Any, module)


class _WindowsCredentialApi:
    def __init__(self) -> None:
        from ctypes import wintypes

        class Credential(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(wintypes.BYTE)),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", ctypes.c_void_p),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        win_dll = getattr(ctypes, "WinDLL", None)
        if win_dll is None:
            raise SecureStoreUnavailable(
                "O Gerenciador de Credenciais do Windows está indisponível."
            )
        api = win_dll("Advapi32.dll", use_last_error=True)
        pointer_type = ctypes.POINTER(Credential)
        api.CredReadW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.POINTER(pointer_type),
        ]
        api.CredReadW.restype = wintypes.BOOL
        api.CredWriteW.argtypes = [pointer_type, wintypes.DWORD]
        api.CredWriteW.restype = wintypes.BOOL
        api.CredDeleteW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
        ]
        api.CredDeleteW.restype = wintypes.BOOL
        api.CredFree.argtypes = [ctypes.c_void_p]
        api.CredFree.restype = None

        self.api = api
        self.credential_type = Credential
        self.pointer_type = pointer_type
        self.byte_pointer = ctypes.POINTER(wintypes.BYTE)

    def read(self, target: str) -> bytes | None:
        pointer = self.pointer_type()
        if not self.api.CredReadW(target, CRED_TYPE_GENERIC, 0, ctypes.byref(pointer)):
            error = _windows_last_error()
            if error == ERROR_NOT_FOUND:
                return None
            raise CredentialError(
                f"Não foi possível ler a chave nas Credenciais do Windows "
                f"(código {error})."
            )
        try:
            credential = pointer.contents
            return ctypes.string_at(
                credential.CredentialBlob,
                credential.CredentialBlobSize,
            )
        finally:
            self.api.CredFree(pointer)

    def save(self, target: str, account: str, value: bytes) -> None:
        blob = ctypes.create_string_buffer(value, len(value))
        credential = self.credential_type()
        credential.Type = CRED_TYPE_GENERIC
        credential.TargetName = target
        credential.CredentialBlobSize = len(value)
        credential.CredentialBlob = ctypes.cast(blob, self.byte_pointer)
        credential.Persist = CRED_PERSIST_LOCAL_MACHINE
        credential.UserName = account
        if not self.api.CredWriteW(ctypes.byref(credential), 0):
            error = _windows_last_error()
            raise CredentialError(
                f"Não foi possível salvar a chave nas Credenciais do Windows "
                f"(código {error})."
            )

    def delete(self, target: str) -> None:
        if self.api.CredDeleteW(target, CRED_TYPE_GENERIC, 0):
            return
        error = _windows_last_error()
        if error != ERROR_NOT_FOUND:
            raise CredentialError(
                f"Não foi possível remover a chave das Credenciais do Windows "
                f"(código {error})."
            )


@lru_cache(maxsize=1)
def _windows_api() -> _WindowsCredentialApi:
    if sys.platform != "win32":
        raise SecureStoreUnavailable(
            "O Gerenciador de Credenciais do Windows está indisponível."
        )
    return _WindowsCredentialApi()


def _target(account: str) -> str:
    return f"{SERVICE_NAME}/{account}"


def _read_native(account: str) -> str | None:
    if sys.platform == "darwin":
        try:
            security = _security_framework()
        except SecureStoreUnavailable:
            return None
        query = _macos_query(security, account)
        query[security.kSecReturnData] = True
        query[security.kSecMatchLimit] = security.kSecMatchLimitOne
        status, result = security.SecItemCopyMatching(query, None)
        if status == ERR_SEC_ITEM_NOT_FOUND:
            return None
        if status != ERR_SEC_SUCCESS:
            raise CredentialError(
                f"Não foi possível ler a chave no macOS Keychain (código {status})."
            )
        return _decode_secret(bytes(result))
    if sys.platform == "win32":
        value = _windows_api().read(_target(account))
        return _decode_secret(value) if value is not None else None
    return None


def _save_native(account: str, value: str) -> None:
    if sys.platform == "darwin":
        security = _security_framework()
        query = _macos_query(security, account)
        data = value.encode("utf-8")
        status, _ = security.SecItemAdd(
            {**query, security.kSecValueData: data},
            None,
        )
        if status == ERR_SEC_DUPLICATE_ITEM:
            status = security.SecItemUpdate(
                query,
                {security.kSecValueData: data},
            )
        if status != ERR_SEC_SUCCESS:
            raise CredentialError(
                f"Não foi possível salvar a chave no macOS Keychain "
                f"(código {status})."
            )
        return
    if sys.platform == "win32":
        _windows_api().save(_target(account), account, value.encode("utf-8"))
        return
    raise SecureStoreUnavailable(
        "O São Francisco não salva chaves em texto simples. "
        "Use uma variável de ambiente nesta plataforma."
    )


def _delete_native(account: str) -> None:
    if sys.platform == "darwin":
        security = _security_framework()
        status = security.SecItemDelete(_macos_query(security, account))
        if status not in {ERR_SEC_SUCCESS, ERR_SEC_ITEM_NOT_FOUND}:
            raise CredentialError(
                f"Não foi possível remover a chave do macOS Keychain "
                f"(código {status})."
            )
        return
    if sys.platform == "win32":
        _windows_api().delete(_target(account))
        return
    raise SecureStoreUnavailable("O cofre seguro não está disponível nesta plataforma.")


def _save_native_verified(account: str, value: str) -> None:
    previous = _read_native(account)
    _save_native(account, value)
    if _same_secret(value, _read_native(account)):
        return
    try:
        _delete_native(account)
        _save_native(account, value)
        if _same_secret(value, _read_native(account)):
            return
    except CredentialError:
        pass
    _restore_previous(account, previous)
    raise CredentialError(
        f"O {secure_store_label()} não confirmou a substituição da chave. "
        "A configuração anterior foi preservada."
    )


def _restore_previous(account: str, previous: str | None) -> None:
    try:
        _delete_native(account)
        if previous is not None:
            _save_native(account, previous)
    except CredentialError:
        return


def _same_secret(expected: str, actual: str | None) -> bool:
    return actual is not None and hmac.compare_digest(expected, actual)


def _macos_query(security: Any, account: str) -> dict[Any, object]:
    return {
        security.kSecClass: security.kSecClassGenericPassword,
        security.kSecAttrService: SERVICE_NAME,
        security.kSecAttrAccount: account,
    }


def _decode_secret(value: bytes) -> str:
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CredentialError(
            "O cofre seguro devolveu uma credencial em formato inválido."
        ) from exc


def _windows_last_error() -> int:
    getter: Callable[[], int] | None = getattr(ctypes, "get_last_error", None)
    return int(getter()) if callable(getter) else -1
