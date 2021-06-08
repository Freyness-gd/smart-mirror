import requests, json

def get_weather():
    country='Austria'
    city='Brixlegg'

    url = "http://api.openweathermap.org/data/2.5/weather?q={1},{0}&appid=RANDOM&units=metric"
    url = url.format(country, city)

    try:

        res = requests.get(url)
        data=json.dumps((res.json()), indent=4, sort_keys=True)

        return data

    except Exception as e:
        print("Ooops!! Something went wrong: \n")
        print(e.__class__, "\n")
        print("Contact the support service!\n")

        return -1

def main():
    print(get_weather())

#if __name__ == '__main__':
#    main()
