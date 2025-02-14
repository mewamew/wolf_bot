import GameData from "./data.js";
import { sleep } from "./utils.js";

class Action {
    constructor(game) {
        this.game = game;
    }

    async do() {}
}

class DivineAction extends Action {
    constructor(game) {
        super(game);
    }
    async do() {
        /// divine
        const diviner = this.game.get_diviner();
        if (diviner.is_alive) {
            console.log("== 预言家开始预言 ==");

            const response = await this.game.gameData.divine({player_idx: diviner.index});
            await this.game.ui.showPlayer(diviner.index);
            await this.game.ui.speak(`${diviner.index}号玩家 预言家 思考中：`, response.thinking);
        }
    }
}

class WolfAction extends Action {
    constructor(game) {
        super(game);
    }
    processKillVote(kill_votes) {
        // 统计每个玩家获得的票数
        let killedPlayer = -1;
        const voteCount = {};
        
        for (const vote of kill_votes) {
            const target = vote.kill;  // 获取投票目标
            if (target !== undefined && target !== -1) {  // 确保有效投票
                voteCount[target] = (voteCount[target] || 0) + 1;
            }
        }
        
        if (Object.keys(voteCount).length === 0) {  // 如果没有有效投票
            return -1;
        }
        
        // 找出最高票数
        const maxVotes = Math.max(...Object.values(voteCount));
        
        // 找出获得最高票数的玩家
        const candidates = Object.entries(voteCount)
            .filter(([_, votes]) => votes === maxVotes)
            .map(([player, _]) => parseInt(player));
        
        // 如果只有一个人得票最高，返回该玩家
        if (candidates.length === 1) {
            killedPlayer = candidates[0];
        }
        
        return killedPlayer;
    }
    
    async do() {
        console.log("== 狼人开始行动 ==");
        //重置投票
        await this.game.gameData.resetWolfWantKill();
        const wolves = this.game.get_wolves();
        /// 第一轮投票
        for (const wolf of wolves) {
            if (wolf.is_alive) {
                const response = await this.game.gameData.decideKill({ player_idx: wolf.index,is_second_vote: false });
                console.log(response);
                await this.game.ui.showPlayer(wolf.index);
                let killWho = "我决定今晚不杀人！"
                if (-1 !== response.kill) {
                    killWho = `我决定杀掉【${response.kill}】 号玩家!`;
                }
                await this.game.ui.speak(`${wolf.index}号玩家 狼人 思考中：`, response.reason+killWho);
            }
        }

        /// 获取投票结果
        const votes = await this.game.gameData.getWolfWantKill();
        console.log("狼人投票结果：", votes);
        const killedPlayer = this.processKillVote(votes.wolf_want_kill);
        console.log(`被杀死的玩家是：${killedPlayer}`);
        if (killedPlayer == -1) {
            //无效投票，继续下一轮投票
            for (const wolf of wolves) {
                if (wolf.is_alive) {
                    const response = await this.game.gameData.decideKill({ player_idx: wolf.index,is_second_vote: true });
                    console.log(response);
                    await this.game.ui.showPlayer(wolf.index);
                    let killWho = "我决定今晚不杀人！"
                    if (-1 !== response.kill) {
                        killWho = `我决定杀掉【${response.kill}】 号玩家!`;
                    }
                    await this.game.ui.speak(`${wolf.index}号玩家 狼人 思考中：`, response.reason+killWho);
                }
            }
            /// 获取投票结果
            const votes = await this.game.gameData.getWolfWantKill();
            console.log("狼人投票结果：", votes);
            const killedPlayer = this.processKillVote(votes.wolf_want_kill);
            console.log(`被杀死的玩家是：${killedPlayer}`);
            
        } else {
            //有有效投票，杀死指定玩家

        }
    }
}

class Game {
    constructor(ui) {
        this.gameData = new GameData();
        this.players = {}
        this.ui = ui;
        this.current_action_index  = 0;
    }

    async start() {
        console.log("== Start Game ==");
        const result = await this.gameData.startGame();
        console.log(result.message);
        
        ///设置行动类
        this.actions = []
        this.actions.push(new DivineAction(this));
        this.actions.push(new WolfAction(this));
    }



    async run() {
        //更新玩家状态
        const playersData = await this.gameData.getStatus();
        this.players = Object.values(playersData);
        
        if (this.current_action_index < this.actions.length) {
            const action = this.actions[this.current_action_index++];
            await action.do();
        } else {
            console.log("没事干了")
        }
        await sleep(1000);
    }

    get_diviner() {
        return this.players.find(player => player.role_type === "预言家");
    }

    get_wolves() {
        return this.players.filter(player => player.role_type === "狼人");
    }
}

export default Game;