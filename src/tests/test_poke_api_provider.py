"""Testa o adapter da PokéAPI sem internet: a sessão HTTP é substituída por respostas prontas."""
from controllers.poke_api_provider import PokeApiProvider
from controllers.provedor_cache import ProvedorPokemonComCache


class Resposta:
    def __init__(self, dados, status=200):
        self._dados, self.status_code = dados, status
        self.ok = status < 400

    def json(self):
        return self._dados

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(self.status_code)


class SessaoFalsa:
    def __init__(self, rotas):
        self.rotas, self.chamadas = rotas, []

    def get(self, url, timeout=None):
        self.chamadas.append(url)
        return self.rotas.get(url, Resposta({}, 404))


def golpe(nome, tipo, poder):
    return {"name": nome, "type": {"name": tipo}, "damage_class": {"name": "physical"}, "power": poder}


def pokemon_json(id_, nome, tipos, speed, golpes):
    return {
        "id": id_, "name": nome,
        "types": [{"type": {"name": t}} for t in tipos],
        "stats": [{"stat": {"name": "hp"}, "base_stat": 1}, {"stat": {"name": "speed"}, "base_stat": speed}],
        "moves": [{"move": {"url": f"https://api.test/move/{g}/"}} for g in golpes],
        "sprites": {"front_default": "front.png", "other": {"official-artwork": {"front_default": "arte.png"}}},
    }


def provedor(rotas):
    PokeApiProvider._cache_golpes.clear()
    sessao = SessaoFalsa(rotas)
    return PokeApiProvider("https://api.test", sessao=sessao), sessao


def test_converte_json_para_pokemon_com_4_golpes_de_tipos_variados():
    rotas = {
        "https://api.test/pokemon/25": Resposta(pokemon_json(25, "pikachu", ["electric"], 90,
                                                             ["a", "b", "c", "d", "e", "f"])),
        "https://api.test/move/a/": Resposta(golpe("thunderbolt", "electric", 90)),
        "https://api.test/move/b/": Resposta(golpe("thunder", "electric", 110)),
        "https://api.test/move/c/": Resposta(golpe("growl", "normal", None)),
        "https://api.test/move/d/": Resposta(golpe("iron-tail", "steel", 100)),
        "https://api.test/move/e/": Resposta(golpe("slam", "normal", 80)),
        "https://api.test/move/f/": Resposta(golpe("quick-attack", "normal", 40)),
    }
    p, _ = provedor(rotas)
    pikachu = p.buscar(25)
    assert (pikachu.nome, pikachu.tipos, pikachu.velocidade, pikachu.sprite) == ("pikachu", ["electric"], 90, "arte.png")
    assert [m.nome for m in pikachu.movimentos] == ["thunder", "iron-tail", "slam", "thunderbolt"]


def test_pokemon_sem_golpe_de_dano_recebe_golpe_reserva():
    rotas = {
        "https://api.test/pokemon/ditto": Resposta(pokemon_json(132, "ditto", ["normal"], 48, ["t"])),
        "https://api.test/move/t/": Resposta(golpe("transform", "normal", None)),
    }
    p, _ = provedor(rotas)
    assert [m.nome for m in p.buscar("ditto").movimentos] == ["struggle"]


def test_pokemon_inexistente_devolve_none():
    p, _ = provedor({})
    assert p.buscar("nao-existe") is None


def test_cache_evita_buscar_duas_vezes():
    rotas = {
        "https://api.test/pokemon/ditto": Resposta(pokemon_json(132, "ditto", ["normal"], 48, [])),
    }
    p, sessao = provedor(rotas)
    cache = ProvedorPokemonComCache(p)
    cache.buscar("ditto")
    cache.buscar("DITTO")
    cache.buscar(132)
    assert sessao.chamadas == ["https://api.test/pokemon/ditto"]
