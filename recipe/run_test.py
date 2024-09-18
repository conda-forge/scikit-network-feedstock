import os, pathlib, subprocess, sys
from pathlib import Path

# platform detection
PYPY = "__pypy__" in sys.builtin_module_names
WIN = os.name == "nt"

# hopefully only these need to be changed per-PR
WITH_COV = all(
    [
        # coverage is slow and flaky on pypy
        not PYPY,
        # so many skips on windows,
        not WIN,
    ]
)
COV_FAIL_UNDER = 93
SKIPS = [
    # 0.31.0 https://github.com/conda-forge/scikit-network-feedstock/pull/18
    "bfs",
    # ???
    "gnn_classifier_early_stopping",
    # 0.20.0 https://github.com/conda-forge/scikit-network-feedstock/pull/13
    "gnn_classifier_reinit",
    # https://github.com/conda-forge/scikit-network-feedstock/pull/19
    "test_edge_list",
]


TEST_DIR_SKIPS = (
    []
    if not WIN
    else [
        # https://github.com/conda-forge/scikit-network-feedstock/pull/23
        # lots of
        #
        #   TypeError: No matching signature found
        #
        "classification",
        "clustering",
        "embedding",
        "hierarchy",
        "visualization",
    ]
)

SRC_DIR = pathlib.Path(os.environ["SRC_DIR"])
SKN = SRC_DIR / "sknetwork"
ROOT_TESTS = sorted(SKN.glob("test_*.py"))
TEST_DIRS = sorted(t for t in SKN.glob("*/tests") if t not in TEST_DIR_SKIPS)

PYTEST_ARGS = ["pytest", "-vv", "--color=yes", "--tb=long", "--no-header"]

if WITH_COV:
    PYTEST_ARGS = [
        "coverage",
        "run",
        "--source=sknetwork",
        "--omit",
        '"tests/*.py,test_*.py,sknetwork.py',
        "--branch",
        "--parallel",
        "--data-file",
        str(Path(__file__).parent / ".coverage"),
        "-m",
        *PYTEST_ARGS,
    ]

# pytest handles parentheses weirdly
if len(SKIPS) == 1:
    PYTEST_ARGS += ["-k", f"not {SKIPS[0]}"]
elif len(SKIPS) > 1:
    PYTEST_ARGS += ["-k", f"not ({ ' or '.join(SKIPS) })"]


def run():
    failed = []
    # need to run multiple times because of relative imports of `test.*`
    passed = []

    print("    >>>", *PYTEST_ARGS, flush=True)

    print("... in _root", flush=True)
    if subprocess.call([*PYTEST_ARGS, *list(map(str, ROOT_TESTS))], cwd=str(SKN)):
        failed += ["_root"]
    else:
        passed += ["_root"]

    for test_dir in TEST_DIRS:
        print("... in", test_dir.parent.name, flush=True)
        if subprocess.call(PYTEST_ARGS, cwd=str(test_dir)):
            failed += [test_dir.parent.name]
        else:
            passed += [test_dir.parent.name]

    print("Passed tests in:", "\n".join(passed), flush=True)

    if failed:
        print("FAILED tests in:", "\n".join(failed), flush=True)
        return 1

    if WITH_COV:
        subprocess.call(["coverage", "combine"])
        return subprocess.call(
            [
                "coverage",
                "report",
                "--show-missing",
                "--skip-covered",
                f"--fail-under={COV_FAIL_UNDER}",
            ]
        )

    return 0


if __name__ == "__main__":
    sys.exit(run())
