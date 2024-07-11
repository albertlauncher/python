# -*- coding: utf-8 -*-
# Copyright (c) 2017-2014 Manuel Schneider

from __future__ import annotations

import ast
import asyncio
import inspect
import time
from pathlib import Path
from typing import Any

import import_expression
from albert import (
    Action,
    PluginInstance,
    StandardItem,
    TriggerQueryHandler,
    setClipboardText,
)

md_iid = "2.3"
md_version = "1.7"
md_name = "Python Eval"
md_description = "Evaluate Python code"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/main/python_eval"
md_authors = ["@rtk-rnjn"]
md_credits = ["@Gorialis", "@manuelschneid3r"]
md_lib_dependencies = "import-expression"

CORE_CODE = r"""
def _print(*args, **kwargs):
    import sys
    import io
    original_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        _original_print(*args, **kwargs)
        output = buffer.getvalue()
    finally:
        sys.stdout = original_stdout

    return output

async def _coro_repl():
    import math
    import random
    import os
    import sys
    import asyncio
    import time
    import datetime
    import re
    import io
    import json

    print = _print

    try:
        pass
    finally:
        pass
"""


class KeywordTransformer(ast.NodeTransformer):
    # Source: https://github.com/Gorialis/jishaku/blob/master/jishaku/repl/walkers.py

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return node

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        return node

    def visit_Return(self, node: ast.Return) -> ast.Return | ast.If:
        if node.value is None:
            return node

        return ast.If(
            test=ast.Constant(
                value=True, lineno=node.lineno, col_offset=node.col_offset
            ),
            body=[
                ast.Expr(
                    value=ast.Yield(
                        value=node.value, lineno=node.lineno, col_offset=node.col_offset
                    ),
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                ),
                ast.Return(value=None, lineno=node.lineno, col_offset=node.col_offset),
            ],
            orelse=[],
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def globals_call(self, node: ast.AST) -> ast.Call:
        return ast.Call(
            func=ast.Name(
                id="globals",
                ctx=ast.Load(),
                lineno=node.lineno,
                col_offset=node.col_offset,
            ),
            args=[],
            keywords=[],
            lineno=node.lineno,
            col_offset=node.col_offset,
        )


def wrap_code(code: str) -> ast.Module:
    user_code = import_expression.parse(code, mode="exec")
    mod = ast.parse(CORE_CODE)

    for node in ast.walk(mod):
        node.lineno = -100_000
        node.end_lineno = -100_000

    definition = mod.body[-1]
    assert isinstance(definition, ast.AsyncFunctionDef)

    try_block = definition.body[-1]
    assert isinstance(try_block, ast.Try)

    try_block.body.extend(user_code.body)

    ast.fix_missing_locations(mod)

    KeywordTransformer().generic_visit(try_block)

    last_expr = try_block.body[-1]

    if not isinstance(last_expr, ast.Expr):
        return mod

    if not isinstance(last_expr.value, ast.Yield):
        yield_stmt = ast.Yield(last_expr.value)
        ast.copy_location(yield_stmt, last_expr)
        yield_expr = ast.Expr(yield_stmt)
        ast.copy_location(yield_expr, last_expr)

        try_block.body[-1] = yield_expr

    return mod


class Scope:
    __slots__ = ("globals", "locals")

    def __init__(
        self,
        globals_: dict[str | Any] | None = None,
        locals_: dict[str | Any] | None = None,
    ):
        self.globals: dict[str | Any] | None = globals_ or {}
        self.locals: dict[str | Any] | None = locals_ or {}

    def clear_intersection(self, other_dict: dict[str | Any] | None):
        for key, value in other_dict.items():
            if key in self.globals and self.globals[key] is value:
                del self.globals[key]
            if key in self.locals and self.locals[key] is value:
                del self.locals[key]

        return self

    def update(self, other: "Scope"):
        self.globals.update(other.globals)
        self.locals.update(other.locals)
        return self

    def update_globals(self, other: dict[str | Any]):
        self.globals.update(other)
        return self

    def update_locals(self, other: dict[str | Any]):
        self.locals.update(other)
        return self


scope = Scope(globals(), locals())
scope_with_print = Scope({"_original_print": print})
scope.update(scope_with_print)


class AsyncCodeExecutor:
    def __init__(self, code: str) -> None:
        self.source = code
        self.code = wrap_code(code)
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._function = None

    @property
    def function(self):
        if self._function:
            return self._function

        exec(compile(self.code, "<repl>", "exec"), scope.globals, scope.locals)
        self._function = scope.locals.get("_coro_repl") or scope.globals.get(
            "_coro_repl"
        )
        return self._function

    async def run(self):
        try:
            if inspect.isasyncgenfunction(self.function):
                async for result in self.function():
                    yield result
            else:
                yield await self.function()
        except Exception as e:
            yield f"{type(e).__name__}: {e}"


def run_code(code: str) -> str:
    async def _run_code(code: str) -> list[str]:
        executor = AsyncCodeExecutor(code)
        result = ""
        async for output in executor.run():
            result += str(output)

        return result

    return asyncio.run(_run_code(code))


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self,
            self.id,
            self.name,
            self.description,
            synopsis="<Python expression>",
            defaultTrigger="py2 ",
        )
        self.iconUrls = [f"file:{Path(__file__).parent}/python.svg"]

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if not stripped:
            return

        ini = time.perf_counter()
        try:
            result = run_code(stripped)
        except Exception as ex:
            result = f"{type(ex).__name__}: {ex}"

        result_str = str(result).strip()

        fin = time.perf_counter()
        milis = (fin - ini) * 1000
        subtext = f"Execution time: {milis:.2f}ms"

        query.add(
            StandardItem(
                id=self.id,
                text=result_str,
                subtext=subtext,
                inputActionText=query.trigger + result_str,
                iconUrls=self.iconUrls,
                actions=[
                    Action("copy", "Copy result to clipboard", lambda r=result_str: setClipboardText(r)),
                    Action("exec", "Execute python code", lambda r=result_str: run_code(r).strip()),
                ],
            )
        )
