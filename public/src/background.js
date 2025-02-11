class Background {
    constructor(app) {
        this.app = app;
        this.bgLayers = {
            'day': this.loadSprite('bg_day', 0),
            'night': this.loadSprite('bg_night', 1),
            'dark': this.loadSprite('bg_dark', 2),
            'dark2': this.loadSprite('bg_dark', 100),
        };

        this.infoLayers = {
            'speak': this.loadSprite('info_speak', 3, 1),
            'think': this.loadSprite('info_think', 3, 1),
            'result': this.loadSprite('info_result', 103, 1),
        }
        this.titleTextSpirit = this.initTitleTextSpirit(app);
        this.textSpirit = this.initTextSpirit(app);
        this.resultTextSpirit = this.initResutlTextSpirit(app);
        this.hideInfo();
    }

    initResutlTextSpirit(app) {
        const wr = app.screen.width/1800;
        const hr = app.screen.height/900;
        const textStyle = new PIXI.TextStyle({
            fontFamily: '钉钉进步体',
            fontSize: 38*wr,
            fill: '#00ff00',
            lineHeight: 46*hr,
            stroke: { color: '#000000', width: 2*wr }
        });
        const textSpirit = new PIXI.Text({text:"", style:textStyle});
        textSpirit.x = 900 * wr;
        textSpirit.y = 450 * hr;
        textSpirit.anchor.set(0.5, 0.5);
        textSpirit.zIndex = 104;
        app.stage.addChild(textSpirit);
        return textSpirit;
    }

    initTitleTextSpirit(app) {
        const wr = app.screen.width/1800;
        const hr = app.screen.height/900;
        const textStyle = new PIXI.TextStyle({
            fontFamily: '钉钉进步体',
            fontSize: 36*wr,
            fill: '#00ff00',
            lineHeight: 40*hr,
            stroke: { color: '#000000', width: 2*wr }
        });
        const textSpirit = new PIXI.Text({text:"", style:textStyle});
        textSpirit.x = (520-36) * wr;
        textSpirit.y = 520 * hr;
        textSpirit.zIndex = 4;
        app.stage.addChild(textSpirit);
        return textSpirit;
    }

    initTextSpirit(app) {
        const wr = app.screen.width/1800;
        const hr = app.screen.height/900;
        const textStyle = new PIXI.TextStyle({
            fontFamily: '钉钉进步体',
            fontSize: 32*wr,
            fill: '#ffffff',
            lineHeight: 38*hr,
            stroke: { color: '#000000', width: 2*wr }
        });
        const textSpirit = new PIXI.Text({text:"", style:textStyle});
        textSpirit.x = (520-36) * wr;
        textSpirit.y = 580 * hr;
        textSpirit.zIndex = 4;
        app.stage.addChild(textSpirit);
        return textSpirit;
    }

    loadSprite(sprite_name, zIndex, alpha=0) {
        let sprite = PIXI.Sprite.from(sprite_name);
        sprite.width = this.app.screen.width;
        sprite.height = this.app.screen.height;
        sprite.visible = true;
        sprite.zIndex = zIndex;
        sprite.alpha = alpha;
        this.app.stage.addChild(sprite);
        return sprite;
    }

    async fadeIn(sprite) {
        return new Promise((resolve) => {
            const fadeInterval = setInterval(() => {
                if (sprite.alpha < 1) {
                    sprite.alpha += 0.05;
                } else {
                    clearInterval(fadeInterval);
                    resolve();
                }
            }, 16);
        });
    }

    async fadeOut(sprite) {
        return new Promise((resolve) => {
            const fadeInterval = setInterval(() => {
                if (sprite.alpha > 0) {
                    sprite.alpha -= 0.05;
                } else {
                    clearInterval(fadeInterval);
                    resolve();
                }
            }, 16);
        });
    }

    async showDayBackground(day) {
        this.bgLayers['day'].alpha = 0;
        this.bgLayers['day'].zIndex = 1;
        this.bgLayers['night'].zIndex = 0;

        await this.showDarkBackground('dark2');
        // 创建并显示第day天的文本
        const wr = this.app.screen.width / 1800;
        const hr = this.app.screen.height / 900;
        const dayTextStyle = new PIXI.TextStyle({
            fontFamily: '钉钉进步体',
            fontSize: 400 * wr,
            fill: '#ffffff',
            stroke: { color: '#000000', width: 20 * wr }
        });
        const dayText = new PIXI.Text({text: `第${day}天`, style: dayTextStyle });
        dayText.x = this.app.screen.width / 2;
        dayText.y = this.app.screen.height / 2;
        dayText.anchor.set(0.5, 0.5);
        dayText.zIndex = 106;
        dayText.alpha = 0;
        this.app.stage.addChild(dayText);

        // 动画显示文本
        await new Promise((resolve) => {
            const fadeInInterval = setInterval(() => {
                if (dayText.alpha < 1) {
                    dayText.alpha += 0.02;
                } else {
                    clearInterval(fadeInInterval);
                    setTimeout(() => {
                        const fadeOutInterval = setInterval(() => {
                            if (dayText.alpha > 0) {
                                dayText.alpha -= 0.02;
                            } else {
                                clearInterval(fadeOutInterval);
                                this.app.stage.removeChild(dayText);
                                resolve();
                            }
                        }, 16);
                    }, 1000); // 显示1秒后开始渐隐
                }
            }, 16);
        });
        await this.hideDarkBackground('dark2');
        await this.fadeIn(this.bgLayers['day']);

        
    }

    async showNightBackground() {
        this.bgLayers['night'].alpha = 0;
        this.bgLayers['night'].zIndex = 1;
        this.bgLayers['day'].zIndex = 0;

        await this.showDarkBackground('dark2');
        // 创建并显示"天黑了"文本
        const wr = this.app.screen.width / 1800;
        const hr = this.app.screen.height / 900;
        const nightTextStyle = new PIXI.TextStyle({
            fontFamily: '钉钉进步体',
            fontSize: 400 * wr,
            fill: '#ff0000',
            stroke: { color: '#000000', width: 20 * wr }
        });
        const nightText = new PIXI.Text({text: "天黑了", style: nightTextStyle });
        nightText.x = this.app.screen.width / 2;
        nightText.y = this.app.screen.height / 2;
        nightText.anchor.set(0.5, 0.5);
        nightText.zIndex = 106;
        nightText.alpha = 0;
        this.app.stage.addChild(nightText);

        // 动画显示文本
        await new Promise((resolve) => {
            const fadeInInterval = setInterval(() => {
                if (nightText.alpha < 1) {
                    nightText.alpha += 0.02;
                } else {
                    clearInterval(fadeInInterval);
                    setTimeout(() => {
                        const fadeOutInterval = setInterval(() => {
                            if (nightText.alpha > 0) {
                                nightText.alpha -= 0.02;
                            } else {
                                clearInterval(fadeOutInterval);
                                this.app.stage.removeChild(nightText);
                                resolve();
                            }
                        }, 16);
                    }, 1000); // 显示1秒后开始渐隐
                }
            }, 16);
        });
        await this.hideDarkBackground('dark2');
        await this.fadeIn(this.bgLayers['night']);
    }

    async showDarkBackground(dark='dark') {
        this.bgLayers[dark].alpha = 0;
        await this.fadeIn(this.bgLayers[dark]);
    }

    async hideDarkBackground(dark='dark') {
        this.bgLayers[dark].alpha = 1;
        await this.fadeOut(this.bgLayers[dark]);
    }

    formatText(what) {
        // 按标点符号分割字符串，并在每个标点后添加换行符
        let formattedText = what.replace(/([。！？，]|\.{3})/g, '$1\n');
        
        // 合并短行，确保每行不超过24个字
        let lines = formattedText.split('\n');
        let mergedLines = [];
        let currentLine = "";

        for (let line of lines) {
            if ((currentLine + line).length <= 24) {
                currentLine += line;
            } else {
                if (currentLine) mergedLines.push(currentLine);
                currentLine = line;
            }
        }
        if (currentLine) mergedLines.push(currentLine);
        return mergedLines;
    }

    async typeWriterEffect(formattedText, textSpirit) {
        const interval = 50; // 每个字符显示的间隔时间，单位为毫秒
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

    async sleep(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    async showSpeakInfo(title, text, text_color) {
        this.infoLayers['speak'].visible = true;
        this.infoLayers['think'].visible = false;
        this.infoLayers['result'].visible = false;
        this.textSpirit.style.fill = text_color;
        this.titleTextSpirit.text = title;
        this.titleTextSpirit.visible = true;
        const lines = this.formatText(text);
        
        // 每5行分组显示
        for (let i = 0; i < lines.length; i += 7) {
            const batch = lines.slice(i, i + 7);
            const formattedText = batch.join('\n');
            await this.typeWriterEffect(formattedText, this.textSpirit);
            if (i + 5 < lines.length) {
                await this.sleep(1000); // 每组之间暂停1秒
                this.textSpirit.text = ''; // 清空文本，准备显示下一组
            }
        }
        
        await this.sleep(2000);
        await this.hideInfo();
    }

    async showThinkInfo(title, text) {
        this.infoLayers['think'].visible = true;
        this.infoLayers['speak'].visible = false;        
        this.infoLayers['result'].visible = false;
        this.textSpirit.style.fill = "0xffffff";
        this.titleTextSpirit.text = title;
        this.titleTextSpirit.visible = true;

        await this.showDarkBackground();
        const lines = this.formatText(text);
        // 每5行分组显示
        for (let i = 0; i < lines.length; i += 7) {
            const batch = lines.slice(i, i + 7);
            const formattedText = batch.join('\n');
            await this.typeWriterEffect(formattedText, this.textSpirit);
            if (i + 5 < lines.length) {
                await this.sleep(1000); // 每组之间暂停1秒
                this.textSpirit.text = ''; // 清空文本，准备显示下一组
            }
        }
        await this.sleep(2000);
        await this.hideInfo();
        await this.hideDarkBackground();
    }
    
    async showResultInfo(text) {
        this.infoLayers['result'].visible = true;
        this.infoLayers['speak'].visible = false;
        this.infoLayers['think'].visible = false;
        this.resultTextSpirit.style.fill = "0xff0000";
        await this.showDarkBackground('dark2');
        await this.typeWriterEffect(text, this.resultTextSpirit);
        await this.sleep(3000);
        await this.hideInfo();
        await this.hideDarkBackground('dark2');
    }

    hideInfo() {
        this.infoLayers['speak'].visible = false;
        this.infoLayers['think'].visible = false;
        this.infoLayers['result'].visible = false;
        this.textSpirit.visible = false;
        this.titleTextSpirit.visible = false;
        this.resultTextSpirit.visible = false;
    }
}

export default Background;