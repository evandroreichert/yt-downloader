# yt-downloader

Baixa vídeos e áudios do YouTube e transcreve arquivos de áudio/vídeo com Whisper. Feito para Windows.

## Instalação

Precisa de Windows 10 ou 11 com `winget`.

```powershell
git clone https://github.com/evandroreichert/yt-downloader.git
cd yt-downloader
.\instalar.bat
```

O instalador confere Python, FFmpeg, Node.js e Git, oferece instalar o que faltar, cria a `.venv` e o `config.json`.

## Uso

Abra `iniciar.bat`.

```text
1 - Baixar vídeo ou áudio do YouTube
2 - Transcrever arquivo de áudio ou vídeo
3 - Baixar do YouTube e transcrever
0 - Sair
```

Os downloads ficam em `downloads/`. Na primeira transcrição o modelo Whisper é baixado, o que pode demorar. Se houver GPU NVIDIA com CUDA ela é usada, senão a CPU.

## Configuração

Edite `config.json`:

- `language`: idioma da transcrição
- `model`: `tiny`, `base`, `small`, `medium`, `large-v3` ou `turbo`
- `transcript_formats`: `txt` e/ou `srt`
- `keep_downloaded_audio`: manter o áudio depois de transcrever

## Atualização e diagnóstico

`atualizar.bat` atualiza o código e o `yt-dlp`. Rode quando o YouTube parar de funcionar.

`diagnostico.bat` mostra versões instaladas e se a GPU está disponível.
