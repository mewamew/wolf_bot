class Ui {
    constructor() {
        this.app = new PIXI.Application();
    }

    async preload()
    {
        const assets = [
            { alias: 'bg_day', src: 'assets/bg_day.png' }, //3840 x 2160
            { alias: 'bg_night', src: 'assets/bg_night.png' },
            { alias: 'bg_black', src: 'assets/bg_black.png' },
            { alias: 'chat_box', src: 'assets/chat_box.png' },
            { alias: 'status_bar', src: 'assets/status_bar.png' },
            //数字
            { alias: '1', src: 'assets/1.png' },
            { alias: '2', src: 'assets/2.png' },
            { alias: '3', src: 'assets/3.png' },
            { alias: '4', src: 'assets/4.png' },
            { alias: '5', src: 'assets/5.png' },
            //玩家编号
            { alias: 'n1', src: 'assets/n1.png' },
            { alias: 'n2', src: 'assets/n2.png' },
            { alias: 'n3', src: 'assets/n3.png' },
            { alias: 'n4', src: 'assets/n4.png' },
            { alias: 'n5', src: 'assets/n5.png' },
            { alias: 'n6', src: 'assets/n6.png' },
            { alias: 'n7', src: 'assets/n7.png' },
            { alias: 'n8', src: 'assets/n8.png' },
            { alias: 'n9', src: 'assets/n9.png' },
            //玩家大头像
            { alias: 'player_1', src: 'assets/player_1.png' },
            { alias: 'player_2', src: 'assets/player_2.png' },
            { alias: 'player_3', src: 'assets/player_3.png' },
            { alias: 'player_4', src: 'assets/player_4.png' },
            { alias: 'player_5', src: 'assets/player_5.png' },
            { alias: 'player_6', src: 'assets/player_6.png' },
            { alias: 'player_7', src: 'assets/player_7.png' },
            { alias: 'player_8', src: 'assets/player_8.png' },
            { alias: 'player_9', src: 'assets/player_9.png' },
            //玩家小头像
            { alias: 'player_1_small', src: 'assets/player_1_small.png' },
            { alias: 'player_2_small', src: 'assets/player_2_small.png' },
            { alias: 'player_3_small', src: 'assets/player_3_small.png' },
            { alias: 'player_4_small', src: 'assets/player_4_small.png' },
            { alias: 'player_5_small', src: 'assets/player_5_small.png' },
            { alias: 'player_6_small', src: 'assets/player_6_small.png' },
            { alias: 'player_7_small', src: 'assets/player_7_small.png' },
            { alias: 'player_8_small', src: 'assets/player_8_small.png' },
            { alias: 'player_9_small', src: 'assets/player_9_small.png' },
            //墓碑
            { alias: 'death', src: 'assets/death.png' },
        ];
        await PIXI.Assets.load(assets);
    }

    async setup()
    {
        this.bgSize = this.calculateSize();
        console.log("初始化： 背景宽=", this.bgSize.width, "背景高=", this.bgSize.height)
        await this.app.init({ 
            resolution: window.devicePixelRatio || 1,  // 设置分辨率
    autoDensity: true,  // 自动调整密度
            background: '#F00000',
            width: this.bgSize.width,
            height: this.bgSize.height
        });
        document.body.appendChild(this.app.canvas);
    }

    async loadSprites() {
        this.bg_day = await this.loadSprite('bg_day', 1, false, 0, 0); //背景图
        this.bg_night = await this.loadSprite('bg_night', 1, true, 0, 0); //对话框
        this.bg_black = await this.loadSprite('bg_black', 101, false, 0, 0); //对话框
        this.chat_box = await this.loadSprite('chat_box', 3, false, 1450, 150); //聊天框
        this.status_bar = await this.loadSprite('status_bar', 3, true, 0, 1710); //状态栏

        //加载玩家大头像
        this.players = [];
        for (let i = 1; i <= 9; i++) {
            this.players.push(await this.loadSprite(`player_${i}`, 2, false, 0, 0));
        }

        //加载玩家小头像
        this.players_small = [];
        for (let i = 1; i <= 9; i++) {
            this.players_small.push(await this.loadSprite(`player_${i}_small`, 4, true, 100+(i-1)*420, 1800, 0.7));
        }

        //加载墓碑
        this.death = []
        for (let i = 1; i <= 9; i++) {
            this.death.push(await this.loadSprite(`death`, 5, false, 100+(i-1)*420, 1800, 0.8));
        }

        //加载数字
        this.players_vote = [];
        for (let i = 1; i <= 9; i++) {
            let votes = [];
            for (let j = 1; j <= 5; j++) {
                votes.push(await this.loadSprite(`${j}`, 4, false, 100+(i-1) * 420, 1600, 0.9));
            }
            this.players_vote.push(votes);
        }

        //加载玩家编号
        this.players_number = [];
        for (let i = 1; i <= 9; i++) {
            this.players_number.push(await this.loadSprite(`n${i}`, 6, true, 200+(i-1) * 420, 2010));
        }

        //加载文字spirit
        this.speakTextSpirit = this.initTextSpirit(5, 1600, 400, 80, 110, '#ffffff');
        this.titleTextSpirit = this.initTextSpirit(5, 1600, 200, 90, 90, '#00ffff');
    }

    //显示说话内容
    async speak(title, text) {
        const formattedText = this.formatText(text);
        console.log("说话内容：", formattedText);

        this.titleTextSpirit.text = title;
        this.titleTextSpirit.visible = true;

        this.speakTextSpirit.text = "";
        this.speakTextSpirit.visible = true;
        this.chat_box.visible = true;
        await this.typeWriterEffect(formattedText, this.speakTextSpirit);        
    }

    async hideSpeak() {
        this.chat_box.visible = false;
        this.titleTextSpirit.visible = false;
        this.speakTextSpirit.visible = false;
    }
    
    //在指定的玩家头顶显示投票
    async showVote(player_index, number) {
        for (let i = 0; i < 5; i++) {
            this.players_vote[player_index-1][i].visible = false;
        }
        this.players_vote[player_index-1][number-1].visible = true;
    }

    async killPlayer(player_index) {
        this.death[player_index-1].visible = true;
    }

    //隐藏所有投票
    async hideAllVotes() {
        for (let i = 0; i < this.players_vote.length; i++) {
            for (let j = 0; j < this.players_vote[i].length; j++) {
                this.players_vote[i][j].visible = false;
            }
        }
    }

    async showPlayer(player_index) {
        for (let i = 0; i < this.players.length; i++) {
            this.players[i].visible = false;
        }
        this.players[player_index-1].visible = true;
    }


    async showDayBackground() {
        this.bg_day.visible = true;
        this.bg_night.visible = false;
        this.bg_black.visible = false;
    }
    async showNightBackground() {
        this.bg_day.visible = false;
        this.bg_night.visible = true;
        this.bg_black.visible = false;
    }
    async showBlackBackground() {
        this.bg_day.visible = false;
        this.bg_night.visible = false;
        this.bg_black.visible = true;
    }

    async loadSprite(sprite_name, zIndex, visible, x, y, scale=1.0) {
        console.log("loadSprite ", sprite_name);
        let sprite = PIXI.Sprite.from(sprite_name);
        sprite.width *= this.bgSize.scale * scale;
        sprite.height *= this.bgSize.scale * scale;
        sprite.visible = visible;//默认不显示
        sprite.zIndex = zIndex;
        sprite.x = x * this.bgSize.scale;
        sprite.y = y * this.bgSize.scale;
        this.app.stage.addChild(sprite);
        return sprite;
    }

    calculateSize() {
        const targetRatio = 3840 / 2160;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        const windowRatio = windowWidth / windowHeight;
        let width, height, scale;
        if (windowRatio > targetRatio) {
            // 窗口太宽，以高度为基准
            height = windowHeight;
            width = height * targetRatio;
        } else {
            // 窗口太高，以宽度为基准
            width = windowWidth;
            height = width / targetRatio;
        }
        scale = width / 3840;
        return { width, height, scale };
    }

    initTextSpirit(zIndex, x, y, fontSize, lineHeight, color) {
        const textStyle = new PIXI.TextStyle({
            fontFamily: '钉钉进步体',
            fontSize: fontSize*this.bgSize.scale,
            fill: color,
            lineHeight: lineHeight*this.bgSize.scale,
            stroke: { color: '#000000', width: 2*this.bgSize.scale }
        });
        const textSpirit = new PIXI.Text({text:"", style:textStyle});
        textSpirit.x = x * this.bgSize.scale;
        textSpirit.y = y * this.bgSize.scale;
        textSpirit.zIndex = zIndex;
        textSpirit.visible = true;
        this.app.stage.addChild(textSpirit);
        return textSpirit;
    }

    async typeWriterEffect(formattedText, textSpirit) {
        const interval = 10; // 每个字符显示的间隔时间，单位为毫秒
        let currentIndex = 0;
        textSpirit.text = "";
        textSpirit.visible = true;
        return new Promise((resolve) => {
            const typeWriter = () => {
                if (currentIndex < formattedText.length) {
                    textSpirit.text += formattedText[currentIndex];
                    currentIndex++;
                    setTimeout(typeWriter, interval);
                } else {
                    resolve();
                }
            };
            typeWriter();
        });
    }

    formatText(what) {
        // 按标点符号分割字符串，并在每个标点后添加换行符
        let formattedText = what.replace(/([。！？，,]|\.{3})/g, '$1\n');
        
        // 合并短行，确保每行不超过24个字
        let lines = formattedText.split('\n');
        return lines.join('\n');
    }

}

export default Ui;