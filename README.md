# parlez

*parlez* is a Discord bot for generating text-to-speech.

## How to use

The recommended way to use this project is to:
1. Clone it with git
2. Add the voice clips in the `robot/voices` directory,
   [the procedure is the same as tortoise-tts](https://github.com/neonbjb/tortoise-tts#adding-a-new-voice)
3. Create an application->bot on the Discord interface, and add the bot token
   to `config.ini`
4. While you're at it, modify the parameters in `config.ini` to suit your needs

## Limitations

The default TTS generation is based on `tortoise-tts`, an open-source 
multi-voice text-to-speech engine.

> It shouldn't be too hard to switch it with another TTS engine if necessary:
feel free to fork this repo or submit a pull request!
