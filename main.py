import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime
import os
import urllib.request
import urllib.parse
import json 
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
from keep_alive import keep_alive

# --- 秘密の情報を .env から読み込む ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URL = os.getenv("MONGODB_URI")

# --- データベース（MongoDB）の初期設定 ---
# タイムアウトを短めに設定してBotが固まるのを防ぐ
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
db = client["mario_bot_db"]
fcs_collection = db["user_fcs"]
ta_collection = db["ta_records"]

# --- コースの定義 ---
COURSES = {
    "kinopio_coin": {
        "coin_1": "フラワー王国へようこそ はじまりの花畑",
        "coin_2": "解き明かせ！ ひっぱり砂漠に眠る謎",
        "coin_3": "ちょっと一息 回転！ダッシュレール",
        "coin_4": "コロンポリン 宙をゆく",
        "coin_5": "アップ＆ダウン もこもこリフト",
        "coin_6": "ビヨンたちの トワイライトフォレスト",
        "coin_7": "バッジチャレンジ 帽子パラシュートLv.1",
        "coin_8": "ブースケ スカイアドベンチャー",
        "coin_9": "ここはどこ？ 赤青迷宮"
    },
    "kinopio_teki": {
        "teki_1": "転がれ コロンポリン",
        "teki_2": "ガボンのアジト 沈む土管の谷",
        "teki_3": "ズラカルたちの 駆ける丘",
        "teki_4": "退く？引く？ オッポーの毒沼",
        "teki_5": "たおして進め！ モックモックコロシアム",
        "teki_6": "ヘビムシの 雪山登山道",
        "teki_7": "ゴロボーの 地下帝国",
        "teki_8": "メリコンドルは 飛んでくる",
        "teki_9": "ブースケ泳ぐ 白砂漠",
        "teki_10": "バッジチャレンジ 帽子パラシュートLv.2",
        "teki_11": "たおして進め！ マグマノコロシアム",
        "teki_12": "ゆたかな大地 パックンガーデン",
        "teki_13": "なんでも食べるぞ アングリの並木"
    },
    "kinopio_clear": {
        "clear_1": "歌って踊って パックンマーチ",
        "clear_2": "ズラカルたちの 駆ける丘",
        "clear_3": "バッジチャレンジ つるショットLv.1",
        "clear_4": "中間試練！ ジャンプの達人を追え！",
        "clear_5": "よりどりみどり ホッピンの試練",
        "clear_6": "頭上注意！ ゴロゴロ回廊",
        "clear_7": "嵐の予感！ どしゃぶり雲で雨のぼり",
        "clear_8": "バッジチャレンジ フロートスピンLv.1",
        "clear_9": "かいくぐれ！ 追撃のチェイスキラー",
        "clear_10": "溶岩トンネルの 波リフト(復帰ジャンプ)",
        "clear_11": "達人バッジチャレンジ バネLv.2",
        "clear_12": "溶岩トンネルの 波リフト(バネ)"
    },
    "kinopio_star": {
        "star_1": "フラワー王国へようこそ はじまりの花畑",
        "star_2": "吹き矢で登って フキヤンの巣",
        "star_3": "そこのけ マジローの散歩道",
        "star_4": "土管もりもり 森の沼",
        "star_5": "ビヨンたちの トワイライトフォレスト",
        "star_6": "ブースケ泳ぐ 白砂漠",
        "star_7": "コロブーいっぱい 砂漠の橋わたり",
        "star_8": "灼熱の アチアチストリート",
        "star_9": "頭上注意！ ゴロゴロ回廊",
        "star_10": "氷つるつる ズンドコの谷",
        "star_11": "メリコンドルは 飛んでくる"
    },
    "kinopio_extra": {
        "extra_1": "フラワー王国へようこそ はじまりの花畑(バネ)",
        "extra_2": "転がれ コロンポリン",
        "extra_3": "コロブーいっぱい 砂漠の橋わたり",
        "extra_4": "最後の秘境 ドクドク遺跡",
        "extra_5": "かいくぐれ！追撃のチェイスキラー",
        "extra_6": "猪突猛進 ぼくトッシン",
        "extra_7": "食欲旺盛 ガシガシのほら穴",
        "extra_8": "フラワー王国へようこそ はじまりの花畑(透明)",
        "extra_9": "ライトでナイトな お化け屋敷",
        "extra_10": "バッジチャレンジ カベ登りジャンプLv.1",
        "extra_11": "コンペイと 星空わたしの試練",
        "extra_12": "叩いて足して 連結リフト",
        "extra_13": "ブースケ スカイアドベンチャー",
        "extra_14": "激闘！強いウェンディ！",
        "extra_15": "激闘！強いレミー！",
        "extra_16": "激闘！強いラリー！",
        "extra_17": "激闘！強いロイ！",
        "extra_18": "激闘！強いイギー！",
        "extra_19": "激闘！強いモートン！",
        "extra_20": "激闘！強いルドウィッグ！",
        "extra_21": "ブースケ泳ぐ 白砂漠",
        "extra_22": "古代の記憶 化石ドラゴン",
        "extra_23": "ちびで激闘！強いウェンディ！",
        "extra_24": "ちびで激闘！強いレミー！",
        "extra_25": "ちびで激闘！強いラリー！",
        "extra_26": "ちびで激闘！強いロイ！",
        "extra_27": "ちびで激闘！強いイギー！",
        "extra_28": "ちびで激闘！強いモートン！",
        "extra_29": "ちびで激闘！強いルドウィッグ！"
    },
    "colosseum": {
        "colo_w1": "W1 ドカンロックコロシアム",
        "colo_w2": "W2 モックモックコロシアム",
        "colo_w4": "W4 ヒデリーコロシアム",
        "colo_w5": "W5 キンキンコロシアム",
        "colo_w6": "W6 マグマノコロシアム",
        "colo_f1": "フラワーコロシアム",
    },
    "wiggler": {
        "wig_w1": "丘超え山越え ハナチャンレース",
        "wig_f1": "走って泳いで ハナチャンレース",
        "wig_f2": "洞窟駆け抜け ハナチャンレース"
    }
}

CATEGORY_NAMES = {
    "kinopio_coin": "キノピオ探検隊 訓練所 - 時間内にコインをすべて集めろ",
    "kinopio_teki": "キノピオ探検隊 訓練所 - 時間内に敵をすべてたおせ",
    "kinopio_clear": "キノピオ探検隊 訓練所 - 時間内にクリア",
    "kinopio_star": "キノピオ探検隊 訓練所 - 無敵のままクリア",
    "kinopio_extra": "キノピオ探検隊 訓練所 - エクストラ訓練",
    "colosseum": "コロシアム",
    "wiggler": "ハナチャンレース"
}

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# --- 補助関数 ---
def parse_time(time_str: str) -> int:
    time_str = time_str.translate(str.maketrans('０１２３４５６７８９．、。,', '0123456789....'))
    try:
        return int(float(time_str) * 1000)
    except ValueError:
        return -1

def format_time(ms: int) -> str:
    return f"{ms / 1000:.2f}"

def update_user_profile(user: discord.User | discord.Member):
    user_id_str = str(user.id)
    try:
        fcs_collection.update_one(
            {"user_id": user_id_str},
            {"$set": {"user_name": user.display_name}},
            upsert=True
        )
    except Exception as e:
        print(f"DB更新エラー(Profile): {e}")

def update_web_ranking():
    user_profiles = {}
    try:
        for doc in fcs_collection.find():
            if "user_name" in doc:
                user_profiles[str(doc["user_id"])] = doc["user_name"]

        data_to_send = {
            "last_updated": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y/%m/%d %H:%M:%S"),
            "records": {},
            "user_records": {}
        }

        for cat_id in CATEGORY_NAMES.keys():
            data_to_send["records"][cat_id] = {}
            for course_id in COURSES.get(cat_id, {}).keys():
                all_records = list(ta_collection.find({"category_id": cat_id, "course_id": course_id}, {"_id": 0, "timestamp": 0}).sort("time_ms", 1))
                top_10 = []
                for rank, record in enumerate(all_records, start=1):
                    uid = str(record.get("user_id"))
                    latest_name = user_profiles.get(uid, record.get("user_name", "Unknown"))
                    if rank <= 10:
                        top_10.append({"user_name": latest_name, "time_ms": record["time_ms"]})
                    if uid not in data_to_send["user_records"]:
                        data_to_send["user_records"][uid] = {"name": latest_name, "records": {}}
                    if cat_id not in data_to_send["user_records"][uid]["records"]:
                        data_to_send["user_records"][uid]["records"][cat_id] = {}
                    data_to_send["user_records"][uid]["records"][cat_id][course_id] = {"time_ms": record["time_ms"], "rank": rank}
                if top_10:
                    data_to_send["records"][cat_id][course_id] = top_10

        json_str = json.dumps(data_to_send, ensure_ascii=False)
        url = "https://yamakyu5800.stars.ne.jp/SMBW/update_ranking.php"
        data = urllib.parse.urlencode({'key': 'mario_wonder_secret', 'json': json_str}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            print(f"Web更新完了: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"Web更新エラー: {e}")

# --- 募集用View ---
class RecruitView(discord.ui.View):
    def __init__(self, host: discord.Member, min_p: int, max_p: int, fc: str, timeout: float):
        super().__init__(timeout=timeout)
        self.host = host
        self.min_p = min_p
        self.max_p = max_p
        self.fc = fc
        self.participants = [host]
        self.is_started = False

    @discord.ui.button(label="参加する", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.participants:
            await interaction.response.send_message("既に参加しています！", ephemeral=True)
            return
        self.participants.append(interaction.user)
        update_user_profile(interaction.user)
        await interaction.response.send_message("参加を登録しました！", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.set_field_at(0, name=f"参加者 ({len(self.participants)}/{self.max_p}人)", value="\n".join([p.display_name for p in self.participants]))
        await interaction.message.edit(embed=embed)
        if len(self.participants) >= self.max_p:
            await self.start_session(interaction.message)

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.host:
            if self.is_started: return
            self.is_started = True
            await interaction.message.edit(content=f"🚫 {self.host.mention}の募集はキャンセルされました。", embed=None, view=None)
            await interaction.response.send_message("募集を中止しました。", ephemeral=True)
            return
        if interaction.user in self.participants:
            self.participants.remove(interaction.user)
            await interaction.response.send_message("参加をキャンセルしました。", ephemeral=True)
            embed = interaction.message.embeds[0]
            embed.set_field_at(0, name=f"参加者 ({len(self.participants)}/{self.max_p}人)", value="\n".join([p.display_name for p in self.participants]))
            await interaction.message.edit(embed=embed)
        else:
            await interaction.response.send_message("参加していません。", ephemeral=True)

    async def start_session(self, message: discord.Message):
        if self.is_started: return
        self.is_started = True
        if len(self.participants) >= self.min_p:
            await message.edit(content=f"✅ {self.host.mention}の募集は終了しました。", embed=None, view=None)
            thread = await message.channel.create_thread(name=f"{self.host.display_name}の募集", auto_archive_duration=60, type=discord.ChannelType.private_thread)
            for p in self.participants:
                try: await thread.add_user(p)
                except: pass
            mentions = " ".join([p.mention for p in self.participants])
            await thread.send(f"{mentions}\nメンバーが集まりました！\nホストのフレンドコード: `{self.fc}`")
        else:
            await message.edit(content=f"🚫 メンバーが集まらなかったため、 {self.host.mention}の募集はキャンセルされました。", embed=None, view=None)

# --- オートコンプリート ---
async def course_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    # カテゴリーが未選択でもエラーにならないようにgetattrを使用
    category_val = getattr(interaction.namespace, "category", None)
    
    if category_val and category_val in COURSES:
        target_courses = COURSES[category_val]
    else:
        # カテゴリー未選択時は全コースを表示
        target_courses = {c_id: name for cat in COURSES.values() for c_id, name in cat.items()}
    
    return [
        app_commands.Choice(name=name, value=c_id)
        for c_id, name in target_courses.items() if current.lower() in name.lower()
    ][:25]

# --- コマンド群 ---

@bot.tree.command(name="set_fc", description="自分のフレンドコードを登録します")
async def set_fc(interaction: discord.Interaction, fc: str):
    await interaction.response.defer(ephemeral=True) # 自分のメッセージを隠す設定
    user_id_str = str(interaction.user.id)
    fcs_collection.update_one({"user_id": user_id_str}, {"$set": {"fc": fc, "user_name": interaction.user.display_name}}, upsert=True)
    await interaction.followup.send(f"✅ {interaction.user.mention} さんのフレンドコードを登録しました： `{fc}`")

@bot.tree.command(name="host", description="募集を開始します")
async def recruit_host(interaction: discord.Interaction, end_time: str, min_p: int, max_p: int):
    await interaction.response.defer() # 外部通信があるため最初にdefer
    update_user_profile(interaction.user) 
    user_data = fcs_collection.find_one({"user_id": str(interaction.user.id)})
    
    if not user_data or "fc" not in user_data:
        await interaction.followup.send("先に `/set_fc` でフレンドコードを登録してください！")
        return
    if min_p > max_p:
        await interaction.followup.send("最少人数は最大人数以下にしてください！")
        return

    try:
        jst = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(jst)
        target_time = datetime.datetime.strptime(end_time, "%H:%M").time()
        target_dt = datetime.datetime.combine(now.date(), target_time, tzinfo=jst)
        if target_dt < now: target_dt += datetime.timedelta(days=1)
        wait_seconds = (target_dt - now).total_seconds()
    except:
        await interaction.followup.send("時刻形式が正しくありません(例: 21:30)")
        return
    
    embed = discord.Embed(title="マリオワンダー メンバー募集", color=0x00ff00)
    embed.add_field(name=f"参加者 (1/{max_p}人)", value=interaction.user.display_name, inline=False)
    embed.add_field(name="募集条件", value=f"最少人数: {min_p}人 / 最大人数: {max_p}人\n締切: {target_dt.strftime('%m/%d %H:%M')}", inline=False)
    
    view = RecruitView(host=interaction.user, min_p=min_p, max_p=max_p, fc=user_data["fc"], timeout=wait_seconds)
    msg = await interaction.followup.send(embed=embed, view=view)
    
    await asyncio.sleep(wait_seconds)
    try:
        # インタラクションの有効期限対策
        fetched_message = await interaction.channel.fetch_message(msg.id)
        await view.start_session(fetched_message)
    except: pass

@bot.tree.command(name="ta", description="タイムアタックの記録を登録します")
@app_commands.choices(category=[
    app_commands.Choice(name="訓練(コイン)", value="kinopio_coin"),
    app_commands.Choice(name="訓練(敵討伐)", value="kinopio_teki"),
    app_commands.Choice(name="訓練(クリア)", value="kinopio_clear"),
    app_commands.Choice(name="訓練(無敵)", value="kinopio_star"),
    app_commands.Choice(name="訓練(EX)", value="kinopio_extra"),
    app_commands.Choice(name="コロシアム", value="colosseum"),
    app_commands.Choice(name="ハナチャン", value="wiggler"),
])
@app_commands.autocomplete(course=course_autocomplete)
async def ta_cmd(interaction: discord.Interaction, category: app_commands.Choice[str], course: str, time_str: str):
    await interaction.response.defer() # DB処理の前に必ずdefer
    
    cat_id = category.value
    user_id_str = str(interaction.user.id)
    update_user_profile(interaction.user)

    user_data = fcs_collection.find_one({"user_id": user_id_str})
    if not user_data or "fc" not in user_data:
        await interaction.followup.send("❌ 先に `/set_fc` でフレンドコードを登録してください！")
        return
    if course not in COURSES.get(cat_id, {}):
        await interaction.followup.send("❌ コースが正しくありません。")
        return

    time_ms = parse_time(time_str)
    if time_ms < 0:
        await interaction.followup.send("❌ タイムの形式が正しくありません。 `12.34` または `123.45` の形式で入力してください。")
        return

    existing = ta_collection.find_one({"user_id": user_id_str, "category_id": cat_id, "course_id": course})
    if existing and existing["time_ms"] <= time_ms:
        await interaction.followup.send(f"記録更新ならず！\n自己ベスト: `{format_time(existing['time_ms'])}`")
        return

    ta_collection.update_one(
        {"user_id": user_id_str, "category_id": cat_id, "course_id": course},
        {"$set": {"user_name": interaction.user.display_name, "time_ms": time_ms, "timestamp": datetime.datetime.now(datetime.timezone.utc)}},
        upsert=True
    )
    await interaction.followup.send(f"新記録を登録しました！\n**{COURSES[cat_id][course]}**: `{format_time(time_ms)}`")
    asyncio.create_task(asyncio.to_thread(update_web_ranking))

@bot.tree.command(name="ta_ranking", description="ランキングを表示します")
@app_commands.choices(category=[
    app_commands.Choice(name="訓練(コイン)", value="kinopio_coin"),
    app_commands.Choice(name="訓練(敵討伐)", value="kinopio_teki"),
    app_commands.Choice(name="訓練(クリア)", value="kinopio_clear"),
    app_commands.Choice(name="訓練(無敵)", value="kinopio_star"),
    app_commands.Choice(name="訓練(EX)", value="kinopio_extra"),
    app_commands.Choice(name="コロシアム", value="colosseum"),
    app_commands.Choice(name="ハナチャン", value="wiggler"),
])
@app_commands.autocomplete(course=course_autocomplete)
async def ta_ranking_cmd(interaction: discord.Interaction, category: app_commands.Choice[str], course: str):
    await interaction.response.defer() # DB処理の前に必ずdefer
    
    cat_id = category.value
    if course not in COURSES.get(cat_id, {}):
        await interaction.followup.send("❌ コースが正しくありません。")
        return

    records = list(ta_collection.find({"category_id": cat_id, "course_id": course}).sort("time_ms", 1).limit(10))
    embed = discord.Embed(title=f"🏆 {COURSES[cat_id][course]}", color=0xffd700)
    
    if not records:
        embed.description = "記録がありません。"
    else:
        desc = ""
        for i, r in enumerate(records):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"` {i+1}位 `"
            desc += f"{medal} **{r['user_name']}** - `{format_time(r['time_ms'])}`\n"
        embed.add_field(name="Top 10", value=desc)
    
    await interaction.followup.send(embed=embed)

if __name__ == "__main__":
    keep_alive() 
    bot.run(TOKEN)
