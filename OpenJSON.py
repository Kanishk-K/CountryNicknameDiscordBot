import json

with open('EmojiToCountry.json', encoding='utf8') as json_file:
    data = json.load(json_file)

with open('CountryStateCodes.json', encoding='utf8') as Country_State:
    Country_State_JSON = json.load(Country_State)
    
Country_State.close()
json_file.close()

for item in list(data):
    if data[item] not in list(Country_State_JSON):
        print(data[item])
