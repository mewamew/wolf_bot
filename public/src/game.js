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
        const result = await this.game.gameData.getWolfWantKill();
        console.log("狼人投票结果：", result);
        const killedPlayer = result.wolf_want_kill;
        if (killedPlayer != -1) {
            console.log(`被杀死的玩家是：${killedPlayer} 号玩家`);
        } else {
            //无效投票，继续下一轮投票
            console.log("无效投票，继续下一轮投票");
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
            const result = await this.game.gameData.getWolfWantKill();
            console.log("狼人投票结果：", result);
            const killedPlayer = result.wolf_want_kill;
            if (killedPlayer != -1) {
                console.log(`被杀死的玩家是：${killedPlayer}`);
            } else {
                console.log("投票无效，今晚狼人不杀人");
            }
        }
    }
}

class WitchAction extends Action {
    constructor(game) {
        super(game);
    }

    async do() {
        const witch = this.game.get_witch();
        if (!witch.is_alive) {
            //女巫已经死了
            const result = await this.game.gameData.getWolfWantKill();
            const killedPlayer = result.wolf_want_kill;
            if (killedPlayer != -1) {
                await this.game.gameData.kill({ player_idx: killedPlayer });
                await this.someone_die(killedPlayer, "被狼人杀死");
            }
        } else {
            console.log("== 女巫开始行动 ==");
            const result = await this.game.gameData.decideCureOrPoison({ player_idx: witch.index });
            console.log(result);
            await this.game.ui.showPlayer(witch.index);
            let cureWho = "我决定今晚不治疗！"
            if (1 == result.cure) {
                cureWho = `我决定治疗玩家！`;
            }

            let poisonWho = "我决定今晚不毒杀！"
            if (-1 != result.poison) {
                poisonWho = `我决定毒杀【${result.poison}】 号玩家！`;
            }
            await this.game.ui.speak(`${witch.index}号玩家 女巫 思考中：`, result.thinking + cureWho + poisonWho);
            //根据女巫的决策结果进行操作
            if (1 != result.cure) {
                //不治疗，玩家死
                const result = await this.game.gameData.getWolfWantKill();
                const killedPlayer = result.wolf_want_kill;
                if (killedPlayer != -1) {
                    await this.game.gameData.kill({ player_idx: killedPlayer });
                    await this.game.someone_die(killedPlayer, "被狼人杀死");
                }
            }

            if (-1 != result.poison) {
                //不毒杀，玩家死
                await this.game.gameData.poison({ player_idx: result.poison });
                await this.game.someone_die(result.poison, "被女巫毒杀");
            }
        }
    }
}

class EndNightAction extends Action {
    constructor(game) {
        super(game);
    }
    async do() {
        console.log("=== 天亮了 ===");
        await this.game.gameData.toggleDayNight();
        //TODO 显示天亮
        //TODO 显示哪些玩家死亡
        //切换到白天的背景
        await this.game.ui.hidePlayer();
        await this.game.ui.hideSpeak();
        await this.game.ui.showDayBackground();
        //重置投票结果
        await this.game.gameData.resetVoteResult();
    }
}

class SpeakAction extends Action {
    constructor(game, player_idx) {
        super(game);
        this.player_idx = player_idx;
    }

    async do() {
        if (this.game.players[this.player_idx - 1].is_alive) {
            const result = await this.game.gameData.speak({ player_idx: this.player_idx });
            console.log(result);
            await this.game.ui.showPlayer(this.player_idx);
            await this.game.ui.speak(`${this.player_idx}号玩家 思考中：`, result.thinking);
            await this.game.ui.speak(`${this.player_idx}号玩家 发言：`, result.speak);
        }
    }
}

class VoteAction extends Action {
    constructor(game, player_idx) {
        super(game);    
        this.player_idx = player_idx;
    }

    async do() {
        if (this.game.players[this.player_idx - 1].is_alive) {
            const result = await this.game.gameData.vote({ player_idx: this.player_idx });
            console.log(result);
            await this.game.ui.showPlayer(this.player_idx);
            await this.game.ui.speak(`${this.player_idx}号玩家 思考中：`, result.thinking);
            const vote_id = result.vote;
            if (vote_id == -1) {
                await this.game.ui.speak(`${this.player_idx}号玩家 投票：`, "我决定不投票！");
            } else { 
                await this.game.ui.speak(`${this.player_idx}号玩家 投票：`, `我决定投票投给【${vote_id}】号玩家！`);
            } 
            ///更新投票结果
            const vote_result = await this.game.gameData.getVoteResult();
            console.log(vote_result);
            
            // 遍历投票结果字典并显示
            for (const [player_idx, votes] of Object.entries(vote_result.vote_result)) {
                await this.game.ui.showVote(player_idx, votes);
            }
        }
    }
}

class ExecuteAction extends Action {
    constructor(game) {
        super(game);
    }

    async do() {
        //处决接口
        const result = await this.game.gameData.execute();
        console.log(result);
        //TODO 显示处决结果

        ///玩家发表遗言
        if (-1 != result.executed_player) {
            await this.game.someone_die(result.executed_player, "被投票处决");
        }
    }
}

class CheckWinnerAction extends Action {
    constructor(game) {
        super(game);
    }

    async do() {
        //检查胜利
    }
}

class Game {
    constructor(ui) {
        this.gameData = new GameData();
        this.players = {}
        this.ui = ui;
        this.current_action_index  = 0;
    }
    async someone_die(player_idx, death_reason) {
        console.log(`被杀死的玩家是：${player_idx}`);
        await this.ui.killPlayer(player_idx);
        const result = await this.gameData.getCurrentTime();
        console.log(result);
        if (1 == result.current_day || result.current_phase == "夜晚") {
            //如果是第一夜，允许发表遗言
            const result = await this.gameData.lastWords({ player_idx: player_idx, death_reason: death_reason });
            console.log(result);
            await this.ui.showPlayer(player_idx);
            await this.ui.speak(`${player_idx}号玩家思考中：`, result.thinking);
            await this.ui.speak(`${player_idx}号玩家发言：`, result.speak);

            //如果是猎人，允许反击
            const  hunter = this.get_hunter();
            if (hunter.index == player_idx) {
                if (result.attack !== undefined && result.attack !== -1) {
                    await this.gameData.attack({ player_idx: player_idx, target_idx: result.attack });
                    console.log(`猎人发动反击，杀死了：${player_idx}号玩家`);
                } else {
                    console.log(`猎人决定不反击`);
                }
            }
        }
    }

    async start() {
        console.log("== Start Game ==");
        const result = await this.gameData.startGame();
        console.log(result.message);
        
        ///获取玩家列表
        const playersData = await this.gameData.getStatus();
        this.players = Object.values(playersData);
        console.log(this.players);

        ///按顺序设置行动类
        this.actions = []
        this.actions.push(new DivineAction(this));
        this.actions.push(new WolfAction(this));
        this.actions.push(new WitchAction(this));
        this.actions.push(new EndNightAction(this));
        for (const player of this.players) {
            this.actions.push(new SpeakAction(this, player.index));
        }
        for (const player of this.players) {
            this.actions.push(new VoteAction(this, player.index));
        }

        ///白天最后一个环节是处决投票
        this.actions.push(new ExecuteAction(this));
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

    get_witch() {
        return this.players.find(player => player.role_type === "女巫");
    }

    get_hunter() {
        return this.players.find(player => player.role_type === "猎人");
    }
}

export default Game;