import express from "express";
import bodyParser from "body-parser";
import axios from "axios";
import fs from "fs"
import { parse } from "csv-parse"
import { Worker } from "worker_threads";

const app = express();
const port = 3000;
const API_URL = "http://localhost:5000/blas";
const CHUNK_SIZE = 1000000;

const users = ["Camilla", "Pedro", "Paulo", "Ana", "Maria", "Eduardo", "José"];
let files = [];
let arquivo = [];
  fs.createReadStream("../G-1.csv").pipe(parse({delimiter: ","})).on("data", function(row){
    arquivo.push(row);
  });
  files.push(arquivo);
  let arquivo2 = [];
  fs.createReadStream("../G-2.csv").pipe(parse({delimiter: ","})).on("data", function(row){
    arquivo2.push(row);
  });
  files.push(arquivo2);
  let arquivo3 = [];
  fs.createReadStream("../A-60x60-1.csv").pipe(parse({delimiter: ","})).on("data", function(row){
    arquivo3.push(row);
  });
  files.push(arquivo3);
  let arquivo4 = [];
  fs.createReadStream("../g-30x30-1.csv").pipe(parse({delimiter: ","})).on("data", function(row){
    arquivo4.push(row);
  });
  files.push(arquivo4);
  let arquivo5 = [];
  fs.createReadStream("../g-30x30-2.csv").pipe(parse({delimiter: ","})).on("data", function(row){
    arquivo5.push(row);
  });
  files.push(arquivo5);
  let arquivo6 = [];
  fs.createReadStream("../A-30x30-1.csv").pipe(parse({delimiter: ","})).on("data", function(row){
    arquivo6.push(row);
  });
  files.push(arquivo6);

app.use(bodyParser.urlencoded({ extended: true }));

app.get("/", (req, res) => {
  res.render("index.ejs");
});

app.get("/random", async (req, res)=>{
  const result = await axios.post(API_URL, {
    "usuario": users[0],
    "sinal": files[0],
    "modelo": 1
  }
  );
  console.log(result)
  res.redirect("/");
});

app.get('/many-tests', async (req, res) => {
  const count = parseInt(40);
  const requests = [];

  for (let i = 0; i < count; i++) {
      requests.push(getRandomDataWithDelay());
  }

  try {
      const results = await Promise.all(requests);
      res.json(results);
  } catch (error) {
      res.status(500).json({ error: 'Something went wrong' });
  }
});

const getRandomDataWithDelay = async () => {
  const delay = Math.floor(Math.random() * 5000);
  await new Promise(resolve => setTimeout(resolve, delay));
  return getRandomData();
};

const getRandomData = async () => {
  try {
      const response = await axios.post(API_URL, {
        "usuario": users[0],
        "sinal": files[0],
        "modelo": 1
      }
      );
      return response.data;
  } catch (error) {
      throw new Error('Error fetching data');
  }
};

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
