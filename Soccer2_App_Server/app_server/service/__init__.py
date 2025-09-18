import re


def translate_re(result_str):
    all_valid_trades = []
    # wave 安卓单页详情
    if result_str.strip().startswith("Successful"):
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Successful (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 安卓单页详情2
    if result_str.strip().startswith("Type successful"):
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"amount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 苹果单页详情
    elif result_str.strip().startswith("Note"):
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"(\d+\s?,?\d+) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色安卓
    elif "Comment" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"mount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色苹果
    elif "Note Lay" in result_str or "Lay Nar Note" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Amount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色苹果
    elif "Note Lay" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Amount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色安卓
    elif "Successfully" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Amount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色安卓2
    elif "successful Lay" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"amount (\d+.*?) kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 列表安卓
    elif "list" in result_str:
        trans_ids = re.findall(r"number.*?(\d{8,})", result_str)
        amounts = re.findall(r"([+-]\d+,?\d+) \b(ks|kyat|Kyat|kyats)\b", result_str)
        print(min(len(trans_ids), len(amounts)))
        for i in range(min(len(trans_ids), len(amounts))):
            if not amounts[i]:
                continue
            amount = int(amounts[i][0].replace(" ", "").replace(",", ""))
            if amount > 0:
                continue
            all_valid_trades.append({'transaction_id': trans_ids[i], 'amount': abs(amount)})
    # ks 单张苹果
    if not len(all_valid_trades) and re.search(r"Detail.*? Operation ", result_str):
        transaction_id = re.search(r"(\d{20})", result_str)
        result_str_lower = result_str.lower()
        amount_re = re.search(r"-(\d+,?\d+).00 ks", result_str_lower)
        if not amount_re:
            amount_re = re.search(r"-(\d+,?\d+).00\(Ks", result_str_lower.replace(" ", ""))
        print(transaction_id, amount_re)
        if amount_re and transaction_id:
            transaction_id = transaction_id[1]
            amount = float(amount_re[1].replace(",", ""))
            amount = abs(amount)
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    print("mian translate:", all_valid_trades)
    if not len(all_valid_trades):
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"-(\d+,?\d+).00 \wyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    return all_valid_trades


def translate_re_en(result_str):
    all_valid_trades = []
    # wave 安卓单页详情
    if result_str.strip().startswith("Successful"):
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Successful (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 列表安卓
    elif "History" in result_str:
        all_trades = re.findall(r"Send Money -(.*?) Kyat.*?TransactionID-?(\d+)", result_str)
        for trade in all_trades:
            print(trade)
            amount = int(trade[0].replace(",", ""))
            all_valid_trades.append({'transaction_id': trade[1], 'amount': amount})
    # wave 苹果单页详情
    elif result_str.strip().startswith("Note"):
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"(\d+\s?,?\d+) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色安卓
    elif "Comment" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Amount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色苹果
    elif "Note Lay" in result_str or "Lay Nar" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Amount (\d+.*?)\s?Kyat", result_str)
        if not amount_re:
            amount_re = re.search(r"Send Money (\d+.*?)\s?Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色苹果
    elif "Note Lay" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Amount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # wave 单张黄色苹果
    elif "Successfully" in result_str:
        transaction_id = re.search(r".*\s(\d{8,})", result_str)
        amount_re = re.search(r"Amount (\d+.*?) Kyat", result_str)
        if transaction_id and amount_re:
            transaction_id = transaction_id[1]
            amount = int(amount_re[1].replace(",", ""))
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # ks 单张苹果
    elif "Detailed Operation" in result_str:
        transaction_id = re.search(r"(\d{20})", result_str)
        amount_re = re.search(r"-(\d+,?\d+).00 Ks", result_str)
        print(transaction_id, amount_re)
        if amount_re and transaction_id:
            transaction_id = transaction_id[1]
            amount = float(amount_re[1].replace(",", ""))
            amount = abs(amount)
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    # ks 单张苹果
    elif "Details Payment" in result_str:
        transaction_id = re.search(r"(\d{20})", result_str)
        amount_re = re.search(r"-(\d+,?\d+).00\s?Ks", result_str)
        print(transaction_id, amount_re)
        if amount_re and transaction_id:
            transaction_id = transaction_id[1]
            amount = float(amount_re[1].replace(",", ""))
            amount = abs(amount)
            all_valid_trades.append({'transaction_id': transaction_id, 'amount': amount})
    print("en translate:", all_valid_trades)
    return all_valid_trades
