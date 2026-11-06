"""Build the portable skill download from its maintained source on every MkDocs build."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def on_pre_build(config):
    site_root = Path(config.config_file_path).resolve().parent
    skill = site_root / "skills" / "lifecycle-center-recovery"
    destination = Path(config["docs_dir"]) / "downloads" / f"{skill.name}.zip"
    destination.parent.mkdir(parents=True, exist_ok=True)
    files = [skill / "SKILL.md", skill / "agents" / "openai.yaml"]
    files.extend(sorted((skill / "references").glob("*.md")))
    # Explicit inputs exclude caches, credentials and unrelated lab files.
    # Stable metadata makes unchanged source produce the same archive.
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            info = ZipInfo(path.relative_to(skill.parent).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
