from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from game import WerewolfGame

app = FastAPI()
game = WerewolfGame()

class PlayerAction(BaseModel):
    player_idx:int

class LastWordsAction(BaseModel):
    player_idx: int
    death_reason: str
    
class AttackAction(BaseModel):
    player_idx: int
    target_idx: int
    
class DecideKillAction(BaseModel):
    player_idx: int
    is_second_vote: bool
    
class DecideCureOrPoisonAction(BaseModel):
    player_idx: int


class PoisonAction(BaseModel):
    player_idx: int
    
# 设置静态文件目录
app.mount("/static", StaticFiles(directory="public"), name="public")

@app.get("/")
def default():
    return RedirectResponse(url="/static/index.html")

@app.get("/start")
def start_game():
    game.start()
    return {"message": "Game started"}

@app.get("/status")
def get_status():
    players = game.get_players()
    return players

@app.post("/divine")
def divine(action: PlayerAction):
    result = game.divine(action.player_idx)
    return result


@app.post("/reset_wolf_want_kill")
def reset_wolf_want_kill():
    game.reset_wolf_want_kill()
    return {"message": "狼人想杀的目标已重置"}

@app.get("/get_wolf_want_kill")
def get_wolf_want_kill():
    result = game.get_wolf_want_kill()
    return {"wolf_want_kill": result}


@app.post("/decide_kill")
def decide_kill(action: DecideKillAction):
    result = game.decide_kill(action.player_idx, action.is_second_vote)
    return result

@app.post("/kill")
def kill(action: PlayerAction):
    game.kill(action.player_idx)
    return {"message": f"玩家 {action.player_idx} 被杀死"}
    
@app.get("/current_time")
def get_current_time():
    return {
        "current_day": game.get_day(),
        "current_phase": game.current_phase
    }

@app.post("/last_words")
def last_words(action: LastWordsAction):
    result = game.last_words(action.player_idx, action.death_reason)
    return result


@app.post("/attack")
def attack(action: AttackAction):
    result = game.attack(action.target_idx)
    players = game.get_players()
    return {
        "message": f"{players[action.player_idx]['name']} 攻击了 {players[action.target_idx]['name']}",
        "attacked_player": action.target_idx
    }

@app.post("/toggle_day_night")
def toggle_day_night():
    game.toggle_day_night()
    return {"message": "Day/Night toggled"}



@app.post("/decide_cure_or_poison")
def decide_cure_or_poison(action: DecideCureOrPoisonAction):
    result = game.decide_cure_or_poison(action.player_idx)
    return result


@app.post("/poison")
def poison(action: PoisonAction):
    game.poison(action.player_idx)
    return {"message": f"玩家 {action.player_idx} 被毒死"}

@app.post("/cure")
def cure(action: PlayerAction):
    game.cure(action.player_idx)
    return {"message": "治疗成功"}

@app.post("/speak")
def speak(action: PlayerAction):
    result = game.speak(action.player_idx)
    return result


@app.post("/vote")
def vote(action: PlayerAction):
    result = game.vote(action.player_idx)
    return result

@app.post("/reset_vote_result")
def reset_vote_result():
    game.reset_vote_result()
    return {"message": "投票结果已重置"}

@app.get("/get_vote_result")
def get_vote_result():
    result = game.get_vote_result()
    return {"vote_result": result}

@app.post("/execute")
def execute():
    players = game.get_players()
    votes = game.get_vote_result()

    max_votes = max(votes.values())
    voted_out = [player for player, count in votes.items() if count == max_votes]
    
    if len(voted_out) > 1:
        return {
            "message": "投票结果有多个，没人被处决",
            "executed_player": -1
        }
    else:
        voted_out_player = voted_out[0]
        game.execute(voted_out_player)
        return {
            "message": f"{players[voted_out_player]['name']} 被处决!",
            "executed_player": voted_out_player
        }

@app.get("/check_winner")
def check_winner():
    result = game.check_winner()
    return {"winner": result}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)