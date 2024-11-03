const express = require("express");
const path = require("path");
const http = require("http");
const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));

const app = express();

app.get("/status", (request, response) => {
  const status = {
    Status: "Running",
  };

  response.send(status);
});

app.get("/info", async (res, req) => {
  const url =
    "https://geocoding.geo.census.gov/geocoder/geographies/address?street=4600+Silver+Hill+Rd&city=Washington&state=DC&benchmark=Public_AR_Current&vintage=Current_Current&layers=10&format=json";

  const options = {
    method: "GET",
    headers: {},
  };
  // promise syntax
  // fetch(url, options)
  //   .then((res) => res.json())
  //   .then((json) => {console.log(json)})
  //   .catch((err) => console.error("error:" + err));

  try {
    let response = await fetch(url, options);
    const data = await response.json();
    const city = data.result.input.address.city;
    const geoInfo =
      data.result.addressMatches[0].geographies["Census Block Groups"][0];
    const tract = geoInfo["TRACT"];

    console.log(`city is: ${city}`);
    console.log(`tract is: ${tract}`);
    // console.log(`data is: ${JSON.stringify(data)}`)

    const tractInfo = {
      tract: tract,
    };

    res.status(200);
  } catch (err) {
    console.log(err);
    res.status(500).json({ msg: `Internal Server Error.` });
  }
});

app.listen(3000, () => {
  console.log("Server Listening on PORT: 3000");
});
