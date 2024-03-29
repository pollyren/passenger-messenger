import gspread
import datetime
import random
import sys

def read_sheet(gspread_file, workbook, worksheet):
    acc = gspread.service_account(filename = gspread_file)
    sheet = acc.open(workbook)
    wks = sheet.worksheet(worksheet)
    return wks.get_all_records()

def process_names(data):
    if "-d" in sys.argv:
        weekday = sys.argv[sys.argv.index("-d") + 1]
    else:
        tmr = datetime.datetime.today() + datetime.timedelta(days=1)
        weekday = tmr.strftime('%a')

    name_cnt = {}
    woodlawn = []
    crown = []
    fifty_third = []
    drivers = [] # list of all drivers, their preferred pickup location, and number of passengers
    total_cap = 0

    for person in data:
        name = person['name'].strip()
        fname = name.split()[0]
        if fname in name_cnt:
            name_cnt[fname] += 1
        else: 
            name_cnt[fname] = 1
        match person[weekday].lower():
            case "x":
                match person['pickup_location']:
                    case "Woodlawn":
                        woodlawn.append(name)
                    case "Crown":
                        crown.append(name)
                    case "53rd":
                        fifty_third.append(name)
                    case _:
                        pass
            case "d":
                total_cap += person["car_spots"]
                if person["car_spots"] == 12:
                    drivers.insert(0, {"name": name, "pickup_location": person["pickup_location"], "capacity": 12, "passengers": [], "passengers1": [], "passengers2": []})
                else: 
                    drivers.append({"name": name, "pickup_location": person["pickup_location"], "capacity": person["car_spots"], "passengers": [], "passengers1": [], "passengers2": []})
            case _:
                pass
    return name_cnt, woodlawn, crown, fifty_third, drivers, total_cap

def shuffle(woodlawn, crown, fifty_third):
    random.shuffle(woodlawn)
    random.shuffle(crown)
    random.shuffle(fifty_third)
    return woodlawn, crown, fifty_third

def determine_ubers(woodlawn, crown, fifty_third, drivers, total_cap):
    woodlawners = len(woodlawn)
    crowners = len(crown)
    fifty_thirders = len(fifty_third)
    driverers = len(drivers)
    # print(woodlawners, crowners, fifty_thirders, driverers, total_cap)

    diff = 0
    if woodlawners + crowners + fifty_thirders + driverers > total_cap:
        diff = woodlawners + crowners + fifty_thirders + driverers - total_cap
        # print(diff)
    if diff < 4:
        drivers.insert(0, {"name": "Uber", "pickup_location": "", "capacity": 4, "passengers": []})
        diff -= 4
    elif diff < 6:
        drivers.insert(0, {"name": "UberXL", "pickup_location": "", "capacity": 6, "passengers": []})
        diff -= 6
    # elif diff <= 10:
    #     print("case 3")
    #     drivers.insert(0, {"name": "UberXL", "pickup_location": "", "capacity": 6, "passengers": []})
    #     diff -= 6
    #     drivers.insert(0, {"name": "Uber", "pickup_location": "", "capacity": 4, "passengers": []})
    #     diff -= min(diff, 4)
    else:
        while diff >= 9:
            drivers.insert(0, {"name": "UberXL", "pickup_location": "", "capacity": 6, "passengers": []})
            diff -= 6
        while diff > 0:
            drivers.insert(0, {"name": "Uber", "pickup_location": "", "capacity": 4, "passengers": []})
            diff -= 4

def fill_cars(woodlawn, crown, fifty_third, drivers):
    for driver in drivers:
        match driver["pickup_location"]:
            case "Woodlawn":
                for _ in range(driver["capacity"] - 1):
                    if len(woodlawn) == 0: break
                    driver["passengers"].append(woodlawn.pop())
            case "Crown":
                for _ in range(driver["capacity"] - 1):
                    if len(crown) == 0: break
                    driver["passengers"].append(crown.pop())
            case "53rd":
                for _ in range(driver["capacity"] - 1):
                    if len(fifty_third) == 0: break
                    driver["passengers"].append(fifty_third.pop())
            case _: # rideshare case
                if len(woodlawn) > len(crown): 
                    driver["pickup_location"] = "Woodlawn"
                    for _ in range(driver["capacity"]):
                        if len(woodlawn) == 0: break
                        driver["passengers"].append(woodlawn.pop())
                else:
                    driver["pickup_location"] = "Crown"
                    for _ in range(driver["capacity"]):
                        if len(crown) == 0: break
                        driver["passengers"].append(crown.pop())

def check_empty(drivers):
    for i, driver in enumerate(drivers):
        if len(driver["passengers"]) == 0:
            drivers.insert(0, drivers.pop(i)) # moves empty cars to pickup stragglers first

def pickup_stragglers(woodlawn, crown, fifty_third, drivers): 
    for driver in drivers:
        if "Uber" in driver["name"]: continue
        open_seats = driver["capacity"] - len(driver["passengers"]) - 1
        if open_seats == 0: continue
        if len(woodlawn) > 0:
            driver["passengers1"].append("Woodlawn")
            for _ in range(open_seats):
                if len(woodlawn) == 0: break
                driver["passengers1"].append(woodlawn.pop())
            open_seats -= (len(driver["passengers1"]) - 1)
        if len(crown) > 0:
            if len(driver["passengers1"]) == 0:
                driver["passengers1"].append("Crown")
                for _ in range(open_seats):
                    if len(crown) == 0: break
                    driver["passengers1"].append(crown.pop())
                open_seats -= (len(driver["passengers1"]) - 1)
            else: 
                driver["passengers2"].append("Crown")
                for _ in range(open_seats):
                    if len(crown) == 0: break
                    driver["passengers2"].append(crown.pop())
                open_seats -= (len(driver["passengers2"]) - 1)
        if len(fifty_third) > 0:
            if len(driver["passengers1"]) == 0:
                driver["passengers1"].append("53rd")
                for _ in range(open_seats):
                    if len(fifty_third) == 0: break
                    driver["passengers1"].append(fifty_third.pop())
                open_seats -= (len(driver["passengers1"]) - 1)
            else: 
                driver["passengers2"].append("53rd")
                for _ in range(open_seats):
                    if len(fifty_third) == 0: break
                    driver["passengers2"].append(fifty_third.pop())
                open_seats -= (len(driver["passengers2"]) - 1)

def sort_and_check_duplicates(driver, name_cnt):
    driver["passengers"].sort()
    for i, passenger in enumerate(driver["passengers"]):
        fname = passenger.split()[0]
        if name_cnt[fname] == 1:
            driver["passengers"][i] = fname
        else:
            driver["passengers"][i] = passenger[:passenger.index(" ") + 2]
    if "Uber" not in driver["name"]:
        for i, passenger in enumerate(driver["passengers1"]):
            fname = passenger.split()[0]
            try:
                if name_cnt[fname] == 1:
                    driver["passengers1"][i] = fname
                else:
                    driver["passengers1"][i] = passenger[:passenger.index(" ") + 2]
            except: continue
        for i, passenger in enumerate(driver["passengers2"]):
            fname = passenger.split()[0]
            try:
                if name_cnt[fname] == 1:
                    driver["passengers2"][i] = fname
                else:
                    driver["passengers2"][i] = passenger[:passenger.index(" ") + 2]
            except: continue

def print_assignments(driver):
    if len(driver["passengers"]) > 0:
        print(driver["name"], "to", driver["pickup_location"] + ":", ", ".join(driver["passengers"]))
    elif "Uber" not in driver["name"] and len(driver["passengers1"]) == 0:
        print(driver["name"], "to", driver["name"] + ":", driver["name"])
    if "Uber" not in driver["name"] and len(driver["passengers1"]) > 0:
        print(driver["name"], "to", driver["passengers1"].pop(0) + ": ", end = "")
        driver["passengers1"].sort()
        print(", ".join(driver["passengers1"]))
        if len(driver["passengers2"]) > 0:
            print(driver["name"], "to", driver["passengers2"].pop(0) + ": ", end = "")
            driver["passengers2"].sort()
            print(", ".join(driver["passengers2"]))

def finalise_assignments(drivers, name_cnt):
    for driver in drivers:
        driver["name"] = driver["name"].split()[0]
        sort_and_check_duplicates(driver, name_cnt)
        print_assignments(driver)

def main():
    sheet = sys.argv[sys.argv.index("-s") + 1] if "-s" in sys.argv else "crew_attendance"
    book = sys.argv[sys.argv.index("-b") + 1] if "-b" in sys.argv else "attendance"
    data = read_sheet("service_account.json", sheet, book)
    name_cnt, woodlawn, crown, fifty_third, drivers, total_cap = process_names(data)
    woodlawn, crown, fifty_third = shuffle(woodlawn, crown, fifty_third)
    determine_ubers(woodlawn, crown, fifty_third, drivers, total_cap)
    fill_cars(woodlawn, crown, fifty_third, drivers)
    check_empty(drivers)
    pickup_stragglers(woodlawn, crown, fifty_third, drivers)
    finalise_assignments(drivers, name_cnt)

if __name__ == "__main__":
    main()