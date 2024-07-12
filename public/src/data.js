


class GameData {
    async fetchData(url, options = {}) {
        const response = await fetch(url, options);
        await this.delay(1000);
        return response.json();
    }

    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async startGame() {
        return this.fetchData('/start', { method: 'GET' });
    }

    async getStatus() {
        return this.fetchData('/status');
    }

    async getCurrentTime() {
        const response = await fetch('/current_time');
        return await response.json();
    }


    async speak(action) {
        return this.fetchData('/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async resetVoteResult() {
        return this.fetchData('/reset_vote_result', { method: 'POST' });
    }

    async getVoteResult() {
        return this.fetchData('/get_vote_result');
    }

    async vote(action) {
        return this.fetchData('/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async execute() {
        return this.fetchData('/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    async lastWords(action) {
        return this.fetchData('/last_words', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_idx: action.player_idx,
                death_reason: action.death_reason
            })
        });
    }

    async attack(action) {
        return this.fetchData('/attack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async toggleDayNight() {
        return this.fetchData('/toggle_day_night', { method: 'POST' });
    }

    async checkWinner() {
        return this.fetchData('/check_winner');
    }

    async divine(action) {
        return this.fetchData('/divine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async resetWolfWantKill() {
        return this.fetchData('/reset_wolf_want_kill', { method: 'POST' });
    }

    async getWolfWantKill() {
        return this.fetchData('/get_wolf_want_kill');
    }

    async decideKill(action) {
        return this.fetchData('/decide_kill', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }


    async cure(action) {
        return this.fetchData('/cure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async decidePoison(action) {
        return this.fetchData('/decide_poison', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async poison(action) {
        return this.fetchData('/poison', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async kill(action) {
        return this.fetchData('/kill', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }
    
}

export default GameData;
