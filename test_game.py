from game import WerewolfGame

def process_kill_votes(kill_votes):
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
    
    # 如果只有一个人得票最高，处决该玩家
    if len(candidates) == 1:
        killed_player = candidates[0]
    return killed_player


def get_players_info(players):
    print("玩家信息:")
    wolves = []
    witch = None
    seer  = None
    hunter = None
    for p in players.values():
        print(f"{p['index']}号玩家: {p['name']}, 角色: {p['role_type']}, 存活状态: {'存活' if p['is_alive'] else '死亡'}")
        if p['role_type'] == '狼人':
            wolves.append(p)
        elif p['role_type'] == '女巫':
            witch = p
        elif p['role_type'] == '预言家':
            seer = p
        elif p['role_type'] == '猎人':
            hunter = p

    print("狼人列表:")
    for wolf in wolves:
        print(f"{wolf['index']}号玩家: {'存活' if wolf['is_alive'] else '死亡'}")
        
    print(f"女巫信息：{witch['index']}号玩家: {'存活' if witch['is_alive'] else '死亡'}") if witch else print("女巫不存在")
    print(f"预言家信息：{seer['index']}号玩家: {'存活' if seer['is_alive'] else '死亡'}") if seer else print("预言家不存在")
    print(f"猎人信息：{hunter['index']}号玩家: {'存活' if hunter['is_alive'] else '死亡'}") if hunter else print("猎人不存在")
    return wolves, witch, seer, hunter

def night_phase(game):
    print("====================夜晚====================")
    # 夜晚阶段逻辑
    current_day = game.get_day()
    print(f"当前是第{current_day}天夜晚")
    players = game.get_players()
    wolves, witch, seer, hunter = get_players_info(players)
    
    #预言家预言
    if seer['is_alive']:
        game.divine(seer['index'])
        
    #狼人投票
    game.reset_wolf_want_kill()
    kill_votes=[]
    for wolf in wolves:
        if wolf['is_alive']:
            kill_votes.append(game.decide_kill(wolf['index']))
    killed_player = process_kill_votes(kill_votes)
    if killed_player != -1:
        print(f"第一轮投票结果: {killed_player} 号玩家被杀")
    else:
        print("投票无效，继续第二轮投票")
        for wolf in wolves:
            if wolf['is_alive']:
                kill_votes.append(game.decide_kill(wolf['index'], is_second_vote=True))
        killed_player = process_kill_votes(kill_votes)
        if killed_player != -1:
            print(f"第二轮投票结果: {killed_player} 号玩家被杀")
        else:
            print(f"第二轮投票结果: 平安夜")
    
    
    if witch['is_alive']:
        decision = game.decide_cure_or_poison(witch['index'], killed_player)
        if decision["cure"] == 0:
            if killed_player != -1:
                if current_day == 1:
                    #第一个晚上才允许发言
                    last_words = game.last_words(killed_player, "被狼人杀死")
                    if killed_player == hunter['index']:
                        print("猎人被杀死，发动反击")
                        if last_words["attack"] != -1:
                            game.attack(last_words["attack"])
                
                #女巫不救
                game.kill(killed_player)
        else:
            #女巫救人
            if killed_player != -1:
                game.cure(killed_player)
            

        if decision["poison"] != -1:
            if current_day == 1:
                #第一个晚上才允许发言
                last_words = game.last_words(decision["poison"], "被女巫毒死")
                if decision["poison"] == hunter['index']:
                    print("猎人被杀死，发动反击")
                    if last_words["attack"] != -1:
                        game.attack(last_words["attack"])
            game.poison(decision["poison"])
    else:
        #女巫不在
        if killed_player != -1:
            game.kill(killed_player)

    
def day_phase(game):
    # 天亮了...
    print("====================天亮了...====================")
    current_day = game.get_day()
    print(f"当前是第{current_day}天白天")
    
    players = game.get_players()
    wolves, witch, seer, hunter = get_players_info(players)
    
    #发言
    for player in players.values():
        if player['is_alive']:
            game.speak(player['index'])
    #投票
    for player in players.values():
        if player['is_alive']:
            game.vote(player['index'])
    
    vote_result = game.get_vote_result()
    print("投票结果：")
    print(vote_result)
    
    # 找出得票最多的玩家
    max_votes = max(vote_result.values())
    executed_players = [player for player, votes in vote_result.items() if votes == max_votes]

    # 如果只有一个人得票最高，处决该玩家
    if len(executed_players) == 1:
        executed_player = executed_players[0]
        # 让被处决玩家发表遗言
        last_words_result = game.last_words(executed_player, "被投票处决")
        # 处决玩家
        game.execute(executed_player)
        
        #如果被处决的玩家是猎人，判断是否要发动技能
        if "attack" in last_words_result:
            # 发动技能
            if last_words_result["attack"] != -1:
                game.attack(last_words_result["attack"])
    else:
        print("出现平票，本轮无人被处决")
        
if __name__ == "__main__":
    game = WerewolfGame()
    game.start()
    
    while True:
        #进入夜晚
        night_phase(game)
        result = game.check_winner()
        if result != "胜负未分":
            print(result)
            break
        game.toggle_day_night()
        
        day_phase(game)
        result = game.check_winner()
        if result != "胜负未分":
            print(result)
            break
        
        game.toggle_day_night()
    