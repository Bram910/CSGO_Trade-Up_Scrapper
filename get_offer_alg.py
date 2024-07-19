import pylightxl as xl
import Case_Skins as cls
from itertools import chain
import random


def calc_procent(skins, skins_set):
    nr = []
    for index, skin in enumerate(skins_set):
        nr_aux = 0
        for i in skins:
            if i == skin:
                nr_aux += 1
        nr.append(nr_aux)
    for i, sansa in enumerate(nr):
        nr[i] = nr[i] / len(skins)
    return nr


def read_xl(db, sheet_name, Cases):
    Covert = []
    Classified = []
    Restricted = []
    Mil = []
    [roww, coll] = db.ws(sheet_name).size
    data = db.ws(sheet_name).range('A2:N' + str(roww))
    for row in data:
        ObjSkin = cls.Skin()
        ObjSkin.name = row[0]
        ObjSkin.weapon = row[1]
        for i in range(0, 10):
            ObjSkin.prices.append(row[i + 3])
        if row[2] == 'Covert':
            Covert.append(ObjSkin)
        if row[2] == 'Classified':
            Classified.append(ObjSkin)
        if row[2] == 'Restricted':
            Restricted.append(ObjSkin)
        if row[2] == 'Mil-Spec':
            Mil.append(ObjSkin)
    Cases.byRarity.append(Covert)
    Cases.byRarity.append(Classified)
    Cases.byRarity.append(Restricted)
    Cases.byRarity.append(Mil)


def cheapest_skin(skin_list, i):
    minimum = 99999
    index = -1
    for index_2, skin in enumerate(skin_list):
        if skin.prices[i] != '' and skin.prices[i] != 'N/A' and skin.prices[i] is not None:
            if float(skin.prices[i]) < minimum:
                minimum = float(skin.prices[i])
                index = index_2
    if index != -1:
        return skin_list[index]
    else:
        return None


def expensive_skin(skin_list, i):
    maxim = -1
    index = -1
    for index_2, skin in enumerate(skin_list):
        if skin.prices[i] != '' and skin.prices[i] != 'N/A' and skin.prices[i] is not None:
            if float(skin.prices[i]) > maxim:
                maxim = float(skin.prices[i])
                index = index_2
    if index != -1:
        return skin_list[index]
    else:
        return None


def generate_offer(Cases, procent_min_win, procent_max_loss):
    best_deals = []
    for case in Cases:
        concatenated = chain(range(0, 4), range(5, 9))
        for i in concatenated:
            for index_0, skin_list in enumerate(case.byRarity[1:]):
                cheap_skin = cheapest_skin(skin_list, i)
                if cheap_skin != None:
                    trade_price = 10 * float(cheap_skin.prices[i])
                    float_chance = random.randint(0, 1)
                    cheap_skin_2 = cheapest_skin(case.byRarity[index_0], i + float_chance)
                    expensive_skin_2 = expensive_skin(case.byRarity[index_0], i + float_chance)
                    if cheap_skin_2 != None and expensive_skin_2 != None:
                        loss = float(cheap_skin_2.prices[i + float_chance]) / trade_price
                        win = float(expensive_skin_2.prices[i + float_chance]) / trade_price
                        if loss >= (1 - procent_max_loss / 100) and win >= (1 + procent_min_win / 100):
                            print(f"Adding deal: {case.name}, {cheap_skin.name}, {i}, {float_chance}, {len(case.byRarity[index_0])} outcomes")
                            best_deals.append([case.name, cheap_skin, i, float_chance, case.byRarity[index_0],
                                               cheap_skin_2, expensive_skin_2])
    return best_deals


def num_to_quality(number):
    qualities = ["FN", "MW", "FT", "WW", "BS", "SFN", "SMW", "SFT", "SWW", "SBS"]
    return qualities[number] if number < len(qualities) else None


def get_offer(prices_list, min_profit_procent, max_loss_procent):
    Cases = []
    db = xl.readxl(prices_list)
    sheet_names = db.ws_names
    for sheet in sheet_names[1:]:
        ObjCase = cls.Case()
        ObjCase.name = sheet
        read_xl(db, sheet, ObjCase)
        Cases.append(ObjCase)
    best_deals = generate_offer(Cases, min_profit_procent, max_loss_procent)
    if best_deals:
        random_trade = random.randint(0, len(best_deals)-1)
        return best_deals[random_trade]
    return None

