import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class FFmpegTool(BaseModelTool):
    """
    Tool for basic video editing operations using FFmpeg.
    """

    def _run(self, cmd: str) -> None:
        p = subprocess.run(cmd, shell=True)
        if p.returncode != 0:
            raise RuntimeError(f"FFmpeg falló: {cmd}")

    def split_audio(
        self,
        audio_in: Path,
        audio_out: Path,
        start_time: float,
        duration: float
    ) -> None:
        """
        Splits an audio file into a segment starting at start_time with duration.
        """
        cmd = (
            f"ffmpeg -y -i {shlex.quote(str(audio_in))} "
            f"-ss {start_time} -t {duration} {shlex.quote(str(audio_out))} "
            f"-v error"
        )
        self._run(cmd)

    def mix_sfx_into_audio(
        self,
        narration_wav: Path,
        sfx_mp3: Path,
        out_wav: Path,
        sfx_volume: float = 0.45,
        sfx_offset_sec: float = 0.0,
    ) -> None:
        """
        Mixes a sound effect on top of a narration audio file.
        The SFX is placed at sfx_offset_sec within the narration.
        Narration always stays at 1.0 volume. The result matches
        the exact duration of the narration (duration=first).
        """
        delay_ms = int(sfx_offset_sec * 1000)
        filter_complex = (
            f"[0:a]volume=1.0[narr];"
            f"[1:a]volume={sfx_volume},adelay={delay_ms}|{delay_ms}[sfx];"
            "[narr][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        )
        cmd = (
            f"ffmpeg -y "
            f"-i {shlex.quote(str(narration_wav))} "
            f"-i {shlex.quote(str(sfx_mp3))} "
            f'-filter_complex "{filter_complex}" '
            f'-map "[out]" '
            f"{shlex.quote(str(out_wav))} -v error"
        )
        self._run(cmd)

    def make_transition_video(
        self,
        img_a: Path,
        img_b: Path,
        out_path: Path,
        seconds: int = 4
    ) -> None:
        offset = max(0, seconds - 1)
        xfade_filter = f"[0:v][1:v]xfade=transition=fade:duration=1:offset={offset},format=yuv420p"
        cmd = f"""
        ffmpeg -y \
          -loop 1 -t {seconds} -i {shlex.quote(str(img_a))} \
          -loop 1 -t {seconds} -i {shlex.quote(str(img_b))} \
          -filter_complex "{xfade_filter}" \
          -t {seconds} {shlex.quote(str(out_path))}
        """
        self._run(cmd)

    def concat_videos(
        self,
        video_list: List[Path],
        out_path: Path,
        reencode: bool = False,
    ) -> None:
        with tempfile.TemporaryDirectory() as td_str:
            td = Path(td_str)
            list_path = td / "files.txt"
            with open(list_path, "w", encoding="utf-8") as f:
                for v in video_list:
                    abs_v = v.absolute()
                    f.write(f"file '{abs_v}'\n")

            if reencode:
                cmd = f"""
                ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(list_path))} \
                    -c:v libx264 -c:a aac -pix_fmt yuv420p -movflags +faststart \
                    {shlex.quote(str(out_path))} -v error
                """
            else:
                cmd = f"""
                ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(list_path))} \
                    -c copy -movflags +faststart {shlex.quote(str(out_path))} -v error
                """
            self._run(cmd)

    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Retrieves the duration of an audio file using ffprobe.
        """
        cmd_base = (
            "ffprobe -v error -show_entries format=duration "
            "-of default=noprint_wrappers=1:nokey=1"
        )
        cmd = f"{cmd_base} {shlex.quote(str(audio_path))}"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return float(output)

    def get_video_duration(self, video_path: Path) -> float:
        """
        Retrieves the duration of a video file using ffprobe.
        """
        cmd_base = (
            "ffprobe -v error -select_streams v:0 -show_entries format=duration "
            "-of default=noprint_wrappers=1:nokey=1"
        )
        cmd = f"{cmd_base} {shlex.quote(str(video_path))}"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return float(output)

    def sync_video_and_audio(
        self,
        video_in: Path,
        audio_in: Path,
        video_out: Path
    ) -> None:
        """
        Synchronizes a video file to an audio file's duration.
        The video playback speed is adjusted (stretched or shrunk) to match
        the exact duration of the audio, ensuring the entire video is shown.
        Also applies a subtle fade-in (40ms) and fade-out (80ms) to the audio
        to prevent abrupt hard-cut transitions between scenes (CapCut-style).
        """
        audio_dur = self.get_audio_duration(audio_in)
        video_dur = self.get_video_duration(video_in)

        if video_dur <= 0:
            raise RuntimeError(f"Invalid video duration: {video_dur} for {video_in}")

        # Calculate speed factor (scale) for video PTS
        # new_duration = old_duration * scale -> scale = a_dur / v_dur
        scale = audio_dur / video_dur

        # Fade-in: 40ms at start. Fade-out: 80ms before end.
        fade_in_dur = 0.04
        fade_out_start = max(0.0, audio_dur - 0.08)

        cmd = (
            f"ffmpeg -y -i {shlex.quote(str(video_in))} "
            f"-i {shlex.quote(str(audio_in))} "
            f'-filter_complex "'
            f"[0:v]setpts={scale:.6f}*PTS,fps=25[v];"
            f"[1:a]afade=t=in:st=0:d={fade_in_dur},"
            f"afade=t=out:st={fade_out_start:.3f}:d=0.08[a]"
            f'" '
            f'-map "[v]" -map "[a]" '
            f"-c:v libx264 -c:a aac -ar 44100 -ac 2 -pix_fmt yuv420p -r 25 "
            f"{shlex.quote(str(video_out))} -v error"
        )
        self._run(cmd)

    def get_video_height(self, video_path: Path) -> int:
        """
        Retrieves the height of a video file using ffprobe.
        """
        cmd_base = (
            "ffprobe -v error -select_streams v:0 -show_entries stream=height "
            "-of default=noprint_wrappers=1:nokey=1"
        )
        cmd = f"{cmd_base} {shlex.quote(str(video_path))}"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return int(output)

    def get_video_width(self, video_path: Path) -> int:
        """
        Retrieves the width of a video file using ffprobe.
        """
        cmd_base = (
            "ffprobe -v error -select_streams v:0 -show_entries stream=width "
            "-of default=noprint_wrappers=1:nokey=1"
        )
        cmd = f"{cmd_base} {shlex.quote(str(video_path))}"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return int(output)

    def create_composite_scene_video(
        self,
        img_path: Path,
        audio_path: Path,
        out_path: Path
    ) -> None:
        """
        Creates a video with a 3-part dynamic sequence:
        1. Zoom In (30%) - from 1.0 to 1.2
        2. Soft Swing Loop (40%) - at 1.2
        3. Zoom Out (30%) - from 1.2 to 1.0
        """
        duration = self.get_audio_duration(audio_path)
        fps = 25
        total_frames = int(duration * fps)
        f1 = total_frames * 0.3
        f2 = total_frames * 0.7

        # Infer dimensions from the source image
        width = self.get_video_width(img_path)
        height = self.get_video_height(img_path)

        # Zoom expression (per frame)
        # Part 1: 1.0 -> 1.2 | Part 2: 1.2 | Part 3: 1.2 -> 1.0
        z_expr = (
            f"if(lt(on,{f1}), 1.0+0.2*(on/{f1}), "
            f"if(lt(on,{f2}), 1.2, "
            f"1.2-0.2*((on-{f2})/({total_frames}-{f2}))))"
        )
        pos_filter = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        zoom_filter = f"zoompan=z='{z_expr}':d=1:{pos_filter}:s={width}x{height},format=yuv420p"

        # Rotation filter: constant soft swing
        rotate_filter = "rotate='1*PI/180*sin(2*PI*t/3)'"

        cmd = f"""
        ffmpeg -y -loop 1 -i {shlex.quote(str(img_path))} \
          -i {shlex.quote(str(audio_path))} \
          -vf "{zoom_filter},{rotate_filter},fps=25" \
          -shortest \
          -c:v libx264 -c:a aac -ar 44100 -ac 2 -pix_fmt yuv420p -r 25 {shlex.quote(str(out_path))}
        """
        self._run(cmd)

    def extract_audio(self, video_in: Path, audio_out: Path) -> None:
        """
        Extracts audio from a video file, optimized for Whisper STT.
        16kHz, mono, WAV.
        """
        cmd = f"""
        ffmpeg -y -i {shlex.quote(str(video_in))} \
          -vn -ac 1 -ar 16000 \
          {shlex.quote(str(audio_out))}
        """
        self._run(cmd)

    def add_subtitles_to_video(
        self,
        video_in: Path,
        ass_path: Path,
        video_out: Path,
    ) -> None:
        """
        Adds dynamic ASS subtitles to a video.
        """
        safe_ass = str(ass_path).replace("\\", "/").replace(":", "\\:")
        sub_filter = f"subtitles={safe_ass}"

        cmd = f"""
        ffmpeg -y -i {shlex.quote(str(video_in))} \
          -vf "{sub_filter}" \
          -c:a copy {shlex.quote(str(video_out))}
        """
        self._run(cmd)

    def add_background_music(
        self,
        video_in: Path,
        audio_bg: Path,
        video_out: Path,
        bg_volume: float = 0.15
    ) -> None:
        """
        Mixes a background audio track into a video.
        The music loops and is mixed at a low volume.
        """
        # [0:a] is video narration (Step 5/6)
        # [1:a] is background music (Step 7)
        filter_complex = (
            f"[0:a]volume=1.0[v_a]; "
            f"[1:a]volume={bg_volume}[bg_a]; "
            "[v_a][bg_a]amix=inputs=2:duration=first:normalize=0[fixed_a]"
        )

        # -stream_loop -1 loops the background audio indefinitely
        cmd = f"""
        ffmpeg -y -i {shlex.quote(str(video_in))} \
          -stream_loop -1 -i {shlex.quote(str(audio_bg))} \
          -filter_complex "{filter_complex}" \
          -map 0:v -map "[fixed_a]" \
          -c:v copy -c:a aac -movflags +faststart {shlex.quote(str(video_out))}
        """
        self._run(cmd)

    def add_background_music_with_ducking(
        self,
        video_in: Path,
        audio_bg: Path,
        video_out: Path,
        bg_volume: float = 0.30,
    ) -> None:
        """
        Mixes background music into a video using sidechain ducking.
        The music automatically lowers when narration is active and rises
        back during silences — exactly like a professional audio mix.

        Parameters
        ----------
        bg_volume : float
            Base volume of the music track (before ducking). Higher than the
            flat mixer because ducking will reduce it during speech anyway.
        """
        # Sidechain ducking explanation:
        #   - threshold: voice amplitude level that triggers ducking (0.02 = very sensitive)
        #   - ratio: how aggressively to compress (6:1 = significant duck)
        #   - attack: how fast the duck kicks in when voice appears (ms)
        #   - release: how slowly music comes back after voice stops (ms) — long for smoothness
        #   - level_sc: sidechain input gain (amplifies the voice signal used to trigger)
        filter_complex = (
            f"[0:a]volume=1.0[narr];"
            f"[1:a]volume={bg_volume}[bg_raw];"
            "[bg_raw][narr]sidechaincompress="
            "threshold=0.02:ratio=6:attack=20:release=800:"
            "level_sc=0.9[bg_ducked];"
            "[narr][bg_ducked]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        )

        # -stream_loop -1 loops background audio indefinitely
        cmd = (
            f"ffmpeg -y "
            f"-i {shlex.quote(str(video_in))} "
            f"-stream_loop -1 -i {shlex.quote(str(audio_bg))} "
            f'-filter_complex "{filter_complex}" '
            f"-map 0:v -map \"[out]\" "
            f"-c:v copy -c:a aac -movflags +faststart {shlex.quote(str(video_out))}"
        )
        self._run(cmd)

    def prepend_and_append_bumpers(
        self,
        main_video: Path,
        out_path: Path,
        intro: Optional[Path] = None,
        outro: Optional[Path] = None,
    ) -> None:
        """
        Concatenates an optional intro clip, the main video, and an optional
        outro clip into a single output file. Clips must share the same
        codec, resolution, and framerate as the main video for a lossless concat.
        If neither intro nor outro are provided, the main video is copied as-is.
        """
        import shutil
        clips: List[Path] = []
        if intro and intro.exists():
            clips.append(intro)
        clips.append(main_video)
        if outro and outro.exists():
            clips.append(outro)

        if len(clips) == 1:
            shutil.copy2(main_video, out_path)
            return

        self.concat_videos(clips, out_path, reencode=True)
