import express from "express";
import bodyParser from "body-parser";
import axios from "axios";
import fs from "fs";
import { parse } from "csv-parse";

const app = express();
const port = 3000;
const API_URL = "http://localhost:5000";

const users = ["Camilla", "Pedro", "Paulo", "Ana", "Maria", "Eduardo", "José"];
let files = [];
let arquivo = [];
fs.createReadStream("../G-1.csv")
  .pipe(parse({ delimiter: "," }))
  .on("data", function (row) {
    arquivo.push(row);
  });
files.push(arquivo);
let arquivo2 = [];
fs.createReadStream("../G-2.csv")
  .pipe(parse({ delimiter: "," }))
  .on("data", function (row) {
    arquivo2.push(row);
  });
files.push(arquivo2);
let arquivo3 = [];
fs.createReadStream("../A-60x60-1.csv")
  .pipe(parse({ delimiter: "," }))
  .on("data", function (row) {
    arquivo3.push(row);
  });
files.push(arquivo3);
let arquivo4 = [];
fs.createReadStream("../g-30x30-1.csv")
  .pipe(parse({ delimiter: "," }))
  .on("data", function (row) {
    arquivo4.push(row);
  });
files.push(arquivo4);
let arquivo5 = [];
fs.createReadStream("../g-30x30-2.csv")
  .pipe(parse({ delimiter: "," }))
  .on("data", function (row) {
    arquivo5.push(row);
  });
files.push(arquivo5);
let arquivo6 = [];
fs.createReadStream("../A-30x30-1.csv")
  .pipe(parse({ delimiter: "," }))
  .on("data", function (row) {
    arquivo6.push(row);
  });
files.push(arquivo6);

app.use(bodyParser.urlencoded({ extended: true }));

app.get("/", (req, res) => {
  res.render("index.ejs");
});

app.get("/random", async (req, res) => {
  let performance1 = await getPerformance();
  const result = await axios.post(API_URL + "/blas", {
    usuario: users[0],
    sinal: files[0],
    modelo: 1,
  });
  let performance2 = await getPerformance();
  let aux = [];
  let aux2 = [];
  aux.push(result.data);
  aux2.push(performance1);
  aux2.push(performance2);
  res.render("relatorios.ejs", { imagens: aux, performance: aux2 });
});

app.get("/many-tests", async (req, res) => {
  const count = 100;
  const requests = [];

  for (let i = 0; i < count; i++) {
    requests.push(getRandomDataWithDelay());
    if (i != 0 && i % 10 == 0) {
      requests.push(getPerformance());
    }
  }
  let aux2 = [];
  let performance1 = await getPerformance();
  const results = await Promise.all(requests);
  let performance2 = await getPerformance();
  aux2.push(performance1);
  let performances = results.filter((result) => result.time);
  for (let i = 0; i < performances.length; i++) {
    aux2.push(performances[i]);
  }
  aux2.push(performance2);
  res.render("relatorios.ejs", {
    imagens: results.filter((result) => result.usuario),
    performance: aux2,
  });
});

const getRandomDataWithDelay = async () => {
  const delay = Math.floor(Math.random() * 5000);
  await new Promise((resolve) => setTimeout(resolve, delay));
  return getRandomData();
};

const getRandomData = async () => {
  const user = Math.floor(Math.random() * 7);
  const file = Math.floor(Math.random() * 6);
  const response = await axios.post(API_URL + "/blas", {
    usuario: users[user],
    sinal: files[file],
    modelo: file > 2 ? 2 : 1,
  });
  return response.data;
};

const getPerformance = async () => {
  const response = await axios.get(API_URL + "/performance");
  return response.data;
};

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
