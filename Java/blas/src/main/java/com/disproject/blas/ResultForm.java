package com.disproject.blas;

public class ResultForm {
    private float[][] sinal;
    private String str;
    private double tempo;
    private String usuario;
    private int interacoes;
    private String dataInicio;
    private String dataFinal;
    private String time;
    private String cpu;
    private String mem;
    private String metodo;

    public ResultForm(float[][] sig, String s, double time, String user, int i, String dateStart, String dateEnd,
            String metodo) {
        this.sinal = sig;
        this.str = s;
        this.tempo = time;
        this.usuario = user;
        this.interacoes = i;
        this.dataInicio = dateStart;
        this.dataFinal = dateEnd;
        this.metodo = metodo;
    }

    public ResultForm(String time, String cpu, String mem) {
        this.time = time;
        this.cpu = cpu;
        this.mem = mem;
    }

    public void setTime(String time) {
        this.time = time;
    }

    public void setMetodo(String metodo) {
        this.metodo = metodo;
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

    public void setSinal(float[][] sig) {
        this.sinal = sig;
    }

    public void setStr(String s) {
        this.str = s;
    }

    public void setTempo(double time) {
        this.tempo = time;
    }

    public void setUsuario(String user) {
        this.usuario = user;
    }

    public void setInteracoes(int i) {
        this.interacoes = i;
    }

    public void setDataInicio(String dateStart) {
        this.dataInicio = dateStart;
    }

    public void setDataFinal(String dateEnd) {
        this.dataFinal = dateEnd;
    }

    public float[][] getSinal() {
        return this.sinal;
    }

    public String getStr() {
        return this.str;
    }

    public double getTempo() {
        return this.tempo;
    }

    public String getUsuario() {
        return this.usuario;
    }

    public int getInteracoes() {
        return this.interacoes;
    }

    public String getDataInicio() {
        return this.dataInicio;
    }

    public String getDataFinal() {
        return this.dataFinal;
    }

    public String getMetodo() {
        return metodo;
    }
}
