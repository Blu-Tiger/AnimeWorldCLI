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
from InquirerPy.base.control import Choice, Separator
from InquirerPy.validator import EmptyInputValidator
from docopt import docopt

basepath = os.path.dirname(os.path.abspath("./libmpv/mpv-2.dll"))
basepath2 = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] = basepath + os.pathsep + basepath2 + os.pathsep + os.environ['PATH']
os.environ["LD_LIBRARY_PATH"] = basepath

import mpv

class AWCLI:
    """
        AnimeWorld CLI
    """
    def __init__(self):
        self.player = mpv.MPV(ytdl=False,
                              input_default_bindings=True,
                              input_vo_keyboard=True)

    def search(self, query, skip=False):
        """
            Ricerca anime
        """
        options = aw.find(query)
        if skip:
            return aw.Anime(link=options[0]['link'])
        animefound = inquirer.fuzzy(
            message="Seleziona Anime:",
            choices=[Choice(name=option["name"],
                            value=option)
                     for option in options],
            mandatory=True,
            qmark="🎞️",
            amark="🎞️",
        ).execute()
        return aw.Anime(link=animefound['link'])

    def seleziona_episodio(self, anime, skip=False):
        """
            Ricerca episodi
        """
        episodi = anime.getEpisodes()
        if skip:
            return episodi[0]
        epsodio = inquirer.fuzzy(
            message="Episodio:",
            choices=[Choice(name=option.number, value=option) for option in episodi],
            mandatory=True,
            qmark="📺",
            amark="📺",
        ).execute()
        return epsodio

    def seleziona_server(self, epsodio, skip=False, servername=None):
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
        if servername:
            server = next((choice for choice in choices if choice.value["name"] == servername), None)
            if server is None:
                print(f"Non è stato trovato alcun server con il nome '{servername}'!")
                sys.exit(1)
            return server.value

        if skip:
            return choices[0].value

        server = inquirer.fuzzy(
            message="Server:",
            choices=choices,
            mandatory=True,
            qmark="📡",
            amark="📡",
        ).execute()
        
        return server

    def my_log(self, loglevel, component, message):
        """
            Log mpv
        """
        print(f'[{loglevel}] {component}: {message}')

    def dworplay(self, server, anime, palyordownload=None, timestamp=None):
        """
            Download o play
        """
        link = server["fileLink"]
        
        if palyordownload is None:
            palyordownload = inquirer.fuzzy(
                message="Cosa vuoi fare?",
                    choices=[Choice(name="Guarda", value=1), Choice(name="Scarica", value=2)],
                    mandatory=True,
                    qmark="💻",
                    amark="💻",
                ).execute()
        match palyordownload:
            case 1:
                print(f"Sati guardando {anime.getName()}, episodio {server['number']}, su {server['name']}")
                self.player.play(link)
                self.player.wait_until_playing()
                if timestamp:
                    self.player.seek(timestamp,  reference='absolute')
                return palyordownload
                # self.player.wait_for_playback()
            case 2:
                return palyordownload

                
    def change_episode(self, anime, epsodio, server):
        """
            Cambia episodio
        """
        epsodi = anime.getEpisodes()
        epsodiocorrente = epsodio
        animecorrente = anime
        servercorrente = server
        while True:
            timestamp = None
            num = int(epsodiocorrente.number)
            choices = [
                Choice(value=num+1, name=" [Prossimo⪢") if epsodiocorrente.number!=epsodi[-1].number else None,
                Choice(value=num-1, name="⪡Precedente]") if epsodiocorrente.number!=epsodi[0].number else None,
                Choice(value=None, name="🔢 Inserisci numero episodio"),
                Separator(),
                Choice(value=-1, name="📡 Cambia Server"),
                Choice(value=-2, name="🔎 Cerca Anime"),
                Separator(),
                Choice(value=-3, name="👋 Esci"),
            ]
            newep = inquirer.select(
                message="Cambia episodio:",
                choices=[choice for choice in choices if choice],
                default="Prossimo",
                qmark="📺",
                amark="",
            ).execute()
            match newep:
                case None:
                    newep = inquirer.number(
                        message="Inserisci numero episodio:",
                        min_allowed=int(epsodi[0].number),
                        max_allowed=int(epsodi[-1].number),
                        validate=EmptyInputValidator(),
                        qmark="📺",
                        amark="📺",
                    ).execute()
                case -1:
                    servercorrente = self.seleziona_server(epsodio=epsodiocorrente)
                    timestamp = self.player.time_pos
                case -2:
                    query = inquirer.text(message="Cerca anime:", qmark="🔎", amark="🔎").execute()
                    animecorrente = self.search(query=query)
                    epsodiocorrente = self.seleziona_episodio(anime=animecorrente)
                case -3:
                    sys.exit(0)
                case _:
                    epsodiocorrente = epsodi[int(newep)-1]
            self.dworplay(server=servercorrente, anime=anime, palyordownload=1, timestamp=timestamp)
            

def main():
    """
        Main
    """
    awcli = AWCLI()

    arguments = docopt(__doc__, argv=None, help=True, version="AnimeWorld CLI 1.0.1", options_first=False)

    skipa = False
    skipe = False
    skips = False
    palydownload = None
    servern = None

    if arguments["--play"] is True:
        palydownload = 1

    if arguments["--download"] is True:
        palydownload = 2

    if arguments["--bypass"]:
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
                
    if arguments["--server"]:
        servern = arguments["--server"]
        

    if arguments["--episodio"]:
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
                    sys.exit(1)
                epsodio = anime.getEpisodes()[int(arguments["--episodio"])-1]
            except IndexError:
                print(f"Episodio {int(arguments["--episodio"])-1} non trovato!")
                sys.exit(1)

    elif arguments["INPUT"] == []:
        query = inquirer.text(message="Cerca anime:", qmark="🔎", amark="🔎").execute()
        anime = awcli.search(query=query, skip=skipa)
        epsodio = awcli.seleziona_episodio(anime=anime, skip=skipe)
    else:
        anime = awcli.search(query=' '.join(arguments["INPUT"]), skip=skipa)
        epsodio = awcli.seleziona_episodio(anime=anime, skip=skipe)
        
    server = awcli.seleziona_server(epsodio=epsodio, skip=skips, servername=servern)
    palydownload = awcli.dworplay(server=server, anime=anime, palyordownload=palydownload)
    if palydownload == 1:
        awcli.change_episode(anime=anime, epsodio=epsodio, server=server)

if __name__ == "__main__":
    main()
