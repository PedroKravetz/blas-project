package com.disproject.blas;

public class RequestForm {
    private String usuario;
    private float[][] sinal;
    private int modelo;

    public RequestForm(String user, float[][] sig, int model){
        this.usuario = user;
        this.sinal = sig;
        this.modelo = model;
    }

    public void setUsuario(String user) {this.usuario = user;}
    public void setSinal(float[][] sig) {this.sinal = sig;}
    public void setModelo(int model) {this.modelo = model;}
    
    public String getUsuario() {return this.usuario;}
    public float[][] getSinal() {return this.sinal;}
    public int getModelo() {return this.modelo;}
}
