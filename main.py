""" python modules """
import os
import logging
import requests

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import Response, JSONResponse, RedirectResponse


API_KEY = os.environ.get('GEO_API_KEY')

app = FastAPI()

logging.basicConfig(filename ='app.log',
                        level = logging.DEBUG)

@app.get("/", response_class=RedirectResponse, status_code=307)
async def home():
    """ redirects home page request to documentation page """
    return "http://127.0.0.1:5000/docs"


@app.post("/getAddressDetails")
async def convertaddresstocoordinates(request: Request):
    """
    Converts address to Geo Coordinates of Longitude and Latitude

    Input:
    {
        "address": "# 3582,13 G Main Road, 4th Cross Rd, Indiranagar,Bengaluru, Karnataka 560008",
        "output_format": "json/xml"
    }


    Response: The GeocoderResult object represents a single geocoding result.
              A geocode request may return multiple result objects.

    Output:

    location contains the geocoded latitude,longitude value.
    Note that we return this location as a LatLng object, not as a formatted string.

    latitude  = res['results'][0]['geometry']['location']['lat']

    longitude = res['results'][0]['geometry']['location']['lng']


    """
    try:
        payload = await request.json()

        if payload['address'] == "" or payload['output_format'] == "":
            return Response("Missing Parameter Values", status_code=400)

        # base_url
        base_url = "https://maps.googleapis.com/maps/api/geocode/json?"

        # sanitizing params for url encoding
        address_data = payload['address'].strip('#').replace(' ', '+')

        # url encoding
        request_url = base_url + 'address=' + address_data + '&key=' + API_KEY

        # requesting the result
        res = requests.get(str(request_url)).json()

        # result in json format
        if payload['output_format'] == 'json':
            return JSONResponse(
                content={
                    "coordinates": {
                        "lat": res['results'][0]['geometry']['location']['lat'],
                        "lng": res['results'][0]['geometry']['location']['lng']},
                    "address": payload['address']},
                media_type="application/json",
                status_code=200)

        # result in xml format
        if payload['output_format'] == 'xml':
            data = f"""<?xml version="1.0" encoding="UTF-8"?>
                <root>
                    <address>{payload['address']}</address>
                    <coordinates>
                        <lat>{res['results'][0]['geometry']['location']['lat']}</lat>
                        <lng>{res['results'][0]['geometry']['location']['lng']}</lng>
                    </coordinates>
                </root>"""
        return Response(
            content=data,
            media_type="application/xml",
            status_code=200)

    except Exception as err:
        logging.error(err)
        return Response(err)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
