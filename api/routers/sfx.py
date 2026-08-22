from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/sfx", tags=["sfx"])

_SFX_LIBRARY = Path("flows/image_content_generator/resource/sfx")
_AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".m4a"}


def _safe_sfx_path(tag: str, filename: str) -> Path:
    """Resolves and validates the SFX file path to prevent path traversal."""
    base = _SFX_LIBRARY.resolve()
    target = (base / tag / filename).resolve()
    if not str(target).startswith(str(base)):
        raise HTTPException(400, "Invalid path")
    return target


@router.get("")
def list_sfx_catalog() -> dict[str, list[str]]:
    """
    Returns a mapping of all SFX tags to their available filenames.
    Example: {"impact": ["impact_boom.mp3"], "glitch": ["glitch_error.mp3"]}
    """
    if not _SFX_LIBRARY.exists():
        return {}

    catalog: dict[str, list[str]] = {}
    for tag_folder in sorted(_SFX_LIBRARY.iterdir()):
        if not tag_folder.is_dir():
            continue
        files = sorted(
            f.name for f in tag_folder.iterdir()
            if f.is_file() and f.suffix.lower() in _AUDIO_EXTENSIONS
        )
        if files:
            catalog[tag_folder.name] = files
    return catalog


@router.get("/{tag}/{filename}/stream")
def stream_sfx(tag: str, filename: str) -> FileResponse:
    """Streams a specific SFX file for in-browser preview."""
    target = _safe_sfx_path(tag, filename)
    if not target.is_file():
        raise HTTPException(404, f"SFX file not found: {tag}/{filename}")
    media_type = "audio/mpeg" if target.suffix.lower() == ".mp3" else "audio/wav"
    return FileResponse(str(target), media_type=media_type)
