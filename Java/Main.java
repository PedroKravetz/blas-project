import java.util.List;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import org.apache.commons.math4.legacy.linear.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
import java.io.IOException;

public class Main {
    static double[][] getMatrix(List<List<Double>> data){
        double[][] matrix = new double[data.size()] [data.get(0).size()];

        for (int i = 0; i < data.size(); i++){
            for (int j = 0; j < data.get(i).size(); j++){
                matrix[i][j] = data.get(i).get(j);
            }
        }
        return matrix;
    }
    
    static double[] getVector(List<Double> data){
        double[] vector = new double[data.size()];
        for (int i = 0; i < data.size(); i++){
            vector[i] = data.get(i);
        }
        return vector;
    }

    static double normalize_RealVector(RealVector v){
        double c = 0;
        for(int j = 0; j < v.getDimension(); j++){
            c += v.getEntry(j) * v.getEntry(j);
        }
        c = Math.sqrt(c);
        return c;
    }

    static void create_image(RealVector image, int n, String alg){
        String dir = System.getProperty("user.dir");
        dir = dir.replace("C:", "");
        int num = 0;
        if (n == 900){ // image is 30x30
            num = 30;
        }
        else if(n == 3600){ // image is 60x60
            num = 60;
        }

        int[][] pixels = new int[num][num];
        int k = 0;
        double min_value = image.getMinValue();
        double max_value = image.getMaxValue();

        for (int i = 0; i < num; i++){
            for (int j = 0; j < num; j++){
                //pixels[i][j] = (int) (Math.abs(image.getEntry(k)*255));
                pixels[i][j] = (int) (Math.abs(image.getEntry(k)*(255/max_value-min_value)));
                k++;
            }
        }

        BufferedImage bi = new BufferedImage(num, num, BufferedImage.TYPE_INT_BGR);

        for (int x = 0; x < num; x++){
            for (int y = 0; y < num; y++){
                int rgbPixel = (int) pixels[x][y]<<16 | (int) pixels[x][y]<<8 | (int) pixels[x][y];
                bi.setRGB(x, y, rgbPixel);
            }
        }

        try{
            ImageIO.write(bi, "png", new File(dir + "\\" + alg + num + ".png"));
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    static RealVector cgnr(RealVector g, RealMatrix h){
        RealVector f0 = new ArrayRealVector();
        RealVector r0 = g;
        RealVector z0 = h.preMultiply(r0);
        RealVector p0 = z0;
        int i = 0;
        while (true) {
            RealVector w = h.transpose().preMultiply(p0);
            double nz0 = normalize_RealVector(z0);
            double nw = normalize_RealVector(w);
            double a = (nz0 * nz0) / (nw * nw);
            if (i == 0){
                f0 = p0.mapMultiply(a);
            }
            else{
                f0 = f0.add(p0.mapMultiply(a));
            }
            RealVector r1 = r0.subtract(w.mapMultiply(a));
            RealVector z1 = h.preMultiply(r1);
            double nz1 = normalize_RealVector(z1);
            double b = (nz1 * nz1) / (nz0 * nz0);

            if(Math.abs(normalize_RealVector(r1) - normalize_RealVector(r0)) < 0.0001){
                // ===== Creating image =====
                create_image(f0, f0.getDimension(), "cgnr");
                return f0;
            }
            p0 = z1.add(p0.mapMultiply(b));
            z0 = z1;
            r0 = r1;
            i++;
        }
    }

    static RealVector cgne(RealVector g, RealMatrix h){
        RealVector f0 = new ArrayRealVector();
        RealVector r0 = g;
        RealVector p0 = h.preMultiply(r0);
        int i = 0;
        while (true) {
            double a = (r0.dotProduct(r0)) / (p0.dotProduct(p0));
            if (i == 0){
                f0 = p0.mapMultiply(a);
            }
            else{
                f0 = f0.add(p0.mapMultiply(a));
            }
            RealVector r1 = r0.subtract(h.transpose().preMultiply(p0).mapMultiply(a));
            double b = (r1.dotProduct(r1)) / r0.dotProduct(r0);

            if (Math.abs(normalize_RealVector(r1) - normalize_RealVector(r0)) < 0.0001){
                // ===== Creating image =====
                create_image(f0, f0.getDimension(), "cgne");
                return f0;
            }
            p0 = h.preMultiply(r1).add(p0.mapMultiply(b));
            r0 = r1;
            i++;
        }
    }

    public static void main(String[] args) throws Exception {
        String dir = System.getProperty("user.dir");
        dir = dir.replace("C:", "");

        
        // ===== Reading CSVs =====

        //List<Double> read_g1 = new ArrayList<Double>(); //delimiter: ;
        List<Double> read_g2 = new ArrayList<Double>(); //delimiter: ;
        List<Double> aux = new ArrayList<Double>();
        //List<List<Double>> read_h1 = new ArrayList<>(); // delimiter: ,
        List<List<Double>> read_h2 = new ArrayList<>(); // delimiter: ,

        /*
        // ===== 60x60 =====
        try(BufferedReader br = new BufferedReader(new FileReader(dir + "\\G-1.csv"))){
            String line;
            while((line = br.readLine()) != null){
                String[] values = line.split(";");
                for (int i = 0; i < values.length; i++){
                    read_g1.add(Double.parseDouble(values[i]));
                }
            }
        }

        try(BufferedReader br = new BufferedReader(new FileReader(dir + "\\h1.csv"))){
            String line;
            while((line = br.readLine()) != null){
                if (aux.isEmpty() == false){
                    aux.clear();
                }
                String[] values = line.split(",");
                for (int i = 0; i < values.length; i++){
                    aux.add(Double.parseDouble(values[i]));
                }
                read_h1.add(List.copyOf(aux));
            }
        }
        */

        // ===== 30x30 =====
        try(BufferedReader br = new BufferedReader(new FileReader(dir + "\\g-30x30-1.csv"))){
            String line;
            while((line = br.readLine()) != null){
                String[] values = line.split(";");
                for (int i = 0; i < values.length; i++){
                    read_g2.add(Double.parseDouble(values[i]));
                }
            }
        }

        try(BufferedReader br = new BufferedReader(new FileReader(dir + "\\h2.csv"))){
            String line;
            while((line = br.readLine()) != null){
                if (aux.isEmpty() == false){
                    aux.clear();
                }
                String[] values = line.split(",");
                for (int i = 0; i < values.length; i++){
                    aux.add(Double.parseDouble(values[i]));
                }
                read_h2.add(List.copyOf(aux));
            }
        }

        // ===== Changing list to [] =====
        //double[] vector_g1 = getVector(read_g1);
        //double[][] matrix_h1 = getMatrix(read_h1);
        double[] vector_g2 = getVector(read_g2);
        double[][] matrix_h2 = getMatrix(read_h2);

        // ===== Working with Apache Commons Math
        //RealVector g1 = new ArrayRealVector(vector_g1);
        //RealMatrix h1 = new Array2DRowRealMatrix(matrix_h1);
        RealVector g2 = new ArrayRealVector(vector_g2);
        RealMatrix h2 = new Array2DRowRealMatrix(matrix_h2);

        // CGNR and CGNE
        //RealVector result1 = cgnr(g1, h1);
        //RealVector result2 = cgne(g1, h1);
        RealVector result3 = cgnr(g2, h2);
        RealVector result4 = cgne(g2, h2);
        
        /*
        System.out.println("CGNR 60x60: ");
        System.out.println(result1);
        System.out.println("CGNE 60x60: ");
        System.out.println(result2);
        System.out.println("CGNR 30x30: ");
        System.out.println(result3);
        System.out.println("CGNE 30x30: ");
        System.out.println(result4);
        */
    }
}
