import json
import random

class Choice:
    def __init__(self, text: str, next_scene_id: str, stat_changes: dict = None):
        self.text = text
        self.next_scene_id = next_scene_id
        self.stat_changes = stat_changes if stat_changes else {}

class Scene:
    def __init__(self, scene_id: str, text: str, background_key: str, character_sprite: str = None, next_scene_id: str = None, is_ending: bool = False):
        self.scene_id = scene_id
        self.text = text
        self.background_key = background_key
        self.character_sprite = character_sprite 
        self.next_scene_id = next_scene_id 
        self.is_ending = is_ending
        self.choices: list[Choice] = []

    def add_choice(self, text: str, next_scene_id: str, stat_changes: dict = None):
        self.choices.append(Choice(text, next_scene_id, stat_changes))

    @classmethod
    def from_dict(cls, scene_id: str, data: dict):
        scene = cls(
            scene_id=scene_id,
            text=data.get("text", ""),
            background_key=data.get("background_key"),
            character_sprite=data.get("character_sprite"),
            next_scene_id=data.get("next_scene_id"),
            is_ending=data.get("is_ending", False)
        )
        for choice_data in data.get("choices", []):
            scene.add_choice(choice_data["text"], choice_data["next_scene_id"], choice_data.get("stat_changes"))
        return scene

class GameEngine:
    def __init__(self):
        self._scenes: dict[str, Scene] = {}
        self._current_scene: Scene | None = None
        self._affinities = {"Lola": 0, "Bibi": 0, "Lily": 0}
        self._fila_eventos: list[str] = []
        self._isekai_flag = False

    @property
    def current_scene(self) -> Scene:
        return self._current_scene    

    @property
    def affinities(self) -> dict:
        return self._affinities

    def load_script_from_json(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        for scene_id, data in script_data.items():
            self._scenes[scene_id] = Scene.from_dict(scene_id, data)

    def start(self, start_scene_id: str):
        self.reset(start_scene_id)

    def reset(self, start_scene_id: str):
        self._affinities = {chave: 0 for chave in self._affinities}
        self._fila_eventos.clear()
        self._isekai_flag = random.random() <= 0.20 # 20% de chance (1/5)
        self._current_scene = self._scenes[start_scene_id]

    def _update_affinity(self, character: str, amount: int):
        if character in self._affinities:
            self._affinities[character] += amount

    def make_choice(self, choice_index: int):
        if self._current_scene and self._current_scene.choices:
            if 0 <= choice_index < len(self._current_scene.choices):
                choice = self._current_scene.choices[choice_index]
                for personagem, alteracao in choice.stat_changes.items():
                    self._update_affinity(personagem, alteracao)
                self._rotear_ou_avancar(choice.next_scene_id)

    def advance_linear_scene(self):
        if self._current_scene and not self._current_scene.choices and self._current_scene.next_scene_id:
            self._rotear_ou_avancar(self._current_scene.next_scene_id)

    def _rotear_ou_avancar(self, next_scene_id: str):
        if next_scene_id == "AVALIAR_FINAIS":
            self._avaliar_finais()
            
        elif next_scene_id == "VERIFICAR_EVENTOS_ESPECIAIS":
            lily_pts, lola_pts, bibi_pts = self._affinities.get("Lily", 0), self._affinities.get("Lola", 0), self._affinities.get("Bibi", 0)
            if bibi_pts >= 3 and lola_pts <= 0 and lily_pts <= 0:
                self._current_scene = self._scenes["bibi_praia_1"]
            elif lily_pts >= 3 and lola_pts <= 0 and bibi_pts <= 0:
                self._current_scene = self._scenes["ddlc_inicio"]
            elif lola_pts >= 3 and lily_pts <= 0 and bibi_pts <= 0:
                self._current_scene = self._scenes["fnaf_inicio"]
            else:
                self._fila_eventos = [nome for nome, pts in self._affinities.items() if pts >= 3]
                if not self._fila_eventos:
                    self._current_scene = self._scenes["d4_sozinho"]
                else:
                    self._rotear_proximo_evento()
                    
        elif next_scene_id == "PROXIMO_EVENTO_ESPECIAL":
            self._rotear_proximo_evento()
            
        elif next_scene_id == "ROTEAR_DIA2_LILY":
            self._current_scene = self._scenes["dia2_lily_raiva"] if self._affinities.get("Lily", 0) < 0 else self._scenes["dia2_lily_conversa"]
                
        elif next_scene_id == "ROTEAR_DIA2_LOLA":
            self._current_scene = self._scenes["dia2_lola_conversa"] if self._affinities.get("Lola", 0) > 0 else self._scenes["dia2_lola_bobao"]
                
        elif next_scene_id == "ROTEAR_DIA3_BIBI":
            if self._affinities.get("Bibi", 0) >= 2: self._current_scene = self._scenes["d3_bibi_inicio"]
            else: self._rotear_ou_avancar("ROTEAR_DIA3_LILY") 
                
        elif next_scene_id == "ROTEAR_DIA3_LILY":
            if self._affinities.get("Lily", 0) >= 2: self._current_scene = self._scenes["d3_lily_inicio"]
            else: self._rotear_ou_avancar("ROTEAR_DIA3_LOLA")
                
        elif next_scene_id == "ROTEAR_DIA3_LOLA":
            if self._affinities.get("Lola", 0) >= 2: self._current_scene = self._scenes["d3_lola_inicio"]
            else: self._rotear_ou_avancar("VERIFICAR_EVENTOS_ESPECIAIS")

        else:
            self._current_scene = self._scenes.get(next_scene_id)

    def _rotear_proximo_evento(self):
        if self._fila_eventos:
            menina_atual = self._fila_eventos.pop(0)
            self._current_scene = self._scenes[f"ev_especial_{menina_atual.lower()}"]
        else:
            self._avaliar_finais()

    def _avaliar_finais(self):
        meninas_pontuadas = [nome for nome, pontos in self._affinities.items() if pontos >= 3]
        quantidade = len(meninas_pontuadas)

        if quantidade == 0:
            total_pontos = sum(self._affinities.values())
            if total_pontos <= 0 and self._isekai_flag:
                self._current_scene = self._scenes["isekai_atropelamento"]
            else:
                self._current_scene = self._scenes["final_mr_white"]
        elif quantidade == 1:
            self._current_scene = self._scenes[f"final_namoro_{meninas_pontuadas[0]}"]
        else:
            cena_harem = self._scenes["final_harem_escolha"]
            cena_harem.choices.clear() 
            for menina in meninas_pontuadas:
                cena_harem.add_choice(f"Escolher {menina}", f"final_namoro_{menina}")
            if quantidade == 3:
                cena_harem.add_choice("Escolher TODAS (Harem Route)", "end_harem_king")
            self._current_scene = cena_harem
