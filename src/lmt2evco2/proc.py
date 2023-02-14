"""Processing Module
"""

from loggin import getLogger
from json import load

import requests
import pandas as pd


logger = getLogger("lmt2evco2.proc")


def call_api(from_date, to_date):
    """Calls the API for a specific time frame
    """

    url1 = "https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date={}T00:00&end_date={}T23:59&time_trunc=day"
    r = requests.get(url1.format(from_date, to_date)).json()
    ren = r["included"][0]["attributes"]["content"][-1]["attributes"]["total"]
    nren = r["included"][1]["attributes"]["content"][-1]["attributes"]["total"]
    tenergy = ren + nren

    Combined_cycle = r["included"][1]["attributes"]["content"][2]["attributes"]["total"]
    Coal = r["included"][1]["attributes"]["content"][3]["attributes"]["total"]
    Diesel_engines = r["included"][1]["attributes"]["content"][4]["attributes"]["total"]
    Gas_turbine = r["included"][1]["attributes"]["content"][5]["attributes"]["total"]
    Steam_turbine = r["included"][1]["attributes"]["content"][6]["attributes"]["total"]
    Cogeneration = r["included"][1]["attributes"]["content"][7]["attributes"]["total"]
    Non_renewable_waste = r["included"][1]["attributes"]["content"][8]["attributes"]["total"]

    return {
        "Combined_cycle_p": 100 * Combined_cycle / tenergy,
        "Coal_p": 100 * Coal/tenergy,
        "Diesel_engines_p": 100 * Diesel_engines/tenergy,
        "Gas_turbine_p": 100 * Gas_turbine / tenergy,
        "Steam_turbine_p": 100 * Steam_turbine/ tenergy,
        "ogeneration_p": 100 * Cogeneration / tenergy,
        "Non_renewable_waste_p": 100 * Non_renewable_waste/ tenergy
    }


def run_model(lmtjson, factors, from_date, to_date):
    """Runs the model
    """

    df1 = pd.read_excel(factors)
    api_result = call_api(from_date, to_date)
    df1["Generation_percentage"] = [
        api_result["Combined_cycle_p"],
        api_result["Coal_p"],
        api_result["Diesel_engines_p"],
        api_result["Gas_turbine_p"],
        api_result["Steam_turbine_p"],
        api_result["ogeneration_p"],
        api_result["Non_renewable_waste_p"]
    ]
    df1.to_excel("factors.xlsx", index = False)

    with open(lmtjson, encoding='utf8') as fp:
        lmt_data = load(fp)[0]

        a1 = lmt_data["ResponsePlanId"]
        a2 = lmt_data["Category"]
        a3 = lmt_data["Fuel"]
        a4 = lmt_data["Segment"]
        a5 = lmt_data["EuroStandard"]
        a6 = lmt_data["Stock"]
        a7 = lmt_data["MeanActivity"]

        if a2 == "Three-wheeler" and a3 == "Electric" and a4 =="Cargo" and a5 == "Vehicle":
            factor = 0.087
        elif a2 == "Transit" and a3 == "Electric" and a4 =="Cargo" and a5 == "Vehicle":
            factor = 0.227
        elif a2 == "Big Transit" and a3 == "Electric" and a4 =="Cargo" and a5 == "Vehicle":
            factor = 0.250
        else:
            factor = 0.0

        a8 = factor * 3.6 * 10**(-6) * a7
        a9 = factor * a7

        columns = ["ResponsePlanId", "Category", "Fuel",
                   "Segment", "EuroStandard", "Stock",
                   "MeanActivity", "energyTJ", "energykwh"]
        df2_1 = pd.DataFrame(
            [[a1, a2, a3,a4,a5,a6,a7,a8,a9]],
            columns = columns
        )
        df2_1.to_excel("consumption.xlsx", index = False)
