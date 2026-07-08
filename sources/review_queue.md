# Review queue — low-confidence tool attributions

Best-guess tool assigned by heuristic; **please confirm or correct**.
These are devdanzin-authored CPython artifacts that name no tool — a mix
of manual contributions, fusil crashes, and JIT (lafleur) crashes.

**25 bugs to review.**

## best-guess: fusil  (12)
| artifact | title | reason |
|---|---|---|
| python/cpython#122353 | Import errors with loo long entry in sys.path or PYTHONPATH in Windows | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#122398 | Crash in _curses when calling .initscr() after ignoring exception from | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#122461 | Incorrect information about exception raised if source contains null b | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#125732 | gh-125666: Avoid PyREPL exiting when a null byte is in input | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#126018 | `sys.audit(0)` aborts due to an assertion in debug build | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#130999 | New REPL exits when there are non-string candidates for suggestions | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#131878 | New REPL on Windows exits when accented character is pasted/typed | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#131936 | Abort from type checking mismatch between `_suggestions__generate_sugg | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#132470 | Building a `ctypes.CField` with wrong `byte_size` aborts | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#132565 | Aborts from working with memoryviews and buffers across threads in fre | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#141805 | Segfault from `repr()` of a corrupted set | cpython-crash-untagged(REVIEW:fusil-vs-manual) |
| python/cpython#142029 | Assertion failures from calling `create_builtin` with invalid object | cpython-crash-untagged(REVIEW:fusil-vs-manual) |

## best-guess: lafleur  (6)
| artifact | title | reason |
|---|---|---|
| python/cpython#130163 | Crash when concurrently writing with `print` and concurrently modifyin | cpython-jit-crash(REVIEW) |
| python/cpython#137218 | Main segfaults importing `_pyrepl` with low value for `JUMP_BACKWARD_I | cpython-jit-crash(REVIEW) |
| python/cpython#139193 | JIT (interpreter): running hot code with `PYTHON_LLTRACE=4` segfaults | cpython-jit-crash(REVIEW) |
| python/cpython#142629 | JIT: Global buffer overflow in `_PyUOpPrint` when running with `PYTHON | cpython-jit-crash(REVIEW) |
| python/cpython#143751 | JIT: Segfault from setting `UOP_MAX_TRACE_LENGTH` to a large value | cpython-jit-crash(REVIEW) |
| python/cpython#145064 | JIT: `co != NULL` assertion failure in `*_Py_uop_frame_new` | cpython-jit-crash(REVIEW) |

## best-guess: manual  (7)
| artifact | title | reason |
|---|---|---|
| python/cpython#122145 | Exception raised in traceback.StackSummary._should_show_carets exits i | cpython-untagged(REVIEW) |
| python/cpython#122170 | Interpreter exits on Windows due to ValueError raised in linecache.py | cpython-untagged(REVIEW) |
| python/cpython#122533 | New REPL will exit the interpreter due to errors from substituting bui | cpython-untagged(REVIEW) |
| python/cpython#122692 | gh-123572: Fix key codes in VK_MAP in windows_console.py | cpython-untagged(REVIEW) |
| python/cpython#125852 | `sys.addaudithook(None)` breaks the REPL | cpython-untagged(REVIEW) |
| python/cpython#126032 | gh-126019 Fix inspect.getsource for classes created in PyREPL | cpython-untagged(REVIEW) |
| python/cpython#30135 | gh-90117: handle dict and mapping views in pprint | cpython-untagged(REVIEW) |

