import random
from pathlib import Path
from typing import Any, Optional

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class AudioTool(BaseModelTool):
    """
    Tool for audio-related operations, like selecting random files.
    """
    bg_music_dir: Path
    sfx_dir: Optional[Path] = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def get_random_audio(self) -> Optional[Path]:
        """
        Lists audio files in the background music directory and returns a random one.
        Supported formats: .wav, .mp3, .aac, .m4a.
        """
        if not self.bg_music_dir.exists():
            Messenger.warning(f"Audio directory not found: {self.bg_music_dir}")
            return None

        extensions = {".wav", ".mp3", ".aac", ".m4a"}
        bg_audios = [
            f for f in self.bg_music_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

        if not bg_audios:
            Messenger.warning(f"No audio files found in: {self.bg_music_dir}")
            return None

        selected = random.choice(bg_audios)
        Messenger.info(f"Selected background audio: {selected.name}")
        return selected

    def get_sfx_by_tag(self, tag: str) -> Optional[Path]:
        """
        Returns a randomly selected SFX file from the subfolder matching the tag.
        Folder structure expected: sfx_dir / <tag> / *.mp3
        Returns None if sfx_dir is not set, the tag folder doesn't exist, or is empty.
        """
        if not self.sfx_dir:
            Messenger.warning("sfx_dir not configured in AudioTool.")
            return None

        tag_folder = self.sfx_dir / tag
        if not tag_folder.exists():
            Messenger.warning(f"SFX folder not found for tag '{tag}': {tag_folder}")
            return None

        extensions = {".wav", ".mp3", ".aac", ".m4a"}
        files = [
            f for f in tag_folder.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

        if not files:
            Messenger.warning(f"No SFX files found in: {tag_folder}")
            return None

        selected = random.choice(files)
        Messenger.info(f"SFX selected: [{tag}] → {selected.name}")
        return selected

    def get_sfx_by_file(self, tag: str, filename: str) -> Optional[Path]:
        """
        Returns the exact SFX file path given a tag and a filename.
        Returns None if the file doesn't exist.
        """
        if not self.sfx_dir:
            return None
        target = self.sfx_dir / tag / filename
        return target if target.exists() else None

    def list_sfx_catalog(self) -> dict[str, list[str]]:
        """
        Scans sfx_dir and returns a mapping of tag -> sorted list of filenames.
        Example: {"impact": ["impact_boom.mp3"], "glitch": ["glitch_digital.mp3"]}
        """
        if not self.sfx_dir or not self.sfx_dir.exists():
            return {}

        extensions = {".wav", ".mp3", ".aac", ".m4a"}
        catalog: dict[str, list[str]] = {}
        for tag_folder in sorted(self.sfx_dir.iterdir()):
            if not tag_folder.is_dir():
                continue
            files = sorted(
                f.name for f in tag_folder.iterdir()
                if f.is_file() and f.suffix.lower() in extensions
            )
            if files:
                catalog[tag_folder.name] = files
        return catalog
