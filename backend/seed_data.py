"""Curated built-in English vocabulary, situational dialogues, and grammar lessons."""

SEED_WORDS = [
    # 日常高频 (Daily Essentials)
    ("authentic", "/ɔːˈθentɪk/", "adj.", "真实的；地道的", "We found an authentic Italian restaurant downtown.", "我们在市中心找到了一家地道的意大利餐厅。", "日常高频", 2),
    ("consistent", "/kənˈsɪstənt/", "adj.", "持续的；一致的", "Consistent practice is the key to mastering a language.", "持续练习是掌握一门语言的关键。", "日常高频", 2),
    ("efficient", "/ɪˈfɪʃnt/", "adj.", "高效的；有能力的", "Using flashcards is an efficient way to review vocabulary.", "使用记忆卡片是一种高效的复习词汇方式。", "日常高频", 1),
    ("flexible", "/ˈfleksəbl/", "adj.", "灵活的；有弹性的", "My schedule is quite flexible this week.", "我这周的日程安排相当灵活。", "日常高频", 1),
    ("gradually", "/ˈɡrædʒuəli/", "adv.", "逐渐地；逐步地", "Your listening skills will gradually improve over time.", "随着时间的推移，你的听力会逐渐提高。", "日常高频", 1),
    ("hesitate", "/ˈhezɪteɪt/", "v.", "犹豫；迟疑", "Don't hesitate to ask if you have any questions.", "如果有任何问题，请不要犹豫尽管问。", "日常高频", 2),
    ("immerse", "/ɪˈmɜːrs/", "v.", "沉浸；使专心于", "Try to immerse yourself in English podcasts every morning.", "试着每天早上沉浸在英语播客中。", "日常高频", 2),
    ("motivation", "/ˌməʊtɪˈveɪʃn/", "n.", "动力；动机", "Setting small goals helps keep your motivation high.", "设定小目标有助于保持高昂的学习动力。", "日常高频", 1),
    ("obvious", "/ˈɒbviəs/", "adj.", "明显的；显而易见的", "It is obvious that she has practiced speaking a lot.", "很明显，她练习了很多口语。", "日常高频", 1),
    ("persuade", "/pəˈsweɪd/", "v.", "说服；劝说", "He managed to persuade his friend to join the study group.", "他成功说服了朋友加入学习小组。", "日常高频", 2),
    ("practical", "/ˈpræktɪkl/", "adj.", "实用的；实际的", "This handbook offers practical tips for daily conversation.", "这本手册提供了日常对话的实用技巧。", "日常高频", 1),
    ("reliable", "/rɪˈlaɪəbl/", "adj.", "可靠的；可信赖的", "She is a reliable partner for language exchange.", "她是一位可靠的语言交换伙伴。", "日常高频", 1),
    ("routine", "/ruːˈtiːn/", "n.", "日常惯例；常规", "Reading for twenty minutes is part of my evening routine.", "阅读二十分钟是我晚间日常的一部分。", "日常高频", 1),
    ("subtle", "/ˈsʌtl/", "adj.", "微妙的；细微的", "There is a subtle difference between these two synonyms.", "这两个近义词之间存在细微的差别。", "日常高频", 3),
    ("vivid", "/ˈvɪvɪd/", "adj.", "生动的；鲜明的", "The speaker gave a vivid description of her hometown.", "演讲者对她的家乡进行了生动的描述。", "日常高频", 2),

    # 职场商务 (Business & Career)
    ("agenda", "/əˈdʒendə/", "n.", "议程；日程表", "Let's review the first item on today's agenda.", "我们先来看一下今天议程的第一项。", "职场商务", 2),
    ("collaborate", "/kəˈlæbəreɪt/", "v.", "合作；协作", "Our design and engineering teams collaborate closely.", "我们的设计和工程团队紧密合作。", "职场商务", 2),
    ("consensus", "/kənˈsensəs/", "n.", "共识；一致意见", "After an hour of discussion, we reached a consensus.", "经过一小时的讨论，我们达成了共识。", "职场商务", 3),
    ("deadline", "/ˈdedlaɪn/", "n.", "截止日期", "We need to submit the proposal before Friday's deadline.", "我们需要在周五截止日期前提交方案。", "职场商务", 1),
    ("delegate", "/ˈdelɪɡeɪt/", "v.", "委派；授权", "A good manager knows how to delegate tasks effectively.", "优秀的管理者懂得如何有效地委派任务。", "职场商务", 3),
    ("feedback", "/ˈfiːdbæk/", "n.", "反馈；意见", "Thank you for your constructive feedback on my report.", "感谢你对我报告提出的建设性反馈。", "职场商务", 1),
    ("implement", "/ˈɪmplɪment/", "v.", "实施；执行", "We plan to implement the new workflow next month.", "我们计划下个月实施新的工作流程。", "职场商务", 2),
    ("initiative", "/ɪˈnɪʃətɪv/", "n.", "主动性；新举措", "She took the initiative to organize the weekly review.", "她主动发起了每周复盘会。", "职场商务", 3),
    ("negotiate", "/nɪˈɡəʊʃieɪt/", "v.", "谈判；协商", "They are trying to negotiate a better contract.", "他们正试图协商一份更好的合同。", "职场商务", 2),
    ("outcome", "/ˈaʊtkʌm/", "n.", "结果；成果", "Everyone was satisfied with the outcome of the meeting.", "大家对会议的结果都很满意。", "职场商务", 2),
    ("priority", "/praɪˈɒrəti/", "n.", "优先事项", "Improving customer support is our top priority.", "提升客户支持是我们的首要任务。", "职场商务", 2),
    ("proposal", "/prəˈpəʊzl/", "n.", "提议；方案", "The client approved our project proposal yesterday.", "客户昨天批准了我们的项目方案。", "职场商务", 2),
    ("quarterly", "/ˈkwɔːtəli/", "adj.", "季度的", "We hold a quarterly review to track our progress.", "我们每季度举行一次复盘来追踪进度。", "职场商务", 2),
    ("resolve", "/rɪˈzɒlv/", "v.", "解决；下决心", "The support team helped resolve the issue quickly.", "支持团队迅速帮助解决了这个问题。", "职场商务", 2),
    ("streamline", "/ˈstriːmlaɪn/", "v.", "精简；使高效", "Automation helped us streamline the approval process.", "自动化帮助我们精简了审批流程。", "职场商务", 3),

    # 旅行出行 (Travel & Exploration)
    ("accommodation", "/əˌkɒməˈdeɪʃn/", "n.", "住宿；住处", "Did you book your accommodation near the train station?", "你在火车站附近预订住宿了吗？", "旅行出行", 2),
    ("boarding", "/ˈbɔːdɪŋ/", "n.", "登机；上船", "Please have your boarding pass ready at Gate 12.", "请在12号登机口准备好您的登机牌。", "旅行出行", 1),
    ("currency", "/ˈkʌrənsi/", "n.", "货币；通货", "You can exchange foreign currency at the airport.", "你可以在机场兑换外币。", "旅行出行", 2),
    ("customs", "/ˈkʌstəmz/", "n.", "海关", "It took twenty minutes to go through customs.", "过海关花了二十分钟。", "旅行出行", 1),
    ("departure", "/dɪˈpɑːtʃər/", "n.", "出发；离开", "Check the departure board for any gate changes.", "查看出发信息牌确认登机口是否有变动。", "旅行出行", 2),
    ("destination", "/ˌdestɪˈneɪʃn/", "n.", "目的地", "Kyoto is a popular destination in autumn.", "京都秋天是一个热门目的地。", "旅行出行", 1),
    ("excursion", "/ɪkˈskɜːʃn/", "n.", "短途旅行；远足", "We booked a day excursion to the nearby island.", "我们预订了去附近海岛的一日游。", "旅行出行", 3),
    ("itinerary", "/aɪˈtɪnərəri/", "n.", "行程表；旅行路线", "Let me share our five-day travel itinerary with you.", "让我把我们的五天旅行行程表发给你。", "旅行出行", 3),
    ("luggage", "/ˈlʌɡɪdʒ/", "n.", "行李", "You can leave your luggage at the hotel reception.", "你可以把行李寄存在酒店前台。", "旅行出行", 1),
    ("navigate", "/ˈnævɪɡeɪt/", "v.", "导航；找路", "Offline maps make it easy to navigate a new city.", "离线地图让你在新城市找路变得很容易。", "旅行出行", 2),
    ("recommend", "/ˌrekəˈmend/", "v.", "推荐；建议", "Could you recommend a good local cafe nearby?", "你能推荐一家附近不错的本地咖啡馆吗？", "旅行出行", 1),
    ("reservation", "/ˌrezəˈveɪʃn/", "n.", "预订；预约", "I have a reservation under the name Zhang.", "我以 Zhang 的名字预订了房间。", "旅行出行", 2),
    ("scenery", "/ˈsiːnəri/", "n.", "风景；景色", "The mountain scenery along the train route was breathtaking.", "火车沿线的山景美得令人惊叹。", "旅行出行", 2),
    ("souvenir", "/ˌsuːvəˈnɪər/", "n.", "纪念品", "I bought a handmade mug as a souvenir.", "我买了一个手工马克杯作为纪念品。", "旅行出行", 2),
    ("transit", "/ˈtrænzɪt/", "n.", "中转；运输", "Public transit in this city is clean and punctual.", "这座城市的公共交通既干净又准时。", "旅行出行", 2),

    # 学术进阶 (Academic & Expression)
    ("abstract", "/ˈæbstrækt/", "adj.", "抽象的；n. 摘要", "Please read the abstract before diving into the full paper.", "在深入阅读全文前，请先阅读摘要。", "学术进阶", 2),
    ("accurate", "/ˈækjərət/", "adj.", "精确的；准确的", "Make sure your translation is accurate and natural.", "确保你的翻译既准确又自然。", "学术进阶", 1),
    ("analyze", "/ˈænəlaɪz/", "v.", "分析；解析", "We need to analyze the data before drawing a conclusion.", "在得出结论之前，我们需要先分析数据。", "学术进阶", 2),
    ("comprehensive", "/ˌkɒmprɪˈhensɪv/", "adj.", "全面的；综合的", "The textbook provides a comprehensive overview of grammar.", "这本教材提供了全面的语法概览。", "学术进阶", 3),
    ("context", "/ˈkɒntekst/", "n.", "语境；上下文", "You can often guess a word's meaning from context.", "你通常可以根据上下文猜测词义。", "学术进阶", 2),
    ("contrast", "/ˈkɒntrɑːst/", "n./v.", "对比；对照", "In contrast to yesterday, today's weather is mild.", "与昨天相比，今天的天气很温和。", "学术进阶", 2),
    ("crucial", "/ˈkruːʃl/", "adj.", "至关重要的", "Pronunciation plays a crucial role in clear communication.", "发音在清晰沟通中起着至关重要的作用。", "学术进阶", 2),
    ("demonstrate", "/ˈdemənstreɪt/", "v.", "证明；演示", "The experiment clearly demonstrates how the rule works.", "这个实验清楚地演示了该规则是如何运作的。", "学术进阶", 2),
    ("emphasize", "/ˈemfəsaɪz/", "v.", "强调；着重", "The teacher emphasized the importance of active recall.", "老师强调了主动回忆的重要性。", "学术进阶", 2),
    ("evaluate", "/ɪˈvæljueɪt/", "v.", "评估；评价", "Weekly quizzes help you evaluate your learning progress.", "每周测验有助于你评估学习进度。", "学术进阶", 2),
    ("hypothesis", "/haɪˈpɒθəsɪs/", "n.", "假设；假说", "They tested their hypothesis through three experiments.", "他们通过三个实验检验了他们的假设。", "学术进阶", 3),
    ("interpret", "/ɪnˈtɜːprɪt/", "v.", "解释；口译", "How do you interpret this sentence in the article?", "你如何理解文章中的这句话？", "学术进阶", 2),
    ("perspective", "/pəˈspektɪv/", "n.", "视角；观点", "Learning a new language gives you a fresh perspective.", "学习一门新语言会给你带来全新的视角。", "学术进阶", 2),
    ("significant", "/sɪɡˈnɪfɪkənt/", "adj.", "显著的；重要的", "There has been a significant improvement in her writing.", "她的写作水平有了显著提高。", "学术进阶", 2),
    ("summarize", "/ˈsʌməraɪz/", "v.", "总结；概括", "Try to summarize the story in three sentences.", "试着用三句话总结这个故事。", "学术进阶", 1),
]

from backend.seed_words_extra import EXTRA_WORDS as _EXTRA_WORDS

_seen_words = {w[0].strip().lower() for w in SEED_WORDS}
for _item in _EXTRA_WORDS:
    _key = _item[0].strip().lower()
    if _key not in _seen_words:
        _seen_words.add(_key)
        SEED_WORDS.append(_item)

import gzip as _gzip
import json as _json
import sys as _sys
from pathlib import Path as _Path

_ecdict_candidates = [
    _Path(__file__).resolve().parent / "ecdict_core.json.gz",
    _Path(getattr(_sys, "_MEIPASS", _Path(__file__).resolve().parent.parent)) / "backend" / "ecdict_core.json.gz",
]
for _ecdict_gz in _ecdict_candidates:
    if _ecdict_gz.is_file():
        with _gzip.open(_ecdict_gz, "rt", encoding="utf-8") as _f:
            for _row in _json.load(_f):
                _key = _row[0].strip().lower()
                if _key not in _seen_words:
                    _seen_words.add(_key)
                    SEED_WORDS.append((_row[0], _row[1], _row[2], _row[3], "", "", _row[4], _row[5]))
        break

SEED_DIALOGUES = [
    {
        "title": "咖啡店点单 (Ordering at a Cafe)",
        "scene": "日常出行",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Barista", "en": "Hi there! What can I get started for you today?", "zh": "你好！今天想点些什么？"},
            {"speaker": "You", "en": "Hi! Could I get an iced oat latte, please?", "zh": "你好！请给我来一杯冰燕麦拿铁。"},
            {"speaker": "Barista", "en": "Sure thing. What size would you like—regular or large?", "zh": "好的。您要什么杯型——中杯还是大杯？"},
            {"speaker": "You", "en": "Regular is fine. Also, could you go easy on the ice?", "zh": "中杯就好。另外，可以少冰吗？"},
            {"speaker": "Barista", "en": "No problem at all. Would you like anything to eat with that?", "zh": "完全没问题。需要搭配点吃的吗？"},
            {"speaker": "You", "en": "Just a blueberry muffin, please. Is that for here or to go? For here.", "zh": "只要一个蓝莓马芬就好。我在这里吃。"},
            {"speaker": "Barista", "en": "Got it. That'll be nine dollars and fifty cents. You can tap your card here.", "zh": "好的，一共 9.5 美元。您可以在这里刷卡。"},
        ],
        "key_phrases": [
            {"en": "What can I get started for you?", "zh": "您今天想点些什么？"},
            {"en": "go easy on the ice", "zh": "少放点冰"},
            {"en": "for here or to go", "zh": "堂食还是打包"},
        ],
    },
    {
        "title": "机场值机与托运 (Airport Check-in)",
        "scene": "旅行出行",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Agent", "en": "Good morning! May I see your passport and booking confirmation?", "zh": "早上好！请出示您的护照和预订确认单。"},
            {"speaker": "You", "en": "Good morning. Here you go.", "zh": "早上好，给您。"},
            {"speaker": "Agent", "en": "Thank you. Are you checking any bags today?", "zh": "谢谢。您今天有行李需要托运吗？"},
            {"speaker": "You", "en": "Yes, just this suitcase. Can I keep my backpack as a carry-on?", "zh": "是的，就这个行李箱。我的双肩包可以随身携带吗？"},
            {"speaker": "Agent", "en": "Of course. Do you prefer a window seat or an aisle seat?", "zh": "当然可以。您偏好靠窗还是靠过道的座位？"},
            {"speaker": "You", "en": "An aisle seat if one is available, please.", "zh": "如果有的话，请给我靠过道的座位。"},
            {"speaker": "Agent", "en": "All set! Boarding begins at 10:20 at Gate B14.", "zh": "都办好了！10:20 在 B14 登机口开始登机。"},
        ],
        "key_phrases": [
            {"en": "check a bag", "zh": "托运行李"},
            {"en": "carry-on", "zh": "随身行李"},
            {"en": "window seat / aisle seat", "zh": "靠窗座位 / 靠过道座位"},
        ],
    },
    {
        "title": "酒店入住沟通 (Hotel Check-in)",
        "scene": "旅行出行",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Receptionist", "en": "Welcome to the Horizon Hotel. How may I assist you?", "zh": "欢迎来到地平线酒店。请问有什么可以帮您？"},
            {"speaker": "You", "en": "Hi, I have a reservation for three nights under Alex Chen.", "zh": "你好，我以 Alex Chen 的名字预订了三晚的房间。"},
            {"speaker": "Receptionist", "en": "Let me pull that up. Yes, a deluxe queen room. Is breakfast included?", "zh": "我查一下。是的，豪华大床房。包含早餐吗？"},
            {"speaker": "You", "en": "I believe so, and I also requested a quiet room on a higher floor.", "zh": "应该是包含的，我还备注了想要高楼层安静一点的房间。"},
            {"speaker": "Receptionist", "en": "We have room 1408 ready for you—it faces the courtyard.", "zh": "我们为您准备了 1408 房，朝向庭院，非常安静。"},
            {"speaker": "You", "en": "That sounds great. What time is check-out on Sunday?", "zh": "听起来很棒。周日几点退房？"},
            {"speaker": "Receptionist", "en": "Check-out is at noon, and the Wi-Fi password is on your keycard sleeve.", "zh": "退房时间是中午 12 点，Wi-Fi 密码印在房卡套上。"},
        ],
        "key_phrases": [
            {"en": "have a reservation under...", "zh": "以……名字预订了"},
            {"en": "pull that up", "zh": "调出/查询（信息）"},
            {"en": "keycard sleeve", "zh": "房卡套"},
        ],
    },
    {
        "title": "线上会议开场与同步 (Remote Standup Meeting)",
        "scene": "职场商务",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Manager", "en": "Morning everyone! Can you all hear me clearly?", "zh": "大家早上好！都能听清我说话吗？"},
            {"speaker": "You", "en": "Loud and clear. Let's get started whenever you're ready.", "zh": "非常清楚。您准备好了我们就可以开始。"},
            {"speaker": "Manager", "en": "Great. Today's agenda is to review the Q3 release timeline.", "zh": "好。今天的议程是过一下第三季度的发布时间表。"},
            {"speaker": "You", "en": "On my end, the API integration is complete and under testing.", "zh": "我这边接口集成已经完成，正在测试中。"},
            {"speaker": "Manager", "en": "Awesome. Are there any blockers we should address right now?", "zh": "太棒了。目前有什么需要立刻解决的阻碍吗？"},
            {"speaker": "You", "en": "Just one minor thing—I'm waiting on the final copy from the design team.", "zh": "只有一个小问题——我还在等设计团队的最终文案。"},
            {"speaker": "Manager", "en": "Got it. I'll follow up with them right after this call.", "zh": "明白了，会议结束后我立刻跟进他们。"},
        ],
        "key_phrases": [
            {"en": "Loud and clear.", "zh": "声音很清晰。"},
            {"en": "On my end", "zh": "就我这边而言"},
            {"en": "follow up with...", "zh": "跟进……"},
        ],
    },
    {
        "title": "求职面试自我介绍 (Job Interview Intro)",
        "scene": "职场商务",
        "level": "中高级 B2",
        "lines": [
            {"speaker": "Interviewer", "en": "Thanks for coming in today. Could you walk me through your background?", "zh": "感谢你今天来面试。能简单介绍一下你的背景吗？"},
            {"speaker": "You", "en": "Certainly. I have four years of experience in product analytics.", "zh": "当然。我有四年的产品数据分析经验。"},
            {"speaker": "Interviewer", "en": "What attracted you to this particular role?", "zh": "是什么吸引你申请这个职位的？"},
            {"speaker": "You", "en": "I admire your team's focus on user-centered design and rapid iteration.", "zh": "我非常欣赏贵团队对以用户为中心的设计和快速迭代的重视。"},
            {"speaker": "Interviewer", "en": "Can you share a project where you had to resolve a tough challenge?", "zh": "能分享一个你解决过棘手挑战的项目吗？"},
            {"speaker": "You", "en": "Sure. Last year, I streamlined our reporting pipeline, cutting prep time by 40%.", "zh": "好的。去年我精简了我们的报表流程，把准备时间缩短了 40%。"},
        ],
        "key_phrases": [
            {"en": "walk someone through...", "zh": "向某人详细/梳理介绍……"},
            {"en": "user-centered design", "zh": "以用户为中心的设计"},
            {"en": "cut ... by 40%", "zh": "把……减少了 40%"},
        ],
    },
    {
        "title": "餐厅点餐与结账 (Dining Out)",
        "scene": "日常出行",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Server", "en": "Good evening! Are you ready to order, or do you need a few more minutes?", "zh": "晚上好！您准备好点餐了吗，还是需要再看几分钟？"},
            {"speaker": "You", "en": "We're ready. Could you tell me what the chef's special is tonight?", "zh": "我们准备好了。请问今晚的主厨特推是什么？"},
            {"speaker": "Server", "en": "Tonight it's grilled salmon with roasted seasonal vegetables.", "zh": "今晚是烤三文鱼配时令烤蔬菜。"},
            {"speaker": "You", "en": "That sounds delicious. I'll have that, and a glass of sparkling water.", "zh": "听起来很美味。我要这个，再来一杯气泡水。"},
            {"speaker": "Server", "en": "How was everything with your meal?", "zh": "您的餐点还合胃口吗？"},
            {"speaker": "You", "en": "Everything was wonderful. Could we get the check when you have a moment?", "zh": "非常棒。方便的时候可以帮我们结账吗？"},
        ],
        "key_phrases": [
            {"en": "chef's special", "zh": "主厨特推菜"},
            {"en": "sparkling water", "zh": "气泡水"},
            {"en": "get the check", "zh": "结账/买单"},
        ],
    },
    {
        "title": "租房看房沟通 (Apartment Viewing)",
        "scene": "生活实用",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Agent", "en": "Welcome! This is the one-bedroom apartment you inquired about.", "zh": "欢迎！这就是您之前咨询的一居室公寓。"},
            {"speaker": "You", "en": "Thanks! It gets great natural light. Are utilities included in the rent?", "zh": "谢谢！采光真不错。水电煤气费包含在房租里吗？"},
            {"speaker": "Agent", "en": "Water and heating are included, while electricity and Wi-Fi are separate.", "zh": "水费和暖气包含在内，电费和 Wi-Fi 需要单独缴纳。"},
            {"speaker": "You", "en": "Got it. What is the minimum lease term and security deposit?", "zh": "明白了。最短租期是多久，押金是多少？"},
            {"speaker": "Agent", "en": "It's a twelve-month lease with one month's rent as the deposit.", "zh": "租期至少十二个月，押金为一个月房租。"},
            {"speaker": "You", "en": "That sounds reasonable. How close is the nearest subway station?", "zh": "听起来很合理。最近的地铁站有多远？"},
        ],
        "key_phrases": [
            {"en": "utilities included", "zh": "水电等杂费全包"},
            {"en": "lease term", "zh": "租期"},
            {"en": "security deposit", "zh": "租房押金"},
        ],
    },
    {
        "title": "医院看病与买药 (Seeing a Doctor)",
        "scene": "生活实用",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Doctor", "en": "Hello, what brings you in today?", "zh": "你好，今天哪里不舒服？"},
            {"speaker": "You", "en": "I've had a sore throat and a mild fever since yesterday evening.", "zh": "从昨晚开始我就一直喉咙痛，还有点低烧。"},
            {"speaker": "Doctor", "en": "Do you have any allergies to medication?", "zh": "您对什么药物过敏吗？"},
            {"speaker": "You", "en": "No known allergies. Should I take anything specific for the fever?", "zh": "没有已知过敏史。发烧需要吃什么特别的药吗？"},
            {"speaker": "Doctor", "en": "It looks like a common viral cold. Rest well and take this twice a day after meals.", "zh": "看起来是普通病毒性感冒。多休息，这个药饭后服用，每天两次。"},
        ],
        "key_phrases": [
            {"en": "what brings you in?", "zh": "今天怎么过来了 / 哪里不舒服？"},
            {"en": "sore throat", "zh": "喉咙痛"},
            {"en": "twice a day after meals", "zh": "每日两次饭后服用"},
        ],
    },
    {
        "title": "银行开户与换汇 (At the Bank)",
        "scene": "生活实用",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Teller", "en": "Good morning, how can I help you today?", "zh": "早上好，今天有什么可以帮您？"},
            {"speaker": "You", "en": "I'd like to open a checking account and exchange some currency.", "zh": "我想开一个活期账户并兑换一些外币。"},
            {"speaker": "Teller", "en": "Certainly. May I see your passport and proof of address?", "zh": "好的，请出示您的护照和住址证明。"},
            {"speaker": "You", "en": "Here they are. Is there any monthly maintenance fee for this account?", "zh": "给您。这个账户有月度管理费吗？"},
            {"speaker": "Teller", "en": "It's completely free as long as you keep a minimum balance of five hundred dollars.", "zh": "只要保持最低 500 美元的余额就完全免费。"},
        ],
        "key_phrases": [
            {"en": "checking account", "zh": "活期/支票账户"},
            {"en": "proof of address", "zh": "住址证明"},
            {"en": "minimum balance", "zh": "最低余额"},
        ],
    },
    {
        "title": "网购退换货沟通 (Customer Support & Return)",
        "scene": "日常出行",
        "level": "中级 B1",
        "lines": [
            {"speaker": "Support", "en": "Thanks for contacting customer support. How may I assist you?", "zh": "感谢联系客服，请问有什么可以帮您？"},
            {"speaker": "You", "en": "I received my order yesterday, but the headphones appear to be defective.", "zh": "我昨天收到了订单，但耳机似乎有故障。"},
            {"speaker": "Support", "en": "I'm sorry to hear that! Would you prefer a replacement or a full refund?", "zh": "非常抱歉！您希望换货还是全额退款？"},
            {"speaker": "You", "en": "A replacement would be great. Do I need to pay for return shipping?", "zh": "换货就好。退回运费需要我自己付吗？"},
            {"speaker": "Support", "en": "Not at all. I've emailed you a prepaid return shipping label.", "zh": "完全不需要。我已经把预付费退货标签发到您邮箱了。"},
        ],
        "key_phrases": [
            {"en": "defective", "zh": "有瑕疵的 / 有故障的"},
            {"en": "full refund", "zh": "全额退款"},
            {"en": "prepaid return label", "zh": "预付费退货标签"},
        ],
    },
    {
        "title": "电话预约与改期 (Rescheduling an Appointment)",
        "scene": "职场商务",
        "level": "初级 A2",
        "lines": [
            {"speaker": "Receptionist", "en": "Good afternoon, Bright Dental Clinic. How may I direct your call?", "zh": "下午好，明亮牙科诊所，请问有什么可以帮您？"},
            {"speaker": "You", "en": "Hi, I have an appointment this Thursday at 2 PM, but I need to reschedule.", "zh": "你好，我预约了本周四下午两点，但我需要改期。"},
            {"speaker": "Receptionist", "en": "No problem at all. Would next Monday morning work for you?", "zh": "没问题。下周一上午您方便吗？"},
            {"speaker": "You", "en": "Next Monday at 10:30 AM would be ideal.", "zh": "下周一上午十点半非常合适。"},
            {"speaker": "Receptionist", "en": "You're all set for Monday at 10:30. Have a great day!", "zh": "已经为您改到周一十点半了，祝您愉快！"},
        ],
        "key_phrases": [
            {"en": "reschedule an appointment", "zh": "改期预约"},
            {"en": "work for you", "zh": "对你来说方便/合适"},
            {"en": "You're all set", "zh": "都为您安排好了"},
        ],
    },
    {
        "title": "商务谈判与报价 (Business Negotiation)",
        "scene": "职场商务",
        "level": "中高级 B2",
        "lines": [
            {"speaker": "Client", "en": "We reviewed your proposal, but the quote is slightly above our budget.", "zh": "我们看了你们的方案，但报价略高于我们的预算。"},
            {"speaker": "You", "en": "I understand. If we commit to an annual contract, we can offer a 15% discount.", "zh": "我理解。如果签订年度合同，我们可以提供 15% 的折扣。"},
            {"speaker": "Client", "en": "That helps a lot. Can you also guarantee priority support?", "zh": "这很有帮助。你们还能保证优先技术支持吗？"},
            {"speaker": "You", "en": "Yes, dedicated support and quarterly reviews are included in that tier.", "zh": "可以，该套餐包含专属支持和每季度复盘。"},
            {"speaker": "Client", "en": "Great, let's finalize the terms and get started next week.", "zh": "太好了，我们敲定条款后下周就开始吧。"},
        ],
        "key_phrases": [
            {"en": "above our budget", "zh": "超出我们的预算"},
            {"en": "annual contract", "zh": "年度合同"},
            {"en": "finalize the terms", "zh": "敲定条款"},
        ],
    },
]

SEED_GRAMMAR = [
    {
        "title": "一般现在时 vs 现在进行时",
        "category": "时态基础",
        "level": "初级 A2",
        "summary": "一般现在时表示习惯、规律和客观事实；现在进行时表示此时此刻正在发生或近期暂时的动作。",
        "explanation": "1. 一般现在时（Simple Present）：主语为第三人称单数时动词加 -s/-es。常与 always, usually, every day 连用。\n2. 现在进行时（Present Continuous）：am / is / are + V-ing。常与 now, right now, this week 连用。\n3. 注意状态动词（如 know, like, believe, want）通常不用于进行时。",
        "examples": [
            {"en": "I drink coffee every morning.", "zh": "我每天早上都喝咖啡。（习惯）"},
            {"en": "I am drinking tea right now.", "zh": "我现在正在喝茶。（此刻动作）"},
            {"en": "She is staying in Shanghai this month.", "zh": "她这个月暂住在上海。（阶段性临时状态）"},
        ],
        "common_mistakes": [
            "错误：I am knowing the answer. → 正确：I know the answer.（know 为状态动词）",
            "错误：He work in a bank. → 正确：He works in a bank.（三单别漏 -s）",
        ],
    },
    {
        "title": "现在完成时核心用法 (have/has + 过去分词)",
        "category": "核心时态",
        "level": "中级 B1",
        "summary": "连接“过去”与“现在”的桥梁：强调过去发生的动作对现在的影响，或从过去持续到现在的状态。",
        "explanation": "结构：have / has + V-ed（过去分词）。\n三大场景：\n1. 经历：Have you ever been to London?（曾经……过）\n2. 结果/影响：I have lost my keys.（钥匙丢了，现在进不去门）\n3. 持续：She has lived here for five years.（for + 时间段 / since + 时间点）。",
        "examples": [
            {"en": "I have already finished my homework.", "zh": "我已经完成作业了。（现在有空了）"},
            {"en": "We have known each other since 2020.", "zh": "我们从 2020 年就认识了。"},
            {"en": "Have you tried this new cafe yet?", "zh": "你试过这家新咖啡馆了吗？"},
        ],
        "common_mistakes": [
            "错误：I have seen him yesterday. → 正确：I saw him yesterday.（有明确过去时间 yesterday 必须用一般过去时）",
            "错误：He has gone to Beijing for 3 days. → 正确：He has been in Beijing for 3 days.（短暂性动词不能接时间段）",
        ],
    },
    {
        "title": "情态动词委婉表达 (can / could / may / would)",
        "category": "交际语法",
        "level": "初级 A2",
        "summary": "在英语口语中，用 could 和 would 代替 can 和 will 可以让请求听起来更礼貌、更地道。",
        "explanation": "1. 请求帮助：Could you please...? / Would you mind + V-ing...?\n2. 礼貌点单或提议：I would like... / May I have...?\n3. 推测可能性：might (可能性较小) < may < could < must (非常肯定)。",
        "examples": [
            {"en": "Could you speak a little more slowly?", "zh": "您能说得稍微慢一点吗？"},
            {"en": "Would you mind opening the window?", "zh": "您介意打开窗户吗？"},
            {"en": "She might be stuck in traffic.", "zh": "她可能堵在路上了。"},
        ],
        "common_mistakes": [
            "错误：Could you to help me? → 正确：Could you help me?（情态动词后接动词原形，不加 to）",
        ],
    },
    {
        "title": "时间与空间介词 (in / on / at)",
        "category": "高频介词",
        "level": "初级 A2",
        "summary": "口诀记忆：大时间/大空间用 in，具体某天/表面接触用 on，精准时刻/小地点用 at。",
        "explanation": "时间：\n- in：年份、月份、季节、上午/下午/晚上（in 2026, in May, in the morning）\n- on：具体某一天、星期几、带修饰的早中晚（on Monday, on May 1st, on a rainy morning）\n- at：具体时刻、正午/午夜（at 8:30, at noon, at night）\n\n地点：\n- in：城市、国家、封闭空间内（in Beijing, in the box）\n- on：表面、楼层、街道（on the table, on the 3rd floor）\n- at：具体点位、门牌地址（at the door, at the bus stop）。",
        "examples": [
            {"en": "The meeting starts at 9:00 AM on Tuesday.", "zh": "会议在周二上午九点开始。"},
            {"en": "I left my notebook on the desk in the study.", "zh": "我把笔记本落在书房的桌上了。"},
        ],
        "common_mistakes": [
            "错误：in Monday morning → 正确：on Monday morning（具体到某一天的早晨用 on）",
        ],
    },
    {
        "title": "被动语态实战 (be + 过去分词)",
        "category": "句型结构",
        "level": "中级 B1",
        "summary": "当不知道谁执行动作、或动作的承受者比执行者更重要时，使用被动语态。",
        "explanation": "基本结构：be + V-ed（过去分词），时态变化体现在 be 动词上。\n- 一般现在：is/are done\n- 一般过去：was/were done\n- 现在完成：has/have been done\n- 情态动词：can/must/should be done。",
        "examples": [
            {"en": "English is spoken all over the world.", "zh": "世界各地都在说英语。"},
            {"en": "The report must be submitted before Friday.", "zh": "报告必须在周五前提交。"},
            {"en": "The bridge was built in 1998.", "zh": "这座桥建于 1998 年。"},
        ],
        "common_mistakes": [
            "错误：The package was arrived yesterday. → 正确：The package arrived yesterday.（arrive 是不及物动词，没有被动语态）",
        ],
    },
    {
        "title": "定语从句关系代词 (who / which / that / where)",
        "category": "复合句",
        "level": "中级 B1",
        "summary": "用从句像形容词一样修饰名词，让你的英语表达从简单句升级为地道长句。",
        "explanation": "1. 指人：who / that\n2. 指物：which / that\n3. 指地点（在从句中作地点状语）：where（= in/at which）\n4. 关系代词在从句中作宾语时可以省略。",
        "examples": [
            {"en": "The app that I use every day is really helpful.", "zh": "我每天用的那个应用真的很有帮助。"},
            {"en": "She is the colleague who helped me with the presentation.", "zh": "她就是那位帮我做演示文稿的同事。"},
            {"en": "This is the cafe where we first met.", "zh": "这就是我们第一次见面的那家咖啡馆。"},
        ],
        "common_mistakes": [
            "错误：This is the book which I bought it yesterday. → 正确：This is the book which I bought yesterday.（从句中不能再重复出现代词 it）",
        ],
    },
    {
        "title": "比较级与最高级",
        "category": "修饰表达",
        "level": "初级 A2",
        "summary": "用于两者比较（-er / more）和三者及以上比较（the -est / the most）。",
        "explanation": "1. 单音节及部分双音节词：词尾加 -er / -est（fast → faster → fastest）。\n2. 多音节词：前加 more / the most（useful → more useful → the most useful）。\n3. 不规则变化：good/well → better → best；bad → worse → worst。\n4. 程度修饰：much / a lot / a bit + 比较级。",
        "examples": [
            {"en": "Listening to podcasts is much more effective than memorizing lists.", "zh": "听播客比死记硬背单词表有效得多。"},
            {"en": "This is the most practical guide I have ever read.", "zh": "这是我读过最实用的指南。"},
        ],
        "common_mistakes": [
            "错误：more better → 正确：much better（不能双重比较）",
        ],
    },
    {
        "title": "虚拟语气常见句型 (If I were... / I wish...)",
        "category": "高级表达",
        "level": "中高级 B2",
        "summary": "用于表达与现在事实相反的假设、礼貌建议或美好愿望。",
        "explanation": "1. 与现在事实相反：If + 主语 + 过去式 (be 动词统一用 were), 主语 + would/could + 动词原形。\n2. I wish + 过去式：表达难以实现的愿望。\n3. 常见口语套用：If I were you, I would...（如果我是你，我会……）。",
        "examples": [
            {"en": "If I were you, I would take that opportunity.", "zh": "如果我是你，我会抓住那个机会。"},
            {"en": "If I had more free time, I would travel around Europe.", "zh": "如果我有更多空闲时间，我会去欧洲旅行。"},
            {"en": "I wish I could speak fluent English.", "zh": "真希望我能说一口流利的英语。"},
        ],
        "common_mistakes": [
            "注意：在正式或标准书面语中，虚拟条件句用 If I were... 而非 If I was...。",
        ],
    },
    {
        "title": "非谓语动词 (to do / doing / done)",
        "category": "核心句法",
        "level": "中级 B1",
        "summary": "一个简单句只能有一个谓语动词，其余动作需变为不定式(表目的/将来)、动名词/现在分词(表主动/进行)或过去分词(表被动/完成)。",
        "explanation": "1. to do（不定式）：表示目的、计划或尚未发生的动作（I came here to learn English.）。\n2. doing（动名词/现在分词）：可作主语或宾语，修饰名词时表示主动或正在进行（Speaking aloud helps memory.）。\n3. done（过去分词）：表示被动或已完成的状态（a spoken language 一门口头语言）。",
        "examples": [
            {"en": "Learning a language takes consistent practice.", "zh": "学习一门语言需要持续练习。（doing 作主语）"},
            {"en": "I use flashcards to review new words.", "zh": "我用记忆卡片来复习新词。（to do 表目的）"},
            {"en": "Here is the revised report you requested.", "zh": "这是您要求的修订版报告。（done 表被动完成）"},
        ],
        "common_mistakes": [
            "错误：I enjoy to listen to music. → 正确：I enjoy listening to music.（enjoy 后只能接动名词 doing）",
        ],
    },
    {
        "title": "名词性从句 (that / what / whether)",
        "category": "复合句",
        "level": "中高级 B2",
        "summary": "用整个句子充当主语、宾语或表语；核心区分：that 不充当成分且无实义，what 在从句中作主/宾/表语。",
        "explanation": "1. that 引导：从句结构已经完整（I believe that practice makes perfect.）。\n2. what 引导：相当于 the thing that，在从句中缺主语或宾语时使用（What matters most is consistency.）。\n3. whether / if：表示“是否”（I wonder whether he will join us.）。",
        "examples": [
            {"en": "What you need right now is a clear daily routine.", "zh": "你现在最需要的是一个清晰的日常惯例。"},
            {"en": "I'm not sure whether the flight is on time.", "zh": "我不确定航班是否准点。"},
        ],
        "common_mistakes": [
            "错误：That he said is true. → 正确：What he said is true.（said 缺少宾语，必须用 what）",
        ],
    },
    {
        "title": "倒装句与强调句 (It is... that...)",
        "category": "高级表达",
        "level": "中高级 B2",
        "summary": "用于突出句子重点或增强书面/演讲感染力，是高分写作和口语的常用加分句型。",
        "explanation": "1. 强调句型：It is/was + 被强调部分 + that/who + 其余部分。\n2. 否定词置句首部分倒装：Never / Seldom / Not only + 助动词/情态动词 + 主语 + 动词原形。\n3. Only + 状语置句首也需部分倒装（Only in this way can we improve.）。",
        "examples": [
            {"en": "It is consistent practice that leads to fluency.", "zh": "正是持续的练习带来了流利度。"},
            {"en": "Never have I seen such a helpful learning tool.", "zh": "我从未见过如此有用的学习工具。"},
        ],
        "common_mistakes": [
            "错误：Only by practicing we can improve. → 正确：Only by practicing can we improve.（Only + 状语在句首，主句要部分倒装）",
        ],
    },
    {
        "title": "逻辑衔接词 (However / Therefore / Despite)",
        "category": "写作与口语",
        "level": "中级 B1",
        "summary": "合理使用逻辑连接词能让你的英语表达条理分明，注意区分连词与介词的词性搭配。",
        "explanation": "1. 转折：however（副词，常加逗号隔开）；although/though（连词，接完整句子）；despite / in spite of（介词，接名词或动名词）。\n2. 因果：therefore / thus（副词）；because（接句子）；because of / due to（接名词短语）。\n3. 递进：moreover / furthermore / in addition。",
        "examples": [
            {"en": "Despite the busy schedule, she reviews twenty words daily.", "zh": "尽管日程繁忙，她每天仍复习二十个单词。"},
            {"en": "He practiced every morning; therefore, his listening improved rapidly.", "zh": "他每天早上都练习，因此听力提高得很快。"},
        ],
        "common_mistakes": [
            "错误：Although he was tired, but he kept studying. → 正确：Although he was tired, he kept studying.（although 和 but 不能同时出现在同一句中）",
        ],
    },
]

from backend.seed_data_extra import EXTRA_DIALOGUES, EXTRA_GRAMMAR  # noqa: E402

SEED_DIALOGUES.extend(EXTRA_DIALOGUES)
SEED_GRAMMAR.extend(EXTRA_GRAMMAR)
