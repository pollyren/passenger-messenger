import gspread
import datetime
import random

def read_sheet():
    acc = gspread.service_account(filename="service_account.json")
    sheet = acc.open("crew_attendance")
    wks = sheet.worksheet("attendance")
    return wks.get_all_records()

def main():
    tmr = datetime.datetime.today() + datetime.timedelta(days=1)
    weekday = tmr.strftime('%a')
    data = read_sheet()
    # print(data)

    name_cnt = {}
    woodlawn = []
    crown = []
    fifty_third = []
    drivers = [] # list of all drivers, their preferred pickup location, and number of passengers
    # at_cap_drivers = []
    total_cap = 0

    for person in data:
        # name = person['name'][:person['name'].index(" ") + 2]
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
    
    random.shuffle(woodlawn)
    random.shuffle(crown)
    random.shuffle(fifty_third)
    # print(woodlawn)
    # print(crown)
    # print(fifty_third)
    # print(drivers)

    woodlawners = len(woodlawn)
    crowners = len(crown)
    fifty_thirders = len(fifty_third)
    driverers = len(drivers)
    print("lengths", woodlawners, crowners, fifty_thirders, driverers)

    diff = 0
    if woodlawners + crowners + fifty_thirders + driverers > total_cap:
        diff = woodlawners + crowners + fifty_thirders + driverers - total_cap
        print("==========diff is", diff)
        if diff < 4 or diff % 4 == 0:
            while diff > 0:
                drivers.insert(0, {"name": "uber", "pickup_location": "", "capacity": 4, "passengers": []})
                diff -= min(diff, 4)
        elif diff < 6 or diff % 6 == 0:
            while diff > 0:
                drivers.insert(0, {"name": "uberXL", "pickup_location": "", "capacity": 6, "passengers": []})
                diff -= min(diff, 6)
        elif diff <= 10:
            drivers.insert(0, {"name": "uberXL", "pickup_location": "", "capacity": 6, "passengers": []})
            diff -= 6
            drivers.insert(0, {"name": "uber", "pickup_location": "", "capacity": 4, "passengers": []})
            diff -= min(diff, 4)
        else:
            while diff > 4:
                drivers.insert(0, {"name": "uberXL", "pickup_location": "", "capacity": 6, "passengers": []})
                diff -= 6
            drivers.insert(0, {"name": "uber", "pickup_location": "", "capacity": 4, "passengers": []})
            diff -= min(diff, 4)

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
                    for _ in range(driver["capacity"]):
                        if len(woodlawn) == 0: break
                        driver["passengers"].append(woodlawn.pop())
                else:
                    for _ in range(driver["capacity"]):
                        if len(crown) == 0: break
                        driver["passengers"].append(crown.pop())
        # if len(driver["passengers"]) + 1 >= driver["capacity"]:
        #     at_cap_drivers.append(driver)
    
    print(woodlawn)
    print(crown)
    print(fifty_third)
    print(drivers)
    # print(at_cap_drivers)

    for driver in drivers:
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

    for driver in drivers:
        driver["name"] = driver["name"].split()[0]
        driver["passengers"].sort()
        for i, passenger in enumerate(driver["passengers"]):
            fname = passenger.split()[0]
            if name_cnt[fname] == 1:
                driver["passengers"][i] = fname
            else:
                driver["passengers"][i] = passenger[:passenger.index(" ") + 2]
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
        print(driver["name"], "to", driver["pickup_location"] + ":", ", ".join(driver["passengers"]))
        if len(driver["passengers1"]) > 0:
            print(driver["name"], "to", driver["passengers1"].pop(0) + ": ", end = "")
            driver["passengers1"].sort()
            print(", ".join(driver["passengers1"]))
            if len(driver["passengers2"]) > 0:
                print(driver["name"], "to", driver["passengers2"].pop(0) + ": ", end = "")
                driver["passengers2"].sort()
                print(", ".join(driver["passengers2"]))

if __name__ == "__main__":
    # can maybe pass in an argument for the column header instead
    main()