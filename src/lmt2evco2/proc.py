"""Processing Module
"""

from logging import getLogger
from json import load
from os.path import join

import requests
import pandas as pd


logger = getLogger("lmt2evco2.proc")


def call_api(from_date, to_date):
    """Calls the API for a specific time frame
    """

    url1 = ("https://apidatos.ree.es/en/datos/balance/balance-electrico?"
           "start_date={}T00:00&end_date={}T23:59&time_trunc=day")

    resp = requests.get(url1.format(from_date, to_date), timeout=30.).json()
    ren = resp["included"][0]["attributes"]["content"][-1]["attributes"]["total"]
    nren = resp["included"][1]["attributes"]["content"][-1]["attributes"]["total"]
    tenergy = ren + nren

    combined_cycle = resp["included"][1]["attributes"]["content"][2]["attributes"]["total"]
    coal = resp["included"][1]["attributes"]["content"][3]["attributes"]["total"]
    diesel_engines = resp["included"][1]["attributes"]["content"][4]["attributes"]["total"]
    gas_turbine = resp["included"][1]["attributes"]["content"][5]["attributes"]["total"]
    steam_turbine = resp["included"][1]["attributes"]["content"][6]["attributes"]["total"]
    cogeneration = resp["included"][1]["attributes"]["content"][7]["attributes"]["total"]
    non_renewable_waste = resp["included"][1]["attributes"]["content"][8]["attributes"]["total"]

    return {
        "Combined_cycle_p": 100 * combined_cycle / tenergy,
        "Coal_p": 100 * coal / tenergy,
        "Diesel_engines_p": 100 * diesel_engines / tenergy,
        "Gas_turbine_p": 100 * gas_turbine / tenergy,
        "Steam_turbine_p": 100 * steam_turbine / tenergy,
        "ogeneration_p": 100 * cogeneration / tenergy,
        "Non_renewable_waste_p": 100 * non_renewable_waste / tenergy
    }


def run_model(lmtjson, factors, from_date, to_date, outdir):
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
    df1.to_excel(join(outdir, "factors.xlsx"), index = False)

    with open(lmtjson, encoding='utf8') as f_p:
        lmt_data = load(f_p)[0]

        a_1 = lmt_data["ResponsePlanId"]         # FIXME - KeyError
        a_2 = lmt_data["Category"]
        a_3 = lmt_data["Fuel"]
        a_4 = lmt_data["Segment"]
        a_5 = lmt_data["EuroStandard"]
        a_6 = lmt_data["Stock"]
        a_7 = lmt_data["MeanActivity"]

        if a_2 == "Three-wheeler" and a_3 == "Electric" and a_4 =="Cargo" and a_5 == "Vehicle":
            factor = 0.087
        elif a_2 == "Transit" and a_3 == "Electric" and a_4 =="Cargo" and a_5 == "Vehicle":
            factor = 0.227
        elif a_2 == "Big Transit" and a_3 == "Electric" and a_4 =="Cargo" and a_5 == "Vehicle":
            factor = 0.250
        else:
            factor = 0.0

        a_8 = factor * 3.6 * 10**(-6) * a_7
        a_9 = factor * a_7

        columns = ["ResponsePlanId", "Category", "Fuel",
                   "Segment", "EuroStandard", "Stock",
                   "MeanActivity", "energyTJ", "energykwh"]
        df2 = pd.DataFrame(
            [[a_1, a_2, a_3, a_4, a_5, a_6, a_7, a_8, a_9]],
            columns = columns
        )
        df2.to_excel(join(outdir, "consumption.xlsx"), index = False)
