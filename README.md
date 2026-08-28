# Ferramentas de Mídia

Uma CLI em Python com duas funções:

- baixar vídeos do YouTube em MP4 ou extrair o áudio em MP3;
- transcrever arquivos locais de áudio ou vídeo para TXT.

## Instalação

Abra o PowerShell nesta pasta e instale as dependências no mesmo Python usado para executar a CLI:

```powershell
python -m pip install --upgrade -r requirements.txt
```

O downloader também precisa dos executáveis `ffmpeg` e `ffprobe` disponíveis no `PATH`. Para confirmar:

```powershell
ffmpeg -version
ffprobe -version
```

O `faster-whisper` requer Python 3.9 ou mais recente. A execução em GPU exige CUDA 12, cuBLAS e cuDNN 9 compatíveis. Se a GPU não puder ser iniciada, a ferramenta tenta transcrever pela CPU automaticamente.

## Como executar

```powershell
python cli.py
```

O menu oferece:

```text
1 - Baixar vídeo ou áudio do YouTube
2 - Transcrever arquivo de áudio ou vídeo
3 - Baixar do YouTube e transcrever
0 - Sair
```

### Downloads

Cole o link e escolha `1` para MP4 ou `2` para MP3. Os arquivos são gravados na pasta `downloads`, criada automaticamente ao lado da CLI.

### Transcrições

Cole o caminho de um arquivo de áudio ou vídeo. Caminhos copiados com aspas também são aceitos. O resultado é salvo ao lado do arquivo original com o mesmo nome e extensão `.txt`.

Na primeira transcrição, o modelo `turbo` será baixado automaticamente e poderá levar algum tempo. A transcrição está configurada para português e inclui marcações de tempo.

### Baixar e transcrever pelo link

Escolha a opção `3` e cole o link do YouTube. A ferramenta baixa o áudio em MP3, transcreve automaticamente e mantém os arquivos MP3 e TXT juntos na pasta `downloads`.

Se o YouTube responder temporariamente que a página precisa ser recarregada, a ferramenta tenta novamente uma vez. O Node.js instalado é habilitado para os desafios JavaScript atuais do YouTube.

## Testes

```powershell
python -m unittest discover -v
```

Baixe somente conteúdo que seja seu, esteja em domínio público ou para o qual você tenha autorização.
