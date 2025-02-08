import Background from "./background.js";
import GameData from "./data.js";
import Player from "./player.js";

class Game {
    constructor(app) {
        this.background = new Background(app);
        this.gameData = new GameData();
        this.players = {}
        this.app = app;
    }

    async start() {
        console.log("== Start Game ==");
        const result = await this.gameData.startGame();
        console.log(result.message);
        const playersData = await this.gameData.getStatus();
        const players = Object.values(playersData);
        for (const player of players) {
            this.players[player.index] = new Player(this, player.name, player.index, player.role_type);
        }
    }

    async dayPhase() {
        console.log("== Day Phase ==");
        const timeInfo = await this.gameData.getCurrentTime();
        await this.background.showDayBackground(timeInfo.current_day);
        await this.updatePlayerState();
        await this.speak();

        if (timeInfo.current_day === 1) {
            console.log("第一天，跳过投票处决环节");
            return;
        }
        await this.vote();
    }

    async updatePlayerState() {
        console.log("== Update Player State ==");
        const players = await this.gameData.getStatus();
        console.log(players);
    }

    async speak() {
        console.log("== Speak ==");
        const playersData = await this.gameData.getStatus();
        const players = Object.values(playersData);
        for (const player of players) {
            if (player.is_alive) {
                const result = await this.gameData.speak({ player_idx: player.index });
                await this.players[player.index].think(result.thinking);
                await this.players[player.index].speak(result.speak, '0xffffff', false);
            }
        }
    }

    async vote() {
        console.log("== Vote ==");
        // 重置投票结果
        await this.gameData.resetVoteResult();

        const playersData = await this.gameData.getStatus();
        const players = Object.values(playersData);
        for (const player of players) {
            if (player.is_alive) {
                const result = await this.gameData.vote({ player_idx: player.index });
                await this.players[player.index].think(result.thinking);
                await this.players[player.index].speak(`我投票处决: ${result.vote}号玩家`, '0xffffff');
                this.players[result.vote].showVoteCount(result.vote_count, false); // 更新投票数，不隐藏
            }
        }

        const voteResult = await this.gameData.getVoteResult();
        let voteResultText = "投票结果:\n";
        console.log("投票结果:");
        for (const [voteId, voteCount] of Object.entries(voteResult.vote_result)) {
            console.log(`${voteId} 号玩家被投票: ${voteCount} 票`);
            voteResultText += `${voteId} 号玩家被投票: ${voteCount} 票\n`;
            await this.players[voteId].showVoteCount(voteCount); // 显示投票数并隐藏
        }
        await this.background.showResultInfo(voteResultText);

        const result = await this.gameData.execute();1
        if (result.executed_player !== undefined) {
            const executeStr = `${playersData[result.executed_player].name} 被投票处决`;
            console.log(executeStr);
            await this.background.showResultInfo(executeStr);
            await this.lastWords(result.executed_player, "被投票处决");
        }
    }

    async lastWords(player_idx, death_reason) {
        console.log(`${player_idx}号玩家的死亡原因: ${death_reason}`);

        const result = await this.gameData.lastWords({ player_idx, death_reason });
        await this.players[player_idx].think(result.thinking);
        await this.players[player_idx].lastword(result.speak);
        console.log(`--- lastWords: ${result} ---`);
        if (result.attack !== undefined && result.attack !== -1) {
            await this.attack(player_idx, result.attack); 
        }
    }

    async attack(player_idx, target_idx) {
        console.log("== Attack ==");
        const action = { player_idx, target_idx };
        const result = await this.gameData.attack(action);
        console.log(`${result.message}`);
        await this.background.showResultInfo(result.message);
        await this.lastWords(target_idx, "被猎人反击杀死");
    }

    async checkWinner() {
        console.log("== Check Winner ==");
        const result = await this.gameData.checkWinner();
        console.log(result.winner);
        return result.winner
    }

    async toggleDayNight() {
        console.log("== Toggle Day Night ==");
        await this.gameData.toggleDayNight();
    }

    async nightPhase() {
        console.log("== Night Phase ==");
        await this.background.showNightBackground();
        await this.divine();
        await this.decideKill();
        await this.kill();
    }

    async getPlayerByRole(role_type) {
        const playersData = await this.gameData.getStatus();
        return Object.values(playersData).filter(player => player.role_type === role_type && player.is_alive);
    }

    async divine() {
        console.log("== Divine ==");
        const playersData = await this.gameData.getStatus();
        const seers = await this.getPlayerByRole("预言家");

        if (seers.length === 0) {
            console.log("== 预言家已经死了，跳过预言环节 ==");
            return;
        }

        console.log("== 预言家开始预言 ==");
        const playerSeerIndex = seers[0].index;
        const divineResult = await this.gameData.divine({ player_idx: playerSeerIndex });

        if (divineResult.thinking) {
            await this.players[playerSeerIndex].think(divineResult.thinking);
        }
        if (divineResult.divine) {
            const divineStr = `预言家揭示 ${playersData[divineResult.divine].name} 的身份`;
            console.log(divineStr);
            await this.background.showResultInfo(divineStr);
        }
    }

    async decideKill() {
        console.log("== 狼人开始物色要杀的人 ==");
        const playersData = await this.gameData.getStatus();
        const playerWolves = Object.values(playersData).filter(player => player.role_type === "狼人" && player.is_alive);

        await this.gameData.resetWolfWantKill();

        const wolfDecide = async (wolfIndex, previousKill = -1) => {
            const result = await this.gameData.decideKill({ player_idx: wolfIndex, other_wolf_want_kill: previousKill });
            if (result.thinking) {
                console.log(`${playersData[wolfIndex].name} 思考：${result.thinking}`);
                await this.players[wolfIndex].think(result.thinking);
            }
            console.log(`${playersData[wolfIndex].name} 决定要杀的人 ${playersData[result.kill].name}`);
            await this.players[wolfIndex].speak(`我决定要杀的人是 ${playersData[result.kill].name}`, '0xff0000');
            return result.kill;
        };

        if (playerWolves.length === 1) {
            await wolfDecide(playerWolves[0].index);
            return;
        }

        const firstKill = await wolfDecide(playerWolves[0].index);
        const secondKill = await wolfDecide(playerWolves[1].index, firstKill);

        let killStr = "";
        if (firstKill === secondKill) {
            killStr = `狼人达成一致`;
            console.log(killStr);
            await this.background.showResultInfo(killStr);
        } else {
            killStr = `狼人没有达成一致, 重新选择`;
            await this.gameData.resetWolfWantKill();
            await this.background.showResultInfo(killStr);
            console.log(killStr);
            const newFirstKill = await wolfDecide(playerWolves[0].index, secondKill);
            const newSecondKill = await wolfDecide(playerWolves[1].index, newFirstKill);
            if (newFirstKill === newSecondKill) {
                killStr =  `狼人达成一致`;
                console.log(killStr);
                await this.background.showResultInfo(killStr);
            } else {
                killStr = `狼人没有达成一致, 取第一个狼人决定的结果`
                console.log(killStr);
                await this.background.showResultInfo(killStr);
            }
        }
    }

    async cure(someone_will_be_killed) {
        console.log("== Cure ==, someone_will_be_killed=", someone_will_be_killed);
        const playersData = await this.gameData.getStatus();
        const witches = await this.getPlayerByRole("女巫");
        if (witches.length === 0) {
            return false;
        }
        const witch = witches[0];
        if (witch.index == someone_will_be_killed) {
            return false;
        }

        const action = { player_idx: witch.index, someone_will_be_killed: someone_will_be_killed };
        const result = await this.gameData.cure(action);
        if(result != undefined) {
            console.log(`${witch.name} 思考 ${result.thinking}`);
            await this.players[witch.index].think(result.thinking);
            let cureStr = "";
            if (result.cure === 1) {
                cureStr = `女巫选择救治 ${playersData[someone_will_be_killed].name}`;
                console.log(cureStr);
            } else {
                cureStr = `女巫选择不救治 ${playersData[someone_will_be_killed].name}`;
                console.log(cureStr);
            }
            await this.background.showResultInfo(cureStr);
            return result.cure === 1;
        }
        return false;

    }

    async poison(someoneWillBeKilled) {
        const playersData = await this.gameData.getStatus();
        const witches = await this.getPlayerByRole("女巫");
        if (witches.length === 0) {
            return false;
        }
        
        const witch = witches[0];
        if (witch.index == someoneWillBeKilled) {
            return false;
        }
        const result = await this.gameData.decidePoison({ player_idx: witch.index, someone_will_be_killed: someoneWillBeKilled });
        console.log(`${witch.name} 思考 ${result.thinking}`);
        await this.players[witch.index].think(result.thinking);
        if (result.poison !== -1) {
            console.log(`女巫选择毒杀 ${playersData[result.poison].name}`);
            await this.background.showResultInfo(`女巫选择毒杀 ${playersData[result.poison].name}`);
            await this.gameData.poison({ player_idx: result.poison });
            await this.lastWords(result.poison, "被女巫毒杀");
            return true;
        } else {
            console.log(`女巫选择不毒杀`);
            await this.background.showResultInfo(`女巫选择不毒杀`);
            return false;
        }
    }

    async kill() {
        console.log("== Kill ==");
        const playersData = await this.gameData.getStatus();
        const result = await this.gameData.getWolfWantKill()
        const someoneWillBeKilled = result["wolf_want_kill"][0]
        const cured = await this.cure(someoneWillBeKilled); // 看看女巫要不要救人
        await this.poison(someoneWillBeKilled); // 看看女巫要不要毒人
        if (cured) {
            return;
        }
        // 没人救，就杀人
        await this.gameData.kill({ player_idx: someoneWillBeKilled });
        console.log(`${playersData[someoneWillBeKilled].name} 被杀!`);
        await this.background.showResultInfo(`${playersData[someoneWillBeKilled].name} 被杀!`);
        await this.lastWords(someoneWillBeKilled, "被狼人杀死");
    }
    
}

export default Game;