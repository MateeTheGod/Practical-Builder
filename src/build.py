"""Rebuild index.html from src/template.html and src/model.json.
Usage (from the repo root): python src/build.py"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
template = (root / "src" / "template.html").read_text(encoding="utf-8")
model = (root / "src" / "model.json").read_text(encoding="utf-8").strip()
json.loads(model)  # fail early on a broken model file
(root / "index.html").write_text(template.replace("/*MODEL*/", model), encoding="utf-8", newline="\n")
print("wrote", root / "index.html")
