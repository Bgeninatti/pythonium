from pythonium import cfg


class GameMode:

    name: str

    def __init__(
        self,
        tenacity=cfg.tenacity,
    ):
        self.cfg = cfg
        self.tenacity = tenacity

    def build_galaxy(self, name, players):
        """
        Fabrica la galaxy

        Retorna una instancia de :class:`Galaxy`
        """
        raise NotImplementedError("Metodo no implementado")

    def galaxy_for_player(self, player, t):
        """
        Devuelve una galaxy que muestra sólo las cosas que puede ver el player
        en un turn determinado
        """
        raise NotImplementedError("Metodo no implementado")

    def get_context(self, galaxy, players, turn):
        """
        Genera variables de context para el player en un turn determinado
        """
        raise NotImplementedError("Metodo no implementado")
