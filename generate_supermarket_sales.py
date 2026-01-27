import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def main():
    # 生成 2024 年的所有日期
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    num_days = (end_date - start_date).days + 1

    dates = [start_date + timedelta(days=i) for i in range(num_days)]

    # 产品类别与商品
    categories = {
        "水果": ["苹果", "香蕉", "橙子", "葡萄", "西瓜", "草莓"],
        "蔬菜": ["西红柿", "黄瓜", "土豆", "胡萝卜", "菠菜", "西兰花"],
        "乳制品": ["纯牛奶", "酸奶", "奶酪", "黄油", "炼乳"],
    }

    # 销售地区（按城市，后续在看板中可绘制中国地图）
    cities = [
        ("北京", "华北"),
        ("天津", "华北"),
        ("上海", "华东"),
        ("广州", "华南"),
        ("深圳", "华南"),
        ("杭州", "华东"),
        ("南京", "华东"),
        ("成都", "西南"),
        ("重庆", "西南"),
        ("武汉", "华中"),
        ("西安", "西北"),
    ]

    np.random.seed(2024)
    rows = []

    for current_date in dates:
        # 每天生成 30~80 条销售记录
        num_records = np.random.randint(30, 81)
        for _ in range(num_records):
            category = np.random.choice(list(categories.keys()))
            product = np.random.choice(categories[category])
            quantity = np.random.randint(1, 11)
            city, region = cities[np.random.randint(0, len(cities))]

            # 根据类别设定一个合理的单价区间（人民币）
            if category == "水果":
                unit_price = np.round(np.random.uniform(3, 25), 2)
            elif category == "蔬菜":
                unit_price = np.round(np.random.uniform(2, 15), 2)
            else:  # 乳制品
                unit_price = np.round(np.random.uniform(5, 40), 2)

            total_amount = np.round(quantity * unit_price, 2)

            rows.append(
                {
                    "日期": current_date.date(),
                    "产品类别": category,
                    "商品名称": product,
                    "销售地区": city,
                    "销售数量": quantity,
                    "单价": unit_price,
                    "总金额": total_amount,
                }
            )

    # 构建 DataFrame
    sales_df = pd.DataFrame(rows)

    # 保存到当前项目目录
    output_path = "supermarket_sales.xlsx"
    sales_df.to_excel(output_path, index=False)
    print(f"生成完成: {output_path}, 记录数: {len(sales_df)}")


if __name__ == "__main__":
    main()

