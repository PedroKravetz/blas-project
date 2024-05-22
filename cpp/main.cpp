#include <iostream>
#include <vector>
#include <fstream>
#include <cmath>
using namespace std;
#include <Eigen/Dense>
using namespace Eigen;


MatrixXd openData(string fileToOpen, string delimiter)
{
    // original from: https://github.com/AleksandarHaber/Save-and-Load-Eigen-Cpp-Matrices-Arrays-to-and-from-CSV-files
    // the inspiration for creating this function was drawn from here (I did NOT copy and paste the code)
    // https://stackoverflow.com/questions/34247057/how-to-read-csv-file-and-assign-to-eigen-matrix

    // the input is the file: "fileToOpen.csv":
    // a,b,c
    // d,e,f
    // This function converts input file data into the Eigen matrix format



    // the matrix entries are stored in this variable row-wise. For example if we have the matrix:
    // M=[a b c 
    //	  d e f]
    // the entries are stored as matrixEntries=[a,b,c,d,e,f], that is the variable "matrixEntries" is a row vector
    // later on, this vector is mapped into the Eigen matrix format
    vector<double> matrixEntries;

    // in this object we store the data from the matrix
    ifstream matrixDataFile(fileToOpen);

    // this variable is used to store the row of the matrix that contains commas 
    string matrixRowString;

    // this variable is used to store the matrix entry;
    string matrixEntry;

    // this variable is used to track the number of rows
    int matrixRowNumber = 0;


    while (getline(matrixDataFile, matrixRowString)) // here we read a row by row of matrixDataFile and store every line into the string variable matrixRowString
    {
        stringstream matrixRowStringStream(matrixRowString); //convert matrixRowString that is a string to a stream variable.

        if (delimiter.find(";") != string::npos)
        {
            while (getline(matrixRowStringStream, matrixEntry, ';')) // here we read pieces of the stream matrixRowStringStream until every comma, and store the resulting character into the matrixEntry
            {
                matrixEntries.push_back(stod(matrixEntry));   //here we convert the string to double and fill in the row vector storing all the matrix entries
            }
        }
        else {
            while (getline(matrixRowStringStream, matrixEntry, ',')) // here we read pieces of the stream matrixRowStringStream until every comma, and store the resulting character into the matrixEntry
            {
                matrixEntries.push_back(stod(matrixEntry));   //here we convert the string to double and fill in the row vector storing all the matrix entries
            }
        }

        matrixRowNumber++; //update the column numbers
    }

    // here we convet the vector variable into the matrix and return the resulting object, 
    // note that matrixEntries.data() is the pointer to the first memory location at which the entries of the vector matrixEntries are stored;
    return Map<Matrix<double, Dynamic, Dynamic, RowMajor>>(matrixEntries.data(), matrixRowNumber, matrixEntries.size() / matrixRowNumber);

}

double normalize(MatrixXd l)
{
    double c = 0;
    for (int j = 0; j < l.rows(); j++)
    {
        for (int i = 0; i < l.cols(); i++)
        {
            //cout << "I: " << i << " J: " << j << " Rows: " << l.rows() << " Cols: " << l.cols() << endl;
            c += l(j, i) * l(j, i);
        }
    }
    c = sqrt(c);
    return c;
}

VectorXd cgnr(VectorXd g, MatrixXd h)
{
    VectorXd f0;
    VectorXd r0 = g;
    VectorXd z0 = h.transpose() * r0;
    VectorXd p0 = z0;

    int i = 0;
    while (1)
    {
        VectorXd w = h * p0;
        double nz0 = normalize(z0);
        double nw = normalize(w);
        double a = (nz0 * nz0) / (nw * nw);
        if (i == 0) {
            f0 = a * p0;
        }
        else
        {
            f0 = f0 + a * p0;
        }
        VectorXd r1 = r0 - a * w;
        VectorXd z1 = h.transpose() * r1;
        double nz1 = normalize(z1);
        double b = (nz1 * nz1) / (nz0 * nz0);

        if (abs(normalize(r1) - normalize(r0)) < 0.0001)
        {
            // create image here
            return f0;
        }

        p0 = z1 + b * p0;
        z0 = z1;
        r0 = r1;

        i++;
    }
}

VectorXd cgne(VectorXd g, MatrixXd h)
{
    VectorXd f0;
    VectorXd r0 = g;
    VectorXd p0 = h.transpose() * r0;

    int i = 0;
    while (1)
    {
        double a = (r0.transpose().dot(r0)) / (p0.transpose().dot(p0));
        if (i == 0) {
            f0 = a * p0;
        }
        else
        {
            f0 = f0 + a * p0;
        }
        VectorXd r1 = r0 - a * (h * p0); // r1 = r0 - a0*h.dot(p0)
        double b = (r1.transpose().dot(r1)) / (r0.transpose().dot(r0));

        if (abs(normalize(r1) - normalize(r0)) < 0.0001)
        {
            // image here
            return f0;
        }

        p0 = h.transpose() * r1 + b * p0;
        r0 = r1;
        i++;
    }
}

int main()
{
    
    MatrixXd h1 = openData("h1.csv", ",");
    MatrixXd aux1 = openData("G-1.csv", ";");
    VectorXd g1(Map<VectorXd>(aux1.data(), aux1.cols() * aux1.rows()));

    cout << "Half read..." << endl;
    
    
    MatrixXd h2 = openData("h2.csv", ",");
    MatrixXd aux2 = openData("g-30x30-1.csv", ";");
    VectorXd g2(Map<VectorXd>(aux2.data(), aux2.cols() * aux2.rows()));
    
    
    cout << "Finished reading..." << endl;

    VectorXd result1, result2, result3, result4;

    /*
    // Everything takes too much time, because there are too many rows and cols
    // (h1.transpose() * h1).transpose() -> too much time
    MatrixXd aux = h1;
    cout << "Matrix aux done" << endl;
    double c1 = normalize(aux);
    cout << "Normalize 60x60: " << endl;
    cout << c1 << endl;
    
    double regularizacao1 = -1;
    aux = h1.transpose() * g1; //aux = h1.transpose().dot(g1)
    for (int j = 0; j < aux.rows(); j++){
        for (int i = 0; i < aux.cols(); i++){
            if (abs(i) > regularizacao1) {
                regularizacao1 = abs(i);
            }
        }
    }
    regularizacao1 *= 0.1;
    cout << "Regularizar 60x60: " << endl;
    cout << regularizacao1 << endl;

    double ganho1 = 0;
    for (int x = 0; x < 65; x++) {
        if (x){
            for (int y = 0; y < 795; y++) {
                if (y) {
                    ganho1 = 100 + 0.05 * y * sqrt(y);
                }
            }
        }
    }
    cout << "Ganho 60x60: " << endl;
    cout << ganho1 << endl;
    */
    
    /*
    // Normalize takes way too much time
    // (h2.transpose() * h2).transpose() -> Takes too much time
    MatrixXd aux = h2;
    cout << "Finished this" << endl;
    double c2 = normalize(aux);
    cout << "Normalize 30x30: " << endl;
    cout << c2 << endl;
    
    double regularizacao2 = -1;
    MatrixXd aux = h2.transpose() * g2; //aux = h2.transpose().dot(g2)
    for (int j = 0; j < aux.rows(); j++) {
        for (int i = 0; i < aux.cols(); i++) {
            if (abs(i) > regularizacao2) {
                regularizacao2 = abs(i);
            }
        }
    }
    regularizacao2 *= 0.1;
    cout << "Regularizar 30x30: " << endl;
    cout << regularizacao2 << endl;
    
    double ganho2 = 0;
    for (int x = 0; x < 65; x++) {
        if (x) {
            for (int y = 0; y < 437; y++) {
                if (y) {
                    ganho2 = 100 + 0.05 * y * sqrt(y);
                }
            }
        }
    }
    cout << "Ganho 30x30: " << endl;
    cout << ganho2 << endl;
    */

    result1 = cgnr(g1, h1);
    result2 = cgne(g1, h1);

    result3 = cgnr(g2, h2);
    result4 = cgne(g2, h2);

    cout << "Result CGNR 60x60 : " << result1 << endl;
    cout << "Result CGNE 60x60 : " << result2 << endl;
    cout << "Result CGNR 30x30 : " << result3 << endl;
    cout << "Result CGNE 30x30 : " << result4 << endl;
    
}