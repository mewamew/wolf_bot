import { LAYOUT, TEXT_STYLES } from './config.js';

let wolfCount = 0; // 全局变量，用于跟踪狼人数量

class Player {
    constructor(game, name, index, role_type) {
        this.game = game;
        this.name = name;
        this.index = index;
        this.role_type = role_type;
        if (role_type != "狼人") {
            this.spirit = this.initSpirit(game.app, role_type); 
            this.spirit_small = this.initSmallSpirit(game.app, index, role_type+"_小");
            this.spirit_title = this.initSmallSpiritTitle(game.app, index, role_type);
        } else {
            if(wolfCount == 0) {
                this.spirit = this.initSpirit(game.app, "狼人a"); 
                this.spirit_small = this.initSmallSpirit(game.app, index, "狼人a_小");
                this.spirit_title = this.initSmallSpiritTitle(game.app, index, "狼人a");
                wolfCount = 1;
            } else {
                this.spirit = this.initSpirit(game.app, "狼人b"); 
                this.spirit_small = this.initSmallSpirit(game.app, index, "狼人b_小");
                this.spirit_title = this.initSmallSpiritTitle(game.app, index, "狼人b");
                wolfCount = 0;
            }
        }
        this.spirit_dead = this.initDeadSpirit(game.app, index);
        this.voteText = this.initVoteText(game.app); // 初始化投票文本
    }

    getScreenScale() {
        return {
            wr: this.game.app.screen.width / LAYOUT.BASE_WIDTH,
            hr: this.game.app.screen.height / LAYOUT.BASE_HEIGHT
        };
    }

    initSpirit(app, role_type) {
        const { wr, hr } = this.getScreenScale();
        const spirit = PIXI.Sprite.from(role_type);
        spirit.x = LAYOUT.MAIN_SPIRIT.x * wr;
        spirit.y = LAYOUT.MAIN_SPIRIT.y * hr;
        spirit.zIndex = 4;
        spirit.visible = false;
        spirit.scale.set(wr, hr);
        app.stage.addChild(spirit);
        return spirit;
    }

    initSmallSpirit(app, index, role_type) {
        const { wr, hr } = this.getScreenScale();
        const spirit = PIXI.Sprite.from(role_type);
        spirit.x = (LAYOUT.SMALL_SPIRIT.START_X + (index-1) * LAYOUT.SMALL_SPIRIT.SPACING) * wr;
        spirit.y = LAYOUT.SMALL_SPIRIT.Y * hr;
        spirit.zIndex = 4;
        spirit.visible = true;
        spirit.scale.set(wr, hr);
        app.stage.addChild(spirit);
        return spirit;
    }

    initDeadSpirit(app, index) {
        const { wr, hr } = this.getScreenScale();
        const spirit = PIXI.Sprite.from('dead');
        spirit.x = (LAYOUT.SMALL_SPIRIT.START_X + (index-1) * LAYOUT.SMALL_SPIRIT.SPACING) * wr;
        spirit.y = LAYOUT.SMALL_SPIRIT.Y * hr;
        spirit.zIndex = 5;
        spirit.visible = false;
        spirit.scale.set(wr, hr);
        app.stage.addChild(spirit);
        return spirit;
    }

    initSmallSpiritTitle(app, index, role_type) {
        const { wr, hr } = this.getScreenScale();
        const textStyle = new PIXI.TextStyle({
            ...TEXT_STYLES.TITLE,
            fontSize: LAYOUT.TITLE_TEXT.FONT_SIZE * wr
        });
        const textSpirit = new PIXI.Text({text:`${index}.${role_type}`, style:textStyle});
        textSpirit.x = (LAYOUT.TITLE_TEXT.OFFSET_X + (index-1) * LAYOUT.SMALL_SPIRIT.SPACING) * wr;
        textSpirit.y = LAYOUT.TITLE_TEXT.Y * hr;
        textSpirit.scale.set(wr, hr);
        textSpirit.zIndex = 4;
        app.stage.addChild(textSpirit);
        return textSpirit;
    }

    initVoteText(app) {
        const { wr, hr } = this.getScreenScale();
        const textStyle = new PIXI.TextStyle({
            ...TEXT_STYLES.VOTE,
            fontSize: LAYOUT.VOTE_TEXT.FONT_SIZE * wr
        });
        const voteText = new PIXI.Text({text:'', style:textStyle});
        voteText.zIndex = 6;
        voteText.visible = false;
        app.stage.addChild(voteText);
        return voteText;
    }

    async think(what, animate=true) {
        console.log(`${this.name} 思考: ${what}`);
        await this.animateSpirit(animate);
        this.shakeSpiritSmall(); // 添加抖动效果
        await this.game.background.showThinkInfo(`${this.name} 内心活动:`, what);
        await this.hide();
    }

    async speak(what, text_color='0xffffff', animate=true) {
        console.log(`${this.name} 发言: ${what}`);
        await this.animateSpirit(animate);
        this.shakeSpiritSmall(); // 添加抖动效果
        await this.game.background.showSpeakInfo(`${this.name} 发言:`, what, text_color);
        await this.hide();
    }

    async lastword(what) {
        console.log(`${this.name} 临终遗言: ${what}`);
        await this.animateSpirit(false);
        this.shakeSpiritSmall(); // 添加抖动效果
        await this.game.background.showSpeakInfo(`${this.name} 临终遗言:`, what, '0xff0000');
        await this.dead(); // 调用dead方法
        await this.hide();
    }

    async dead() {
        this.spirit_dead.visible = true;

        // spirit_title变成红色并加上[死亡]
        this.spirit_title.style.fill = '#ff0000';
        this.spirit_title.text = `${this.spirit_title.text}\n[死亡]`;
    }

    async shakeSpiritSmall() {
        const originalY = this.spirit_small.y;
        const amplitude = 8; // 抖动幅度
        const duration = 3000; // 抖动持续时间，单位为毫秒
        const startTime = Date.now();

        await new Promise((resolve) => {
            const ticker = new PIXI.Ticker();
            ticker.add(() => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1); // 计算进度，范围在0到1之间
                const shake = amplitude * Math.sin(progress * Math.PI * 4); // 抖动公式

                this.spirit_small.y = originalY + shake;

                if (progress >= 1) {
                    this.spirit_small.y = originalY;
                    ticker.stop();
                    resolve();
                }
            });
            ticker.start();
        });
    }

    async sleep(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    async hide() {
        this.spirit.visible = false;
    }

    async animateSpirit(animate) {
        this.spirit.visible = true;

        if (!animate) {
            this.spirit.x = 0;
        } else {
            this.spirit.x = -this.spirit.width;
            const targetX = 0;
            const duration = 500; // 动画持续时间，单位为毫秒
            const startTime = Date.now();

            await new Promise((resolve) => {
                const ticker = new PIXI.Ticker();
                ticker.add(() => {
                    const elapsed = Date.now() - startTime;
                    const progress = Math.min(elapsed / duration, 1); // 计算进度，范围在0到1之间
                    const easeOutQuad = (t) => t * (2 - t); // 缓动函数

                    this.spirit.x = -this.spirit.width + (targetX + this.spirit.width) * easeOutQuad(progress);

                    if (progress >= 1) {
                        this.spirit.x = targetX;
                        ticker.stop();
                        resolve();
                    }
                });
                ticker.start();
            });
        }
    }

    async showVoteCount(voteCount, hide = true) {
        const { wr, hr } = this.getScreenScale();
        this.voteText.text = `+${voteCount}`;
        this.voteText.x = this.spirit_small.x+20*wr;
        this.voteText.y = this.spirit_small.y - 50 * hr; // 显示在玩家头上
        this.voteText.visible = true;

        if (hide) {
            // 动画效果
            const duration = 1000; // 持续时间
            const startTime = Date.now();
            await new Promise((resolve) => {
                const ticker = new PIXI.Ticker();
                ticker.add(() => {
                    const elapsed = Date.now() - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    this.voteText.alpha = 1 - progress; // 渐隐效果
                    if (progress >= 1) {
                        this.voteText.visible = false;
                        ticker.stop();
                        resolve();
                    }
                });
                ticker.start();
            });
        }
    }
}

export default Player;