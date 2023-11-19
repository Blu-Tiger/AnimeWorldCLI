# AnimeWorldCLI
A cli to browse and watch anime from [AnimeWorld](https://www.animeworld.so)
---
```AnimeWorld CLI

Usage:
    awcli [-b BYPASS | --bypass=BYPASS] [-s SERVER | --server SERVER]
            [-p | --play] [-d | --download] [INPUT ...]
    awcli [-s SERVER | --server SERVER] [-p | --play] [-d | --download]
            [-b BYPASS | --bypass=BYPASS] [-e EPISODIO | --episodio EPISODIO] (INPUT ...)
    awcli -h | --help

Options:
    -h  --help                      mostra questo
    -e, --episodio EPISODIO         seleziona numero episodio
    -s, --server SERVER             seleziona server
    -p, --play                      play
    -d, --download                  download (non ancora implementato)
    -b, --bypass=BYPASS             salta selezione anime, episodio o server 
                                    separati da virgola
                                    (a,e,s o all)
```
