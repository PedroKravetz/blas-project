#include <iostream>
//#include <random>
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

        if(delimiter.find(";") != string::npos)
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
    VectorXd z0 = h.transpose()*r0;
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
    
    MatrixXd h2 = openData("h2.csv", ",");
    MatrixXd aux2 = openData("g-30x30-1.csv", ";");
    VectorXd g2(Map<VectorXd>(aux2.data(), aux2.cols() * aux2.rows()));
    
    VectorXd result1, result2;
    result1 = cgnr(g2, h2);
    result2 = cgne(g2, h2);
    cout << "Result CGNR 30x30 : " << result1 << endl;
    cout << "Result CGNE 30x30 : " << result2 << endl;
    
}
