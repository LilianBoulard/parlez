"""
parlez
======

Resources
---------

- tortoise-tts: https://github.com/neonbjb/tortoise-tts
- pycord's API reference: https://docs.pycord.dev/en/stable/
- Discord applications: https://discord.com/developers/applications/
"""

# Created during docker setup
from .tortoise.api import TextToSpeech
from .tortoise.utils.audio import load_audio

from ._config import config

import discord
import torchaudio
import pydub
import torch
import os

from hashlib import md5
from loguru import logger
from tempfile import TemporaryDirectory
from time import sleep
from pathlib import Path


bot = discord.Bot()


reference_clips = {
    voice_directory.name: [
        load_audio(str(clip), 22050)
        for clip in audio_clips
        if clip.suffix == ".wav"
    ]
    for voice_directory in (Path(__file__).parent / "voices").iterdir()
    if voice_directory.is_dir()
    and (audio_clips := list(voice_directory.iterdir()))
}
if bool(config["PARAMETERS"]["USE_DEFAULT_VOICES"]):
    reference_clips.update({
        voice_directory.name: [
            load_audio(str(clip), 22050)
            for clip in audio_clips
            if clip.suffix == ".wav"
        ]
        for voice_directory in (Path(__file__).parent / "tortoise" / "tortoise_voices").iterdir()
        if voice_directory.is_dir()
        and (
            voice_directory.name not in ["myself"]
            or voice_directory.name.startswith("train_")
        )
        and (audio_clips := list(voice_directory.iterdir()))
    })

supported_voices = list(reference_clips.keys())


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user!s} (ID: {bot.user.id})")
    logger.info(f"Supported voices: {supported_voices}")


@bot.slash_command(description="Says something with a synthetic voice.")
async def say(
        ctx: discord.ApplicationContext,
        voice: discord.Option(str, choices=supported_voices, description="The synthetic voice to use"),
        message: discord.Option(str, description="The message to speak"),
):
    tts = TextToSpeech()

    request_id = md5(voice + message)

    logger.info(
        f"Received TTS request {request_id}. "
        f"Parameters: {voice=} ; {ctx.author=} ; {message=}"
    )

    interaction = await ctx.respond("Processing, please wait...")
    if not interaction:
        logger.error(
            "Could not send initial status message, trying to continue..."
        )

    logger.debug(f"Generating audio for query {request_id}")
    pcm_audio = tts.tts_with_preset(
        message,
        voice_samples=reference_clips[voice],
        preset=config["PARAMETERS"]["QUALITY"],
    )

    with TemporaryDirectory() as temp_dir:

        if bool(config["RESULTS"]["SAVE_RESULTS"]):
            output_dir = config["RESULTS"]("OUTPUT_DIRECTORY")
            # Save the tensor to disk
            tensor_file = os.path.join(
                output_dir,
                f"{request_id}.tensor",
            )
            torch.save(
                pcm_audio,
                tensor_file,
            )
            final_file = os.path.join(output_dir, f"{request_id}.mp3")
        else:
            final_file = f"{temp_dir}/{request_id}.mp3"

        intermediary_file = f"{temp_dir}/{request_id}.wav"

        torchaudio.save(intermediary_file, pcm_audio.reshape(1, -1), 24000)
        pydub.AudioSegment.from_wav(intermediary_file).export(final_file)

        author_in_voice_channel = not not ctx.user.voice
        if author_in_voice_channel and bool(config["PARAMETERS"]["ALLOW_VOICE"]):
            # Play the file in the vocal channel
            vc: discord.VoiceClient = await ctx.user.voice.channel.connect()
            vc.play(
                discord.FFmpegPCMAudio(final_file),
                after=lambda e: logger.error(f"Player error: {e}") if e else None,
            )
            # Wait for the play to end
            # Note: could also use `after` in `play()`.
            sleep(pcm_audio.shape[2] / 24000)

            await vc.disconnect()
            await interaction.edit_original_response(content="Done, played in channel!")
        else:
            # Send the clip as a file in the textual channel
            await interaction.edit_original_response(content="Done, here's the audio:", file=discord.File(final_file))

        del_interaction_val = int(config["PARAMETERS"]["DELETE_INTERACTION"])
        if del_interaction_val > 0:
            sleep(del_interaction_val)
            await interaction.delete_original_message()
