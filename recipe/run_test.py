import os, pathlib, subprocess, sys

SRC_DIR = pathlib.Path(os.environ["SRC_DIR"])
SKN = SRC_DIR / "sknetwork"
TEST_DIRS = SKN.glob("*/tests")

PYTEST_ARGS = ["pytest", "-vv"]

SKIPS = [
    # ???
    "gnn_classifier_early_stopping",
    # 0.20.0 https://github.com/conda-forge/scikit-network-feedstock/pull/13
    "gnn_classifier_reinit",
]

# pytest handles parenthesis weirdly
if len(SKIPS) == 1:
    PYTEST_ARGS += ["-k", f"not {SKIPS[0]}"]
elif len(SKIPS) > 1:
    PYTEST_ARGS += ["-k", f"not ({ ' or '.join(SKIPS) })"]

failed = []


# need to run multiple times because of relative imports of `test.*`
for test_dir in TEST_DIRS:
    print("in", test_dir.name)
    print(">>>", *PYTEST_ARGS)
    if subprocess.call(PYTEST_ARGS, cwd=str(test_dir)):
        failed += [test_dir.parent.name]

if failed:
    print("Failed tests in:", sorted(failed))

sys.exit(len(failed))
