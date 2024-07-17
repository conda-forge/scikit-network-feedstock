import subprocess, sys

# platform detection
PYPY = "__pypy__" in sys.builtin_module_names

# hopefully only these need to be changed per-PR
WITH_COV = (
    # coverage is slow and flaky on pypy
    not PYPY
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


PYTEST_ARGS = [
    "pytest",
    "--pyargs",
    "sknetwork",
    "-vv",
    "--color=yes",
    "--no-header",
    "--tb=long",
]

if WITH_COV:
    PYTEST_ARGS = [
        *PYTEST_ARGS,
        "--cov=sknetwork",
        "--cov-branch",
        "--cov-report=term-missing:skip-covered",
        "--no-cov-on-fail",
        f"--cov-fail-under={COV_FAIL_UNDER}",
    ]

# pytest handles parentheses weirdly
if len(SKIPS) == 1:
    PYTEST_ARGS += ["-k", f"not {SKIPS[0]}"]
elif len(SKIPS) > 1:
    PYTEST_ARGS += ["-k", f"not ({ ' or '.join(SKIPS) })"]


def run():
    print("    >>>", *PYTEST_ARGS, flush=True)
    return subprocess.call(PYTEST_ARGS)


if __name__ == "__main__":
    sys.exit(run())
