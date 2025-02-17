1.在config.json中配置模型和API KEY
2.python web.py 启动服务
3.在浏览器中访问 `http://127.0.0.1:8000/` 开始游戏
4.按空格键可以暂停/恢复游戏
5.默认显示角色信息，如果想屏蔽角色信息， 修改index.js中的变量 show_role 为 false
6.默认显示思考信息，如果想屏蔽思考信息， 修改index.js中的变量 show_thinking 为 false
7.游戏结束后，会在logs/下生成一个 replay_{}.json 文件， 其中{}代表游戏开始的时间, 如果想回放游戏，可以python web.py <回放文件路径>
8.如果想让人类玩家参战，config.json中的model_name字段可以设置为 "human"