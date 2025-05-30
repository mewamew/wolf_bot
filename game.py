from role import *
from history import *
from judge import *
import random
import json
import os
from datetime import datetime

#WerewolfGame负责保存游戏状态，游戏逻辑由前端脚本负责
class WerewolfGame:
    def __init__(self):
        self.players = [] 
        self.history = None # 存储游戏的历史记录
        self.current_day = 1
        self.current_phase = "夜晚" 
        self.vote_result = []
        self.wolf_want_kill = {}
        self.start_time = datetime.now().strftime("%Y%m%d%H%M")

        # 创建logs目录（如果不存在）
        if not os.path.exists('logs'):
            os.makedirs('logs')

    def dump_history(self):
        self.history.dump()

    def start(self):
        self.history = History()
        self.vote_result = []
        self.wolf_want_kill = {}
        self.current_day = 1  # 游戏开始时,设置为第1天
        self.current_phase = "夜晚"  # 初始化当前阶段为夜晚
        self.start_time = datetime.now().strftime("%Y%m%d%H%M")
        self.initialize_roles()
        display_config = {
            "display_role": True,
            "display_thinking": True,
            "display_witch_action": True,
            "display_wolf_action": True,
            "display_hunter_action": True,
            "display_divine_action": True,
            "display_vote_action": True,
            "display_model": True,
            "auto_play": True
        }
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            if "display_role" in config:
                display_config["display_role"] = config["display_role"]
            if "display_thinking" in config:
                display_config["display_thinking"] = config["display_thinking"]
            if "display_witch_action" in config:
                display_config["display_witch_action"] = config["display_witch_action"]
            if "display_wolf_action" in config:
                display_config["display_wolf_action"] = config["display_wolf_action"]
            if "display_hunter_action" in config:
                display_config["display_hunter_action"] = config["display_hunter_action"]
            if "display_divine_action" in config:
                display_config["display_divine_action"] = config["display_divine_action"]
            if "display_vote_action" in config:
                display_config["display_vote_action"] = config["display_vote_action"]
            if "auto_play" in config:
                display_config["auto_play"] = config["auto_play"]
            if "display_model" in config:
                display_config["display_model"] = config["display_model"]
        
        return display_config

        
    def initialize_roles(self):
        roles = [Wolf, Wolf, Wolf, Seer, Witch, Hunter, Villager, Villager, Villager]
        
        # 角色类映射
        role_classes = {
            '狼人': Wolf,
            '村民': Villager,
            '预言家': Seer,
            '女巫': Witch,
            '猎人': Hunter
        }

        # 读取配置文件决定每个玩家使用的模型
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 新增：模型分配逻辑
        if config.get("random_model") and config.get("models"):
            models = config["models"]
            n_models = len(models)
            n_players = len(config["players"])
            # 先确保每个模型至少分配一次
            assigned = [i for i in range(n_models)]
            # 多余玩家随机分配
            if n_players > n_models:
                import random
                assigned += random.choices(range(n_models), k=n_players - n_models)
            random.shuffle(assigned)
            assign_idx = 0
            for idx, player in enumerate(config["players"]):
                # 如果原本配置的是human则不分配模型
                if str(player.get("model_name", "")).lower() == "human":
                    player["model_name"] = "human"
                    player["api_key"] = ""
                else:
                    model = models[assigned[assign_idx]]
                    player["model_name"] = model["model_name"]
                    player["api_key"] = model["api_key"]
                    assign_idx += 1

        if config["randomize_roles"]:
            random.shuffle(roles)
        else:
            for i in range(len(roles)):
                role_str = config["players"][i].get("role")
                if not role_str:
                    raise ValueError(f"玩家 {i} 没有设置角色")
                role_class = role_classes.get(role_str.lower())
                if not role_class:
                    raise ValueError(f"无效的角色 '{role_str}' 对玩家 {i}")
                roles[i] = role_class
                
        # 使用配置文件中的模型和API key
        self.players = [
            role(i + 1, config["players"][i]["model_name"], config["players"][i]["api_key"], self) 
            for i, role in enumerate(roles)
        ]
        
        if config["randomize_position"]:
            print("随机排序玩家")
            random.shuffle(self.players)
            for i, player in enumerate(self.players):
                player.player_index = i + 1
        
        with open(f'logs/result_{self.start_time}.txt', 'a', encoding='utf-8') as log_file:
            for player in self.players:
                log_file.write(f"{player.player_index}号玩家的角色是{player.role_type}, 模型使用{player.model.model_name}\n")
                print(f"{player.player_index}号玩家的角色是{player.role_type}, 模型使用{player.model.model_name}")
            
        # 创建判决者
        self.judge = Judge(self, config["judge"]["model_name"], config["judge"]["api_key"])

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
                "name": f"{player.player_index}号玩家",
                "role_type": player.role_type,
                "is_alive": player.is_alive,
                "model": player.model.model_name,
                "is_human": True if player.model.model_name == "human" else False
            }
        return players
    
    def get_wolves(self):
        wolfs = []
        for player in self.players:
            if player.role_type == "狼人":
                wolfs.append({
                    "player_index": player.player_index,
                    "is_alive": player.is_alive
                })
        return wolfs
    
    def divine(self, player_idx):
        # 预言家揭示身份逻辑
        resp = self.players[player_idx-1].divine()
        return resp
    
    def decide_kill(self, player_idx, kill_id, is_second_vote=False):
        # 决定杀谁
        if is_second_vote:
            # 将字典转换为对象列表
            kill_list = [{"player_index": idx, "kill": info["kill"], "reason": info["reason"]} 
                        for idx, info in self.wolf_want_kill.items()]
            result = self.players[player_idx-1].decide_kill(kill_id, kill_list)
        else:
            result = self.players[player_idx-1].decide_kill(kill_id)
        
        self.wolf_want_kill[player_idx] = {
            "kill": result["kill"],
            "reason": result["reason"]
        }
        
        return result

    def get_wolf_want_kill(self):
        # 统计每个玩家获得的票数
        vote_count = {}
        for player_idx, info in self.wolf_want_kill.items():
            target = info.get('kill')  # 获取投票目标
            if target is not None:  # 确保有效投票
                if target in vote_count:
                    vote_count[target] += 1
                else:
                    vote_count[target] = 1
        
        if not vote_count:  # 如果没有有效投票
            print("没有有效投票")
            return -1
        
        # 找出最高票数
        max_votes = max(vote_count.values())
        
        # 找出获得最高票数的玩家
        candidates = [player for player, votes in vote_count.items() if votes == max_votes]
        
        # 如果只有一个人得票最高，处决该玩家
        if len(candidates) == 1:
            return candidates[0]

        print("多人投票一致")
        print(candidates)
        return -1
    
    def kill(self, player_idx):
        if player_idx == -1:
            raise ValueError("player_idx == -1")
        # 狼人杀人
        self.players[player_idx-1].be_killed()
        
    def decide_cure_or_poison(self, player_idx):
        someone_will_be_killed = self.get_wolf_want_kill()
        result = self.players[player_idx-1].decide_cure_or_poison(someone_will_be_killed)
        return result
    
    def poison(self, player_idx):
        self.players[player_idx-1].be_poisoned()
        
    def cure(self, player_idx):
        self.players[player_idx-1].be_cured()
        
    def speak(self, player_idx, content=None):            
        resp = self.players[player_idx-1].speak(content)
        return resp
    
    def vote(self, player_idx, vote_id) -> int:
        # 投票逻辑
        result = self.players[player_idx-1].vote(vote_id)
        vote_id = result["vote"]
        
        #记录投票结果
        self.vote_result.append({
                "player_idx": player_idx,
                "vote_id": vote_id
            })
        
        return result

    
    def reset_vote_result(self):
        self.vote_result = []
    
    def get_vote_result(self):
        return self.vote_result

    def last_words(self, player_idx, speak, death_reason):
        # 最后发言            
        resp = self.players[player_idx-1].last_words(speak, death_reason)
        return resp

    def revenge(self, player_idx, death_reason):
        resp = self.players[player_idx-1].revenge(death_reason)
        return resp
    
    def execute(self, player_idx, vote_result):
        # 处决玩家
        self.players[player_idx-1].be_executed(vote_result)

    def reset_wolf_want_kill(self):
        self.wolf_want_kill = {}

    
    def attack(self, player_idx):
        # 猎人攻击
        self.players[player_idx-1].be_attacked()
    
    def get_day(self):
        return self.current_day
    
    
    def check_winner(self) -> str:
        werewolf_count = sum(1 for player in self.players if player.role_type == '狼人' and player.is_alive)
        villager_count = sum(1 for player in self.players if player.role_type != '狼人' and player.is_alive)
        print("--- 检查胜负 ----")
        print(f"狼人数：{werewolf_count},村民数：{villager_count}")

        if werewolf_count > villager_count:
            with open(f'logs/result_{self.start_time}.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f"【{self.current_day} {self.current_phase}】 狼人胜利\n")
            return '狼人胜利'
        if werewolf_count == 0:
            with open(f'logs/result_{self.start_time}.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f"【{self.current_day} {self.current_phase}】 村民胜利\n")
            return '村民胜利'
        if villager_count > werewolf_count:
            return '胜负未分'
        return self.judge.decide()