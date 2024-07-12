from role import *
from history import *
import random
import json


class WerewolfGame:
    def __init__(self):
        self.players = [] 
        self.history = None # 存储游戏的历史记录
        self.current_day = 1
        self.current_phase = "白天" 
        self.vote_result = {}
        self.wolf_want_kill = []

    def dump_history(self):
        self.history.dump()

    def start(self):
        self.history = History()
        self.vote_result = {}
        self.wolf_want_kill = []
        self.current_day = 1  # 游戏开始时,设置为第1天
        self.current_phase = "白天"  # 初始化当前阶段为白天
        self.initialize_roles()
        
    def initialize_roles(self):
        # 随机初始化玩家列表
        roles = [Wolf, Villager, Wolf, Seer, Witch, Hunter]
        styles = [
            "高冷智慧型：语调冷静理性",
            "热情幽默型：活泼开朗，常用幽默的方式表达观点，喜欢调侃",
            "神经质型：言辞跳跃,常常让人摸不着头脑",
            "直接果断型：说话简洁直白，毫不犹豫地表达自己的立场和观点",
            "冷嘲热讽型：言辞尖锐，喜欢用讽刺的方式表达观点，常常让人无言以对",
            "挑衅激进型：喜欢挑衅和制造冲突，言辞激烈，常激怒其他玩家"
        ]
        random.shuffle(roles)
        random.shuffle(styles)
        
        # 读取配置文件决定每个玩家使用的模型
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 使用配置文件中的模型和API key
        self.players = [
            role(i + 1, config["models"][i]["name"], config["models"][i]["api_key"], styles[i], self) 
            for i, role in enumerate(roles)
        ]

    def toggle_day_night(self):
        self.history.toggle_day_night()
        if self.current_phase == "白天":
            self.current_phase = "夜晚"
        else:
            self.current_phase = "白天"
            self.current_day += 1  # 每当从夜晚切换到白天时,天数加1
        
    def get_players(self):
        players = {}
        for player in self.players:
            players[player.player_index] = {
                "index": player.player_index,
                "name": f"{player.player_index}号玩家[{player.role_type}@{player.model.model_name}]",
                "role_type": player.role_type,
                "is_alive": player.is_alive,
                "model": player.model.model_name
            }
        return players
    

    def speak(self, player_idx):
        resp = self.players[player_idx-1].speak()
        return resp
    
    def vote(self, player_idx) -> int:
        # 投票逻辑
        result = self.players[player_idx-1].vote()
        vote_id = result["vote"]
        if vote_id in self.vote_result:
            self.vote_result[vote_id] += 1
        else:
            self.vote_result[vote_id] = 1
        
        result["vote_count"] = self.vote_result[vote_id]
        return result
    
    def reset_vote_result(self):
        self.vote_result = {}
    
    def get_vote_result(self):
        return self.vote_result


    def last_words(self, player_idx, death_reason):
        # 最后发言
        resp = self.players[player_idx-1].last_words(death_reason)
        return resp
    
    def execute(self, player_idx):
        # 处决玩家
        self.players[player_idx-1].be_executed()

    def attack(self, player_idx):
        # 猎人攻击
        self.players[player_idx-1].be_attacked()
        
    def divine(self, player_idx):
        # 预言家揭示身份逻辑
        resp = self.players[player_idx-1].divine()
        return resp
    
    def reset_wolf_want_kill(self):
        self.wolf_want_kill = []
        
    def get_wolf_want_kill(self):
        return self.wolf_want_kill

    def decide_kill(self, player_idx, other_wolf_want_kill=-1):
        # 决定杀谁
        result = self.players[player_idx-1].decide_kill(other_wolf_want_kill)
        self.wolf_want_kill.append(result["kill"])
        return result

    def kill(self, player_idx):
        # 狼人杀人
        self.players[player_idx-1].be_killed()

    def get_day(self):
        return self.current_day
    
    def cure(self, player_idx, someone_will_be_killed):
        return self.players[player_idx-1].cure(someone_will_be_killed)

    def decide_poison(self, player_idx, someone_will_be_killed) -> int:
        return self.players[player_idx-1].poison(someone_will_be_killed)

    def poison(self, player_idx):
        self.players[player_idx-1].be_poisoned()
    
    def check_winner(self) -> str:
        n_wolf_alive = 0
        n_villager_alive = 0
        n_total_alive = 0
        hunter = None
        witch = None
        for player in self.players:
            if player.is_alive:
                n_total_alive += 1
                if player.role_type == "狼人":
                    n_wolf_alive += 1
                else:
                    n_villager_alive += 1
                if player.role_type == "猎人":
                    hunter = player
                if player.role_type == "女巫":
                    witch = player

        if n_wolf_alive == 0:
            return "村民胜利"

        if n_wolf_alive>n_villager_alive:
            return "狼人胜利"
        
        if n_villager_alive == 1:
            #到了这个分支，狼人一定是剩下一个了
            #如果猎人被杀可以反击杀死狼人
            #女巫可以使用毒药毒死狼人
            #这两种情况都会杀光狼人，达成好人胜利
            if hunter or (witch and witch.cured_someone == -1): #女巫的毒药技能还没用过
                return "村民胜利"
            else:
                return "狼人胜利"

        if n_villager_alive == 2:
            #猎人死了和女巫也失效了（包括死掉）
            #这种情况下要分时间，如果是白天，狼人胜利，因为到了晚上可以杀掉一个村民
            #或者这种情况下还有两个狼人，狼人也胜利
            if not hunter and not (witch and witch.poisoned_someone == -1):
                if n_wolf_alive == 2:
                    return "狼人胜利"
                if self.current_phase == "白天":
                    return "狼人胜利"

        return "胜负未分"
        
    