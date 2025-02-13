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
        self.vote_result = {}
        self.wolf_want_kill = {}
        self.start_time = datetime.now().strftime("%Y%m%d%H%M")

        # 创建logs目录（如果不存在）
        if not os.path.exists('logs'):
            os.makedirs('logs')

    def dump_history(self):
        self.history.dump()

    def start(self):
        self.history = History()
        self.vote_result = {}
        self.wolf_want_kill = {}
        self.current_day = 1  # 游戏开始时,设置为第1天
        self.current_phase = "夜晚"  # 初始化当前阶段为夜晚
        self.initialize_roles()

        
    def initialize_roles(self):
        # 随机初始化玩家列表
        roles = [Wolf, Wolf, Wolf, Seer, Witch, Hunter, Villager, Villager, Villager]
        
        # 角色类映射
        role_classes = {
            '狼人': Wolf,
            '村民': Villager,
            '预言者': Seer,
            '女巫': Witch,
            '猎人': Hunter
        }

        # 读取配置文件决定每个玩家使用的模型
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
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
        
        # 记录角色初始化信息到日志
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write("=== 游戏角色初始化 ===\n")
            for i, player in enumerate(self.players):
                f.write(f"{i+1}号玩家 - 角色：{player.role_type}，使用模型：{config['players'][i]['model_name']}\n")
            f.write("==================\n")
        
        # 创建判决者
        self.judge = Judge(self, config["judge"]["model_name"], config["judge"]["api_key"])

    def toggle_day_night(self):
        self.history.toggle_day_night()
        if self.current_phase == "白天":
            self.current_phase = "夜晚"
            with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
                f.write(f"=== 第{self.current_day}天夜晚 ===\n")
        else:
            self.current_phase = "白天"
            self.current_day += 1  # 每当从夜晚切换到白天时,天数加1
            with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
                f.write(f"=== 第{self.current_day}天白天===\n")
        
    def get_players(self):
        players = {}
        for player in self.players:
            players[player.player_index] = {
                "index": player.player_index,
                "name": f"{player.player_index}号玩家",
                "role_type": player.role_type,
                "is_alive": player.is_alive,
                "model": player.model.model_name
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
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write(f"[预言家查验]\n")
        resp = self.players[player_idx-1].divine()
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            if "thinking" in resp:
                f.write(f"思考过程：{resp['thinking']}\n")
            role_type = self.players[resp['divine']-1].role_type
            f.write(f"查验了{resp['divine']}号玩家，身份是：{role_type}\n")
        return resp
    
    def decide_kill(self, player_idx, is_second_vote=False):
        # 决定杀谁
        if is_second_vote:
            # 将字典转换为对象列表
            kill_list = [{"player_index": idx, "kill": info["kill"], "reason": info["reason"]} 
                        for idx, info in self.wolf_want_kill.items()]
            result = self.players[player_idx-1].decide_kill(kill_list)
        else:
            result = self.players[player_idx-1].decide_kill()
            self.wolf_want_kill[player_idx] = {
                "kill": result["kill"],
                "reason": result["reason"]
            }
        
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write(f"[狼人{player_idx}号决定杀人]\n")
            if "thinking" in result:
                f.write(f"思考过程：{result['thinking']}\n")
            f.write(f"决定杀死{result['kill']}号玩家\n")
        return result
    
    def kill(self, player_idx):
        # 狼人杀人
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write(f"[狼人杀人] {player_idx}号玩家被狼人杀死\n")
        self.players[player_idx-1].be_killed()
        
    def decide_cure_or_poison(self, player_idx, someone_will_be_killed):
        return self.players[player_idx-1].decide_cure_or_poison(someone_will_be_killed)
    
    def poison(self, player_idx):
        self.players[player_idx-1].be_poisoned()
        
    
    ###########################################################################
    def speak(self, player_idx):
        # TODO增加一个log类吧！
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write(f"[{player_idx}号玩家【{self.players[player_idx-1].role_type}】发言]\n")
        resp = self.players[player_idx-1].speak()
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            if "thinking" in resp:
                f.write(f"=== 发言前思考===\n{resp['thinking']} \n=== 发言内容===\n")
            f.write(f"{resp['speak']}\n")
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
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            if "thinking" in result:
                f.write(f"=== [{player_idx}号玩家({self.players[player_idx-1].role_type})的思考过程]===\n{result['thinking']}\n")
            f.write(f"[{player_idx}号玩家投票] 投给了{vote_id}号玩家 (当前{vote_id}号玩家已获得{self.vote_result[vote_id]}票)\n")
        return result
    
    def reset_vote_result(self):
        self.vote_result = {}
    
    def get_vote_result(self):
        return self.vote_result


    def last_words(self, player_idx, death_reason):
        # 最后发言
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write(f"[{player_idx}号玩家遗言] 死亡原因：{death_reason}\n")
        resp = self.players[player_idx-1].last_words(death_reason)
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            if "thinking" in resp:
                f.write(f"思考过程：{resp['thinking']}\n")
            f.write(f"{resp['speak']}\n")
        return resp
    
    def execute(self, player_idx):
        # 处决玩家
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write(f"[处决] {player_idx}号玩家被处决\n")
        self.players[player_idx-1].be_executed()

    def attack(self, player_idx):
        # 猎人攻击
        with open(f"logs/log_{self.start_time}.txt", "a", encoding="utf-8") as f:
            f.write(f"[猎人攻击] {player_idx}号玩家被猎人攻击\n")
        self.players[player_idx-1].be_attacked()
        
    def reset_wolf_want_kill(self):
        self.wolf_want_kill = []
        
    def get_wolf_want_kill(self):
        return self.wolf_want_kill

    
    def get_day(self):
        return self.current_day
    

    
    def check_winner(self) -> str:
        return self.judge.decide()
    
    def process_kill_votes(self, kill_votes):
        # 统计每个玩家获得的票数
        killed_player = -1
        vote_count = {}
        for vote in kill_votes:
            target = vote.get('kill')  # 获取投票目标
            if target is not None:  # 确保有效投票
                if target in vote_count:
                    vote_count[target] += 1
                else:
                    vote_count[target] = 1
        
        if not vote_count:  # 如果没有有效投票
            return -1
        
        # 找出最高票数
        max_votes = max(vote_count.values())
        
        # 找出获得最高票数的玩家
        candidates = [player for player, votes in vote_count.items() if votes == max_votes]
        
        # 如果只有一个最高票，直接返回；如果有平票，随机选择一个
        if len(candidates) == 1:
            killed_player = candidates[0]
        return killed_player


if __name__ == "__main__":
    game = WerewolfGame()
    game.start()
   
    #player = game.get_players()
    #print(player)
    
    #测试第一晚
    game.divine(5) #预言家查验
    kill_votes=[]
    kill_votes.append(game.decide_kill(1)) #狼人决定杀人
    kill_votes.append(game.decide_kill(8)) #狼人决定杀人
    kill_votes.append(game.decide_kill(9)) #狼人决定杀人
    
    killed_player = game.process_kill_votes(kill_votes)
    if killed_player != -1:
        print(f"第一轮投票结果: {killed_player} 号玩家被杀")
    else:
        print("投票无效，继续第二轮投票")
        kill_votes.append(game.decide_kill(1)) #狼人决定杀人
        kill_votes.append(game.decide_kill(8)) #狼人决定杀人
        kill_votes.append(game.decide_kill(9)) #狼人决定杀人
        killed_player = game.process_kill_votes(kill_votes)
        print(f"第二轮投票结果: {killed_player} 号玩家被杀")
    
    decision = game.decide_cure_or_poison(6, killed_player)
    if decision["cure"] == 0:
        game.kill(killed_player)
    
    if decision["poison"] != -1:
        game.poison(decision["poison"])
        
    
    
