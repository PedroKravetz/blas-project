package com.disproject.blas;

public class PerformanceForm {
    private String time;
    private String cpu;
    private String mem;

    public PerformanceForm(String time, String cpu, String mem) {
        this.time = time;
        this.cpu = cpu;
        this.mem = mem;
    }

    public void setTime(String time) {
        this.time = time;
    }

    public void setCpu(String cpu) {
        this.cpu = cpu;
    }

    public void setMem(String mem) {
        this.mem = mem;
    }

    public String getTime() {
        return this.time;
    }

    public String getCpu() {
        return this.cpu;
    }

    public String getMem() {
        return this.mem;
    }
}
