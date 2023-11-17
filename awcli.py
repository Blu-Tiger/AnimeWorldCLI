"""AnimeWorld CLI

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
    -d, --download                  download
    -b, --bypass=BYPASS             salta selezione anime, episodio o seraver 
                                    separati da virgola
                                    (a,e,s o all)


"""
import os
import sys
import animeworld as aw
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from docopt import docopt

basepath = os.path.dirname(os.path.abspath("./libmpv/mpv-1.dll"))
print(basepath)
os.environ['PATH'] = basepath + os.pathsep + os.environ['PATH']
os.environ["LD_LIBRARY_PATH"] = basepath

import mpv   

class AWCLI:
    """
        AnimeWorld CLI
    """
    def __init__(self):
        self.player = mpv.MPV(log_handler=self.my_log, ytdl=False,
                              input_default_bindings=True,
                              input_vo_keyboard=True)

    def search(self, query, skip=False):
        """
            Ricerca anime
        """
        options = aw.find(query)
        if skip:
            return options[0]
        anime = inquirer.fuzzy(
            message="Risultati:",
            choices=[Choice(name=option["name"],
                            value=option)
                     for option in options],
            mandatory=True
        ).execute()
        return anime

    def seleziona_episodio(self, anime, skip=False):
        """
            Ricerca episodi
        """
        animelink = aw.Anime(link=anime['link'])
        episodi = animelink.getEpisodes()
        if skip:
            return episodi[0]
        epsodio = inquirer.fuzzy(
            message="Episodi:",
            choices=[Choice(name=option.number, value=option) for option in episodi],
            mandatory=True
        ).execute()
        return epsodio

    def seleziona_server(self, epsodio, skip=False):
        """
            Ricerca server
        """
        linkepsodio = epsodio.links
        choices =[]
        for server in linkepsodio:
            try:
                completeserver = server
                completeserver={"number": server.number,"name": server.name,
                                "Nid": server.Nid, "link": server.link,
                                "fileLink": server.fileLink()}
                choices.append(Choice(name=server.name, value=completeserver))
            except aw.exceptions.ServerNotSupported:
                # choices.append(Choice(name=server.name, value=''))
                continue

        if skip:
            return choices[0].value

        server = inquirer.fuzzy(
            message="Server:",
            choices=choices,
            mandatory=True
        ).execute()
        return server

    def my_log(self, loglevel, component, message):
        """
            Log mpv
        """
        print(f'[{loglevel}] {component}: {message}')

    def dworplay(self, server, palyordownload=None):
        """
            Download o play
        """
        link = server["fileLink"]

        match palyordownload:
            case 'play':
                self.player.play(link)
                self.player.wait_for_playback()
            case 'download':
                pass
            case None:
                ch = inquirer.fuzzy(
                    message="Server:",
                    choices=[Choice(name="Guarda", value=1), Choice(name="Scarica", value=2)],
                    mandatory=True
                ).execute()
                if ch == 1:
                    print("Loading...")
                    self.player.play(link)
                    self.player.wait_for_playback()
                elif ch == 2:
                    pass

def main():
    """
        Main
    """
    awcli = AWCLI()

    arguments = docopt(__doc__, argv=None, help=True, version=None, options_first=False)

    skipa = False
    skipe = False
    skips = False
    palydownload = None

    if arguments["--play"] is True:
        palydownload = 'play'

    if arguments["--download"] is True:
        palydownload = 'download'

    if arguments["--bypass"] is not None:
        skip = arguments["--bypass"].split(',')
        if skip != '':
            if  'a' not in skip and 'e' not in skip and 's' not in skip:
                if skip != ['all']:
                    print("Sintassi bypass non corretto!")
                    sys.exit(1)
            if 'a' in skip:
                skipa = True
            if 'e' in skip:
                skipe = True
            if 's' in skip:
                skips = True
            if skip == ['all']:
                skipa = True
                skipe = True
                skips = True

    if arguments["--episodio"] is not None:
        if not int(arguments["--episodio"]):
            print("Sintassi numero episodio non corretto!")
            sys.exit(1)

        if arguments["--episodio"] is None or arguments["--episodio"] == '':
            print("Numero episodio non inserito!")
            sys.exit(1)

        if arguments["INPUT"] == []:
            print("Nessun anime cercato!")
            sys.exit(1)

        if arguments["--episodio"] != '' and arguments["INPUT"] != []:
            anime = awcli.search(query=' '.join(arguments["INPUT"]), skip=skipa)
            try:
                if int(arguments["--episodio"])-1 < 0:
                    print("Episodio non valido!")
                epsodio = aw.Anime(link=anime['link']).getEpisodes()[int(arguments["--episodio"])-1]
            except IndexError:
                print("Episodio non trovato!")
                sys.exit(1)
            server = awcli.seleziona_server(epsodio=epsodio, skip=skips)
            awcli.dworplay(server=server, palyordownload=palydownload)
            
            
    if arguments["INPUT"] == []:
        query = inquirer.text(message="Cerca anime:").execute()
        anime = awcli.search(query=query, skip=skipa)
        epsodio = awcli.seleziona_episodio(anime=anime, skip=skipe)
        server = awcli.seleziona_server(epsodio=epsodio, skip=skips)
        awcli.dworplay(server=server, palyordownload=palydownload)
    else:
        anime = awcli.search(query=' '.join(arguments["INPUT"]), skip=skipa)
        epsodio = awcli.seleziona_episodio(anime=anime, skip=skipe)
        server = awcli.seleziona_server(epsodio=epsodio, skip=skips)
        awcli.dworplay(server=server, palyordownload=palydownload)


if __name__ == "__main__":
    main()
