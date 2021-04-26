import unittest
import sqlite3
import json
import os
import requests

# team name: Ann Arbor COVID Boys
# teammates: Akshay Saxena,
# APIs used:

# function 1: set up database (check if it exists first)
def setUpDatabase(db_name):
    count = 0
    path = os.path.dirname(os.path.abspath(__file__))
    # if os.path.exists(path + '/' + db_name):
    #     count += 1
    # else:
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn

# get API 1 information and return proper data; current data
def getCovidActNowData():
    actnow_api_key = "0d3ca56959c64772b13872f6ea1284ed"
    state = "MI"
    base_url = "https://api.covidactnow.org/v2/county/{}.json?apiKey={}"
    request_url = base_url.format(state, actnow_api_key)
    print(request_url)

    try:
        r = requests.get(request_url)
    except Exception:
        print("exception")
    data = r.text
    actnow_dict = json.loads(data)
    return actnow_dict

# get API 2 information and return proper data (might be able to do this in 1 function); historical data
def getCovidTrackingData():
    request_url = "https://api.covidtracking.com/v1/states/mi/daily.json"
    try:
        r = requests.get(request_url)
    except Exception:
        print("exception")
    data = r.text
    tracking_dict = json.loads(data)
    return tracking_dict


# add information to databases (if we don't know a way to do 2nd table, add ids for all districts)
def populateDatabase(historic_data, current_data, cur, conn):
    cur.execute('DROP TABLE IF EXISTS historical_covid')
    cur.execute('CREATE TABLE IF NOT EXISTS historical_covid (date INT, state TEXT, positive INT, currently_hospitalized INT, currently_in_icu INT, currently_on_ventilator INT, recovered INT, positive_tests INT, positive_cases INT, confirmed_deaths INT, antibody_tests INT, positive_test_increases INT, death_increases INT)')
    conn.commit()

    for data in historic_data:
        date = data['date']
        state = data['state']
        positivecases = data['positive']
        hospitalized = data['hospitalizedCurrently']
        icu = data['inIcuCurrently']
        ventilator = data['onVentilatorCurrently']
        recovered = data['recovered']
        pos_tests = data['positiveTestsViral']
        pos_cases = data['positiveCasesViral']
        deaths = data['deathConfirmed']
        antibody_tests = data['totalTestsAntibody']
        pos_increase = data['positiveIncrease']
        death_increase = data['deathIncrease']
        cur.execute('INSERT INTO historical_covid (date, state, positive, currently_hospitalized, currently_in_icu, currently_on_ventilator, recovered, positive_tests, positive_cases, confirmed_deaths, antibody_tests, positive_test_increases, death_increases) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (date, state, positivecases, hospitalized, icu, ventilator, recovered, pos_tests, pos_cases, deaths, antibody_tests, pos_increase, death_increase))
        conn.commit()

    cur.execute('DROP TABLE IF EXISTS michigan_county_data')
    cur.execute('CREATE TABLE IF NOT EXISTS michigan_county_data (county_id INT, county TEXT, population INT, infection_rate INT, cases INT, deaths INT, positive_tests INT, negative_tests INT, new_cases INT, new_deaths INT, vaccinations_initiated INT, vaccinations_completed INT, vaccines_administered INT)')
    conn.commit()

    for data in current_data:
        countyid = data['fips']
        county = data['county']
        population = data['population']
        infectionrate = data['metrics']['infectionRate']
        cases = data['actuals']['cases']
        deaths = data['actuals']['deaths']
        pos_tests = data['actuals']['positiveTests']
        neg_tests = data['actuals']['negativeTests']
        newcases = data['actuals']['newCases']
        newdeaths = data['actuals']['newDeaths']
        vacc_init = data['actuals']['vaccinationsInitiated']
        vacc_completed = data['actuals']['vaccinationsCompleted']
        vacc_admin = data['actuals']['vaccinesAdministered']
        cur.execute('INSERT INTO michigan_county_data (county_id, county, population, infection_rate, cases, deaths, positive_tests, negative_tests, new_cases, new_deaths, vaccinations_initiated, vaccinations_completed, vaccines_administered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (countyid, county, population, infectionrate, cases, deaths, pos_tests, neg_tests, newcases, newdeaths, vacc_init, vacc_completed, vacc_admin))
        conn.commit()


# select pertinenent data from database and do analysis 1 on the numbers, return analyzed data

# select next data and do analysis 2 on those numbers, return analyzed data

# take in returned data, create visualizations using matplotlib

# add test functions?

# add main function
def main():
    cur, conn = setUpDatabase("covid.db")
    currentdata = getCovidActNowData()
    histdata = getCovidTrackingData()
    populateDatabase(histdata, currentdata, cur, conn)

if __name__ == "__main__":
    main()
    # unittest.main(verbosity = 2)
