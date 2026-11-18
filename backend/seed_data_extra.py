"""Extended situational dialogues (+18, total 30) and grammar handbook lessons (+18, total 30)."""

from __future__ import annotations

EXTRA_DIALOGUES = [
    {
        "title": "打车与问路沟通 (Taking a Taxi & Directions)",
        "scene": "日常出行",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Driver", "en": "Hi there! Where are we heading today?", "zh": "你好！今天去哪里？"},
            {"speaker": "You", "en": "Could you take me to Central Station, please?", "zh": "麻烦带我去中央车站。"},
            {"speaker": "Driver", "en": "Sure. Do you want me to take the highway or local streets?", "zh": "好的。您想走高速还是市区普通道路？"},
            {"speaker": "You", "en": "Whichever is faster—I have a train to catch in thirty minutes.", "zh": "哪条快走哪条——我三十分钟后还要赶火车。"},
            {"speaker": "Driver", "en": "Got it. Highway traffic looks clear, so we should make it in fifteen.", "zh": "明白，高速现在很通畅，我们十五分钟就能到。"},
            {"speaker": "You", "en": "Perfect! Could you drop me off near the East Entrance?", "zh": "太好了！方便在东入口附近放下我吗？"},
        ],
        "key_phrases": [
            {"en": "Where are we heading?", "zh": "我们要去哪里？"},
            {"en": "catch a train", "zh": "赶火车"},
            {"en": "drop me off near...", "zh": "在……附近放我下车"},
        ],
    },
    {
        "title": "健身房办卡咨询 (Joining a Gym)",
        "scene": "日常出行",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Staff", "en": "Welcome to FitCore! Are you interested in a membership today?", "zh": "欢迎来到 FitCore！您今天想了解一下会员卡吗？"},
            {"speaker": "You", "en": "Yes, I'd like to know about your monthly plans and class schedules.", "zh": "是的，我想了解一下月卡套餐和团体课安排。"},
            {"speaker": "Staff", "en": "Our standard plan includes 24-hour gym access plus two group classes a week.", "zh": "我们的标准套餐包含全天 24 小时器械区权限，外加每周两节团课。"},
            {"speaker": "You", "en": "Do you offer a free trial session before I sign up?", "zh": "签约办卡前提供免费体验课吗？"},
            {"speaker": "Staff", "en": "Absolutely! You can book a free one-day pass right at the front desk.", "zh": "当然！您现在就可以在前台预约一张免费单日体验卡。"},
        ],
        "key_phrases": [
            {"en": "monthly plan", "zh": "月度套餐"},
            {"en": "free trial session", "zh": "免费体验课"},
            {"en": "sign up", "zh": "报名/办理"},
        ],
    },
    {
        "title": "超市购物与会员结账 (At the Supermarket)",
        "scene": "日常出行",
        "level": "初级 A2",
        "lines": [
            {"speaker": "You", "en": "Excuse me, could you tell me which aisle the olive oil is in?", "zh": "打扰一下，请问橄榄油在几号货架通道？"},
            {"speaker": "Clerk", "en": "It's in aisle five, right next to the pasta sauces.", "zh": "在 5 号通道，就在意面酱旁边。"},
            {"speaker": "Cashier", "en": "Did you find everything you were looking for today?", "zh": "今天需要的东西都找齐了吗？"},
            {"speaker": "You", "en": "Yes, thanks! Do I enter my phone number here for the member discount?", "zh": "齐了，谢谢！会员折扣是在这里输入手机号吗？"},
            {"speaker": "Cashier", "en": "Yes, right on the keypad. Would you like a paper receipt or digital?", "zh": "是的，就在小键盘上输。您需要纸质小票还是电子小票？"},
        ],
        "key_phrases": [
            {"en": "which aisle ... is in", "zh": "……在几号通道"},
            {"en": "member discount", "zh": "会员折扣"},
            {"en": "paper receipt", "zh": "纸质收据/小票"},
        ],
    },
    {
        "title": "加油站与车辆检查 (Gas Station & Car Service)",
        "scene": "日常出行",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Attendant", "en": "Good morning! How can I help you with your car today?", "zh": "早上好！今天车子有什么需要服务的？"},
            {"speaker": "You", "en": "Hi, my tire pressure warning light just came on. Could you check the tires?", "zh": "你好，我的胎压报警灯刚亮了，能帮我检查一下轮胎吗？"},
            {"speaker": "Attendant", "en": "No problem. Your front left tire was a bit low, so I topped it up.", "zh": "没问题。左前轮胎压稍微低了点，我已经帮你补足气了。"},
            {"speaker": "You", "en": "Thanks so much! Also, I'd like to fill up with regular unleaded gas.", "zh": "非常感谢！另外帮我加满普通无铅汽油。"},
            {"speaker": "Attendant", "en": "All topped off! Would you like me to wipe down the windshield too?", "zh": "加满啦！需要顺便擦一下挡风玻璃吗？"},
        ],
        "key_phrases": [
            {"en": "warning light came on", "zh": "报警灯亮了"},
            {"en": "top up", "zh": "加满 / 补足"},
            {"en": "fill up with regular", "zh": "加满普通汽油"},
        ],
    },
    {
        "title": "机场海关入境问询 (Immigration & Customs)",
        "scene": "旅行出行",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Officer", "en": "Passport, please. What is the purpose of your visit?", "zh": "请出示护照。您此行的目的是什么？"},
            {"speaker": "You", "en": "I'm here for tourism and visiting a friend in Seattle.", "zh": "我是来旅游的，并拜访一位在西雅图的朋友。"},
            {"speaker": "Officer", "en": "How long will you be staying, and where will you stay?", "zh": "您计划停留多久？住在哪里？"},
            {"speaker": "You", "en": "I'll be staying for ten days at the Downtown Harbor Hotel.", "zh": "我打算停留十天，住在市中心海港酒店。"},
            {"speaker": "Officer", "en": "Do you have anything to declare—food, plants, or large amounts of cash?", "zh": "有需要申报的物品吗——比如食物、植物或大额现金？"},
            {"speaker": "You", "en": "Nothing to declare. Here is my return ticket confirmation if you need it.", "zh": "没有需要申报的物品。如果您需要的话，这是我的返程机票确认单。"},
        ],
        "key_phrases": [
            {"en": "purpose of your visit", "zh": "来访目的"},
            {"en": "anything to declare", "zh": "有需要申报的物品吗"},
            {"en": "return ticket", "zh": "返程机票"},
        ],
    },
    {
        "title": "航班延误与改签交涉 (Flight Delay & Rebooking)",
        "scene": "旅行出行",
        "level": "中级 B1",
        "lines": [
            {"speaker": "You", "en": "Excuse me, my connecting flight was delayed and I might miss my next leg.", "zh": "打扰一下，我的联程航班延误了，我可能会赶不上下一程。"},
            {"speaker": "Agent", "en": "Let me check your itinerary. Yes, the connection looks too tight now.", "zh": "我查一下您的行程单。是的，现在中转时间太紧张了。"},
            {"speaker": "You", "en": "Could you put me on the next available flight to Chicago at no extra charge?", "zh": "可以免费帮我改签到下一班飞往芝加哥的航班吗？"},
            {"speaker": "Agent", "en": "Of course. There's a direct flight departing at 4:15 PM. Does that work?", "zh": "当然可以。下午 4:15 有一班直飞，这个时间合适吗？"},
            {"speaker": "You", "en": "That works well. Will my checked luggage be transferred automatically?", "zh": "非常合适。我托运的行李会自动转运过去吗？"},
        ],
        "key_phrases": [
            {"en": "connecting flight", "zh": "联程/中转航班"},
            {"en": "next available flight", "zh": "最近一班有空位的航班"},
            {"en": "at no extra charge", "zh": "无需额外费用"},
        ],
    },
    {
        "title": "租车门店取车沟通 (Renting a Car)",
        "scene": "旅行出行",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Agent", "en": "Welcome to EcoDrive Rentals. May I see your driver's license and credit card?", "zh": "欢迎来到 EcoDrive 租车。请出示您的驾照和信用卡。"},
            {"speaker": "You", "en": "Here they are. Does the rental include basic collision insurance?", "zh": "给您。租金里包含基础碰撞险吗？"},
            {"speaker": "Agent", "en": "Basic liability is included, and full coverage is fifteen dollars extra per day.", "zh": "基础责任险已包含，全险每天加收 15 美元。"},
            {"speaker": "You", "en": "I'll add the full coverage for peace of mind. Should I return it with a full tank?", "zh": "为了省心我加个全险吧。还车时要加满油吗？"},
            {"speaker": "Agent", "en": "Yes, full-to-full policy. Have a safe trip!", "zh": "是的，满油取满油还。祝您旅途平安！"},
        ],
        "key_phrases": [
            {"en": "driver's license", "zh": "驾驶证"},
            {"en": "full coverage", "zh": "全险保障"},
            {"en": "full tank", "zh": "满油箱"},
        ],
    },
    {
        "title": "职场催办项目进度 (Following Up on Deliverables)",
        "scene": "职场商务",
        "level": "中级 B1",
        "lines": [
            {"speaker": "You", "en": "Hi Maya, just checking in on the Q4 budget spreadsheet we discussed.", "zh": "你好 Maya，跟你跟进一下我们之前聊的第四季度预算表。"},
            {"speaker": "Maya", "en": "Hey! Sorry for the wait—we're waiting on final numbers from the regional leads.", "zh": "嘿！不好意思让你久等了——我们还在等各区负责人的最终数据。"},
            {"speaker": "You", "en": "Totally understand. Is there an ETA on when we can review the draft?", "zh": "完全理解。大概预计什么时候能看一下初稿？"},
            {"speaker": "Maya", "en": "I should have a working draft ready for you by tomorrow noon.", "zh": "我明天中午之前应该能把可审阅的初稿发给你。"},
            {"speaker": "You", "en": "Awesome, appreciate it! Let me know if you need any help compiling the data.", "zh": "太棒了，非常感谢！如果整理数据需要帮忙随时跟我说。"},
        ],
        "key_phrases": [
            {"en": "just checking in on...", "zh": "来跟进确认一下……"},
            {"en": "Is there an ETA?", "zh": "预计什么时候完成/到达？"},
            {"en": "working draft", "zh": "可用初稿"},
        ],
    },
    {
        "title": "英文产品演示与答疑 (Product Demo & Q&A)",
        "scene": "职场商务",
        "level": "中高级 B2",
        "lines": [
            {"speaker": "You", "en": "Today I'd like to demonstrate how our dashboard automates daily reporting.", "zh": "今天我来演示一下我们的仪表盘是如何自动生成日报的。"},
            {"speaker": "Client", "en": "Looks clean! How well does it scale if we import fifty thousand records?", "zh": "界面很清爽！如果我们导入五万条记录，性能扩展表现怎么样？"},
            {"speaker": "You", "en": "Great question. Queries are indexed locally, so results load in under fifty milliseconds.", "zh": "好问题。查询都在本地建了索引，所以加载结果不到 50 毫秒。"},
            {"speaker": "Client", "en": "That's impressive. Can non-technical teammates export custom views easily?", "zh": "很厉害。非技术同事也能轻松导出自定义视图吗？"},
            {"speaker": "You", "en": "Yes, it's one click to export CSV or share a live snapshot.", "zh": "可以，一键就能导出表格或者分享实时快照。"},
        ],
        "key_phrases": [
            {"en": "scale well", "zh": "扩展性好"},
            {"en": "Great question.", "zh": "好问题（答疑过渡神句）"},
            {"en": "one click to export", "zh": "一键导出"},
        ],
    },
    {
        "title": "跨部门分歧协调 (Cross-Team Alignment)",
        "scene": "职场商务",
        "level": "中高级 B2",
        "lines": [
            {"speaker": "Lead", "en": "Marketing wants to launch next Friday, but engineering prefers two more weeks.", "zh": "市场部想下周五上线，但研发这边希望再多两周缓冲。"},
            {"speaker": "You", "en": "I see both perspectives. What if we split the launch into two phases?", "zh": "我理解双方的考虑。不如我们把发布拆成两个阶段怎么样？"},
            {"speaker": "Lead", "en": "How would that work in practice?", "zh": "具体落地上要怎么安排？"},
            {"speaker": "You", "en": "We release the core workflow next Friday, then roll out advanced analytics later.", "zh": "下周五先发核心流程，随后再推高阶分析功能。"},
            {"speaker": "Lead", "en": "That lowers risk while still hitting the campaign window. Let's propose that.", "zh": "这样既降低了风险，又不耽误营销窗口期，就按这个提议吧。"},
        ],
        "key_phrases": [
            {"en": "see both perspectives", "zh": "理解双方立场"},
            {"en": "split ... into two phases", "zh": "拆分为两阶段推进"},
            {"en": "roll out", "zh": "陆续上线/推出"},
        ],
    },
    {
        "title": "Offer 与薪资福利沟通 (Salary Negotiation)",
        "scene": "职场商务",
        "level": "中高级 B2",
        "lines": [
            {"speaker": "Recruiter", "en": "We're thrilled to offer you the position! Have you had a chance to review the package?", "zh": "我们很高兴给你发放录用通知！你有看薪资方案了吗？"},
            {"speaker": "You", "en": "Thank you so much—I'm really excited about the team and the mission.", "zh": "非常感谢——我对团队和业务方向都很期待。"},
            {"speaker": "You", "en": "Based on my prior impact and market benchmarks, is there flexibility on base salary?", "zh": "基于我过往的项目成果和市场水平，基本薪资上还有调整空间吗？"},
            {"speaker": "Recruiter", "en": "Let me check with our compensation team. What range did you have in mind?", "zh": "我去和薪酬团队确认一下。你心里预期大概是什么范围？"},
            {"speaker": "You", "en": "If we could move closer to an eight percent bump or add a sign-on bonus, I can accept today.", "zh": "如果能上浮大约 8% 或者加一笔签约奖金，我今天就可以确认接 Offer。"},
        ],
        "key_phrases": [
            {"en": "flexibility on base salary", "zh": "底薪调整空间"},
            {"en": "market benchmarks", "zh": "市场薪酬基准"},
            {"en": "sign-on bonus", "zh": "签约奖金"},
        ],
    },
    {
        "title": "茶水间破冰与周末闲聊 (Office Small Talk)",
        "scene": "职场商务",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Colleague", "en": "Morning! How was your weekend? Did you get up to anything fun?", "zh": "早安！周末过得怎么样？有什么好玩的事吗？"},
            {"speaker": "You", "en": "Pretty relaxing! I went hiking on Saturday and finally finished a great novel.", "zh": "很放松！周六去徒步了，还终于看完了一本好小说。"},
            {"speaker": "Colleague", "en": "Nice! Which trail did you take?", "zh": "不错呀！去的哪条徒步路线？"},
            {"speaker": "You", "en": "The Pine Ridge loop. The weather couldn't have been better.", "zh": "松岭环线。天气好得没话说。"},
            {"speaker": "Colleague", "en": "I'll have to check that out sometime. Catch you at the 10 AM sync!", "zh": "改天我也得去走走。10 点同步会见！"},
        ],
        "key_phrases": [
            {"en": "get up to anything fun?", "zh": "做啥好玩的了吗？"},
            {"en": "couldn't have been better", "zh": "好到不能再好了"},
            {"en": "Catch you later!", "zh": "待会见！"},
        ],
    },
    {
        "title": "大学图书馆借阅与检索 (Campus Library Help)",
        "scene": "校园学术",
        "level": "中级 B1",
        "lines": [
            {"speaker": "You", "en": "Hi, I'm looking for reference books on cognitive psychology, but they seem checked out.", "zh": "你好，我在找认知心理学的参考书，但好像都被借走了。"},
            {"speaker": "Librarian", "en": "Let me check the catalog. You can place a hold or use our online database copy.", "zh": "我查一下目录。您可以预约排队，或者直接看我们线上数据库里的电子版。"},
            {"speaker": "You", "en": "An e-book copy works! How long can I check out printed books normally?", "zh": "电子版太好了！纸质书一般能借多久？"},
            {"speaker": "Librarian", "en": "Standard loans are three weeks, and you can renew twice online if nobody waits.", "zh": "常规借期是三周，没人预约的话可以在网上续借两次。"},
        ],
        "key_phrases": [
            {"en": "checked out", "zh": "被借出"},
            {"en": "place a hold", "zh": "预约占座/留书"},
            {"en": "renew online", "zh": "在线续借"},
        ],
    },
    {
        "title": "教授答疑 Office Hours (Discussing an Essay)",
        "scene": "校园学术",
        "level": "中高级 B2",
        "lines": [
            {"speaker": "You", "en": "Hi Professor Reed, do you have a minute to go over my essay outline?", "zh": "Reed 教授您好，方便花几分钟帮我看一下论文大纲吗？"},
            {"speaker": "Professor", "en": "Come on in! Your thesis statement is clear, though the scope feels slightly broad.", "zh": "进来吧！你的核心论点很明确，只是研究范围稍微有点泛。"},
            {"speaker": "You", "en": "Would narrowing it down to post-2020 urban policy make the argument stronger?", "zh": "如果缩小到 2020 年后的城市政策，论证会更有说服力吗？"},
            {"speaker": "Professor", "en": "Yes, much sharper. Just back up each claim with two empirical studies.", "zh": "是的，犀利得多。每条论断配合两项实证研究数据就好。"},
        ],
        "key_phrases": [
            {"en": "thesis statement", "zh": "中心论点"},
            {"en": "narrow it down to...", "zh": "把范围缩小到……"},
            {"en": "empirical studies", "zh": "实证研究"},
        ],
    },
    {
        "title": "小组课题分工讨论 (Group Project Sync)",
        "scene": "校园学术",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Teammate", "en": "Our presentation slides are due Thursday. How should we divide the workload?", "zh": "我们的演示文稿周四交，咱们怎么分工比较好？"},
            {"speaker": "You", "en": "I'm happy to handle the data charts and summary, if someone takes literature review.", "zh": "如果有人负责文献综述，我很乐意包揽数据图表和总结。"},
            {"speaker": "Teammate", "en": "Count me in for literature review. Can we do a quick rehearsal Wednesday night?", "zh": "文献综述算我一个。周三晚上我们合练彩排一下可以吗？"},
            {"speaker": "You", "en": "Sounds like a solid plan. Let's drop everything into a shared folder by Tuesday.", "zh": "计划很靠谱。周二前我们把各自内容先放进共享文件夹。"},
        ],
        "key_phrases": [
            {"en": "divide the workload", "zh": "分配工作量"},
            {"en": "Count me in", "zh": "算我一个"},
            {"en": "do a quick rehearsal", "zh": "快速彩排一次"},
        ],
    },
    {
        "title": "药店购买非处方药 (At the Pharmacy)",
        "scene": "生活实用",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Pharmacist", "en": "Hi, how can I help you today?", "zh": "你好，今天需要买什么药？"},
            {"speaker": "You", "en": "I have seasonal allergies—mostly sneezing and itchy eyes. What do you recommend?", "zh": "我有点季节性过敏——主要是一直打喷嚏和眼睛痒，您推荐什么药？"},
            {"speaker": "Pharmacist", "en": "I'd recommend a non-drowsy antihistamine tablet plus soothing eye drops.", "zh": "我建议吃不含嗜睡成分的抗组胺药片，再配点舒缓眼药水。"},
            {"speaker": "You", "en": "Does this tablet make me sleepy while driving?", "zh": "这片药开车的时候会犯困吗？"},
            {"speaker": "Pharmacist", "en": "Not at all—this formula is specifically non-drowsy. Just take one pill every 24 hours.", "zh": "完全不会，这是专门防嗜睡配方。每 24 小时吃一片就行。"},
        ],
        "key_phrases": [
            {"en": "seasonal allergies", "zh": "季节性过敏"},
            {"en": "non-drowsy", "zh": "不犯困 / 无嗜睡配方"},
            {"en": "every 24 hours", "zh": "每 24 小时一次"},
        ],
    },
    {
        "title": "理发店造型沟通 (At the Hair Salon)",
        "scene": "生活实用",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Stylist", "en": "What are we doing with your hair today?", "zh": "今天头发想怎么剪？"},
            {"speaker": "You", "en": "Just a trim, please—take about an inch off the ends and thin out the sides.", "zh": "稍微修剪一下就行——发尾剪短大概一英寸，两侧稍微打薄一点。"},
            {"speaker": "Stylist", "en": "Got it. Do you want me to keep the top long enough to style back?", "zh": "明白。头顶部分要保留足够长度方便往后抓造型吗？"},
            {"speaker": "You", "en": "Yes, keep plenty of length on top, and fade the back cleanly.", "zh": "对，头顶留长一点，后面推干净渐变就行。"},
        ],
        "key_phrases": [
            {"en": "just a trim", "zh": "只修剪一下"},
            {"en": "thin out the sides", "zh": "两侧打薄"},
            {"en": "keep plenty of length", "zh": "多保留些长度"},
        ],
    },
    {
        "title": "公寓报修与物业沟通 (Reporting Maintenance)",
        "scene": "生活实用",
        "level": "中级 B1",
        "lines": [
            {"speaker": "You", "en": "Hi, I'm in apartment 502. My kitchen sink has been leaking steadily since this morning.", "zh": "你好，我是 502 室的住户。厨房水槽从今早开始一直在漏水。"},
            {"speaker": "Manager", "en": "Sorry about that! Is the water shut-off valve holding, or is it flooding the floor?", "zh": "抱歉给您添麻烦了！下面阀门还能关紧吗，还是已经漏了一地？"},
            {"speaker": "You", "en": "I put a bucket underneath so it's contained, though the cabinet is damp.", "zh": "我在下面放了个水桶暂时接住了，但橱柜已经受潮了。"},
            {"speaker": "Manager", "en": "I'll send a plumber over around 2 PM. Is it okay if they enter with a spare key?", "zh": "我下午两点左右派水电工过去。如果您不在，可以用备用钥匙开门维修吗？"},
            {"speaker": "You", "en": "Yes, permission granted—I'll be home anyway. Thanks for acting quickly!", "zh": "可以，我授权进入——不过我下午会在家。谢谢你们处理这么快！"},
        ],
        "key_phrases": [
            {"en": "has been leaking", "zh": "一直在漏水"},
            {"en": "put a bucket underneath", "zh": "在下面放个桶接住"},
            {"en": "send a plumber over", "zh": "派水电工过去"},
        ],
    },
]

EXTRA_GRAMMAR = [
    {
        "title": "一般过去时 vs 过去进行时",
        "category": "时态基础",
        "level": "初级 A2",
        "summary": "一般过去时描述过去完成的单个动作；过去进行时（was/were + doing）常作背景铺垫，描述过去某刻正在进行的动作。",
        "explanation": "1. 一般过去时（did）：昨晚看完了电影、昨天买了咖啡。\n2. 过去进行时（was/were doing）：昨晚八点正在看电影；或“当某事正在发生时，另一件事突然发生”（When + 过去进行, 一般过去 / While + 过去进行）。\n3. 不规则动词过去式需重点记忆（go-went, see-saw, take-took）。",
        "examples": [
            {"en": "I was cooking dinner when the phone rang.", "zh": "电话响的时候，我正在做晚饭。"},
            {"en": "We walked along the river and watched the sunset yesterday.", "zh": "昨天我们沿着河边散步并看了日落。"},
        ],
        "common_mistakes": [
            "错误：I was go home when it rained. → 正确：I was going home when it rained.（be 动词后接 V-ing，不能直接接动词原形）",
        ],
    },
    {
        "title": "将来表达三分法 (will / be going to / doing)",
        "category": "核心时态",
        "level": "初级 A2",
        "summary": "英语谈论未来并不只有 will：临时决定用 will，早已打算或有明显迹象用 be going to，日程安排极确定的出行常用现在进行时。",
        "explanation": "1. will + V原形：说话瞬间做的决定（It's cold, I'll close the window.）、承诺或客观预测。\n2. be going to + V原形：事先盘算好的意图，或眼下有征兆即将发生（Look at those dark clouds—it's going to rain.）。\n3. be V-ing：已定好时间地点的个人日程（We are flying to Tokyo tomorrow morning.）。",
        "examples": [
            {"en": "Hold on, I'll grab a pen and write that down.", "zh": "稍等，我这就拿支笔把它记下来。（临时反应）"},
            {"en": "I'm going to review fifty words tonight.", "zh": "我今晚打算复习五十个单词。（预先计划）"},
            {"en": "She is meeting her advisor at 3 PM.", "zh": "她下午三点要见导师。（既定日程）"},
        ],
        "common_mistakes": [
            "错误：I am going to answer the door! Wait, no—I think it will rain soon (looking at dark clouds). → 正确：Look at those dark clouds—it's going to rain!（有眼下明显征兆或早有计划时用 be going to；临时起意才用 will）",
        ],
    },
    {
        "title": "过去完成时与完成进行时 (had done / have been doing)",
        "category": "高级表达",
        "level": "中高级 B2",
        "summary": "过去完成时表示“过去的过去”；现在完成进行时（have been doing）强调动作从过去持续到现在且此刻仍在继续或刚刚结束。",
        "explanation": "1. 过去完成时（had + 过去分词）：在过去某一事件之前就已经完成（By the time we arrived, the train had already left.）。\n2. 现在完成进行时（have/has been + V-ing）：强调“一直在做、过程和持续时长”（I have been studying English for two hours.）。",
        "examples": [
            {"en": "By the time the meeting started, I had already sent the slides.", "zh": "会议开始时，我早就把演示文稿发过去了。"},
            {"en": "She has been practicing pronunciation all morning.", "zh": "她整个上午都在练习发音。"},
        ],
        "common_mistakes": [
            "错误：By the time we arrived, the train already left. → 正确：By the time we arrived, the train had already left.（“过去的过去”需要过去完成时 had done，句中需有过去参照点）",
        ],
    },
    {
        "title": "冠词精准区分 (a / an / the / 零冠词)",
        "category": "核心句法",
        "level": "初级 A2",
        "summary": "中文没有冠词但英语极敏感：泛指首次提及用 a/an（看发音元音而非字母），特指或双方都知道用 the，泛指复数/抽象/三餐/球类用零冠词。",
        "explanation": "1. a vs an 看音素：an hour（h不发音，元音开头）、a university（/juː/ 半元音开头）。\n2. the：上文提过的、世上独一无二（the sun）、双方心照不宣（Close the door.）、乐器前（play the piano）、最高级前。\n3. 零冠词：三餐（have breakfast）、球类（play basketball）、语言学科、泛指复数名词（Books are helpful.）。",
        "examples": [
            {"en": "I bought an umbrella, and the umbrella is really sturdy.", "zh": "我买了一把伞，这把伞非常结实。（首次 a/an，再提用 the）"},
            {"en": "He studies computer science at a university in Beijing.", "zh": "他在北京一所大学学习计算机科学。（university 读 /juː/ 用 a）"},
        ],
        "common_mistakes": [
            "错误：I usually have the lunch at noon. → 正确：I usually have lunch at noon.（三餐前不加冠词）",
        ],
    },
    {
        "title": "可数/不可数与主谓一致",
        "category": "核心句法",
        "level": "初级 A2",
        "summary": "information, advice, equipment, news 等在英语里都是不可数名词，不能加 -s 也不能配 many/are，必须用 much / a piece of。",
        "explanation": "1. 常见高频不可数坑词：advice（建议）, information（信息）, news（消息）, luggage/baggage（行李）, feedback（反馈）, traffic（交通）, furniture（家具）。\n2. 主谓一致就近与核心词：The number of + 复数 → 单数谓语（……的数量）；A number of + 复数 → 复数谓语（许多）；动名词作主语（Reading books）→ 单数谓语。",
        "examples": [
            {"en": "Thank you for giving me such useful advice.", "zh": "谢谢你给了我这么有用的建议。（advice 不可数）"},
            {"en": "The number of daily users is growing steadily.", "zh": "日活跃用户的数量正在稳步增长。（the number 作主语用 is）"},
        ],
        "common_mistakes": [
            "错误：many informations / two advices → 正确：a lot of information / two pieces of advice",
        ],
    },
    {
        "title": "英语五大基本句型",
        "category": "句型结构",
        "level": "初级 A2",
        "summary": "所有英语句子无论多长，骨架都脱不开五大基本句型；理清及物与不及物动词决定句子通顺与否。",
        "explanation": "1. S + V（主谓）：Birds fly.\n2. S + V + O（主谓宾）：I love coffee.\n3. S + Link-V + P（主系表）：The soup tastes good.（感官动词 look/sound/smell/taste/feel 后接形容词作表语！）\n4. S + V + IO + DO（双宾语）：She sent me an email.（= sent an email to me）\n5. S + V + O + OC（宾补）：Listening makes me confident.",
        "examples": [
            {"en": "The coffee smells amazing this morning.", "zh": "这咖啡今天早上闻起来太香了。（smell 作系动词接形容词）"},
            {"en": "Consistent practice makes English feel natural.", "zh": "持续练习让说英语感觉自然顺畅。（make + 宾语 + 宾补）"},
        ],
        "common_mistakes": [
            "错误：You look happily today. → 正确：You look happy today.（look 是系动词，接形容词 happy，不能用副词）",
        ],
    },
    {
        "title": "疑问句与反意疑问句",
        "category": "交际语法",
        "level": "初级 A2",
        "summary": "记住疑问词作宾语时的“语序不变”原则，以及反意疑问句“前肯后否、前否后肯”的地道口语确认法。",
        "explanation": "1. 间接疑问句语序要恢复陈述句序：Could you tell me where the station IS?（不要写成 where is the station!）\n2. 反意疑问句：前肯后否（It's chilly today, isn't it?）；前否后肯（You haven't seen my bag, have you?）。\n3. 注意否定回答规则：只要事实是否定就一律用 No（Aren't you going? — No, I'm staying home. 不，我不去）。",
        "examples": [
            {"en": "Do you know what time the library closes?", "zh": "你知道图书馆几点关门吗？（宾语从句用陈述语序）"},
            {"en": "You finished the report already, didn't you?", "zh": "你已经写完报告了，对吧？"},
        ],
        "common_mistakes": [
            "错误：Could you tell me how can I get there? → 正确：Could you tell me how I can get there?",
        ],
    },
    {
        "title": "There be 存在句与 It 形式主语",
        "category": "句型结构",
        "level": "初级 A2",
        "summary": "中文常说“有很多人喜欢……”，切忌直接套成 There are many people like...，而是 There are many people who like... 或直接 Many people like...。",
        "explanation": "1. There be 句型只表示“某处存在某物”，一句话不能同时出现 there be 和另一个主动词作双谓语。\n2. It 形式主语避开“头重脚轻”：It takes + 时间 + to do sth.（做某事花费多长时间）；It is + adj. + (for/of sb.) + to do sth.。",
        "examples": [
            {"en": "There is a quiet cafe across the street.", "zh": "街对面有一家很安静的咖啡馆。"},
            {"en": "It takes about twenty minutes to walk to the station.", "zh": "走到车站大概需要二十分钟。"},
        ],
        "common_mistakes": [
            "错误：There have many students in the hall. → 正确：There are many students in the hall.（不能用 there have）",
        ],
    },
    {
        "title": "高频核心短语动词 (Phrasal Verbs)",
        "category": "高频搭配",
        "level": "中级 B1",
        "summary": "短语动词是地道口语的灵魂（如 look forward to, put off, figure out），代词作宾语时必须放在可拆短语中间（turn it off）。",
        "explanation": "1. 必考可拆规律：名词放中间或末尾均可（turn off the light / turn the light off），但代词 it/them 只能放中间（turn it off，不能说 turn off it）。\n2. 高频必背：figure out（搞明白）、put off（推迟）、look forward to + doing（期待）、run out of（用光）、catch up on（补上/跟上）。",
        "examples": [
            {"en": "Don't forget to turn it off before leaving the office.", "zh": "离开办公室前别忘了把它关掉。（代词放中间）"},
            {"en": "I'm really looking forward to visiting your studio.", "zh": "我非常期待去参观你的工作室。（to 是介词，后接 V-ing）"},
        ],
        "common_mistakes": [
            "错误：I look forward to hear from you. → 正确：I look forward to hearing from you.",
        ],
    },
    {
        "title": "易混搭配：to do vs doing 语义翻转",
        "category": "核心句法",
        "level": "中级 B1",
        "summary": "remember, forget, stop, try 这几个常见动词，后面接 to do 还是 doing 意思完全不一样！",
        "explanation": "1. remember/forget + to do（记得/忘了要去做——还没做）；+ doing（记得/忘了曾经做过——已发生）。\n2. stop + to do（停下手头事去做另一件事）；+ doing（停止正在做的事）。\n3. try + to do（努力/试图完成）；+ doing（换个方法试一试看效果）。",
        "examples": [
            {"en": "Please remember to lock the door before bed.", "zh": "睡前请记得把门锁好。（还没锁）"},
            {"en": "I clearly remember locking the door ten minutes ago.", "zh": "我清楚地记得十分钟前锁过门了。（锁过了）"},
            {"en": "Try restarting the app if the screen freezes.", "zh": "如果卡住了，试试看重启一下应用。（尝试某种做法）"},
        ],
        "common_mistakes": [
            "错误：You should stop to smoke for your health. → 正确：You should stop smoking for your health.（stop doing 停止正在做的事；stop to do 停下来去做另一件事）",
        ],
    },
    {
        "title": "使役动词与感官动词 (make / let / have / get)",
        "category": "核心句法",
        "level": "中级 B1",
        "summary": "表达“让某人做某事”或“请人把某事做完（被动）”，关键在于分清什么时候省掉 to、什么时候用过去分词 done。",
        "explanation": "1. 主动不带 to：make / let / have + sb. + do sth.（My teacher made me repeat the sentence.）。\n2. get 必须带 to：get + sb. + to do sth.。\n3. 找人修/剪（受事被动）：have / get + sth. + done（I had my hair cut yesterday. 昨天我去理了发）。\n4. 注意：被动语态中 make 还原 to（be made to do）。",
        "examples": [
            {"en": "Listening to native audio makes my pronunciation sound smoother.", "zh": "听母语音频让我的发音听起来更顺滑。"},
            {"en": "I need to get my laptop repaired this weekend.", "zh": "我这周末得去把笔记本电脑修一下。"},
        ],
        "common_mistakes": [
            "错误：He let me to go early. → 正确：He let me go early.（make/let/have 主动时不加 to）",
        ],
    },
    {
        "title": "时间与条件状语从句（主将从现）",
        "category": "复合句",
        "level": "初级 A2",
        "summary": "英文在 if, when, unless, as soon as, until 引导的时间/条件从句里，即便讲将来的事，从句也要用一般现在时！",
        "explanation": "1. 口诀“主将从现”：主句用 will/情态动词/祈使句，从句用一般现在时表将来。\n2. unless = if ... not（除非……否则……）。\n3. not ... until ...（直到……才……）：瞬时动作配 not...until，延续动作直接配 until。",
        "examples": [
            {"en": "Call me as soon as you arrive at the airport.", "zh": "你一到机场就给我打电话。"},
            {"en": "You won't improve your speaking unless you practice out loud.", "zh": "除非你大声开口练习，否则口语很难提高。"},
        ],
        "common_mistakes": [
            "错误：If it will rain tomorrow, we will stay indoors. → 正确：If it rains tomorrow, we will stay indoors.",
        ],
    },
    {
        "title": "让步与原因状语从句 (since / even though / no matter)",
        "category": "复合句",
        "level": "中级 B1",
        "summary": "掌握 since（既然/自从）、even though（即使）和 no matter wh- / wh-ever 让步表达，写作和汇报逻辑更高级。",
        "explanation": "1. 原因力度对比：because（直接回答 why，语气最强）> since / as（双方已知的前提“既然”）> for（补充解释）。\n2. 让步句：even though / even if + 完整句子；no matter what/how/where（= whatever / however / wherever）。",
        "examples": [
            {"en": "Since everyone is here, let's begin the meeting.", "zh": "既然大家都到了，我们开始开会吧。"},
            {"en": "No matter how busy you are, try to review for ten minutes daily.", "zh": "不管多忙，尽量每天复习十分钟。"},
        ],
        "common_mistakes": [
            "错误：No matter what happens is fine with me. → 正确：Whatever happens is fine with me.（no matter what 只能引导状语从句；作主语或宾语必须用 whatever）",
        ],
    },
    {
        "title": "直接引语与间接引语 (Reported Speech)",
        "category": "句型结构",
        "level": "中级 B1",
        "summary": "职场转述别人的原话时（He said that...），主句为过去时，从句通常要向后退一个时态，并注意人称、时间和语序切换。",
        "explanation": "1. 时态后移规律：am/is → was；will → would；can → could；did/have done → had done。\n2. 真理/客观规律不必后移（She told us that practice builds fluency.）。\n3. 转述疑问句：ask if/whether + 陈述语序；转述祈使句：tell/ask sb. (not) to do sth.。",
        "examples": [
            {"en": "She told me that she would arrive around noon.", "zh": "她告诉我她大概中午会到。（will → would）"},
            {"en": "The coach asked us not to rush through tricky words.", "zh": "教练要求我们遇到难词时不要匆匆含糊带过。"},
        ],
        "common_mistakes": [
            "错误：He said me that he was busy. → 正确：He told me that he was busy.（say 接人用 say to me，tell 直接接 me）",
        ],
    },
    {
        "title": "形容词与副词位置、-ed vs -ing 辨析",
        "category": "修饰表达",
        "level": "初级 A2",
        "summary": "-ing 形容词描述事物“令人……的”；-ed 形容词描述人“感到……的”；频度副词放 be 动词后、实义动词前。",
        "explanation": "1. exciting（令人兴奋的课程）vs excited（感到兴奋的人）；confusing vs confused。\n2. 频度副词位置：always, usually, often, never 放在 be/情态动词/助动词之后，实义动词之前（She is always punctual. / I rarely eat fast food.）。\n3. 形容词修饰不定代词（something, anything, nothing）必须后置（something interesting）。",
        "examples": [
            {"en": "This interactive lesson is super engaging, so I feel excited to continue.", "zh": "这节互动课很有吸引力，所以我很有动力继续学下去。"},
            {"en": "Did you find anything useful in today's vocabulary deck?", "zh": "在今天的词汇卡片里发现什么有用的词了吗？（形容词后置）"},
        ],
        "common_mistakes": [
            "错误：I am interesting in English. → 正确：I am interested in English.",
        ],
    },
    {
        "title": "分词作状语与独立主格 (高级精简句)",
        "category": "高级表达",
        "level": "中高级 B2",
        "summary": "用 V-ing（主动/同时）或 V-ed（被动/完成）开头的短语替换冗长状语从句，是书面报告和高分口语的核心提分句型。",
        "explanation": "1. 核心前提：分词动作的逻辑主语必须和主句主语保持一致！\n2. 主动/同时用 V-ing（Working from home, she saves an hour of commuting.）。\n3. 被动/状态用 V-ed（Compared with last year, our efficiency doubled.）。\n4. 前后主语不同时加独立主格（Weather permitting, we'll go hiking.）。",
        "examples": [
            {"en": "Given the tight deadline, we prioritized the core features first.", "zh": "考虑到截止时间紧张，我们优先保障了核心功能。"},
            {"en": "Walking into the room, he greeted everyone warmly.", "zh": "走进房间时，他热情地和大家打招呼。"},
        ],
        "common_mistakes": [
            "错误：Walking down the street, the building looked huge.（大楼不能自己走路！）→ 正确：Walking down the street, I saw a huge building.",
        ],
    },
    {
        "title": "情态动词+have done（对过去的推测与遗憾）",
        "category": "高级表达",
        "level": "中高级 B2",
        "summary": "must/might/couldn't + have done 对过去已经发生的事作把握度推测；should/could + have done 表达本该做却没做的遗憾。",
        "explanation": "1. 过去推测：\n- must have done：过去肯定做过（The ground is wet; it must have rained.）\n- might/may have done：过去可能做过\n- can't/couldn't have done：过去绝不可能做过\n2. 遗憾与责备：\n- should have done：本应该做某事（结果没做）\n- shouldn't have done：本不该做某事（结果做了）。",
        "examples": [
            {"en": "You must have worked hard to speak so fluently.", "zh": "你能说得这么流利，之前肯定下过苦功。"},
            {"en": "I should have backed up the file earlier!", "zh": "我早该提前备份那个文件的！（后悔遗憾）"},
        ],
        "common_mistakes": [
            "错误：He mustn't have finished the task in ten minutes. → 正确：He couldn't have finished the task in ten minutes.（对过去进行否定推测用 can't / couldn't have done，不用 mustn't have done）",
        ],
    },
    {
        "title": "地道口语省略与交际高频反应句",
        "category": "写作与口语",
        "level": "中级 B1",
        "summary": "母语者在日常对话中大量使用短句反应和上下文省略（So do I / I hope so / Sounds good），比逐字重复更自然。",
        "explanation": "1. 赞同与附和：I love coffee. — So do I. / Me too.（否定附和：Neither do I. / Me neither.）。\n2. 用 so / not 代替整句宾语：I think so / I hope not / I guess so。\n3. 对话自然反应短句：Makes sense（有道理）、Fair enough（也对/可以理解）、No worries（没事/别客气）、You bet（当然/没问题）。",
        "examples": [
            {"en": "Will the package arrive today? I hope so!", "zh": "包裹今天能到吗？希望如此！"},
            {"en": "Sorry for the late reply. No worries at all, makes total sense.", "zh": "抱歉回复晚了。完全没事，完全理解。"},
        ],
        "common_mistakes": [
            "错误：Will it rain tomorrow? — I don't hope so. → 正确：Will it rain tomorrow? — I hope not.（表达“我希望不要这样”不说 I don't hope so，而说 I hope not）",
        ],
    },
]
