import express from "express";
import bodyParser from "body-parser";
import axios from "axios";
import fs from "fs"
import { parse } from "csv-parse"

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
  res.render("index.ejs");
});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
