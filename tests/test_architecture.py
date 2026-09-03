import ast
from pathlib import Path


def test_init_files_must_be_empty() -> None:
    root = Path(__file__).resolve().parent.parent
    init_files = list(root.glob("src/**/__init__.py")) + list(root.glob("tests/**/__init__.py"))
    assert len(init_files) > 0, "No __init__.py files found"
    
    non_empty = [f for f in init_files if f.stat().st_size != 0]
    assert not non_empty, f"The following __init__.py files are not 0 bytes: {non_empty}"


def test_no_relative_imports() -> None:
    src = Path(__file__).resolve().parent.parent / "src"
    violations: list[str] = []

    for py_file in src.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue
        code = py_file.read_text(encoding="utf-8")
        tree = ast.parse(code, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                violations.append(f"{py_file}:{node.lineno} relative import detected")

    assert not violations, f"Relative imports found:\n" + "\n".join(violations)


def test_clean_architecture_compliance() -> None:
    src = Path(__file__).resolve().parent.parent / "src"
    violations: list[str] = []

    for py_file in src.glob("**/*.py"):
        rel = py_file.relative_to(src)
        parts = rel.parts
        if not parts or py_file.name == "__init__.py":
            continue

        layer = parts[0]
        code = py_file.read_text(encoding="utf-8")
        tree = ast.parse(code, filename=str(py_file))

        for node in ast.walk(tree):
            module_name = ""
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module

            if not module_name:
                continue

            if layer == "domain":
                # domain must not import from application, adapters, infrastructure or external packages
                forbidden_prefixes = ("src.application", "src.adapters", "src.infrastructure", "fastapi", "networkx", "starlette")
                if any(module_name.startswith(p) for p in forbidden_prefixes):
                    violations.append(f"Domain layer {rel}:{node.lineno} illegally imports '{module_name}'")
            elif layer == "application":
                # application must not import from adapters or infrastructure
                forbidden_prefixes = ("src.adapters", "src.infrastructure", "fastapi")
                if any(module_name.startswith(p) for p in forbidden_prefixes):
                    violations.append(f"Application layer {rel}:{node.lineno} illegally imports '{module_name}'")
            elif layer == "adapters":
                # adapters must not import from infrastructure
                forbidden_prefixes = ("src.infrastructure",)
                if any(module_name.startswith(p) for p in forbidden_prefixes):
                    violations.append(f"Adapters layer {rel}:{node.lineno} illegally imports '{module_name}'")

    assert not violations, "Clean Architecture dependency violations found:\n" + "\n".join(violations)


def test_all_functions_have_type_annotations() -> None:
    src = Path(__file__).resolve().parent.parent / "src"
    violations: list[str] = []

    for py_file in src.glob("**/*.py"):
        rel = py_file.relative_to(src)
        parts = rel.parts
        if not parts or py_file.name == "__init__.py":
            continue

        # Strictly required in domain and application
        if parts[0] not in ("domain", "application"):
            continue

        code = py_file.read_text(encoding="utf-8")
        tree = ast.parse(code, filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check return type annotation
                if node.returns is None and node.name != "__init__":
                    violations.append(f"{rel}:{node.lineno} function '{node.name}' missing return type annotation")
                
                # Check argument annotations (ignoring 'self' and 'cls')
                for arg in node.args.args:
                    if arg.arg in ("self", "cls"):
                        continue
                    if arg.annotation is None:
                        violations.append(f"{rel}:{node.lineno} function '{node.name}' argument '{arg.arg}' missing type annotation")

    assert not violations, "Missing type annotations found:\n" + "\n".join(violations)


def test_no_hardcoded_secrets() -> None:
    src = Path(__file__).resolve().parent.parent / "src"
    suspicious_keys = {"secret_key", "password", "token", "api_key"}
    violations: list[str] = []

    for py_file in src.glob("**/*.py"):
        if "settings" in py_file.parts:
            # Settings definitions may have default development placeholders
            continue
        code = py_file.read_text(encoding="utf-8")
        tree = ast.parse(code, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(k in name_lower for k in suspicious_keys):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and len(node.value.value) > 10:
                                violations.append(f"{py_file.name}:{node.lineno} suspected hardcoded secret: {target.id}")

    assert not violations, "Suspected hardcoded secrets found:\n" + "\n".join(violations)


if __name__ == "__main__":
    test_init_files_must_be_empty()
    test_no_relative_imports()
    test_clean_architecture_compliance()
    test_all_functions_have_type_annotations()
    test_no_hardcoded_secrets()
    print("All architectural constraint gauntlet checks passed!")
