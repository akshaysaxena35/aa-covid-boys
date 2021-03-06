import unittest
import sqlite3
import json
import os
import requests
import matplotlib.pyplot as plt
import numpy as np

# team name: Ann Arbor COVID Boys
# teammates: Akshay Saxena (akshaysa), Michael Liu (liumic)
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
    # cur.execute('DROP TABLE IF EXISTS historical_covid')
    cur.execute('CREATE TABLE IF NOT EXISTS historical_covid (date INT PRIMARY KEY, state TEXT, positive INT, currently_hospitalized INT, currently_in_icu INT, currently_on_ventilator INT, recovered INT, positive_tests INT, positive_cases INT, confirmed_deaths INT, antibody_tests INT, positive_test_increases INT, death_increases INT)')
    conn.commit()
    count = 0
    more25 = ""
    for data in historic_data:
        count += 1
        

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
        date_list = []
        updated_date_list = []
        cur.execute('SELECT date from historical_covid')
        for i in cur:
            date_list.append(i)
        for datekey in date_list:
            updated_date_list.append(datekey[0])
        if not date in updated_date_list:
            cur.execute('INSERT INTO historical_covid (date, state, positive, currently_hospitalized, currently_in_icu, currently_on_ventilator, recovered, positive_tests, positive_cases, confirmed_deaths, antibody_tests, positive_test_increases, death_increases) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (date, state, positivecases, hospitalized, icu, ventilator, recovered, pos_tests, pos_cases, deaths, antibody_tests, pos_increase, death_increase))
            conn.commit()

        if (count % 25 == 0 and count <= 100):
            more25 = input(str(count) + " Data Stored in historical_covid. Do you want to continue? (YES, NO) : ")
            if(more25 == "YES"):
                continue
            elif (more25 == "NO"):
                break
            else:
                print("Not a valid input. No longer adding data")
                break



    cur.execute('DROP TABLE IF EXISTS michigan_county_data')
    cur.execute('CREATE TABLE IF NOT EXISTS michigan_county_data (county_id INT, population INT, infection_rate INT, cases INT, deaths INT, positive_tests INT, negative_tests INT, new_cases INT, new_deaths INT, vaccinations_initiated INT, vaccinations_completed INT, vaccines_administered INT)')
    conn.commit()
    
    count = 0
    county_list = []
    for data in current_data:
        count += 1
        county_list.append(data['county'])
        if (count % 25 == 0 and count <= 100):
            more25 = input(str(count) + " Data Stored in michigan_county_data. Do you want to continue? (YES, NO) : ")
            if(more25 == "YES"):
                continue
            elif (more25 == "NO"):
                break
            else:
                print("Not a valid input. No longer adding data")
                break

    # cur.execute('DROP TABLE IF EXISTS county_id_table')



    cur.execute('CREATE TABLE IF NOT EXISTS county_id_table (county_id INT PRIMARY KEY, county TEXT)')
    countyid = 1
    check_list = []
    county_check = ""


    for county in county_list:
        cur.execute('SELECT county FROM county_id_table') # WHERE county = ?', (county, ))
        for i in cur:
            check_list.append(i)
        if not county in check_list:
            cur.execute('REPLACE INTO county_id_table (county_id, county) VALUES (?,?)', (countyid, county))
            countyid += 1


    

    newcount = 0
    for data in current_data:
        newcount += 1
        county = data['county'] #have to remove this from table itself
        cur.execute('SELECT county_id from county_id_table WHERE county = ?', (county, ))
        county_addlist = []
        for i in cur:
            county_addlist.append(i)
        countyid = county_addlist[0][0]
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
        cur.execute('INSERT INTO michigan_county_data (county_id, population, infection_rate, cases, deaths, positive_tests, negative_tests, new_cases, new_deaths, vaccinations_initiated, vaccinations_completed, vaccines_administered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (countyid, population, infectionrate, cases, deaths, pos_tests, neg_tests, newcases, newdeaths, vacc_init, vacc_completed, vacc_admin))
        conn.commit()

        if (newcount == count):
            break


# select pertinenent data from database and do analysis 1 on the numbers, return analyzed data
def dataAnalysis():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/covid.db")
    cur = conn.cursor()

    cur.execute('SELECT * FROM historical_covid')
    historicalData = cur.fetchall()
    dateList = []
    posCasesList = []
    for data in historicalData:
        if (str(data[0])[6:8] == "01"):
            strDate = str(data[0])
            strDate = strDate[0:4] + '/' + strDate[4:6] + '/' + strDate[6:8]
            dateList.append(strDate)

            posCasesList.append(data[8])


    posCasesList.reverse()
    dateList.reverse()


    fig, ax = plt.subplots()
    ax.plot(dateList,posCasesList)
    plt.xticks( rotation = 45)
    ax.set_xlabel('Date')
    ax.set_ylabel('Positive Cases')
    ax.set_title("Presence of Covid in Michigan Over One Year")
    ax.grid()

    fig.savefig("timevcovidgraph")
    plt.show()


    #THE FOLLOWING SHOWS THE AVERAGE COVID CASES AND DAILY DEATHS PER MONTH TO SEE IF THERE'S AN
    #INCREASE IN HOW HOSPITALS AND MEDICATION HAVE AIDED IN THE TREATMENT AND PREVENTION OF DEATH IN COVID PATIENTS

    monthlyAverageDailyDeaths = []
    monthlyAverageCovidCases = []

    for month in range (1,14):
        deathCount = 0
        positiveTest = 0
        for days in range(28):
            deathCount += historicalData[days*month][12]
            positiveTest += historicalData[days*month][11]

        monthlyAverageDailyDeaths.append(deathCount/31)
        monthlyAverageCovidCases.append(positiveTest/31)

    monthlyAverageCovidCases.reverse()
    monthlyAverageDailyDeaths.reverse()

    plt.subplot(1,2,1)
    plt.plot(dateList, monthlyAverageCovidCases, 'y-', label = "Average Covid Cases")
    plt.title("Average Covid Cases")
    plt.xticks( rotation = 45)
    plt.grid()

    plt.subplot(1,2,2)
    plt.plot(dateList, monthlyAverageDailyDeaths, 'r-', label = "Average Deaths")
    plt.title("Average Deaths")
    plt.xticks( rotation = 45)
    plt.grid()
    fig.savefig("treatmentimprovgraph")
    plt.show()

    #THE FOLLOWING WILL BE A PIE CHART REPRESENTING MAJOR COUNTIES
    cur.execute('SELECT county FROM county_id_table JOIN michigan_county_data WHERE michigan_county_data.population > ? AND michigan_county_data.county_id = county_id_table.county_id', (160000,))

    countyNames= cur.fetchall()

    cur.execute('SELECT * FROM michigan_county_data WHERE michigan_county_data.population > ?', (160000,))
    countyData = cur.fetchall()

    casesList = []

    for county in countyData:
        casesList.append(county[3])

    plt.pie(casesList, labels = countyNames)
    plt.axis('equal')
    plt.title("Case Distribution by Major Counties in Michigan")
    plt.show()

    percentInfectedRate = []
    for county in countyData:
        percentInfectedRate.append(county[3]/county[1])


    y_pos = np.arange(len(countyNames))

    plt.bar(y_pos, percentInfectedRate, align = 'center', alpha = .5)
    plt.xticks(y_pos, countyNames, rotation = 45)
    
    plt.ylabel('Percent Infected')
    plt.title('Percent of Population Infected in Counties in Michigan with Population > 160,000')
    plt.show()

# select next data and do analysis 2 on those numbers, return analyzed data

# take in returned data, create visualizations using matplotlib


# add main function
def main():
    cur, conn = setUpDatabase("covid.db")
    currentdata = getCovidActNowData()
    histdata = getCovidTrackingData()
    populateDatabase(histdata, currentdata, cur, conn)
    if (input("Do you want to do data analysis? The data analysis will show proper results only if all data is added(YES, NO)") == "YES"):
        dataAnalysis()
    else:
        print("Did not receieve YES, shutting down")
    

if __name__ == "__main__":
    main()
    # unittest.main(verbosity = 2)
