import time
import wave
from pathlib import Path

from google.genai import types

from tools.common.gemini_base import GeminiBase
from tools.common.messenger import Messenger


class GeminiAudioGenerator(GeminiBase):
    tts_model: str = "gemini-2.5-flash-preview-tts"
    voice_name: str = "Fenrir"

    def text_to_speech(
        self,
        text: str,
        audio_path: Path,
    ) -> None:
        """
        Generates audio using Gemini TTS and saves it to disk.
        """
        time.sleep(20)

        audio_path.parent.mkdir(parents=True, exist_ok=True)

        response = self._execute_with_retry(
            self.client.models.generate_content,
            model=self.tts_model,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voice_name,
                        )
                    )
                ),
            ),
        )
        self._extract_usage(response, self.tts_model)

        pcm_chunks: list[bytes] = []
        if response.parts:
            for part in response.parts:
                if part.text:
                    Messenger.info(f"Gemini thoughts: {part.text}")
                elif part.inline_data and part.inline_data.data:
                    pcm_chunks.append(part.inline_data.data)

        if not pcm_chunks:
            raise RuntimeError("❌ No se encontró audio en la respuesta de Gemini")

        combined_pcm = b"".join(pcm_chunks)
        self._write_wav(audio_path, combined_pcm)
        Messenger.audio(f"Audio generado: {audio_path}")

    def _write_wav(
        self,
        filename: Path,
        pcm_data: bytes,
        *,
        sample_rate: int = 24000,
        channels: int = 1,
        sample_width: int = 2,
    ) -> None:
        """
        Writes raw PCM data to a WAV file.
        """
        with wave.open(str(filename), "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
