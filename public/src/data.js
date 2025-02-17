


class GameData {
    async fetchData(url, options = {}) {
        const timeout = 1000*1800; // 30秒超时
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('请求超时')), timeout);
        });

        const fetchPromise = fetch(url, options);
        const response = await Promise.race([fetchPromise, timeoutPromise]);
        return response.json();
    }

    async startGame() {
        return this.fetchData('/start', { method: 'GET' });
    }

    async getStatus() {
        return this.fetchData('/status');
    }

    async divine(action) {
        return this.fetchData('/divine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async decideKill(action) {
        return this.fetchData('/decide_kill', {
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

    async decideCureOrPoison(action) {
        return this.fetchData('/decide_cure_or_poison', {
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

    async getCurrentTime() {
        const response = await fetch('/current_time');
        return await response.json();
    }

    async lastWords(action) {
        return this.fetchData('/last_words', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async revenge(action) {
        return this.fetchData('/revenge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async attack(action) {
        return this.fetchData('/attack', {
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

    async cure(action) {
        return this.fetchData('/cure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async toggleDayNight() {
        return this.fetchData('/toggle_day_night', { method: 'POST' });
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

    async vote(action) {
        return this.fetchData('/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action)
        });
    }

    async getVoteResult() {
        return this.fetchData('/get_vote_result');
    }

    async execute() {
        return this.fetchData('/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
    }

    async checkWinner() {
        return this.fetchData('/check_winner');
    }
    
}

export default GameData;