"""
生成丰富的电商数据仓库初始化 SQL
适配前端展示需求：华北/四川统计、品类对比、趋势、TOP10、退货率、完成率
"""
import random
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)

# ========== 维度数据 ==========
regions = [
    ("R001", "广东省", "广州市", "华南", "中国"),
    ("R002", "浙江省", "杭州市", "华东", "中国"),
    ("R003", "四川省", "成都市", "西南", "中国"),
    ("R004", "北京市", "北京市", "华北", "中国"),
    ("R005", "上海市", "上海市", "华东", "中国"),
    ("R006", "湖北省", "武汉市", "华中", "中国"),
    ("R007", "四川省", "达州市", "西南", "中国"),
    ("R008", "四川省", "绵阳市", "西南", "中国"),
    ("R009", "四川省", "南充市", "西南", "中国"),
    ("R010", "天津市", "天津市", "华北", "中国"),
    ("R011", "河北省", "石家庄市", "华北", "中国"),
    ("R012", "山西省", "太原市", "华北", "中国"),
    ("R013", "山东省", "济南市", "华东", "中国"),
    ("R014", "河南省", "郑州市", "华中", "中国"),
    ("R015", "湖南省", "长沙市", "华中", "中国"),
    ("R016", "江苏省", "南京市", "华东", "中国"),
    ("R017", "福建省", "福州市", "华东", "中国"),
    ("R018", "陕西省", "西安市", "西北", "中国"),
    ("R019", "重庆市", "重庆市", "西南", "中国"),
    ("R020", "辽宁省", "沈阳市", "东北", "中国"),
]

customers = [
    ("C001", "肖胜宇", "男", "钻石"),
    ("C002", "shaw", "男", "铂金"),
    ("C003", "小车", "女", "黄金"),
    ("C004", "李伟", "男", "黄金"),
    ("C005", "王芳", "女", "白银"),
    ("C006", "张敏", "女", "黄金"),
    ("C007", "刘洋", "男", "青铜"),
    ("C008", "陈静", "女", "铂金"),
    ("C009", "赵磊", "男", "白银"),
    ("C010", "黄秀英", "女", "青铜"),
    ("C011", "吴斌", "男", "黄金"),
    ("C012", "周燕", "女", "铂金"),
    ("C013", "徐浩", "男", "白银"),
    ("C014", "孙丽", "女", "黄金"),
    ("C015", "马强", "男", "青铜"),
    ("C016", "朱玲", "女", "白银"),
    ("C017", "胡杰", "男", "黄金"),
    ("C018", "高梅", "女", "铂金"),
    ("C019", "林峰", "男", "青铜"),
    ("C020", "何娜", "女", "白银"),
    ("C021", "郭涛", "男", "黄金"),
    ("C022", "邓慧", "女", "青铜"),
    ("C023", "曹瑞", "男", "铂金"),
    ("C024", "肖宇", "男", "钻石"),  # 肖胜宇相关
    ("C025", "胜宇小店", "女", "黄金"),  # 肖胜宇相关
    ("C026", "肖老板", "男", "铂金"),  # 肖胜宇相关
    ("C027", "肖胜宇二号", "男", "白银"),
    ("C028", "四川 Shaw", "男", "黄金"),
    ("C029", "达州小车", "女", "青铜"),
    ("C030", "华北肖胜宇", "男", "钻石"),
    ("C031", "钱多多", "女", "铂金"),
    ("C032", "孙悟空", "男", "黄金"),
    ("C033", "刘备", "男", "白银"),
    ("C034", "关羽", "男", "黄金"),
    ("C035", "张飞", "男", "青铜"),
    ("C036", "诸葛亮", "男", "钻石"),
    ("C037", "赵云", "男", "铂金"),
    ("C038", "马超", "男", "黄金"),
    ("C039", "黄忠", "男", "白银"),
    ("C040", "貂蝉", "女", "铂金"),
    ("C041", "吕布", "男", "钻石"),
    ("C042", "曹操", "男", "黄金"),
    ("C043", "周瑜", "男", "铂金"),
    ("C044", "小乔", "女", "黄金"),
    ("C045", "大乔", "女", "白银"),
    ("C046", "孙尚香", "女", "黄金"),
    ("C047", "司马懿", "男", "钻石"),
    ("C048", "姜维", "男", "铂金"),
    ("C049", "魏延", "男", "青铜"),
    ("C050", "庞统", "男", "白银"),
]

products = [
    ("P001", "iPhone 16 Pro", "手机数码", "苹果"),
    ("P002", "Galaxy S25 Ultra", "手机数码", "三星"),
    ("P003", "Mate 70 Pro", "手机数码", "华为"),
    ("P004", "小米15", "手机数码", "小米"),
    ("P005", "戴森 V15 吸尘器", "家用电器", "戴森"),
    ("P006", "美的空调 KFR-35GW", "家用电器", "美的"),
    ("P007", "海尔冰箱 535L", "家用电器", "海尔"),
    ("P008", "格力空调 1.5匹", "家用电器", "格力"),
    ("P009", "耐克 Air Max 270", "鞋靴", "耐克"),
    ("P010", "阿迪达斯 Ultraboost", "鞋靴", "阿迪达斯"),
    ("P011", "李宁韦德之道", "鞋靴", "李宁"),
    ("P012", "安踏 KT9", "鞋靴", "安踏"),
    ("P013", "优衣库羽绒服", "服饰", "优衣库"),
    ("P014", "李维斯 501 牛仔裤", "服饰", "李维斯"),
    ("P015", "ZARA 风衣", "服饰", "ZARA"),
    ("P016", "海澜之家衬衫", "服饰", "海澜之家"),
    ("P017", "雀巢金牌速溶咖啡", "食品饮料", "雀巢"),
    ("P018", "蒙牛纯牛奶 250ml*12", "食品饮料", "蒙牛"),
    ("P019", "农夫山泉矿泉水 550ml", "食品饮料", "农夫山泉"),
    ("P020", "可口可乐 330ml", "食品饮料", "可口可乐"),
    ("P021", "乐事原味薯片 150g", "休闲零食", "乐事"),
    ("P022", "奥利奥巧克力夹心饼干", "休闲零食", "奥利奥"),
    ("P023", "卫龙辣条", "休闲零食", "卫龙"),
    ("P024", "三只松鼠坚果礼盒", "休闲零食", "三只松鼠"),
    ("P025", "雅诗兰黛小棕瓶", "美妆护肤", "雅诗兰黛"),
    ("P026", "兰蔻粉水", "美妆护肤", "兰蔻"),
    ("P027", "SK-II 神仙水", "美妆护肤", "SK-II"),
    ("P028", "安耐晒防晒霜", "美妆护肤", "安耐晒"),
    ("P029", "迪卡侬山地自行车", "运动户外", "迪卡侬"),
    ("P030", "骆驼冲锋衣", "运动户外", "骆驼"),
    ("P031", "Kindle Paperwhite", "手机数码", "亚马逊"),
    ("P032", "Instant Pot 电压力锅", "家用电器", "Instant Pot"),
    ("P033", "九阳豆浆机", "家用电器", "九阳"),
    ("P034", "苏泊尔电饭煲", "家用电器", "苏泊尔"),
    ("P035", "完美日记口红", "美妆护肤", "完美日记"),
]

# 价格区间
price_map = {
    "P001": (7999, 9999), "P002": (7499, 9499), "P003": (5999, 7999), "P004": (2999, 3999),
    "P005": (3999, 5499), "P006": (2199, 3299), "P007": (2999, 4599), "P008": (1999, 3199),
    "P009": (699, 1299), "P010": (799, 1399), "P011": (499, 899), "P012": (399, 699),
    "P013": (299, 599), "P014": (399, 799), "P015": (499, 899), "P016": (149, 299),
    "P017": (45, 89), "P018": (35, 65), "P019": (2, 5), "P020": (3, 6),
    "P021": (8, 15), "P022": (12, 25), "P023": (10, 20), "P024": (89, 199),
    "P025": (850, 1200), "P026": (350, 500), "P027": (1200, 1600), "P028": (180, 280),
    "P029": (899, 1599), "P030": (299, 599), "P031": (999, 1399), "P032": (699, 999),
    "P033": (199, 399), "P034": (249, 499), "P035": (59, 129),
}

# 日期范围 2025-01-01 ~ 2025-03-31
start_date = datetime(2025, 1, 1)
dates = []
for i in range(90):
    d = start_date + timedelta(days=i)
    q = f"Q{(d.month - 1) // 3 + 1}"
    dates.append((int(d.strftime("%Y%m%d")), d.year, q, d.month, d.day))

# ========== 生成订单 ==========
orders = []
order_counter = 1

# 让肖胜宇相关用户多买点
shaw_customers = ["C001", "C002", "C024", "C025", "C026", "C027", "C028", "C029", "C030"]

for d in dates:
    date_id, year, quarter, month, day = d
    # 每天 20-40 单
    daily_orders = random.randint(20, 40)
    for _ in range(daily_orders):
        # 肖胜宇相关用户出现概率更高
        if random.random() < 0.15:
            cid = random.choice(shaw_customers)
        else:
            cid = random.choice(customers)[0]
        pid = random.choice(products)[0]
        rid = random.choice(regions)[0]
        qty = random.randint(1, 20)
        base_price = random.randint(*price_map[pid])
        amount = round(qty * base_price * random.uniform(0.85, 1.15), 2)
        # 退货率约 5%-15%
        return_qty = 0
        if random.random() < 0.12:
            return_qty = random.randint(1, max(1, qty // 2))
        orders.append((
            f"ORD{date_id}{order_counter:04d}",
            cid, pid, date_id, rid, qty, amount, return_qty
        ))
        order_counter += 1

# ========== 生成销售目标 ==========
# 每个大区每个月一个目标
targets = []
target_id = 1
for rid, prov, city, region, country in regions:
    for month in range(1, 4):
        base = random.randint(200000, 800000)
        if region == "华北":
            base = random.randint(400000, 1000000)
        if prov == "四川省":
            base = random.randint(300000, 900000)
        targets.append((target_id, rid, 2025, month, base))
        target_id += 1

# ========== 生成 SQL ==========
sql_lines = [
    "SET NAMES utf8mb4;",
    "CREATE DATABASE IF NOT EXISTS dw DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "GRANT ALL PRIVILEGES ON dw.* TO 'shaw'@'%';",
    "USE dw;",
    "",
]

# dim_region
sql_lines.append("DROP TABLE IF EXISTS dim_region;")
sql_lines.append("CREATE TABLE dim_region (")
sql_lines.append("    region_id   VARCHAR(20) PRIMARY KEY,")
sql_lines.append("    province    VARCHAR(50),")
sql_lines.append("    city        VARCHAR(50),")
sql_lines.append("    region_name VARCHAR(50),")
sql_lines.append("    country     VARCHAR(50)")
sql_lines.append(");")
sql_lines.append("")
vals = ",\n".join([f"    ('{r[0]}', '{r[1]}', '{r[2]}', '{r[3]}', '{r[4]}')" for r in regions])
sql_lines.append(f"INSERT INTO dim_region (region_id, province, city, region_name, country) VALUES\n{vals};")
sql_lines.append("")

# dim_customer
sql_lines.append("DROP TABLE IF EXISTS dim_customer;")
sql_lines.append("CREATE TABLE dim_customer (")
sql_lines.append("    customer_id   VARCHAR(20) PRIMARY KEY,")
sql_lines.append("    customer_name VARCHAR(50),")
sql_lines.append("    gender        VARCHAR(10),")
sql_lines.append("    member_level  VARCHAR(20)")
sql_lines.append(");")
sql_lines.append("")
vals = ",\n".join([f"    ('{c[0]}', '{c[1]}', '{c[2]}', '{c[3]}')" for c in customers])
sql_lines.append(f"INSERT INTO dim_customer (customer_id, customer_name, gender, member_level) VALUES\n{vals};")
sql_lines.append("")

# dim_product
sql_lines.append("DROP TABLE IF EXISTS dim_product;")
sql_lines.append("CREATE TABLE dim_product (")
sql_lines.append("    product_id   VARCHAR(20) PRIMARY KEY,")
sql_lines.append("    product_name VARCHAR(200),")
sql_lines.append("    category     VARCHAR(50),")
sql_lines.append("    brand        VARCHAR(50)")
sql_lines.append(");")
sql_lines.append("")
vals = ",\n".join([f"    ('{p[0]}', '{p[1]}', '{p[2]}', '{p[3]}')" for p in products])
sql_lines.append(f"INSERT INTO dim_product (product_id, product_name, category, brand) VALUES\n{vals};")
sql_lines.append("")

# dim_date
sql_lines.append("DROP TABLE IF EXISTS dim_date;")
sql_lines.append("CREATE TABLE dim_date (")
sql_lines.append("    date_id INT PRIMARY KEY,")
sql_lines.append("    year    INT,")
sql_lines.append("    quarter VARCHAR(2),")
sql_lines.append("    month   INT,")
sql_lines.append("    day     INT")
sql_lines.append(");")
sql_lines.append("")
vals = ",\n".join([f"    ({d[0]}, {d[1]}, '{d[2]}', {d[3]}, {d[4]})" for d in dates])
sql_lines.append(f"INSERT INTO dim_date (date_id, year, quarter, month, day) VALUES\n{vals};")
sql_lines.append("")

# fact_order
sql_lines.append("DROP TABLE IF EXISTS fact_order;")
sql_lines.append("CREATE TABLE fact_order (")
sql_lines.append("    order_id       VARCHAR(30) PRIMARY KEY,")
sql_lines.append("    customer_id    VARCHAR(20),")
sql_lines.append("    product_id     VARCHAR(20),")
sql_lines.append("    date_id        INT,")
sql_lines.append("    region_id      VARCHAR(20),")
sql_lines.append("    order_quantity INT,")
sql_lines.append("    order_amount   FLOAT,")
sql_lines.append("    return_quantity INT DEFAULT 0")
sql_lines.append(");")
sql_lines.append("")

batch_size = 500
for i in range(0, len(orders), batch_size):
    batch = orders[i:i+batch_size]
    vals = ",\n".join([
        f"    ('{o[0]}', '{o[1]}', '{o[2]}', {o[3]}, '{o[4]}', {o[5]}, {o[6]:.2f}, {o[7]})"
        for o in batch
    ])
    sql_lines.append(f"INSERT INTO fact_order (order_id, customer_id, product_id, date_id, region_id, order_quantity, order_amount, return_quantity) VALUES\n{vals};")
    sql_lines.append("")

# fact_target
sql_lines.append("DROP TABLE IF EXISTS fact_target;")
sql_lines.append("CREATE TABLE fact_target (")
sql_lines.append("    target_id      INT PRIMARY KEY,")
sql_lines.append("    region_id      VARCHAR(20),")
sql_lines.append("    year           INT,")
sql_lines.append("    month          INT,")
sql_lines.append("    target_amount  FLOAT")
sql_lines.append(");")
sql_lines.append("")
vals = ",\n".join([
    f"    ({t[0]}, '{t[1]}', {t[2]}, {t[3]}, {t[4]:.2f})"
    for t in targets
])
sql_lines.append(f"INSERT INTO fact_target (target_id, region_id, year, month, target_amount) VALUES\n{vals};")
sql_lines.append("")

# 写入文件
out_path = Path(__file__).parents[1] / "docker" / "mysql" / "dw.sql"
out_path.write_text("\n".join(sql_lines), encoding="utf-8")
print(f"已生成 {len(orders)} 条订单数据")
print(f"文件保存至: {out_path}")
