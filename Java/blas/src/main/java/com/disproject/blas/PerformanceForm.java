package com.disproject.blas;

public class PerformanceForm {
    private double cpu;
    private double memory;

    public PerformanceForm(double CPU, double mem){
        this.cpu = CPU;
        this.memory = mem;
    }

    public void setCpu(double CPU) {this.cpu = CPU;}
    public void setMemory(double mem) {this.memory = mem;}

    public double getCpu() {return this.cpu;}
    public double getMemory() {return this.memory;}
}
