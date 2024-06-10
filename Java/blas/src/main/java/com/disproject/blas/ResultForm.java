package com.disproject.blas;

public class ResultForm {
    private float[][] sinal;
    private double tempo;
    private String usuario;
    private int interacoes;
    private String dataInicio;
    private String dataFinal;

    public ResultForm(float[][] sig, double time, String user, int i, String dateStart, String dateEnd){
        this.sinal = sig;
        this.tempo = time;
        this.usuario = user;
        this.interacoes = i;
        this.dataInicio = dateStart;
        this.dataFinal = dateEnd;
    }

    public void setSinal(float[][] sig) {this.sinal = sig;}
    public void setTempo(double time) {this.tempo = time;}
    public void setUsuario(String user) {this.usuario = user;}
    public void setInteracoes(int i) {this.interacoes = i;}
    public void setDataInicio(String dateStart) {this.dataInicio = dateStart;}
    public void setDataFinal(String dateEnd) {this.dataFinal = dateEnd;}

    public float[][] getSinal() {return this.sinal;}
    public double getTempo() {return this.tempo;}
    public String getUsuario() {return this.usuario;}
    public int getInteracoes() {return this.interacoes;}
    public String getDataInicio() {return this.dataInicio;}
    public String getDataFinal() {return this.dataFinal;}
}
