import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import ClassVar, List

from tools.common.base_model import BaseModelTool
from tools.video_editing.whisper_schemas import (
    WhisperTranscription,
    WhisperTranscriptionSegment,
    WhisperWord,
)


class WhisperTool(BaseModelTool):
    """
    Tool for transcribing audio using whisper-cpp and generating SRT files.
    """
    DEFAULT_MODEL: ClassVar[str] = os.getenv(
        "WHISPER_MODEL_PATH", "models/whisper/ggml-small.bin"
    )

    def _run(self, cmd: str) -> None:
        p = subprocess.run(cmd, shell=True)
        if p.returncode != 0:
            raise RuntimeError(f"Whisper Error: {cmd}")

    def _get_transcription_json(
        self,
        audio_path: Path,
    ) -> WhisperTranscription:
        """
        Runs whisper-cli (if needed) and returns the parsed JSON content.
        """
        json_path = audio_path.with_name(audio_path.name + ".json")
        if not json_path.exists():
            # -ojf: output json full (tokens with timestamps)
            cmd_args = [
                "whisper-cli",
                "-m", self.DEFAULT_MODEL,
                "-l", "es",
                "-ojf",
                "-f", str(audio_path)
            ]
            cmd = " ".join(shlex.quote(arg) for arg in cmd_args)
            self._run(cmd)

        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                return WhisperTranscription.model_validate(json.load(f))
            except json.JSONDecodeError:
                # If JSON is corrupted, delete it to ensure next run regenerates
                json_path.unlink(missing_ok=True)
                raise RuntimeError(
                    f"JSON corrupted: {json_path}. Deleted to allow retry."
                )

    def get_transcription_segments(
        self,
        audio_path: Path
    ) -> List[WhisperTranscriptionSegment]:
        """
        Transcribes audio and returns a list of segments with text and timestamps.
        Each segment: {"text": str, "start": float, "end": float} (times in seconds)
        """
        data = self._get_transcription_json(audio_path)
        segments: List[WhisperTranscriptionSegment] = []
        for s in data.transcription:
            segments.append(WhisperTranscriptionSegment(
                text=s.text.strip(),
                start=s.offsets.from_ms / 1000.0,
                end=s.offsets.to_ms / 1000.0
            ))

        return segments

    def get_words(self, audio_path: Path) -> List[WhisperWord]:
        """
        Extracts and merges whisper tokens into a list of words with millisecond timestamps.
        """
        data = self._get_transcription_json(audio_path)
        tokens = [
            t
            for s in data.transcription
            for t in s.tokens
            if not t.text.startswith("[_") and t.text.strip()
        ]

        words: List[WhisperWord] = []
        for t in tokens:
            text, t_from, t_to = t.text, t.offsets.from_ms, t.offsets.to_ms
            if text.startswith(" ") or not words:
                words.append(WhisperWord(text=text.strip(), start=t_from, end=t_to))
            else:
                words[-1].text += text
                words[-1].end = t_to
        return words

    def align_scenes(
        self,
        audio_path: Path,
        scene_texts: List[str]
    ) -> List[dict]:
        """
        Deterministically aligns scene texts to exact whisper word boundary timestamps.
        Cuts tightly from the first spoken word to the last spoken word of each scene,
        eliminating awkward leading silence (so SFX hits on cue) and preventing trailing word bleed.
        """
        import re
        words = self.get_words(audio_path)
        alignments: List[dict] = []
        current_word_idx = 0
        total_words = len(words)

        def norm(t: str) -> str:
            return re.sub(r'[^\w]', '', t.lower())

        for scene_idx, scene_text in enumerate(scene_texts, start=1):
            scene_words = [norm(w) for w in scene_text.split() if norm(w)]
            if not scene_words:
                continue

            first_scene_word = scene_words[0]
            last_scene_word = scene_words[-1]

            # 1. Locate first spoken word of this scene
            found_first_idx = None
            for idx in range(current_word_idx, min(total_words, current_word_idx + 15)):
                if norm(words[idx].text) == first_scene_word:
                    found_first_idx = idx
                    break
            if found_first_idx is None:
                found_first_idx = current_word_idx

            # 2. Locate last spoken word of this scene
            found_last_idx = None
            search_start = found_first_idx + max(0, len(scene_words) - 5)
            search_end = min(total_words, found_first_idx + len(scene_words) + 15)

            for idx in range(search_start, search_end):
                if norm(words[idx].text) == last_scene_word:
                    found_last_idx = idx
                    break

            if found_last_idx is None:
                for idx in range(found_first_idx, min(total_words, found_first_idx + len(scene_words) + 30)):
                    if norm(words[idx].text) == last_scene_word:
                        found_last_idx = idx
                        break

            if found_last_idx is None:
                found_last_idx = min(total_words - 1, found_first_idx + len(scene_words) - 1)

            # Start time: just 0.06s before the first spoken word
            if scene_idx == 1:
                start_s = 0.0
            else:
                start_s = max(0.0, (words[found_first_idx].start / 1000.0) - 0.06)

            # End time: 0.06s after the last spoken word
            if scene_idx == len(scene_texts) and words:
                end_s = words[-1].end / 1000.0
            else:
                end_s = (words[found_last_idx].end / 1000.0) + 0.06

            captured_words = " ".join([w.text for w in words[found_first_idx:found_last_idx+1]])
            print(f"🎬 [Whisper Cut] Escena {scene_idx} ({round(start_s, 2)}s - {round(end_s, 2)}s): {captured_words}")

            alignments.append({
                'scene_number': scene_idx,
                'start_time': round(start_s, 3),
                'end_time': round(end_s, 3)
            })

            current_word_idx = found_last_idx + 1

        # Prevent boundary overlap between consecutive scenes
        for i in range(len(alignments) - 1):
            if alignments[i]['end_time'] > alignments[i+1]['start_time']:
                mid = round((alignments[i]['end_time'] + alignments[i+1]['start_time']) / 2.0, 3)
                alignments[i]['end_time'] = mid
                alignments[i+1]['start_time'] = mid

        return alignments

    def generate_ass(
        self,
        audio_path: Path,
        output_ass: Path,
        width: int = 1080,
        height: int = 1920,
    ) -> None:
        """
        Generates an ASS file from audio file with word-by-word TikTok karaoke style.
        """
        words = self.get_words(audio_path)

        # 2. Group words into blocks (max 3 words or pause > 0.4s)
        blocks: List[List[WhisperWord]] = []
        current: List[WhisperWord] = []
        for w in words:
            pause = (float(w.start) - float(current[-1].end)) / 1000.0 if current else 0.0
            if len(current) >= 3 or pause > 0.4:
                blocks.append(current)
                current = []
            current.append(w)
        if current:
            blocks.append(current)

        def fmt_ass(ms: int) -> str:
            # ASS format: H:MM:SS.cs
            s, ms = divmod(ms, 1000)
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            cs = ms // 10
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

        # Style values — Arial 75px, bold, 5px black outline, 3px shadow
        # MarginV at 15% from bottom keeps subtitles in the lower-center safe zone.
        font_name = "Arial"
        font_size = 75
        margin_v = int(height * 0.15)
        # ASS Header
        ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTok,{font_name},{font_size},&HFFFFFF,&H0000FF,&H000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,3,2,10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        # 3. Write ASS
        with open(output_ass, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            for block in blocks:
                for i, active_word in enumerate(block):
                    start_time = fmt_ass(active_word.start)
                    # For the last word in the block, keep it highlighted until the end of the block's last word
                    # Actually, the active_word's end time is fine, but to avoid blinking, we can hold it until the next word.
                    # Or simpler: just use active_word.start to active_word.end for the highlight.
                    end_time = fmt_ass(active_word.end)
                    
                    # If this is the last word in the block, let it stay on screen a bit longer? No, ASS handles exact times.
                    
                    line_parts = []
                    for j, w in enumerate(block):
                        word_text = w.text.upper()
                        if j == i:
                            # Highlighted word: Yellow (&H00FFFF& in ASS BBGGRR)
                            line_parts.append(f"{{\\c&H00FFFF&}}{word_text}{{\\c}}")
                        else:
                            line_parts.append(word_text)
                    
                    text_line = " ".join(line_parts)
                    f.write(f"Dialogue: 0,{start_time},{end_time},TikTok,,0,0,0,,{text_line}\n")
