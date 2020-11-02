import json
import os
import shutil

src = os.path.join(os.getcwd(),"BaseCountries.geojson")
dst = os.path.join(os.getcwd(),"GuildFiles","NovaCrypt.geojson")
shutil.copyfile(src,dst)
GuildMemberFile = open(f"GuildFiles/NovaCrypt.json","r")
GuildMemberJSON = json.load(GuildMemberFile)
GuildMemberFile.close()
GeoJSONFile = open("GuildFiles/NovaCrypt.geojson","r")
GeoJSON = json.load(GeoJSONFile)
GeoJSONFile.close()
for Country in GeoJSON["features"]:
    if Country["properties"]["ISO2"] != "-99":
        Country["properties"]["Members"] = GuildMemberJSON[Country["properties"]["ISO2"]]
GeoJSONFile = open("GuildFiles/NovaCrypt.geojson","w")
json.dump(GeoJSON,GeoJSONFile,indent=1)
GeoJSONFile.close()
print("GEOJson Generated.")
GeoJSONFile = open("GuildFiles/NovaCrypt.geojson","r")
JavascriptFile = open("GuildFiles/NovaCrypt.js","w")
JavascriptFile.write("var countryData = " + GeoJSONFile.read().replace('\n', '') + ";")

GeoJSONFile.close()
JavascriptFile.close()
print("Javascript Generated!")