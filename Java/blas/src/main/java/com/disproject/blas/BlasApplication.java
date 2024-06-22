package com.disproject.blas;

import java.util.concurrent.atomic.AtomicLong;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.DoubleSummaryStatistics;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;

import cern.colt.matrix.DoubleFactory1D;
import cern.colt.matrix.DoubleMatrix1D;
import cern.colt.matrix.DoubleMatrix2D;
import cern.colt.matrix.impl.DenseDoubleMatrix1D;
import cern.colt.matrix.impl.DenseDoubleMatrix2D;
import cern.colt.matrix.linalg.Algebra;
import cern.jet.math.Functions;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicLong;

@RestController
@SpringBootApplication
public class BlasApplication {

    private static DoubleMatrix2D h1;
    private static DoubleMatrix2D h2;
    private static DoubleMatrix1D g1;
    private static DoubleMatrix1D g2;
    private final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
    private static final int MAX_CONCURRENT_THREADS = 5;
    private final Semaphore semaphore = new Semaphore(MAX_CONCURRENT_THREADS);

    // return here to see if needs this
    static class ResultCG {
        private static DoubleMatrix1D f0;
        private static int iteration;

        public ResultCG(DoubleMatrix1D f, int i) {
            f0 = f;
            iteration = i;
        }

        public DoubleMatrix1D getVectorColt() {
            return f0;
        }

        public float[][] getVectorFloat() {
            double[] vecDouble = f0.toArray();
            float[][] vecFloat = new float[vecDouble.length][1];
            for (int i = 0; i < vecDouble.length; i++) {
                vecFloat[i][0] = (float) vecDouble[i];
            }
            return vecFloat;
        }

        public int getIteration() {
            return iteration;
        }
    }

    private static final String template = "Hello, %s!";
    private final AtomicLong counter = new AtomicLong();

    public record Greeting(long id, String content) {
    }

    @GetMapping("/")
    public String helloWorld() {
        return "Hello world!!";
    }

    @GetMapping("/greeting")
    public Greeting greeting(@RequestParam(value = "name", defaultValue = "world") String name) {
        return new Greeting(counter.incrementAndGet(), String.format(template, name));
    }

    @PostMapping("/blas")
    public ResultForm clientRequest(@RequestBody RequestForm input) {
        try {
            Date start, finished;
            long startTime, stopTime;
            start = new Date();
            startTime = System.currentTimeMillis();
            semaphore.acquire();
            // === Printing what was received
            System.out.println(input.getUsuario());
            for (int i = 0; i < input.getSinal().length; i++) {
                System.out.println(input.getSinal()[i]);
            }
            System.out.println(input.getModelo());
            // === Process
            ResultCG res;
            if (input.getModelo() == 1) {
                System.out.println("Option: CGNR 60x60");
                res = cgnr(g1, h1);
                System.out.println("Finished. Sending result.");
            } else {
                System.out.println("Option: CGNR 30x30");
                res = cgnr(g2, h2);
                System.out.println("Finished. Sending result.");
            }
            stopTime = System.currentTimeMillis();
            finished = new Date();
            return new ResultForm(res.getVectorFloat(), (stopTime - startTime) / 1000.0, input.getUsuario(), res.getIteration(), SDF.format(start), SDF.format(finished));
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            semaphore.release();
        }
    }

    static double[] getVector(List<Double> data) {
        double[] vector = new double[data.size()];
        for (int i = 0; i < data.size(); i++) {
            vector[i] = data.get(i);
        }
        return vector;
    }

    static void create_image(DoubleMatrix1D image, int n, String alg) {
        String dir = System.getProperty("user.dir");
        dir = dir.replace("C:", "");
        int num = 0;
        if (n == 900) { // image is 30x30
            num = 30;
        } else if (n == 3600) { // image is 60x60
            num = 60;
        }

        int[][] pixels = new int[num][num];
        int k = 0;

        DoubleSummaryStatistics stat = Arrays.stream(image.toArray()).summaryStatistics();
        double min_value = stat.getMin();
        double max_value = stat.getMax();

        for (int i = 0; i < num; i++) {
            for (int j = 0; j < num; j++) {
                //pixels[i][j] = (int) (Math.abs(image.get(k)*255));
                pixels[i][j] = (int) (Math.abs(image.get(k) * (255 / max_value - min_value)));
                k++;
            }
        }

        BufferedImage bi = new BufferedImage(num, num, BufferedImage.TYPE_INT_BGR);

        for (int x = 0; x < num; x++) {
            for (int y = 0; y < num; y++) {
                int rgbPixel = (int) pixels[x][y] << 16 | (int) pixels[x][y] << 8 | (int) pixels[x][y];
                bi.setRGB(x, y, rgbPixel);
            }
        }

        try{
            System.out.println(dir);
            ImageIO.write(bi, "png", new File(dir + "\\" + alg + num + ".png"));
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    static DoubleMatrix1D add_ColtVector(DoubleMatrix1D a, DoubleMatrix1D b) {
        DoubleMatrix1D result = new DenseDoubleMatrix1D(a.size());
        for (int i = 0; i < result.size(); i++) {
            result.set(i, a.get(i) + b.get(i));
        }
        return result;
    }

    static DoubleMatrix1D sub_ColtVector(DoubleMatrix1D a, DoubleMatrix1D b) {
        DoubleMatrix1D result = new DenseDoubleMatrix1D(a.size());
        for (int i = 0; i < result.size(); i++) {
            result.set(i, a.get(i) - b.get(i));
        }
        return result;
    }

    static double normalize_ColtVector(DoubleMatrix1D v) {
        double c = 0;
        for (int j = 0; j < v.size(); j++) {
            c += v.get(j) * v.get(j);
        }
        c = Math.sqrt(c);
        return c;
    }

    static ResultCG cgnr(DoubleMatrix1D g, DoubleMatrix2D h) {
        Algebra alg = new Algebra();

        int i = 0;
        DoubleMatrix1D f0 = new DenseDoubleMatrix1D(0);
        DoubleMatrix1D r0 = g;
        DoubleMatrix1D z0 = alg.mult(h.viewDice(), r0);
        DoubleMatrix1D p0 = z0;

        while (true) {
            i += 1;
            DoubleMatrix1D w = alg.mult(h, p0);
            double nz0 = normalize_ColtVector(z0);
            double nw = normalize_ColtVector(w);
            double a = (nz0 * nz0) / (nw * nw);
            if (i == 1) {
                f0 = p0.assign(Functions.mult(a));
            } else {
                f0 = add_ColtVector(f0, p0.assign(Functions.mult(a)));
            }
            DoubleMatrix1D r1 = sub_ColtVector(r0, w.assign(Functions.mult(a)));
            DoubleMatrix1D z1 = alg.mult(h.viewDice(), r1);
            double nz1 = normalize_ColtVector(z1);
            double b = (nz1 * nz1) / (nz0 * nz0);

            if (Math.abs(normalize_ColtVector(r1) - normalize_ColtVector(r0)) < 0.0001) {
                // ===== Creating image =====
                create_image(f0, f0.size(), "cgnr");
                return new ResultCG(f0, i);
            }

            p0 = add_ColtVector(z1, p0.assign(Functions.mult(b)));
            z0 = z1;
            r0 = r1;
        }
    }

    static ResultCG cgne(DoubleMatrix1D g, DoubleMatrix2D h) {
        Algebra alg = new Algebra();

        int i = 0;
        DoubleMatrix1D f0 = new DenseDoubleMatrix1D(0);
        DoubleMatrix1D r0 = g;
        DoubleMatrix1D p0 = alg.mult(h.viewDice(), r0);

        while (true) {
            i += 1;
            double a = r0.zDotProduct(r0) / p0.zDotProduct(p0);
            if (i == 1) {
                f0 = p0.assign(Functions.mult(a));
            } else {
                f0 = add_ColtVector(f0, p0.assign(Functions.mult(a)));
            }
            DoubleMatrix1D r1 = sub_ColtVector(r0, alg.mult(h, p0));
            double b = r1.zDotProduct(r1) / r0.zDotProduct(r0);

            if (Math.abs(normalize_ColtVector(r1) - normalize_ColtVector(r0)) < 0.0001) {
                // ===== Creating image =====
                create_image(f0, f0.size(), "cgne");
                return new ResultCG(f0, i);
            }

            p0 = add_ColtVector(alg.mult(h.viewDice(), r1), p0.assign(Functions.mult(b)));
            r0 = r1;
        }
    }

    public static void main(String[] args) throws Exception {

        String dir = System.getProperty("user.dir");
        dir = dir.replace("C:", "");

        // ===== Reading CSVs =====

        List<Double> read_g1 = new ArrayList<Double>(); //delimiter: ;
        List<Double> read_g2 = new ArrayList<Double>(); //delimiter: ;

        int h1_row = 0;
        int h1_col = 0;
        int count = 0;
        int h2_row = 0;
        int h2_col = 0;
        int count2 = 0;

        // ===== 60x60 =====

        try (BufferedReader br = new BufferedReader(new FileReader(dir + "\\G-1.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(";");
                for (int i = 0; i < values.length; i++) {
                    read_g1.add(Double.parseDouble(values[i]));
                }
            }
            br.close();
        }


        try (BufferedReader br = new BufferedReader(new FileReader(dir + "\\h1.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (count == 0) {
                    String[] values = line.split(",");
                    h1_col = values.length;
                    count += 1;
                }
                h1_row += 1;
            }
            br.close();
        }
        h1 = new DenseDoubleMatrix2D(h1_row, h1_col);
        count = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(dir + "\\h1.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                for (int i = 0; i < values.length; i++) {
                    h1.set(count, i, Double.parseDouble(values[i]));
                }
                count += 1;
            }
            br.close();
        }

        // ===== 30x30 =====

        try (BufferedReader br = new BufferedReader(new FileReader(dir + "\\g-30x30-1.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(";");
                for (int i = 0; i < values.length; i++) {
                    read_g2.add(Double.parseDouble(values[i]));
                }
            }
            br.close();
        }


        try (BufferedReader br = new BufferedReader(new FileReader(dir + "\\h2.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (count2 == 0) {
                    String[] values = line.split(",");
                    h2_col = values.length;
                    count2 += 1;
                }
                h2_row += 1;
            }
            br.close();
        }
        h2 = new DenseDoubleMatrix2D(h2_row, h2_col);
        count2 = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(dir + "\\h2.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                for (int i = 0; i < values.length; i++) {
                    h2.set(count2, i, Double.parseDouble(values[i]));
                }
                count2 += 1;
            }
            br.close();
        }

        // ===== Changing vector list to [] =====
        double[] vector_g1 = getVector(read_g1);
        read_g1.clear();
        double[] vector_g2 = getVector(read_g2);
        read_g2.clear();

        // ===== Vectors to Colt
        g1 = new DenseDoubleMatrix1D(vector_g1);
        g2 = new DenseDoubleMatrix1D(vector_g2);

        // Start application
        SpringApplication.run(BlasApplication.class, args);
    }


}
