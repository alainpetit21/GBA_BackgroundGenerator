from __future__ import annotations

import inspect
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path
from threading import current_thread
from typing import Any


class DebugLogger:
    """
    Append structured debug entries to a local debug.log file.
    """

    LOG_FILE_NAME = "debug.log"
    MAX_VALUE_LENGTH = 500

    @classmethod
    def log_error(
        cls,
        title: str,
        message: str,
        *,
        exception: BaseException | None = None,
        caller_frame: Any = None,
        details: Any = None,
        log_path: Path | None = None,
    ) -> Path:
        target_path = log_path or (Path.cwd() / cls.LOG_FILE_NAME)

        caller_info = cls._build_caller_info(caller_frame)
        traceback_text = cls._resolve_traceback(exception, details)
        details_text = cls._safe_repr(details)

        entry_lines = [
            "=" * 90,
            f"timestamp_utc: {datetime.now(timezone.utc).isoformat()}",
            f"thread: {current_thread().name}",
            f"python: {platform.python_version()}",
            f"title: {title}",
            f"message: {message}",
            f"cwd: {Path.cwd()}",
            f"caller_file: {caller_info['file']}",
            f"caller_line: {caller_info['line']}",
            f"caller_function: {caller_info['function']}",
            f"caller_arguments: {caller_info['arguments']}",
            f"exception_type: {type(exception).__name__ if exception is not None else caller_info['exception_type']}",
            "details:",
            details_text,
            "traceback:",
            traceback_text,
            "",
        ]

        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(entry_lines))

        return target_path

    @classmethod
    def _build_caller_info(cls, frame: Any) -> dict[str, str]:
        if frame is None:
            return {
                "file": "<unknown>",
                "line": "<unknown>",
                "function": "<unknown>",
                "arguments": "{}",
                "exception_type": "<unknown>",
            }

        code = frame.f_code
        arg_info = inspect.getargvalues(frame)
        arguments: dict[str, str] = {}

        for argument_name in arg_info.args:
            arguments[argument_name] = cls._safe_repr(arg_info.locals.get(argument_name))

        if arg_info.varargs:
            arguments[f"*{arg_info.varargs}"] = cls._safe_repr(arg_info.locals.get(arg_info.varargs))

        if arg_info.keywords:
            arguments[f"**{arg_info.keywords}"] = cls._safe_repr(arg_info.locals.get(arg_info.keywords))

        exception_type = "None"
        caught_exception = arg_info.locals.get("exception")
        if isinstance(caught_exception, BaseException):
            exception_type = type(caught_exception).__name__

        return {
            "file": code.co_filename,
            "line": str(frame.f_lineno),
            "function": code.co_name,
            "arguments": cls._safe_repr(arguments),
            "exception_type": exception_type,
        }

    @classmethod
    def _resolve_traceback(cls, exception: BaseException | None, details: Any) -> str:
        if exception is not None:
            return "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__),
            ).rstrip()

        if isinstance(details, dict):
            traceback_text = details.get("traceback")
            if isinstance(traceback_text, str) and traceback_text.strip():
                return traceback_text.strip()

        fallback = traceback.format_exc().strip()
        if fallback and fallback != "NoneType: None":
            return fallback

        return "<no traceback available>"

    @classmethod
    def _safe_repr(cls, value: Any) -> str:
        try:
            rendered = repr(value)
        except Exception:  # noqa: BLE001
            rendered = f"<unrepresentable {type(value).__name__}>"

        if len(rendered) > cls.MAX_VALUE_LENGTH:
            return f"{rendered[: cls.MAX_VALUE_LENGTH]}...<truncated>"

        return rendered
