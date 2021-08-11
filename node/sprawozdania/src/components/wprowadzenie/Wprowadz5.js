import React, { Component } from 'react';
import { Wskazanie, Tekst } from '../forms';

// Założenie kontynuacji działalności

class Wprowadz5 extends Component {

    render() {
        return (
            <div>
                <Wskazanie nazwa="p5_kontynuacja" {...this.props} etykieta="Sprawozdanie finansowe zostało sporządzone przy założeniu kontynuowania działalności gospodarczej przez jednostkę w dającej się przewidzieć przyszłości"/>
                <Wskazanie nazwa="p5_brak_zagrozen" {...this.props} etykieta="Nie istnieją okoliczności wskazujące na zagrożenie kontynuowania przez nią działalności"/>
                <Tekst nazwa="p5_opis_zagrozen" {...this.props} etykieta="Opis okoliczności wskazujących na zagrożenie kontynuowania działalności"/>
            </div>
        );
    }
}

export default Wprowadz5;