import Game from "./game.js";


const app = new PIXI.Application();



async function setup()
{
    await app.init({ background: '#000000', resizeTo: window });
    document.body.appendChild(app.canvas);
}


async function preload()
{
    const assets = [
        { alias: 'bg_day', src: 'assets/bg_day.png' },
        { alias: 'bg_night', src: 'assets/bg_night.png' },
        { alias: 'bg_dark', src: 'assets/bg_dark.png' },
        { alias: 'info_speak', src: 'assets/info_speak.png' },
        { alias: 'info_think', src: 'assets/info_think.png' },
        { alias: 'info_result', src: 'assets/info_result.png' },
        { alias: '狼人a', src: 'assets/红太狼.png' },
        { alias: '狼人b', src: 'assets/灰太狼.png' },
        { alias: '女巫', src: 'assets/芙莉莲.png' },
        { alias: '村民', src: 'assets/村民.png' },
        { alias: '猎人', src: 'assets/猎人.png' },
        { alias: '预言家', src: 'assets/预言家.png' },
        { alias: '狼人a_小', src: 'assets/红太狼_小.png' },
        { alias: '狼人b_小', src: 'assets/灰太狼_小.png' },
        { alias: '女巫_小', src: 'assets/芙莉莲_小.png' },
        { alias: '村民_小', src: 'assets/村民_小.png' },
        { alias: '猎人_小', src: 'assets/猎人_小.png' },
        { alias: '预言家_小', src: 'assets/预言家_小.png' },
        { alias: 'dead', src: 'assets/dead.png' }
    ];
    await PIXI.Assets.load(assets);
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Asynchronous IIFE
(async () => {
    await setup();
    await preload();

    const game = new Game(app);
    await game.start();
    
    while (true) {
        await game.dayPhase();
        const w1 = await game.checkWinner();
        if (w1 != "胜负未分") {
            console.log(`胜利者是 ${w1}`);
            game.background.showResultInfo(`胜利者是 ${w1}`);
            break;
        }

        await game.toggleDayNight();
        await game.nightPhase();

        const w2 = await game.checkWinner();
        if (w2 != "胜负未分") {
            console.log(`胜利者是 ${w2}`);
            game.background.showResultInfo(`胜利者是 ${w2}`);
            break;
        }
        await game.toggleDayNight();
    }


})();
