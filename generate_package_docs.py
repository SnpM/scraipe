#Based on https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages

import os
import argparse
import mkdocs_gen_files
from pathlib import Path
def generate_package_docs(
    package_path: str,
    output_dir:str,
):
    """
    Scan for Python files in the given package path and generate a mkdocs file with docstring reference.

    Args:
        package_path (str): The path to the package to scan.
    """
    
    ignore_files = [
        "__init__.py",
    ]
    src = Path(package_path)
    root = Path(".")
    nav = mkdocs_gen_files.Nav()

    for path in sorted(src.rglob("*.py")):
        module_path = path.relative_to(src).with_suffix("")
        doc_path = path.relative_to(src).with_suffix(".md")
        full_doc_path = Path(output_dir, doc_path)

        parts = tuple(module_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue
        
        # Add package name to parts
        nav_parts = parts
        module_parts = (src.name,) + parts
        
        if nav_parts:
            nav[nav_parts] = doc_path.as_posix()  

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(module_parts)
            content = f"::: {ident}"
            print(content)
            fd.write(content)
            
        mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

    with mkdocs_gen_files.open(f"{output_dir}/__nav__.md", "w") as nav_file:  
        nav_file.writelines(nav.build_literate_nav())  
    
if __name__ == "__main__":
    class Mock():
        pass
    args = Mock()
    args.package_path = "scraipe"
    args.output_dir = "api"
    
    # Delete docs/api before generating new docs
    if os.path.exists(args.output_dir):
        import shutil
        print(f"Deleting existing docs in {args.output_dir}")
        shutil.rmtree(args.output_dir)
    generate_package_docs(args.package_path, args.output_dir)