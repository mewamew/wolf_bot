from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from game import WerewolfGame
import json
import sys
import copy


class PlayerAction(BaseModel):
    player_idx:int

class SpeakAction(BaseModel):
    player_idx: int
    content: str = None

class VoteAction(BaseModel):
    player_idx: int
    vote_id: int = -100

class LastWordsAction(BaseModel):
    player_idx: int
    speak: str = None
    death_reason: str
    
class AttackAction(BaseModel):
    player_idx: int
    target_idx: int
    
class DecideKillAction(BaseModel):
    player_idx: int
    kill_id: int = -100
    is_second_vote: bool
    
class DecideCureOrPoisonAction(BaseModel):
    player_idx: int

class PoisonAction(BaseModel):
    player_idx: int

class RevengeAction(BaseModel):
    player_idx: int
    death_reason: str
    

class Recorder():
    def __init__(self, game):
        self.log = []
        self.is_loaded = False
        self.index  = 0
    
    def record(self, response):
        self.log.append(
            {
                "response": copy.deepcopy(response)
            }
        )

        with open(f"logs/replay_{game.start_time}.json", 'w') as f:
            json.dump(self.log, f)

    def load(self, filename):
        print("加载日志文件")
        with open(filename, 'r') as f:
            self.log = json.load(f)
            self.is_loaded = True

    def fetch(self):
        result = self.log[self.index]
        self.index += 1
        return result["response"]


game = WerewolfGame()
recorder = Recorder(game)

app = FastAPI()
# 设置静态文件目录
app.mount("/static", StaticFiles(directory="public"), name="public")

@app.get("/")
def default():
    return RedirectResponse(url="/static/index.html")

@app.get("/start")
def start_game():
    if recorder.is_loaded:
        display_config = recorder.fetch()
        display_config["auto_play"] = False
        display_config["display_role"] = True
        display_config["display_thinking"] = True
        display_config["display_vote_action"] = True
        display_config["display_divine_action"] = True
        display_config["display_witch_action"] = True
        display_config["display_wolf_action"] = True
        display_config["display_hunter_action"] = True
        display_config["display_model"] = True
        return display_config

    display_config = game.start()
    recorder.record(display_config)
    return display_config

@app.get("/status")
def get_status():
    if recorder.is_loaded:
        return recorder.fetch()
    players = game.get_players()
    recorder.record(players)
    return players

@app.post("/divine")
def divine(action: PlayerAction):
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.divine(action.player_idx)
    recorder.record(result)
    return result


@app.post("/reset_wolf_want_kill")
def reset_wolf_want_kill():
    if recorder.is_loaded:
        return recorder.fetch()
    game.reset_wolf_want_kill()
    recorder.record({"message": "狼人想杀的目标已重置"})
    return {"message": "狼人想杀的目标已重置"}

@app.get("/get_wolf_want_kill")
def get_wolf_want_kill():
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.get_wolf_want_kill()
    wolf_want_kill = {"wolf_want_kill": result}
    recorder.record(wolf_want_kill)
    return wolf_want_kill


@app.post("/decide_kill")
def decide_kill(action: DecideKillAction):
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.decide_kill(action.player_idx, action.kill_id, action.is_second_vote)
    recorder.record(result)
    return result

@app.post("/kill")
def kill(action: PlayerAction):
    if recorder.is_loaded:
        return recorder.fetch()
    game.kill(action.player_idx)
    recorder.record({"message": f"玩家 {action.player_idx} 被杀死"})
    return {"message": f"玩家 {action.player_idx} 被杀死"}
    
@app.get("/current_time")
def get_current_time():
    if recorder.is_loaded:
        return recorder.fetch()

    current_time = {
        "current_day": game.get_day(),
        "current_phase": game.current_phase
    }
    recorder.record(current_time)
    return current_time
    

@app.post("/last_words")
def last_words(action: LastWordsAction):
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.last_words(action.player_idx, action.speak, action.death_reason)
    recorder.record(result)
    return result


@app.post("/attack")
def attack(action: AttackAction):
    if recorder.is_loaded:
        return recorder.fetch()
    attack_result = game.attack(action.target_idx)
    players = game.get_players()
    result = {
        "message": f"{players[action.player_idx]['name']} 攻击了 {players[action.target_idx]['name']}",
        "attacked_player": action.target_idx
    }
    recorder.record(result)
    return result

@app.post("/toggle_day_night")
def toggle_day_night():
    if recorder.is_loaded:
        return recorder.fetch()
    game.toggle_day_night()
    recorder.record({"message": "Day/Night toggled"})
    return {"message": "Day/Night toggled"}



@app.post("/decide_cure_or_poison")
def decide_cure_or_poison(action: DecideCureOrPoisonAction):
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.decide_cure_or_poison(action.player_idx)
    recorder.record(result)
    return result


@app.post("/poison")
def poison(action: PoisonAction):
    if recorder.is_loaded:
        return recorder.fetch()
    game.poison(action.player_idx)
    recorder.record({"message": f"玩家 {action.player_idx} 被毒死"})
    return {"message": f"玩家 {action.player_idx} 被毒死"}

@app.post("/cure")
def cure(action: PlayerAction):
    if recorder.is_loaded:
        return recorder.fetch()
    game.cure(action.player_idx)
    recorder.record({"message": "治疗成功"})
    return {"message": "治疗成功"}

@app.post("/speak")
def speak(action: SpeakAction):
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.speak(action.player_idx, action.content)
    recorder.record(result)
    return result


@app.post("/vote")
def vote(action: VoteAction):
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.vote(action.player_idx, action.vote_id)
    recorder.record(result)
    return result

@app.post("/reset_vote_result")
def reset_vote_result():
    if recorder.is_loaded:
        return recorder.fetch()
    game.reset_vote_result()
    recorder.record({"message": "投票结果已重置"})
    return {"message": "投票结果已重置"}

@app.get("/get_vote_result")
def get_vote_result():
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.get_vote_result()
    recorder.record({"vote_result": result})
    return {"vote_result": result}

@app.post("/revenge")
def revenge(action: RevengeAction):
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.revenge(action.player_idx, action.death_reason)
    recorder.record(result)
    return result

@app.post("/execute")
def execute():
    if recorder.is_loaded:
        return recorder.fetch()
    players = game.get_players()
    vote_results = game.get_vote_result()

    if not vote_results:
        recorder.record({"message": "没有投票结果", "executed_player": -1})
        return {
            "message": "没有投票结果",
            "executed_player": -1
        }

    # 统计每个玩家获得的票数
    votes = {}
    for vote in vote_results:
        if vote["vote_id"] != -1:  # 排除弃票
            votes[vote["vote_id"]] = votes.get(vote["vote_id"], 0) + 1

    if not votes:  # 如果所有人都弃票
        return {
            "message": "所有人都弃票了",
            "executed_player": -1
        }

    max_votes = max(votes.values())
    voted_out = [player for player, count in votes.items() if count == max_votes]
    
    if len(voted_out) > 1:
        return {
            "message": "投票结果有多个，没人被处决",
            "executed_player": -1
        }
    else:
        voted_out_player = voted_out[0]
        game.execute(voted_out_player, vote_results)
        recorder.record({"message": f"{players[voted_out_player]['name']} 被处决!", "executed_player": voted_out_player})
        return {
            "message": f"{players[voted_out_player]['name']} 被处决!",
            "executed_player": voted_out_player
        }

@app.get("/check_winner")
def check_winner():
    if recorder.is_loaded:
        return recorder.fetch()
    result = game.check_winner()
    recorder.record({"winner": result})
    return {"winner": result}




if __name__ == "__main__":
    import uvicorn
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
        recorder.load(log_path)


    uvicorn.run(app, host="127.0.0.1", port=8000, timeout_keep_alive=1800)